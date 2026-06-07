# model.py (PresRecRF Fusion Version)
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import RGCNConv
from config import Config


class WeightedRGCNConv(nn.Module):
    """
    Minimal edge-weighted RGCN layer for dense node features.

    PyG's RGCNConv does not accept per-edge weights in this environment. This
    layer keeps the same relation-specific linear message idea, while applying
    a weighted mean per relation and destination node. When all edge weights
    equal 1.0, it reduces to the standard mean aggregation used by RGCNConv.
    """
    def __init__(self, in_channels, out_channels, num_relations, bias=True, root_weight=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_relations = num_relations
        self.weight = nn.Parameter(torch.empty(num_relations, in_channels, out_channels))
        self.root = nn.Parameter(torch.empty(in_channels, out_channels)) if root_weight else None
        self.bias = nn.Parameter(torch.empty(out_channels)) if bias else None
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight)
        if self.root is not None:
            nn.init.xavier_uniform_(self.root)
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(self, x, edge_index, edge_type, edge_weight=None):
        if edge_weight is None:
            edge_weight = torch.ones(edge_type.size(0), dtype=x.dtype, device=x.device)
        else:
            edge_weight = edge_weight.to(device=x.device, dtype=x.dtype)

        out = x.new_zeros(x.size(0), self.out_channels)
        for relation_id in range(self.num_relations):
            mask = edge_type == relation_id
            if not torch.any(mask):
                continue

            src = edge_index[0, mask]
            dst = edge_index[1, mask]
            rel_weight = edge_weight[mask].unsqueeze(-1)
            msg = x[src].matmul(self.weight[relation_id]) * rel_weight

            rel_out = x.new_zeros(x.size(0), self.out_channels)
            rel_out.index_add_(0, dst, msg)

            denom = x.new_zeros(x.size(0), 1)
            denom.index_add_(0, dst, rel_weight)
            rel_out = rel_out / denom.clamp_min(1e-12)
            out = out + rel_out

        if self.root is not None:
            out = out + x.matmul(self.root)
        if self.bias is not None:
            out = out + self.bias
        return out


class HMC_GNN_SSL(nn.Module):
    def __init__(
        self,
        num_nodes,
        num_relations,
        pretrained_features=None,
        attr_matrix=None,
        chem_matrix=None,
        disease_matrix=None,
        gene_matrix=None,
        fusion_mode='add',
        herb_indices=None,
        disease_indices=None,
        use_branch_gate=False,
        branch_fusion_mode='sum',
        use_global_branch=True,
        use_local_branch=True,
        use_semantic_branch=True,
        use_edge_weighted_rgcn=False,
    ):
        super().__init__()
        
        self.emb_dim = Config.input_dim   # 128
        self.hidden_dim = Config.hidden_dim # 128
        
        # ========================================================
        # 1. 结构特征 (Structural Feature - ST)
        # ========================================================
        self.embedding = nn.Embedding(num_nodes, self.emb_dim)
        nn.init.xavier_uniform_(self.embedding.weight)
        
        # ========================================================
        # 2. 多模态语义特征维度对齐 (Semantic Feature - SE Alignment)
        # ========================================================
        self.use_attr = False
        if attr_matrix is not None:
            self.use_attr = True
            self.register_buffer('attr_matrix', attr_matrix)
            # 对齐到 emb_dim (128)
            self.attr_align = nn.Linear(attr_matrix.size(1), self.emb_dim)

        self.use_chem = False
        if chem_matrix is not None:
            self.use_chem = True
            self.register_buffer('chem_matrix', chem_matrix)
            # 对齐到 emb_dim (128)
            self.chem_align = nn.Linear(chem_matrix.size(1), self.emb_dim)
            
        self.use_disease = False
        if disease_matrix is not None:
            self.use_disease = True
            self.register_buffer('disease_matrix', disease_matrix)
            # 对齐到 emb_dim (128)
            self.disease_align = nn.Linear(disease_matrix.size(1), self.emb_dim)

        self.use_gene = False
        if gene_matrix is not None:
            self.use_gene = True
            if gene_matrix.is_sparse:
                gene_matrix = gene_matrix.coalesce()
            self.register_buffer('gene_matrix', gene_matrix)
            self.gene_align = nn.Linear(gene_matrix.size(1), self.emb_dim)

        if herb_indices is not None and len(herb_indices) > 0:
            self.register_buffer('herb_indices', torch.as_tensor(herb_indices, dtype=torch.long))
        else:
            self.herb_indices = None

        if disease_indices is not None and len(disease_indices) > 0:
            self.register_buffer('disease_indices', torch.as_tensor(disease_indices, dtype=torch.long))
        else:
            self.disease_indices = None

        self.fusion_mode = fusion_mode
        self.use_branch_gate = use_branch_gate
        self.branch_fusion_mode = branch_fusion_mode
        self.use_global_branch = use_global_branch
        self.use_local_branch = use_local_branch
        self.use_semantic_branch = use_semantic_branch
        self.use_edge_weighted_rgcn = use_edge_weighted_rgcn
        self.herb_gate_stream_names = ['structure']
        if self.use_attr:
            self.herb_gate_stream_names.append('attr')
        if self.use_chem:
            self.herb_gate_stream_names.append('chem')
        if self.use_gene:
            self.herb_gate_stream_names.append('gene')

        self.disease_gate_stream_names = ['structure']
        if self.use_disease:
            self.disease_gate_stream_names.append('disease_text')
        if self.use_gene:
            self.disease_gate_stream_names.append('gene')

        self.use_herb_gated_fusion = (
            self.fusion_mode == 'gated'
            and self.herb_indices is not None
            and len(self.herb_gate_stream_names) > 1
        )
        if self.use_herb_gated_fusion:
            self.herb_fusion_gate = nn.Sequential(
                nn.Linear(self.emb_dim * len(self.herb_gate_stream_names), self.emb_dim),
                nn.ReLU(),
                nn.Linear(self.emb_dim, len(self.herb_gate_stream_names))
            )

        self.use_disease_gated_fusion = (
            self.fusion_mode == 'gated'
            and self.disease_indices is not None
            and len(self.disease_gate_stream_names) > 1
        )
        if self.use_disease_gated_fusion:
            self.disease_fusion_gate = nn.Sequential(
                nn.Linear(self.emb_dim * len(self.disease_gate_stream_names), self.emb_dim),
                nn.ReLU(),
                nn.Linear(self.emb_dim, len(self.disease_gate_stream_names))
            )

        self.use_gated_fusion = self.use_herb_gated_fusion or self.use_disease_gated_fusion

        self.herb_semantic_stream_names = []
        if self.use_attr:
            self.herb_semantic_stream_names.append('attr')
        if self.use_chem:
            self.herb_semantic_stream_names.append('chem')
        if self.use_gene:
            self.herb_semantic_stream_names.append('gene')

        self.disease_semantic_stream_names = []
        if self.use_disease:
            self.disease_semantic_stream_names.append('disease_text')
        if self.use_gene:
            self.disease_semantic_stream_names.append('gene')

        self.use_herb_semantic_gate = (
            self.fusion_mode == 'gated'
            and self.herb_indices is not None
            and len(self.herb_semantic_stream_names) > 1
        )
        if self.use_herb_semantic_gate:
            self.herb_semantic_gate = nn.Sequential(
                nn.Linear(self.emb_dim * len(self.herb_semantic_stream_names), self.emb_dim),
                nn.ReLU(),
                nn.Linear(self.emb_dim, len(self.herb_semantic_stream_names))
            )

        self.use_disease_semantic_gate = (
            self.fusion_mode == 'gated'
            and self.disease_indices is not None
            and len(self.disease_semantic_stream_names) > 1
        )
        if self.use_disease_semantic_gate:
            self.disease_semantic_gate = nn.Sequential(
                nn.Linear(self.emb_dim * len(self.disease_semantic_stream_names), self.emb_dim),
                nn.ReLU(),
                nn.Linear(self.emb_dim, len(self.disease_semantic_stream_names))
            )

        # self.use_attr_chem_attn = self.use_attr and self.use_chem
        # if self.use_attr_chem_attn:
        #     self.attr_chem_gate = nn.Sequential(
        #         nn.Linear(self.emb_dim * 2, self.emb_dim),
        #         nn.ReLU(),
        #         nn.Linear(self.emb_dim, 2)  # 输出2个logit，对应 (attr, chem)
        #     )
        # ========================================================
        # 3. PresRecRF 融合层 (Fusion MLP)
        # ========================================================
        # 公式: Relu(W * (ST + SE1 + SE2) + b)
        self.fusion_mlp = nn.Sequential(
            nn.Linear(self.emb_dim, self.emb_dim),
            nn.ReLU()
        )

        # ========================================================
        # 4. RGCN 传播层
        # ========================================================
        # 输入已经是融合并对齐好的 emb_dim (128)
        self.conv1 = RGCNConv(self.emb_dim, self.hidden_dim, num_relations)
        self.bn1 = nn.BatchNorm1d(self.hidden_dim)
        
        self.conv2 = RGCNConv(self.hidden_dim, self.hidden_dim, num_relations)
        self.bn2 = nn.BatchNorm1d(self.hidden_dim)
        
        self.dropout = nn.Dropout(Config.dropout)
        
        # Layer Aggregation Fusion
        self.layer_fusion = nn.Linear(self.hidden_dim * 2, self.hidden_dim)

        # ========================================================
        # 5. MRHAF-style local/global/semantic branch fusion
        # ========================================================
        # global branch: existing RGCN over the full heterogeneous graph.
        # local branch: a second RGCN over disease-herb/Jaccard interaction edges.
        # semantic branch: type-aware fused node semantics without graph propagation.
        if self.use_branch_gate:
            if self.use_local_branch:
                local_conv_cls = WeightedRGCNConv if self.use_edge_weighted_rgcn else RGCNConv
                self.local_conv1 = local_conv_cls(self.emb_dim, self.hidden_dim, num_relations)
                self.local_bn1 = nn.BatchNorm1d(self.hidden_dim)
                self.local_conv2 = local_conv_cls(self.hidden_dim, self.hidden_dim, num_relations)
                self.local_bn2 = nn.BatchNorm1d(self.hidden_dim)
                self.local_layer_fusion = nn.Linear(self.hidden_dim * 2, self.hidden_dim)

            if self.use_semantic_branch:
                self.semantic_proj = nn.Sequential(
                    nn.Linear(self.emb_dim, self.hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(Config.dropout),
                )

            self.branch_stream_names = []
            if self.use_global_branch:
                self.branch_stream_names.append('global')
            if self.use_local_branch:
                self.branch_stream_names.append('local')
            if self.use_semantic_branch:
                self.branch_stream_names.append('semantic')
            if not self.branch_stream_names:
                self.branch_stream_names.append('global')
                self.use_global_branch = True

            if self.branch_fusion_mode == 'gate':
                self.herb_branch_gate = nn.Sequential(
                    nn.Linear(self.hidden_dim * len(self.branch_stream_names), self.hidden_dim),
                    nn.ReLU(),
                    nn.Linear(self.hidden_dim, len(self.branch_stream_names))
                )
                self.disease_branch_gate = nn.Sequential(
                    nn.Linear(self.hidden_dim * len(self.branch_stream_names), self.hidden_dim),
                    nn.ReLU(),
                    nn.Linear(self.hidden_dim, len(self.branch_stream_names))
                )

    def _project_feature_matrix(self, feature_matrix, linear_layer):
        if feature_matrix.is_sparse:
            projected = torch.sparse.mm(feature_matrix, linear_layer.weight.t())
            if linear_layer.bias is not None:
                projected = projected + linear_layer.bias
            return projected
        return linear_layer(feature_matrix)

    def _apply_node_gate(self, x_fused, node_indices, streams, gate):
        if node_indices is None or node_indices.numel() == 0:
            return x_fused
        node_streams = [stream[node_indices] for stream in streams]
        fusion_in = torch.cat(node_streams, dim=-1)
        fusion_logits = gate(fusion_in)
        fusion_w = F.softmax(fusion_logits, dim=-1)
        node_fused = sum(
            fusion_w[:, idx:idx + 1] * stream
            for idx, stream in enumerate(node_streams)
        )
        x_updated = x_fused.clone()
        x_updated[node_indices] = node_fused
        return x_updated

    def _build_fused_input(self):
        # 1. 获取结构特征 (ST)
        x_st = self.embedding.weight # [N, 128]
        
        # 2. 维度对齐，并根据节点类型使用加和或类型感知 gate 融合
        x_attr = None
        x_chem = None
        x_disease = None
        x_gene = None

        if self.use_attr:
            # 投影到 128 维
            attr_buf = self.attr_matrix
            if isinstance(attr_buf, torch.Tensor):
                x_attr = self.attr_align(attr_buf)
            
        if self.use_chem:
            # 投影到 128 维
            chem_buf = self.chem_matrix
            if isinstance(chem_buf, torch.Tensor):
                x_chem = self.chem_align(chem_buf)

        if self.use_disease:
            disease_buf = self.disease_matrix
            if isinstance(disease_buf, torch.Tensor):
                x_disease = self._project_feature_matrix(disease_buf, self.disease_align)

        if self.use_gene:
            gene_buf = self.gene_matrix
            if isinstance(gene_buf, torch.Tensor):
                x_gene = self._project_feature_matrix(gene_buf, self.gene_align)

        add_streams = [x_st]
        for stream in [x_attr, x_chem, x_disease, x_gene]:
            if stream is not None:
                add_streams.append(stream)
        x_fused = sum(add_streams)

        if self.use_herb_gated_fusion:
            herb_streams = [x_st]
            if x_attr is not None:
                herb_streams.append(x_attr)
            if x_chem is not None:
                herb_streams.append(x_chem)
            if x_gene is not None:
                herb_streams.append(x_gene)
            x_fused = self._apply_node_gate(
                x_fused,
                self.herb_indices,
                herb_streams,
                self.herb_fusion_gate,
            )

        if self.use_disease_gated_fusion:
            disease_streams = [x_st]
            if x_disease is not None:
                disease_streams.append(x_disease)
            if x_gene is not None:
                disease_streams.append(x_gene)
            x_fused = self._apply_node_gate(
                x_fused,
                self.disease_indices,
                disease_streams,
                self.disease_fusion_gate,
            )
            
        # # 1. 结构特征
        # x_st = self.embedding.weight  # [N, emb_dim]

        # # 2. 先分别对齐各模态
        # x_attr_aligned = None
        # x_chem_aligned = None

        # if self.use_attr:
        #     x_attr_aligned = self.attr_align(self.attr_matrix)   # [N, emb_dim]

        # if self.use_chem:
        #     x_chem_aligned = self.chem_align(self.chem_matrix)   # [N, emb_dim]

        # # 3. 模态融合
        # if self.use_attr_chem_attn:
        #     # 两个模态都存在，用 attention/gating 来融合
        #     # 拼接后过一层 MLP -> 得到每个节点两个权重
        #     cat = torch.cat([x_attr_aligned, x_chem_aligned], dim=-1)  # [N, 2*emb_dim]
        #     logits = self.attr_chem_gate(cat)                          # [N, 2]
        #     weights = F.softmax(logits, dim=-1)                        # [N, 2]

        #     w_attr = weights[:, 0].unsqueeze(-1)   # [N, 1]
        #     w_chem = weights[:, 1].unsqueeze(-1)   # [N, 1]

        #     x_sem = w_attr * x_attr_aligned + w_chem * x_chem_aligned  # [N, emb_dim]
        #     x_fused = x_st + x_sem
        # else:
        #     # 只有一个模态或都没有，则退回原来的简单加和
        #     x_fused = x_st
        #     if x_attr_aligned is not None:
        #         x_fused = x_fused + x_attr_aligned
        #     if x_chem_aligned is not None:
        #         x_fused = x_fused + x_chem_aligned
        # 3. PresRecRF 非线性融合映射 (ReLU MLP)
        # 此时 x_input 就是论文中的 e_i
        return self.fusion_mlp(x_fused)

    def _build_pure_semantic_input(self):
        x_attr = None
        x_chem = None
        x_disease = None
        x_gene = None

        if self.use_attr:
            attr_buf = self.attr_matrix
            if isinstance(attr_buf, torch.Tensor):
                x_attr = self.attr_align(attr_buf)

        if self.use_chem:
            chem_buf = self.chem_matrix
            if isinstance(chem_buf, torch.Tensor):
                x_chem = self.chem_align(chem_buf)

        if self.use_disease:
            disease_buf = self.disease_matrix
            if isinstance(disease_buf, torch.Tensor):
                x_disease = self._project_feature_matrix(disease_buf, self.disease_align)

        if self.use_gene:
            gene_buf = self.gene_matrix
            if isinstance(gene_buf, torch.Tensor):
                x_gene = self._project_feature_matrix(gene_buf, self.gene_align)

        semantic_streams = [stream for stream in [x_attr, x_chem, x_disease, x_gene] if stream is not None]
        if semantic_streams:
            x_semantic = sum(semantic_streams)
        else:
            x_semantic = torch.zeros_like(self.embedding.weight)

        if self.use_herb_semantic_gate:
            herb_streams = []
            if x_attr is not None:
                herb_streams.append(x_attr)
            if x_chem is not None:
                herb_streams.append(x_chem)
            if x_gene is not None:
                herb_streams.append(x_gene)
            if len(herb_streams) > 1:
                x_semantic = self._apply_node_gate(
                    x_semantic,
                    self.herb_indices,
                    herb_streams,
                    self.herb_semantic_gate,
                )

        if self.use_disease_semantic_gate:
            disease_streams = []
            if x_disease is not None:
                disease_streams.append(x_disease)
            if x_gene is not None:
                disease_streams.append(x_gene)
            if len(disease_streams) > 1:
                x_semantic = self._apply_node_gate(
                    x_semantic,
                    self.disease_indices,
                    disease_streams,
                    self.disease_semantic_gate,
                )

        return self.fusion_mlp(x_semantic)

    def _run_rgcn_stack(
        self,
        x_input,
        edge_index,
        edge_type,
        perturbed,
        conv1,
        bn1,
        conv2,
        bn2,
        layer_fusion,
        edge_weight=None,
    ):
        # ==================================
        # 下面是常规的图传播 (Graph Propagation)
        # ==================================
        if perturbed and self.training:
            mask = torch.rand(edge_index.size(1), device=edge_index.device) > Config.edge_drop_rate
            edge_index = edge_index[:, mask]
            edge_type = edge_type[mask]
            if edge_weight is not None:
                edge_weight = edge_weight[mask]

        if isinstance(conv1, WeightedRGCNConv):
            x1 = conv1(x_input, edge_index, edge_type, edge_weight=edge_weight)
        else:
            x1 = conv1(x_input, edge_index, edge_type)
        x1 = bn1(x1)
        x1 = F.elu(x1)
        x1 = self.dropout(x1)
        
        if isinstance(conv2, WeightedRGCNConv):
            x2 = conv2(x1, edge_index, edge_type, edge_weight=edge_weight)
        else:
            x2 = conv2(x1, edge_index, edge_type)
        x2 = bn2(x2)
        x2 = F.elu(x2)
        x2 = self.dropout(x2)
        
        x_concat = torch.cat([x1, x2], dim=-1)
        return layer_fusion(x_concat)

    def _apply_branch_fusion(self, streams):
        if self.branch_fusion_mode == 'sum':
            return sum(streams)

        if self.branch_fusion_mode != 'gate':
            return sum(streams) / len(streams)

        x_fused = sum(streams) / len(streams)

        if self.herb_indices is not None and self.herb_indices.numel() > 0:
            x_fused = self._apply_node_gate(
                x_fused,
                self.herb_indices,
                streams,
                self.herb_branch_gate,
            )

        if self.disease_indices is not None and self.disease_indices.numel() > 0:
            x_fused = self._apply_node_gate(
                x_fused,
                self.disease_indices,
                streams,
                self.disease_branch_gate,
            )

        return x_fused

    def forward_encoder(
        self,
        edge_index,
        edge_type,
        perturbed=False,
        local_edge_index=None,
        local_edge_type=None,
        edge_weight=None,
        local_edge_weight=None,
    ):
        x_input = self._build_fused_input()

        if not self.use_branch_gate:
            return self._run_rgcn_stack(
                x_input,
                edge_index,
                edge_type,
                perturbed,
                self.conv1,
                self.bn1,
                self.conv2,
                self.bn2,
                self.layer_fusion,
                edge_weight=edge_weight,
            )

        if local_edge_index is None or local_edge_type is None:
            local_edge_index = edge_index
            local_edge_type = edge_type
            local_edge_weight = edge_weight

        streams = []
        if self.use_global_branch:
            streams.append(self._run_rgcn_stack(
                x_input,
                edge_index,
                edge_type,
                perturbed,
                self.conv1,
                self.bn1,
                self.conv2,
                self.bn2,
                self.layer_fusion,
                edge_weight=edge_weight,
            ))

        if self.use_local_branch:
            streams.append(self._run_rgcn_stack(
                x_input,
                local_edge_index,
                local_edge_type,
                perturbed,
                self.local_conv1,
                self.local_bn1,
                self.local_conv2,
                self.local_bn2,
                self.local_layer_fusion,
                edge_weight=local_edge_weight,
            ))

        if self.use_semantic_branch:
            x_semantic_input = self._build_pure_semantic_input()
            streams.append(self.semantic_proj(x_semantic_input))

        return self._apply_branch_fusion(streams)

    # calc_ssl_loss 保持不变
    def calc_ssl_loss(self, x_view1, x_view2, unique_nodes):
        z1 = F.normalize(x_view1[unique_nodes], dim=1)
        z2 = F.normalize(x_view2[unique_nodes], dim=1)
        sim_matrix = torch.matmul(z1, z2.t()) / Config.ssl_temp
        labels = torch.arange(unique_nodes.size(0), device=unique_nodes.device)
        return F.cross_entropy(sim_matrix, labels)
    
    def calc_cross_modal_loss(self, x_gnn, herb_indices):
        """
        跨模态对比学习损失 (Cross-Modal SSL Loss)
        功能：将 GNN 提取的图语义特征与原始化学成分模态特征进行对齐。
        """
        if not self.use_chem:
            return torch.tensor(0.0, device=x_gnn.device)

        # 1. 提取 GNN 视图下的特征并归一化
        # x_gnn 是 forward_encoder 输出的 [N, 128]
        z_gnn = F.normalize(x_gnn[herb_indices], dim=1)

        # 2. 提取原始化学模态特征，投影到 128 维并归一化
        # 复用 init 中的 chem_align 映射层，确保空间一致
        chem_buf = self.chem_matrix
        if not isinstance(chem_buf, torch.Tensor):
            return torch.tensor(0.0, device=x_gnn.device)

        raw_chem_feat = chem_buf[herb_indices]
        z_chem = F.normalize(self.chem_align(raw_chem_feat), dim=1)

        # 3. 计算 InfoNCE 对比损失
        # 计算两组特征的余弦相似度矩阵 [Batch_Size, Batch_Size]
        # 期望：同一个 herb 的图特征和化学特征相似度最高（对角线）
        sim_matrix = torch.matmul(z_gnn, z_chem.t()) / Config.ssl_temp
        
        # 4. 生成标签（对角线即为正样本对）
        labels = torch.arange(herb_indices.size(0), device=herb_indices.device)
        
        # 5. 使用交叉熵计算对比损失
        cm_loss = F.cross_entropy(sim_matrix, labels)
        
        return cm_loss

    def calc_property_chem_loss(self, herb_indices):
        """
        属性-化学跨模态对齐损失。
        目标：让同一 herb 的性味归经表征与化学表征在共享空间中更接近。
        """
        if (not self.use_attr) or (not self.use_chem):
            return torch.tensor(0.0, device=self.embedding.weight.device)

        attr_buf = self.attr_matrix
        chem_buf = self.chem_matrix
        if (not isinstance(attr_buf, torch.Tensor)) or (not isinstance(chem_buf, torch.Tensor)):
            return torch.tensor(0.0, device=self.embedding.weight.device)

        z_attr = F.normalize(self.attr_align(attr_buf[herb_indices]), dim=1)
        z_chem = F.normalize(self.chem_align(chem_buf[herb_indices]), dim=1)

        sim_matrix = torch.matmul(z_attr, z_chem.t()) / Config.ssl_temp
        labels = torch.arange(herb_indices.size(0), device=herb_indices.device)
        return F.cross_entropy(sim_matrix, labels)
