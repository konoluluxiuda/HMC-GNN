#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PresRecRF-style baseline adapted to the HMC-GNN disease-herb setting.

This is not a direct reproduction of the original symptom-set PresRecRF.
It keeps the core idea, semantic + structural representation fusion, and
evaluates it under the same disease-label-disjoint protocol as HMC-GNN.
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import Config
from dataset import GraphDataManager, HerbRecDataset
from utils import set_seed


def resolve_path(path_str):
    path = Path(path_str)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return str(path)


def load_optional_node_matrix(path, expected_num_nodes, label):
    if not os.path.exists(path):
        print(f"⚠️ {label} not found: {path}")
        return None

    matrix = torch.load(path, map_location="cpu")
    if not isinstance(matrix, torch.Tensor):
        print(f"⚠️ {label} is not a tensor: {path}")
        return None
    if matrix.size(0) != expected_num_nodes:
        print(f"⚠️ {label} node mismatch: {matrix.size(0)} != {expected_num_nodes}; skipped.")
        return None

    if matrix.is_sparse:
        matrix = matrix.coalesce().float()
        print(f"✅ Loaded sparse {label}: {tuple(matrix.shape)}, nnz={matrix._nnz()}")
    else:
        matrix = matrix.float()
        print(f"✅ Loaded dense {label}: {tuple(matrix.shape)}")
    return matrix


def load_dense_feature_stack(
    feature_root,
    num_nodes,
    use_base_attr,
    use_chem_multihot,
    use_chem_semantic,
    use_disease_text,
    use_chem_fingerprint,
):
    features = []

    if use_base_attr:
        base_attr = load_optional_node_matrix(
            os.path.join(feature_root, "node_attributes.pt"),
            num_nodes,
            "base herb attribute matrix",
        )
        if base_attr is not None:
            features.append(base_attr)

    if use_chem_multihot:
        chem_multihot = load_optional_node_matrix(
            os.path.join(feature_root, "node_chem_multihot.pt"),
            num_nodes,
            "herb chemical multi-hot matrix",
        )
        if chem_multihot is not None:
            features.append(chem_multihot)

    if use_disease_text:
        disease_text = load_optional_node_matrix(
            os.path.join(feature_root, "node_disease_text.pt"),
            num_nodes,
            "disease text matrix",
        )
        if disease_text is not None:
            features.append(disease_text)

    if use_chem_semantic:
        chem_semantic = load_optional_node_matrix(
            os.path.join(feature_root, "node_chem_dense.pt"),
            num_nodes,
            "dense chemical semantic matrix",
        )
        if chem_semantic is not None:
            if use_chem_fingerprint:
                fp_pt = os.path.join(feature_root, "node_chem_fingerprint.pt")
                fp_npy = os.path.join(feature_root, "node_chem_fingerprint.npy")
                fp = None
                if os.path.exists(fp_pt):
                    fp = load_optional_node_matrix(fp_pt, num_nodes, "chemical fingerprint matrix")
                elif os.path.exists(fp_npy):
                    fp = torch.from_numpy(np.load(fp_npy)).float()
                    if fp.size(0) != num_nodes:
                        print(f"⚠️ chemical fingerprint node mismatch: {fp.size(0)} != {num_nodes}; skipped.")
                        fp = None
                    else:
                        print(f"✅ Loaded dense chemical fingerprint matrix: {tuple(fp.shape)}")
                if fp is not None:
                    chem_semantic = torch.cat([chem_semantic, fp], dim=1)
            features.append(chem_semantic)

    if not features:
        return None
    dense_features = torch.cat(features, dim=1)
    print(f"🔹 PresRecRF-style dense semantic stack: {tuple(dense_features.shape)}")
    return dense_features


def load_relation_name_to_id(graph_dir):
    relation_map_path = os.path.join(graph_dir, "relation_map.csv")
    if not os.path.exists(relation_map_path):
        return {}

    import csv

    relation_to_id = {}
    with open(relation_map_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                relation_to_id[row["relation"]] = int(row["type_id"])
            except (KeyError, TypeError, ValueError):
                continue
    return relation_to_id


def build_local_smoothing_adj(graph_dir, edge_index, edge_type, num_nodes, mode, device):
    if mode == "none":
        return None

    relation_groups = {
        "interaction": {
            "treats_disease",
            "rev_treats_disease",
        },
        "cooccurrence": {
            "treats_disease",
            "rev_treats_disease",
            "herb_disease_jaccard",
            "disease_herb_jaccard",
        },
        "gene_jaccard": {
            "herb_gene_jaccard",
            "disease_gene_jaccard",
        },
        "all_local": {
            "treats_disease",
            "rev_treats_disease",
            "herb_disease_jaccard",
            "disease_herb_jaccard",
            "herb_gene_jaccard",
            "disease_gene_jaccard",
        },
    }
    if mode not in relation_groups:
        raise ValueError(f"Unsupported local smoothing mode: {mode}")

    relation_to_id = load_relation_name_to_id(graph_dir)
    selected_relation_ids = [
        relation_to_id[name]
        for name in relation_groups[mode]
        if name in relation_to_id
    ]
    if not selected_relation_ids:
        raise RuntimeError(f"No relation ids found for local smoothing mode '{mode}'.")

    relation_id_tensor = torch.tensor(selected_relation_ids, dtype=edge_type.dtype)
    mask = torch.isin(edge_type.cpu(), relation_id_tensor)
    local_edges = edge_index.cpu()[:, mask]
    if local_edges.numel() == 0:
        raise RuntimeError(f"No edges selected for local smoothing mode '{mode}'.")

    src = local_edges[0]
    dst = local_edges[1]
    deg = torch.bincount(dst, minlength=num_nodes).float().clamp(min=1.0)
    values = 1.0 / deg[dst]
    indices = torch.stack([dst, src], dim=0)
    adj = torch.sparse_coo_tensor(indices, values, (num_nodes, num_nodes)).coalesce().to(device)

    relation_names = sorted(
        name for name in relation_groups[mode] if name in relation_to_id
    )
    print(
        "✅ PresRecRF-style local smoothing graph: "
        f"mode={mode}, edges={local_edges.size(1)}, relations={relation_names}"
    )
    return adj


class PresRecRFStyleDiseaseHerb(nn.Module):
    """
    Two-tower semantic-structural fusion baseline.

    Structural signal: learnable node ID embedding.
    Semantic signal: projected multimodal node features and optional sparse gene matrix.
    Scoring: disease tower embedding dot herb tower embedding.
    """

    def __init__(
        self,
        num_nodes,
        embedding_dim,
        dense_features=None,
        gene_matrix=None,
        dropout=0.2,
        fusion_mode="gate",
        local_smoothing_adj=None,
        smoothing_layers=1,
        smoothing_alpha=0.5,
    ):
        super().__init__()
        self.num_nodes = num_nodes
        self.embedding_dim = embedding_dim
        self.fusion_mode = fusion_mode
        self.smoothing_layers = smoothing_layers
        self.smoothing_alpha = smoothing_alpha
        self.register_buffer("dense_features", dense_features if dense_features is not None else None)
        self.register_buffer("gene_matrix", gene_matrix if gene_matrix is not None else None)
        self.register_buffer("local_smoothing_adj", local_smoothing_adj if local_smoothing_adj is not None else None)

        self.structure_embedding = nn.Embedding(num_nodes, embedding_dim)
        nn.init.xavier_uniform_(self.structure_embedding.weight)
        self.stream_names = ["structure"]

        self.dense_proj = None
        if dense_features is not None:
            self.dense_proj = nn.Sequential(
                nn.Linear(dense_features.size(1), embedding_dim),
                nn.Tanh(),
                nn.Dropout(dropout),
            )
            self.stream_names.append("dense_semantic")

        self.gene_weight = None
        self.gene_bias = None
        if gene_matrix is not None:
            self.gene_weight = nn.Parameter(torch.empty(gene_matrix.size(1), embedding_dim))
            self.gene_bias = nn.Parameter(torch.zeros(embedding_dim))
            nn.init.xavier_uniform_(self.gene_weight)
            self.stream_names.append("gene")

        self.fusion_gate = None
        if fusion_mode == "gate" and len(self.stream_names) > 1:
            self.fusion_gate = nn.Sequential(
                nn.Linear(embedding_dim * len(self.stream_names), len(self.stream_names)),
                nn.Softmax(dim=-1),
            )
        elif fusion_mode != "add":
            raise ValueError(f"Unsupported fusion mode: {fusion_mode}")

        self.disease_tower = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.Tanh(),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, embedding_dim),
        )
        self.herb_tower = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.Tanh(),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, embedding_dim),
        )

    def encode_base(self):
        streams = [self.structure_embedding.weight]

        if self.dense_proj is not None:
            streams.append(self.dense_proj(self.dense_features))

        if self.gene_matrix is not None:
            if self.gene_matrix.is_sparse:
                gene_z = torch.sparse.mm(self.gene_matrix, self.gene_weight)
            else:
                gene_z = torch.matmul(self.gene_matrix, self.gene_weight)
            streams.append(gene_z + self.gene_bias)

        if self.fusion_gate is not None:
            stacked = torch.stack(streams, dim=1)
            gate_input = torch.cat(streams, dim=-1)
            weights = self.fusion_gate(gate_input).unsqueeze(-1)
            z = torch.sum(stacked * weights, dim=1)
        else:
            z = torch.stack(streams, dim=0).sum(dim=0)

        if self.local_smoothing_adj is not None and self.smoothing_layers > 0:
            smooth_z = z
            for _ in range(self.smoothing_layers):
                smooth_z = torch.sparse.mm(self.local_smoothing_adj, smooth_z)
            z = (1.0 - self.smoothing_alpha) * z + self.smoothing_alpha * smooth_z

        return z

    def encode_disease_herb(self, disease_ids, herb_ids):
        z = self.encode_base()
        disease_emb = F.normalize(self.disease_tower(z[disease_ids]), dim=-1)
        herb_emb = F.normalize(self.herb_tower(z[herb_ids]), dim=-1)
        return disease_emb, herb_emb

    def score_pairs(self, disease_ids, herb_ids):
        disease_emb, herb_emb = self.encode_disease_herb(disease_ids, herb_ids)
        return torch.sum(disease_emb * herb_emb, dim=-1)


def bpr_loss(pos_scores, neg_scores):
    return -F.logsigmoid(pos_scores - neg_scores).mean()


def evaluate(model, eval_dict, herb_indices, k_list, device):
    model.eval()
    metrics = {k: {"p": [], "r": [], "f1": [], "ndcg": []} for k in k_list}
    candidate_tensor = torch.tensor(list(herb_indices), dtype=torch.long, device=device)

    with torch.no_grad():
        z = model.encode_base()
        herb_emb = F.normalize(model.herb_tower(z[candidate_tensor]), dim=-1)

        for disease_idx, truth_list in eval_dict.items():
            if not truth_list:
                continue
            disease_tensor = torch.tensor([disease_idx], dtype=torch.long, device=device)
            disease_emb = F.normalize(model.disease_tower(z[disease_tensor]), dim=-1)
            scores = torch.matmul(disease_emb, herb_emb.t()).squeeze(0)
            _, top_indices = torch.topk(scores, k=max(k_list))
            ranked = candidate_tensor[top_indices].cpu().numpy()
            truth = set(truth_list)

            for k in k_list:
                rec_k = set(ranked[:k])
                hits = len(rec_k & truth)
                p = hits / k
                r = hits / len(truth)
                f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

                dcg = 0.0
                for rank, item_id in enumerate(ranked[:k], start=1):
                    if item_id in truth:
                        dcg += 1.0 / np.log2(rank + 1)
                ideal_hits = min(len(truth), k)
                idcg = sum(1.0 / np.log2(rank + 1) for rank in range(1, ideal_hits + 1))
                ndcg = dcg / idcg if idcg > 0 else 0.0

                metrics[k]["p"].append(p)
                metrics[k]["r"].append(r)
                metrics[k]["f1"].append(f1)
                metrics[k]["ndcg"].append(ndcg)

    results = {}
    for k in k_list:
        results[f"Precision@{k}"] = float(np.mean(metrics[k]["p"]))
        results[f"Recall@{k}"] = float(np.mean(metrics[k]["r"]))
        results[f"F1@{k}"] = float(np.mean(metrics[k]["f1"]))
        results[f"NDCG@{k}"] = float(np.mean(metrics[k]["ndcg"]))
    return results


def print_results(title, results, k_list):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
    for k in k_list:
        print(
            f"  P@{k}={results[f'Precision@{k}']:.4f}  "
            f"R@{k}={results[f'Recall@{k}']:.4f}  "
            f"F1@{k}={results[f'F1@{k}']:.4f}  "
            f"NDCG@{k}={results[f'NDCG@{k}']:.4f}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Run PresRecRF-style baseline on HMC-GNN disease-herb data.")
    parser.add_argument(
        "--graph-dir",
        default="dataset/NEWHERB/disease_split_graph_data_percentile90/g4_gene_bridge_chemical_gene_jaccard",
        help="Graph directory containing rec_data.pt, node_map.csv and split dictionaries.",
    )
    parser.add_argument(
        "--feature-dir",
        default="auto",
        help="Feature directory. 'auto' uses graph-dir if feature files exist, otherwise etcm_graph_data/g4_gene_bridge_chemical.",
    )
    parser.add_argument("--epochs", type=int, default=Config.epochs)
    parser.add_argument("--batch-size", type=int, default=Config.batch_size)
    parser.add_argument("--lr", type=float, default=Config.lr)
    parser.add_argument("--weight-decay", type=float, default=Config.weight_decay)
    parser.add_argument("--embedding-dim", type=int, default=Config.hidden_dim)
    parser.add_argument("--dropout", type=float, default=Config.dropout)
    parser.add_argument("--fusion-mode", choices=["add", "gate"], default="gate")
    parser.add_argument(
        "--local-smoothing",
        choices=["none", "interaction", "cooccurrence", "gene_jaccard", "all_local"],
        default="none",
        help=(
            "Optional relation-agnostic local graph smoothing for the PresRecRF-style baseline. "
            "Use this as a diagnostic/fairness-enhanced baseline, not as direct PresRecRF reproduction."
        ),
    )
    parser.add_argument("--smoothing-layers", type=int, default=1)
    parser.add_argument("--smoothing-alpha", type=float, default=0.5)
    parser.add_argument("--patience", type=int, default=Config.patience)
    parser.add_argument("--eval-interval", type=int, default=Config.eval_interval)
    parser.add_argument("--seed", type=int, default=Config.seed)
    parser.add_argument("--no-base-attr", action="store_true")
    parser.add_argument("--no-chem-multihot", action="store_true")
    parser.add_argument("--no-chem-semantic", action="store_true")
    parser.add_argument("--no-disease-text", action="store_true")
    parser.add_argument("--no-chem-fingerprint", action="store_true")
    parser.add_argument("--no-gene-feature", action="store_true")
    parser.add_argument("--save-path", default="checkpoints/best_presrecrf_style.pt")
    return parser.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    graph_dir = resolve_path(args.graph_dir)
    if args.feature_dir == "auto":
        if os.path.exists(os.path.join(graph_dir, "node_attributes.pt")):
            feature_dir = graph_dir
        else:
            feature_dir = resolve_path("dataset/NEWHERB/etcm_graph_data/g4_gene_bridge_chemical")
    else:
        feature_dir = resolve_path(args.feature_dir)

    Config.REC_DATA_DIR = graph_dir
    Config.device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(Config.device)

    print("\n" + "=" * 50)
    print("PresRecRF-style Disease-Herb Baseline")
    print("=" * 50)
    print(f"Graph dir:   {graph_dir}")
    print(f"Feature dir: {feature_dir}")
    print(f"Device:      {device}")
    print("Protocol:    same disease-label-disjoint split as HMC-GNN")
    if args.local_smoothing == "none":
        print("Graph use:   no graph propagation, no gene-jaccard edges, no SSL")
    else:
        print("Graph use:   relation-agnostic local smoothing, no RGCN, no branch views, no SSL")
    print(f"Fusion:      {args.fusion_mode}")
    print(
        "Smoothing:   "
        f"{args.local_smoothing} "
        f"(layers={args.smoothing_layers}, alpha={args.smoothing_alpha})"
    )

    data_manager = GraphDataManager()
    edge_index, edge_type, train_dict, test_dict = data_manager.load_data()
    val_dict = data_manager.val_dict
    if val_dict is None:
        raise RuntimeError("This baseline expects a precomputed validation split in rec_data.pt.")
    print(f"✅ Split -> Train diseases: {len(train_dict)}, Val: {len(val_dict)}, Test: {len(test_dict)}")

    dense_features = load_dense_feature_stack(
        feature_dir,
        data_manager.num_nodes,
        use_base_attr=not args.no_base_attr,
        use_chem_multihot=not args.no_chem_multihot,
        use_chem_semantic=not args.no_chem_semantic,
        use_disease_text=not args.no_disease_text,
        use_chem_fingerprint=not args.no_chem_fingerprint,
    )
    if dense_features is not None:
        dense_features = dense_features.to(device)

    gene_matrix = None
    if not args.no_gene_feature:
        gene_matrix = load_optional_node_matrix(
            os.path.join(graph_dir, "node_gene_matrix.pt"),
            data_manager.num_nodes,
            "gene multi-hot matrix",
        )
        if gene_matrix is not None:
            gene_matrix = gene_matrix.to(device)

    local_smoothing_adj = build_local_smoothing_adj(
        graph_dir,
        edge_index,
        edge_type,
        data_manager.num_nodes,
        args.local_smoothing,
        device,
    )

    train_dataset = HerbRecDataset(train_dict, data_manager.herb_indices)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)

    model = PresRecRFStyleDiseaseHerb(
        num_nodes=data_manager.num_nodes,
        embedding_dim=args.embedding_dim,
        dense_features=dense_features,
        gene_matrix=gene_matrix,
        dropout=args.dropout,
        fusion_mode=args.fusion_mode,
        local_smoothing_adj=local_smoothing_adj,
        smoothing_layers=args.smoothing_layers,
        smoothing_alpha=args.smoothing_alpha,
    ).to(device)
    print(f"✅ PresRecRF-style fusion streams: {', '.join(model.stream_names)}")

    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    k_list = Config.top_k
    best_f1 = 0.0
    best_state = None
    no_improve = 0

    print(f"\nStart Training... (Max Epochs: {args.epochs}, Patience: {args.patience})")
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0

        for disease_ids, pos_ids, neg_ids in train_loader:
            disease_ids = disease_ids.to(device)
            pos_ids = pos_ids.to(device)
            neg_ids = neg_ids.to(device)

            optimizer.zero_grad()
            pos_scores = model.score_pairs(disease_ids, pos_ids)
            neg_scores = model.score_pairs(disease_ids, neg_ids)
            loss = bpr_loss(pos_scores, neg_scores)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % args.eval_interval == 0:
            val_results = evaluate(model, val_dict, data_manager.herb_indices, k_list, device)
            val_f1 = val_results["F1@10"]
            print(f"Epoch {epoch + 1:03d} | Loss {total_loss / len(train_loader):.4f} | Val F1@10 {val_f1:.4f}")

            if val_f1 > best_f1:
                best_f1 = val_f1
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                no_improve = 0
            else:
                no_improve += 1

            if no_improve >= args.patience:
                print(f"\n[Early Stopping] Triggered after {args.patience} evals without improvement.")
                break

    if best_state is not None:
        model.load_state_dict(best_state)
        save_path = resolve_path(args.save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save(best_state, save_path)
        print(f"✅ Loaded best validation checkpoint: F1@10={best_f1:.4f}")
        print(f"✅ Saved checkpoint: {save_path}")

    test_results = evaluate(model, test_dict, data_manager.herb_indices, k_list, device)
    print_results("Final PresRecRF-style Baseline Test Results", test_results, k_list)


if __name__ == "__main__":
    main()
