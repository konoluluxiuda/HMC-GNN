from pickle import FALSE
from re import T
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import os
import sys
import numpy as np
import csv

# 导入本地模块
from config import Config
from dataset import GraphDataManager, HerbRecDataset
from model import HMC_GNN_SSL
from utils import set_seed, Evaluator

def load_optional_node_matrix(path, expected_num_nodes, label):
    if not os.path.exists(path):
        print(f"⚠️ {label} enabled but file not found at {path}")
        return None

    matrix = torch.load(path, map_location='cpu')
    if not isinstance(matrix, torch.Tensor):
        print(f"⚠️ {label} file is not a tensor: {path}")
        return None

    if matrix.size(0) != expected_num_nodes:
        print(
            f"⚠️ {label} node count mismatch: {matrix.size(0)} != {expected_num_nodes}. "
            f"Skipped. Rebuild this feature against {Config.REC_DATA_DIR}/node_map.csv."
        )
        return None

    return matrix

def build_mrhaf_branch_views(graph_dir, edge_index, edge_type):
    """
    Build complementary MRHAF-style graph views from the current aligned node
    space.

    local branch:
      direct disease-herb recommendation edges and disease/herb Jaccard edges.

    global branch:
      external ETCM knowledge edges after removing local recommendation
      interaction edges. This avoids duplicating the same signal in both
      branches.
    """
    relation_map_path = os.path.join(graph_dir, 'relation_map.csv')
    local_relation_names = {
        'treats_disease',
        'rev_treats_disease',
        'herb_disease_jaccard',
        'disease_herb_jaccard',
        'herb_gene_jaccard',
        'disease_gene_jaccard',
    }

    relation_ids = []
    if os.path.exists(relation_map_path):
        with open(relation_map_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('relation') in local_relation_names:
                    try:
                        relation_ids.append(int(row['type_id']))
                    except (KeyError, TypeError, ValueError):
                        continue

    if not relation_ids:
        relation_ids = [0, 1, 10, 11]
        print("⚠️ Local relation map not found/incomplete; using fallback relation ids: 0,1,10,11")

    mask = torch.zeros(edge_type.size(0), dtype=torch.bool, device=edge_type.device)
    for relation_id in relation_ids:
        mask |= edge_type == relation_id

    local_edge_index = edge_index[:, mask]
    local_edge_type = edge_type[mask]
    global_mask = ~mask
    global_edge_index = edge_index[:, global_mask]
    global_edge_type = edge_type[global_mask]

    print(
        "✅ MRHAF-style local branch edges: "
        f"{local_edge_index.size(1)} / {edge_index.size(1)} "
        f"(relations: {sorted(relation_ids)})"
    )
    print(
        "✅ MRHAF-style global branch external edges: "
        f"{global_edge_index.size(1)} / {edge_index.size(1)}"
    )
    return global_edge_index, global_edge_type, local_edge_index, local_edge_type

def main():
    # =========================================================================
    # 实验配置开关 (Experimental Switches)
    # 修改这里的 True/False 来组合不同的策略
    # =========================================================================

    # 1. 图结构选择
    # - USE_TFIDF_GRAPH: 使用 TF-IDF 惩罚图以降低全局枢纽节点权重
    # - USE_FULL_GRAPH: 绕过 K-pruning (Top-K) 过滤器，保留所有由元路径引导的原始连接
    # - USE_PAPER_GRAPH: 使用标准的 (Jaccard + Top-K) 论文图数据
    # - USE_PAPER_NOLEAK_GRAPH: 使用旧 paper split，但图中移除推荐测试 disease-herb 边
    # - USE_ETCM_LEAK_GRAPH: ETCM leak diagnostic graph; train/test split unchanged, graph contains held-out disease-herb edges
    # - USE_DISEASE_SPLIT_GRAPH: 按 disease 划分 train/val/test，推荐标签边只从 train disease 构图
    # - USE_ETCM_GRAPH: 使用 ETCM-enhanced graph variants
    USE_ETCM_GRAPH = False
    USE_ETCM_LEAK_GRAPH = False
    USE_DISEASE_SPLIT_GRAPH = True
    ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical_gene_jaccard'
    USE_TFIDF_GRAPH = False
    USE_FULL_GRAPH = False
    USE_PAPER_NOLEAK_GRAPH = False
    USE_PAPER_GRAPH = False
    USE_SEMANTIC_GRAPH = False


    # 2. 特征注入选择 (多模态融合)
    # True: 注入 "性味、归经" Multi-hot 向量 (这是之前 SOTA 的核心)
    # Disease-disjoint test: use chemical information, but do not use chemical-gene relations.
    USE_BASE_ATTR = True    

    # 2.1 融合策略
    # add: 原始逐元素相加
    # gated: 类型感知门控融合
    #   Herb:    structure / attr / chem / gene
    #   Disease: structure / disease_text / gene
    FUSION_MODE = 'gated'

    # MRHAF-style branch fusion:
    #   global branch   = external ETCM knowledge RGCN (g4 without local recommendation edges)
    #   local branch    = disease-herb/Jaccard interaction RGCN
    #   semantic branch = pure type-aware fused node features without graph propagation
    USE_MRHAF_BRANCH_FUSION = True
    # sum: follows MRHAF final fusion; gate: learn per-node branch weights.
    BRANCH_FUSION_MODE = 'gate'

    # 开启跨模态对比学习
    USE_CROSS_MODAL = True
    CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
    # 权重系数
    CROSS_MODAL_WEIGHT = 0.2

    # 开启属性-化学语义对齐 (Property-Chemical Alignment)
    USE_PROP_CHEM_ALIGN = True
    PROP_CHEM_WEIGHT = 0.5

    # True: 
    USE_CHEM_DENSE = True

    # True: 融合额外化学指纹特征 (若文件存在)
    USE_CHEM_FINGERPRINT = True

    # True: 使用疾病的中文BERT文本特征，缓解疾病侧的冷启动问题
    USE_DISEASE_TEXT = True

    # Gene-as-feature: sparse node-gene multi-hot -> Linear projection -> fusion.
    # Keep external disease/herb gene side information for disease-disjoint generalization.
    USE_GENE_FEATURE = True

    # =========================================================================

    set_seed(Config.seed)
    print(f"\n{'='*40}")
    print(f"Starting Training on device: {Config.device}")
    print(f"Strategy Config:")
    print(f"  [Experiment] Manual switches in train.py")
    print(f"  [Graph] ETCM Graph: {USE_ETCM_GRAPH} ({ETCM_GRAPH_VARIANT if USE_ETCM_GRAPH else '-'})")
    print(f"  [Graph] ETCM Leak Graph: {USE_ETCM_LEAK_GRAPH} ({ETCM_GRAPH_VARIANT if USE_ETCM_LEAK_GRAPH else '-'})")
    print(f"  [Graph] Disease Split Graph: {USE_DISEASE_SPLIT_GRAPH} ({ETCM_GRAPH_VARIANT if USE_DISEASE_SPLIT_GRAPH else '-'})")
    print(f"  [Graph] Paper NoLeak Graph: {USE_PAPER_NOLEAK_GRAPH}")
    print(f"  [Graph] Paper Graph: {USE_PAPER_GRAPH}")
    print(f"  [Graph] Semantic Graph: {USE_SEMANTIC_GRAPH}")
    print(f"  [Fuse] Fusion Mode: {FUSION_MODE}")
    print(f"  [Fuse] MRHAF-style Branch Fusion: {USE_MRHAF_BRANCH_FUSION}")
    print(f"  [Fuse] Branch Fusion Mode: {BRANCH_FUSION_MODE if USE_MRHAF_BRANCH_FUSION else '-'}")
    print(f"  [Feat]  Base Attributes (Property/Meridian): {USE_BASE_ATTR}")
    print(f"  [Feat]  Deep Chemical (BERT/SMILES): {USE_CHEM_DENSE}")
    print(f"  [Feat]  Gene Feature: {USE_GENE_FEATURE}")
    print(f"  [SSL]  Cross Modal (Graph-Chem): {USE_CROSS_MODAL}")
    print(f"  [Feat] Chem Matrix File: {CHEM_MATRIX_FILENAME if USE_CROSS_MODAL else '-'}")
    print(f"  [SSL]  Property-Chem Align: {USE_PROP_CHEM_ALIGN}")
    print(f"  [Feat] Chem Fingerprint: {USE_CHEM_FINGERPRINT}")
    print(f"  [Feat] Disease Text (BERT): {USE_DISEASE_TEXT}")
    print(f"{'='*40}\n")

    # --- 1. 动态路径调整 ---
    if USE_ETCM_GRAPH:
        print(f">>> [Experiment] Loading ETCM GRAPH variant: {ETCM_GRAPH_VARIANT}")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'etcm_graph_data', ETCM_GRAPH_VARIANT)
    elif USE_ETCM_LEAK_GRAPH:
        print(f">>> [Experiment] Loading ETCM GRAPH LEAK variant: {ETCM_GRAPH_VARIANT}")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'etcm_graph_leak_data', ETCM_GRAPH_VARIANT)
    elif USE_DISEASE_SPLIT_GRAPH:
        print(f">>> [Experiment] Loading DISEASE-SPLIT GRAPH variant: {ETCM_GRAPH_VARIANT}")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'disease_split_graph_data', ETCM_GRAPH_VARIANT)
    elif USE_TFIDF_GRAPH:
        print(">>> [Experiment] Loading TF-IDF GRAPH (Anti-Hub Strategy)...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'tfidf_graph_data')
    elif USE_FULL_GRAPH:
        print(">>> [Experiment] Loading FULL GRAPH (w/o K-pruning)...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'full_graph_data')
    elif USE_PAPER_NOLEAK_GRAPH:
        print(">>> [Experiment] Loading PAPER GRAPH NO-LEAK (original split, train disease-herb edges only)...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'paper_graph_noleak_data')
    elif USE_PAPER_GRAPH:
        print(">>> [Experiment] Loading PAPER GRAPH (Jaccard + Top-K)...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'paper_graph_data')
    elif USE_SEMANTIC_GRAPH:
        print(">>> Loading SEMANTIC GRAPH data...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'semantic_data')
    else:
        print(">>> Loading ORIGINAL COLLABORATIVE GRAPH data (from preprocess_kge)...")
        Config.REC_DATA_DIR = os.path.join(Config.DATA_ROOT, 'recommendation_data')

    feature_data_dir = Config.REC_DATA_DIR
    gene_feature_data_dir = Config.REC_DATA_DIR
    if USE_PAPER_NOLEAK_GRAPH:
        feature_data_dir = os.path.join(Config.DATA_ROOT, 'paper_graph_data')
        gene_feature_data_dir = feature_data_dir
    elif USE_ETCM_LEAK_GRAPH:
        feature_data_dir = os.path.join(Config.DATA_ROOT, 'etcm_graph_data', ETCM_GRAPH_VARIANT)
        gene_feature_data_dir = feature_data_dir
    elif USE_DISEASE_SPLIT_GRAPH:
        current_variant_feature_dir = Config.REC_DATA_DIR
        if os.path.exists(os.path.join(current_variant_feature_dir, 'node_attributes.pt')):
            feature_data_dir = current_variant_feature_dir
        else:
            feature_data_dir = os.path.join(Config.DATA_ROOT, 'etcm_graph_data', 'g4_gene_bridge_chemical')
        gene_feature_data_dir = Config.REC_DATA_DIR
    print(f">>> Feature matrix directory: {feature_data_dir}")
    print(f">>> Gene feature directory: {gene_feature_data_dir}")
        
    # --- 2. 加载图结构数据 ---
    data_manager = GraphDataManager()
    try:
        # load_data 会读取 REC_DATA_DIR 下的 edge_index, edge_type, rec_data.pt
        edge_index, edge_type, train_dict, test_dict = data_manager.load_data()
        
        if data_manager.val_dict is not None:
            val_dict = data_manager.val_dict
            print(f"✅ Using precomputed split -> Train users: {len(train_dict)}, Val users: {len(val_dict)}, Test users: {len(test_dict)}")
        else:
            # [Fallback] 动态生成验证集 (Dynamic Validation Split)
            # 将原始的 20% test 按患者切分为独立的 10% Val 和 10% Test
            import random
            val_dict = {}
            new_test_dict = {}
            all_test_users = list(test_dict.keys())

            all_test_users.sort()
            random.seed(Config.seed)
            random.shuffle(all_test_users)

            half_idx = len(all_test_users) // 2
            for u in all_test_users[:half_idx]:
                val_dict[u] = test_dict[u]
            for u in all_test_users[half_idx:]:
                new_test_dict[u] = test_dict[u]

            test_dict = new_test_dict
            print(f"✅ Data Split completed -> Train users: {len(train_dict)}, Val users: {len(val_dict)}, Test users: {len(test_dict)}")
        
    except FileNotFoundError as e:
        print(f"❌ Error loading graph data: {e}")
        print("Please run 'preprocess_kge.py' or 'preprocess_semantic_graph.py' first.")
        return

        # 3. [新增] 加载深层化学特征 (BERT/ChemBERTa)
    chem_matrix = None
    if USE_CROSS_MODAL:
        chem_path = os.path.join(feature_data_dir, CHEM_MATRIX_FILENAME)
        chem_matrix = load_optional_node_matrix(chem_path, data_manager.num_nodes, "Cross-Modal Chem Matrix")
        if chem_matrix is not None:
            if USE_CHEM_FINGERPRINT:
                fp_path_pt = os.path.join(feature_data_dir, 'node_chem_fingerprint.pt')
                fp_path_npy = os.path.join(feature_data_dir, 'node_chem_fingerprint.npy')
                fp_feat = None
                if os.path.exists(fp_path_pt):
                    fp_feat = load_optional_node_matrix(fp_path_pt, data_manager.num_nodes, "Chem Fingerprint")
                elif os.path.exists(fp_path_npy):
                    fp_feat = torch.from_numpy(np.load(fp_path_npy)).float()
                    if fp_feat.size(0) != data_manager.num_nodes:
                        print(
                            f"⚠️ Chem Fingerprint node count mismatch: {fp_feat.size(0)} != {data_manager.num_nodes}. "
                            f"Skipped. Rebuild this feature against {Config.REC_DATA_DIR}/node_map.csv."
                        )
                        fp_feat = None

                if fp_feat is not None:
                    chem_matrix = torch.cat([chem_matrix, fp_feat], dim=1)
                    print(f"✅ Loaded Chem Fingerprint and concatenated: {fp_feat.shape}")
                else:
                    print("⚠️ Chem Fingerprint enabled but file not found. Using Dense only.")

            chem_matrix = chem_matrix.to(Config.device)
            print(f"✅ Loaded Cross-Modal Chem Matrix: {chem_matrix.shape}")

    # --- 3. 准备特征矩阵 (Attribute Injection) ---
    attr_tensors = []

    # A. 加载基础属性 (Property/Meridian)
    if USE_BASE_ATTR:
        base_attr_path = os.path.join(feature_data_dir, 'node_attributes.pt')
        base_attr = load_optional_node_matrix(base_attr_path, data_manager.num_nodes, "Base Attribute Matrix")
        if base_attr is not None:
            print(f"✅ Loaded Base Attributes: {base_attr.shape}")
            attr_tensors.append(base_attr)

    # B. 加载深度化学特征 (Dense BERT/SMILES)
    if USE_CHEM_DENSE:
        chem_path = os.path.join(feature_data_dir, 'node_chem_multihot.pt')
        chem_attr = load_optional_node_matrix(chem_path, data_manager.num_nodes, "Deep Chemical Features")
        if chem_attr is not None:
            print(f"✅ Loaded Deep Chemical Features: {chem_attr.shape}")
            attr_tensors.append(chem_attr)

    # C. 特征拼接
    if attr_tensors:
        # 在特征维度 (dim=1) 进行拼接
        final_attr_matrix = torch.cat(attr_tensors, dim=1).to(Config.device)
        print(f"🔹 Final Attribute Matrix Shape: {final_attr_matrix.shape}")
    else:
        final_attr_matrix = None
        print("🔹 No external attributes used (Pure Structure Learning).")

    # D. 加载疾病文本特征
    disease_matrix = None
    if USE_DISEASE_TEXT:
        disease_path = os.path.join(feature_data_dir, 'node_disease_text.pt')
        disease_matrix = load_optional_node_matrix(disease_path, data_manager.num_nodes, "Disease Text Matrix")
        if disease_matrix is not None:
            disease_matrix = disease_matrix.to(Config.device)
            print(f"✅ Loaded Disease Text Matrix: {disease_matrix.shape}")

    # E. 加载 Gene-as-feature 稀疏 multi-hot
    gene_matrix = None
    if USE_GENE_FEATURE:
        gene_path = os.path.join(gene_feature_data_dir, 'node_gene_matrix.pt')
        if os.path.exists(gene_path):
            gene_matrix = torch.load(gene_path, map_location='cpu')
            if isinstance(gene_matrix, torch.Tensor) and gene_matrix.is_sparse:
                gene_matrix = gene_matrix.coalesce()
                print(f"✅ Loaded Sparse Gene Matrix: {gene_matrix.shape}, nnz={gene_matrix._nnz()}")
            else:
                print(f"✅ Loaded Dense Gene Matrix: {gene_matrix.shape}")
            gene_matrix = gene_matrix.to(Config.device)
        else:
            print(f"⚠️ Warning: Gene feature enabled but file not found at {gene_path}")

    # --- 4. 准备 DataLoader ---
    train_dataset = HerbRecDataset(train_dict, data_manager.herb_indices)
    train_loader = DataLoader(train_dataset, batch_size=Config.batch_size, shuffle=True)

    # 将图移至 GPU
    edge_index = edge_index.to(Config.device)
    edge_type = edge_type.to(Config.device)

    local_edge_index = None
    local_edge_type = None
    global_edge_index = edge_index
    global_edge_type = edge_type
    if USE_MRHAF_BRANCH_FUSION:
        global_edge_index, global_edge_type, local_edge_index, local_edge_type = build_mrhaf_branch_views(
            Config.REC_DATA_DIR,
            edge_index,
            edge_type,
        )

    # --- 5. 初始化模型 ---
    # 注意: HMC_GNN_SSL 会自动检测 attr_matrix 的维度并初始化 Linear 层
    model = HMC_GNN_SSL(
        num_nodes=data_manager.num_nodes,
        num_relations=data_manager.num_relations,
        pretrained_features=None,    # 始终为 None (我们要保持 Random ID Embedding)
        attr_matrix=final_attr_matrix, # 传入拼接好的属性
        chem_matrix=chem_matrix,  # <--- 传入化学矩阵
        disease_matrix=disease_matrix, # <--- 传入疾病文本矩阵
        gene_matrix=gene_matrix, # <--- 传入 Gene-as-feature 矩阵
        fusion_mode=FUSION_MODE,
        herb_indices=data_manager.herb_node_indices,
        disease_indices=data_manager.disease_indices,
        use_branch_gate=USE_MRHAF_BRANCH_FUSION,
        branch_fusion_mode=BRANCH_FUSION_MODE,
    ).to(Config.device)
    if getattr(model, 'use_gated_fusion', False):
        if getattr(model, 'use_herb_gated_fusion', False):
            print(f"✅ Herb gated fusion streams: {', '.join(model.herb_gate_stream_names)}")
        if getattr(model, 'use_disease_gated_fusion', False):
            print(f"✅ Disease gated fusion streams: {', '.join(model.disease_gate_stream_names)}")
    else:
        print("ℹ️ Gated fusion disabled; enabled feature streams are fused by addition.")
    if getattr(model, 'use_branch_gate', False):
        print(f"✅ Branch-level fusion streams: {', '.join(model.branch_stream_names)} ({model.branch_fusion_mode})")

    # 优化器
    # 由于我们使用的是 Attribute Injection (拼接策略)，所有参数(GCN, Linear, Embedding)
    # 都可以使用统一的学习率，不需要分层，因为 Linear 层会自动适配特征分布。
    optimizer = optim.Adam(model.parameters(), lr=Config.lr, weight_decay=Config.weight_decay)

    evaluator = Evaluator()
    save_path = os.path.join(Config.MODEL_SAVE_PATH, 'best_model.pt')

    # --- 6. 训练循环 (带早停) ---
    best_f1 = 0.0
    no_improve_cnt = 0

    print(f"\nStart Training... (Max Epochs: {Config.epochs}, Patience: {Config.patience})")

    for epoch in range(Config.epochs):
        model.train()
        total_loss = 0.0
        torch.cuda.empty_cache() # 每轮开始清空一下显存碎片
        
        # 进度条
        with tqdm(train_loader, desc=f"Epoch {epoch+1}/{Config.epochs}", unit="batch", leave=False) as tepoch:
            for batch in tepoch:
                u, pos, neg = batch
                u, pos, neg = u.to(Config.device), pos.to(Config.device), neg.to(Config.device)
                
                optimizer.zero_grad()
                
                # --- Forward (SSL Dual Views) ---
                # perturbed=True 会触发 Edge Dropout，生成两个略微不同的视图
                x_view1 = model.forward_encoder(
                    global_edge_index,
                    global_edge_type,
                    perturbed=True,
                    local_edge_index=local_edge_index,
                    local_edge_type=local_edge_type,
                )
                x_view2 = model.forward_encoder(
                    global_edge_index,
                    global_edge_type,
                    perturbed=True,
                    local_edge_index=local_edge_index,
                    local_edge_type=local_edge_type,
                )
                
                # --- Task 1: Recommendation Loss (BPR) ---
                # 使用 View 1 的特征进行推荐
                # A. 推荐 BPR Loss
                u_emb, pos_emb, neg_emb = x_view1[u], x_view1[pos], x_view1[neg]
                pos_scores = (u_emb * pos_emb).sum(dim=1)
                neg_scores = (u_emb * neg_emb).sum(dim=1)
                bpr_loss = -torch.mean(torch.nn.functional.logsigmoid(pos_scores - neg_scores))
                
                # B. 图内扰动对比 Loss (Graph SSL)
                unique_nodes = torch.unique(torch.cat([u, pos, neg]))
                graph_ssl_loss = model.calc_ssl_loss(x_view1, x_view2, unique_nodes)
                
                # C. [新增] 跨模态对比 Loss (Cross-Modal SSL)
                cm_ssl_loss = torch.tensor(0.0, device=Config.device)
                if USE_CROSS_MODAL:
                    # 仅对草药节点计算跨模态损失
                    unique_herbs = torch.unique(torch.cat([pos, neg]))
                    # 我们用无扰动状态的特征或者 View1 的特征去逼近 Chemical
                    cm_ssl_loss = model.calc_cross_modal_loss(x_view1, unique_herbs)

                # D. 属性-化学语义对齐 Loss (Property-Chem SSL)
                pc_ssl_loss = torch.tensor(0.0, device=Config.device)
                if USE_PROP_CHEM_ALIGN:
                    unique_herbs = torch.unique(torch.cat([pos, neg]))
                    pc_ssl_loss = model.calc_property_chem_loss(unique_herbs)
                
                # 总 Loss
                loss = (
                    bpr_loss
                    + Config.ssl_reg * graph_ssl_loss
                    + CROSS_MODAL_WEIGHT * cm_ssl_loss
                    + PROP_CHEM_WEIGHT * pc_ssl_loss
                )
                
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                tepoch.set_postfix(loss=loss.item())
            
        avg_loss = total_loss / len(train_loader)
        
        # --- 7. 评估与早停 (使用验证集 Val Set) ---
        if (epoch + 1) % Config.eval_interval == 0:
            print(f"Epoch {epoch+1} | Loss: {avg_loss:.4f}")
            
            # 使用 val_dict 进行评估
            results = evaluator.evaluate(
                model, 
                val_dict, 
                data_manager.herb_indices, 
                global_edge_index,
                global_edge_type,
                local_edge_index=local_edge_index,
                local_edge_type=local_edge_type,
            )
            
            # 格式化输出
            res_str = " | ".join(
                [f"{k}: {v:.4f}" for k, v in results.items() if 'F1' in k or k == 'NDCG@10']
            )
            print(f"   >> [Validation] Metrics: {res_str}")
            
            cur_f1 = results['F1@10']
            
            # 保存最佳模型
            if cur_f1 > best_f1:
                best_f1 = cur_f1
                no_improve_cnt = 0
                torch.save(model.state_dict(), save_path)
                print(f"   >> ⭐ New Best Model! F1@10: {best_f1:.4f}")
            else:
                no_improve_cnt += 1
                print(f"   >> No improvement. Counter: {no_improve_cnt}/{Config.patience}")
                
                if no_improve_cnt >= Config.patience:
                    print(f"\n[Early Stopping] Triggered after {no_improve_cnt*Config.eval_interval} epochs without improvement.")
                    print(f"Training Finished. Best F1@10: {best_f1:.4f}")
                    break

    # --- 8. 训练结束后的最终评估 ---
    print("\n" + "=" * 50)
    print("Final HMC_GNN_SSL (NEWHERB) Test Results (same protocol)")
    print("=" * 50)

    if os.path.exists(save_path):
        model.load_state_dict(torch.load(save_path, map_location=Config.device))
    else:
        print("⚠️ best_model.pt not found, using current model weights.")

    final_results = evaluator.evaluate(
        model,
        test_dict,
        data_manager.herb_indices,
        global_edge_index,
        global_edge_type,
        local_edge_index=local_edge_index,
        local_edge_type=local_edge_type,
    )

    print("HMC_GNN_SSL (NEWHERB) Test Results:")
    for k in Config.top_k:
        pk = final_results.get(f'Precision@{k}', 0.0)
        rk = final_results.get(f'Recall@{k}', 0.0)
        fk = final_results.get(f'F1@{k}', 0.0)
        nk = final_results.get(f'NDCG@{k}', 0.0)
        print(f"  P@{k}={pk:.4f}  R@{k}={rk:.4f}  F1@{k}={fk:.4f}  NDCG@{k}={nk:.4f}")

if __name__ == "__main__":
    main()
