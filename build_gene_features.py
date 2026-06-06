import argparse
import os

import pandas as pd
import torch


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(CURRENT_DIR, "dataset", "NEWHERB")
ENTITY_DIR = os.path.join(DATA_ROOT, "entities")
RELATION_DIR = os.path.join(DATA_ROOT, "relation")
GRAPH_ROOT = os.path.join(DATA_ROOT, "etcm_graph_data")


def clean_id(value):
    return str(value).replace("\ufeff", "").strip()


def normalize_header(name):
    return clean_id(name).upper()


def load_gene_columns():
    path = os.path.join(ENTITY_DIR, "gene_completed_etcm.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [clean_id(c) for c in df.columns]
    if "id" not in df.columns:
        raise ValueError(f"Missing id column in {path}")
    gene_ids = [clean_id(gene_id) for gene_id in df["id"]]
    return gene_ids, {gene_id: idx for idx, gene_id in enumerate(gene_ids)}


def load_node_map(graph_dir):
    path = os.path.join(graph_dir, "node_map.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [clean_id(c) for c in df.columns]
    required = {"node_id", "node_index"}
    if not required.issubset(df.columns):
        raise ValueError(f"node_map.csv must contain {required}: {path}")
    node_to_idx = {
        clean_id(row["node_id"]): int(row["node_index"])
        for _, row in df.iterrows()
    }
    return node_to_idx, len(df)


def load_relation_pairs(filename):
    path = os.path.join(RELATION_DIR, filename)
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [normalize_header(c) for c in df.columns]
    start_col = ":START_ID" if ":START_ID" in df.columns else df.columns[0]
    end_col = ":END_ID" if ":END_ID" in df.columns else df.columns[1]
    pairs = []
    for start_id, end_id in zip(df[start_col], df[end_col]):
        start_id = clean_id(start_id)
        end_id = clean_id(end_id)
        if start_id and end_id:
            pairs.append((start_id, end_id))
    return pairs


def build_sparse_feature(pairs, node_to_idx, gene_to_col, num_nodes, num_genes):
    coords = set()
    missing_start = 0
    missing_gene = 0

    for start_id, gene_id in pairs:
        row = node_to_idx.get(start_id)
        col = gene_to_col.get(gene_id)
        if row is None:
            missing_start += 1
            continue
        if col is None:
            missing_gene += 1
            continue
        coords.add((row, col))

    if coords:
        sorted_coords = sorted(coords)
        indices = torch.tensor(sorted_coords, dtype=torch.long).t().contiguous()
        values = torch.ones(len(sorted_coords), dtype=torch.float32)
    else:
        indices = torch.empty((2, 0), dtype=torch.long)
        values = torch.empty((0,), dtype=torch.float32)

    tensor = torch.sparse_coo_tensor(
        indices,
        values,
        size=(num_nodes, num_genes),
        dtype=torch.float32,
    ).coalesce()
    return tensor, {
        "nnz": int(tensor._nnz()),
        "missing_start": missing_start,
        "missing_gene": missing_gene,
    }


def save_variant_features(graph_dir, gene_ids, gene_to_col):
    node_to_idx, num_nodes = load_node_map(graph_dir)
    num_genes = len(gene_ids)

    disease_pairs = load_relation_pairs("diseaseTOgene_etcm_matched.csv")
    herb_pairs = load_relation_pairs("herbTOgene_etcm_matched.csv")

    disease_gene, disease_stats = build_sparse_feature(
        disease_pairs, node_to_idx, gene_to_col, num_nodes, num_genes
    )
    herb_gene, herb_stats = build_sparse_feature(
        herb_pairs, node_to_idx, gene_to_col, num_nodes, num_genes
    )
    combined_gene = torch.sparse_coo_tensor(
        torch.cat([disease_gene.indices(), herb_gene.indices()], dim=1),
        torch.cat([disease_gene.values(), herb_gene.values()]),
        size=(num_nodes, num_genes),
        dtype=torch.float32,
    ).coalesce()

    torch.save(disease_gene, os.path.join(graph_dir, "node_disease_gene.pt"))
    torch.save(herb_gene, os.path.join(graph_dir, "node_herb_gene.pt"))
    torch.save(combined_gene, os.path.join(graph_dir, "node_gene_matrix.pt"))

    pd.DataFrame({"gene_index": range(num_genes), "gene_id": gene_ids}).to_csv(
        os.path.join(graph_dir, "gene_feature_map.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    summary = [
        {"item": "num_nodes", "count": num_nodes, "note": ""},
        {"item": "num_genes", "count": num_genes, "note": ""},
        {"item": "disease_gene_nnz", "count": disease_stats["nnz"], "note": "node_disease_gene.pt"},
        {"item": "herb_gene_nnz", "count": herb_stats["nnz"], "note": "node_herb_gene.pt"},
        {"item": "combined_gene_nnz", "count": int(combined_gene._nnz()), "note": "node_gene_matrix.pt"},
        {"item": "disease_missing_start", "count": disease_stats["missing_start"], "note": ""},
        {"item": "disease_missing_gene", "count": disease_stats["missing_gene"], "note": ""},
        {"item": "herb_missing_start", "count": herb_stats["missing_start"], "note": ""},
        {"item": "herb_missing_gene", "count": herb_stats["missing_gene"], "note": ""},
    ]
    pd.DataFrame(summary).to_csv(
        os.path.join(graph_dir, "gene_feature_summary.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"{os.path.basename(graph_dir)}: disease nnz={disease_stats['nnz']}, "
        f"herb nnz={herb_stats['nnz']}, combined nnz={combined_gene._nnz()}, "
        f"shape=({num_nodes}, {num_genes})"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Build sparse node-gene multi-hot features.")
    parser.add_argument("--graph-root", default=GRAPH_ROOT)
    parser.add_argument(
        "--variant",
        default="all",
        help="Graph variant directory name, or 'all'.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    gene_ids, gene_to_col = load_gene_columns()

    if args.variant == "all":
        graph_dirs = [
            os.path.join(args.graph_root, name)
            for name in sorted(os.listdir(args.graph_root))
            if os.path.isdir(os.path.join(args.graph_root, name))
        ]
    else:
        graph_dirs = [os.path.join(args.graph_root, args.variant)]

    for graph_dir in graph_dirs:
        if not os.path.exists(os.path.join(graph_dir, "node_map.csv")):
            print(f"Skipping {graph_dir}: node_map.csv not found")
            continue
        save_variant_features(graph_dir, gene_ids, gene_to_col)


if __name__ == "__main__":
    main()
