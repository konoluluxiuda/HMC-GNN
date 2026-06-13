#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic recommender baselines for HMC-GNN.

This script evaluates two classic recommendation baselines under the same
disease-label-disjoint protocol as HMC-GNN:

1. BPR-MF: Bayesian Personalized Ranking matrix factorization.
2. LightGCN: lightweight graph collaborative filtering on the disease-herb
   interaction graph.

Both baselines intentionally use only train disease-herb interactions. This
keeps their core collaborative-filtering assumptions intact and provides a
clean lower-level comparison against knowledge-aware HMC-GNN variants.
"""

import argparse
import csv
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


def load_relation_name_to_id(graph_dir):
    relation_map_path = os.path.join(graph_dir, "relation_map.csv")
    relation_to_id = {}
    with open(relation_map_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                relation_to_id[row["relation"]] = int(row["type_id"])
            except (KeyError, TypeError, ValueError):
                continue
    return relation_to_id


def select_interaction_edges(graph_dir, edge_index, edge_type):
    relation_to_id = load_relation_name_to_id(graph_dir)
    relation_ids = [
        relation_to_id[name]
        for name in ("treats_disease", "rev_treats_disease")
        if name in relation_to_id
    ]
    if not relation_ids:
        raise RuntimeError("Could not find treats_disease / rev_treats_disease relations.")

    relation_id_tensor = torch.tensor(relation_ids, dtype=edge_type.dtype)
    mask = torch.isin(edge_type.cpu(), relation_id_tensor)
    selected = edge_index.cpu()[:, mask]
    if selected.numel() == 0:
        raise RuntimeError("No disease-herb interaction edges selected.")
    print(f"✅ Interaction graph edges: {selected.size(1)}")
    return selected


def build_symmetric_norm_adj(edge_index, num_nodes, device):
    src = edge_index[0]
    dst = edge_index[1]
    deg = torch.bincount(src, minlength=num_nodes).float().clamp(min=1.0)
    values = 1.0 / torch.sqrt(deg[src] * deg[dst])
    adj = torch.sparse_coo_tensor(
        torch.stack([src, dst], dim=0),
        values,
        (num_nodes, num_nodes),
    ).coalesce()
    return adj.to(device)


class BPRMF(nn.Module):
    def __init__(self, num_nodes, embedding_dim):
        super().__init__()
        self.embedding = nn.Embedding(num_nodes, embedding_dim)
        nn.init.xavier_uniform_(self.embedding.weight)

    def encode(self):
        return self.embedding.weight

    def score_pairs(self, disease_ids, herb_ids):
        z = self.encode()
        return torch.sum(z[disease_ids] * z[herb_ids], dim=-1)


class LightGCN(nn.Module):
    def __init__(self, num_nodes, embedding_dim, num_layers=3):
        super().__init__()
        self.embedding = nn.Embedding(num_nodes, embedding_dim)
        self.num_layers = num_layers
        nn.init.xavier_uniform_(self.embedding.weight)

    def encode(self, adj):
        z = self.embedding.weight
        all_z = [z]
        for _ in range(self.num_layers):
            z = torch.sparse.mm(adj, z)
            all_z.append(z)
        return torch.stack(all_z, dim=0).mean(dim=0)

    def score_pairs(self, disease_ids, herb_ids, adj):
        z = self.encode(adj)
        return torch.sum(z[disease_ids] * z[herb_ids], dim=-1)


def bpr_loss(pos_scores, neg_scores):
    return -F.logsigmoid(pos_scores - neg_scores).mean()


def evaluate(model, eval_dict, herb_indices, k_list, device, adj=None):
    model.eval()
    metrics = {k: {"p": [], "r": [], "f1": [], "ndcg": []} for k in k_list}
    candidate_tensor = torch.tensor(list(herb_indices), dtype=torch.long, device=device)

    with torch.no_grad():
        z = model.encode(adj) if adj is not None else model.encode()
        herb_z = z[candidate_tensor]

        for disease_idx, truth_list in eval_dict.items():
            if not truth_list:
                continue
            disease_z = z[disease_idx].unsqueeze(0)
            scores = torch.matmul(disease_z, herb_z.t()).squeeze(0)
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
    parser = argparse.ArgumentParser(description="Run BPR-MF or LightGCN on HMC-GNN disease-herb data.")
    parser.add_argument("--model", choices=["bprmf", "lightgcn"], required=True)
    parser.add_argument(
        "--graph-dir",
        default="dataset/NEWHERB/disease_split_graph_data_percentile90/g4_gene_bridge_chemical_gene_jaccard",
    )
    parser.add_argument("--epochs", type=int, default=Config.epochs)
    parser.add_argument("--batch-size", type=int, default=Config.batch_size)
    parser.add_argument("--lr", type=float, default=Config.lr)
    parser.add_argument("--weight-decay", type=float, default=Config.weight_decay)
    parser.add_argument("--embedding-dim", type=int, default=Config.hidden_dim)
    parser.add_argument("--lightgcn-layers", type=int, default=3)
    parser.add_argument("--patience", type=int, default=Config.patience)
    parser.add_argument("--eval-interval", type=int, default=Config.eval_interval)
    parser.add_argument("--seed", type=int, default=Config.seed)
    parser.add_argument("--save-path", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    graph_dir = resolve_path(args.graph_dir)
    Config.REC_DATA_DIR = graph_dir
    Config.device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(Config.device)

    print("\n" + "=" * 50)
    print(f"{args.model.upper()} Baseline")
    print("=" * 50)
    print(f"Graph dir:  {graph_dir}")
    print(f"Device:     {device}")
    print("Protocol:   same disease-label-disjoint split as HMC-GNN")
    print("Data use:   train disease-herb interactions only")
    if args.model == "lightgcn":
        print(f"LightGCN layers: {args.lightgcn_layers}")

    data_manager = GraphDataManager()
    edge_index, edge_type, train_dict, test_dict = data_manager.load_data()
    val_dict = data_manager.val_dict
    if val_dict is None:
        raise RuntimeError("This baseline expects a precomputed validation split in rec_data.pt.")
    print(f"✅ Split -> Train diseases: {len(train_dict)}, Val: {len(val_dict)}, Test: {len(test_dict)}")

    adj = None
    if args.model == "lightgcn":
        interaction_edges = select_interaction_edges(graph_dir, edge_index, edge_type)
        adj = build_symmetric_norm_adj(interaction_edges, data_manager.num_nodes, device)

    train_dataset = HerbRecDataset(train_dict, data_manager.herb_indices)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)

    if args.model == "bprmf":
        model = BPRMF(data_manager.num_nodes, args.embedding_dim).to(device)
    else:
        model = LightGCN(data_manager.num_nodes, args.embedding_dim, args.lightgcn_layers).to(device)

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
            if args.model == "lightgcn":
                pos_scores = model.score_pairs(disease_ids, pos_ids, adj)
                neg_scores = model.score_pairs(disease_ids, neg_ids, adj)
            else:
                pos_scores = model.score_pairs(disease_ids, pos_ids)
                neg_scores = model.score_pairs(disease_ids, neg_ids)
            loss = bpr_loss(pos_scores, neg_scores)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % args.eval_interval == 0:
            val_results = evaluate(model, val_dict, data_manager.herb_indices, k_list, device, adj=adj)
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
        if args.save_path is None:
            save_name = f"best_{args.model}.pt"
            save_path = os.path.join(Config.MODEL_SAVE_PATH, save_name)
        else:
            save_path = resolve_path(args.save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save(best_state, save_path)
        print(f"✅ Loaded best validation checkpoint: F1@10={best_f1:.4f}")
        print(f"✅ Saved checkpoint: {save_path}")

    test_results = evaluate(model, test_dict, data_manager.herb_indices, k_list, device, adj=adj)
    print_results(f"Final {args.model.upper()} Baseline Test Results", test_results, k_list)


if __name__ == "__main__":
    main()
