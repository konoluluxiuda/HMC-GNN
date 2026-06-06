import os
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
from scipy import sparse
from tqdm import tqdm


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(CURRENT_DIR, "dataset", "NEWHERB")
KGE_DIR = os.path.join(DATA_ROOT, "kge_data")
PAPER_DIR = os.path.join(DATA_ROOT, "paper_graph_data")
OUTPUT_DIR = os.path.join(DATA_ROOT, "paper_graph_noleak_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VALID_RELATIONS = {
    "treats_disease",
    "has_component",
    "has_effect",
    "has_property",
    "belongs_to_meridian",
}

REL_TYPE_MAP = {
    "treats_disease": 0,
    "has_component": 1,
    "has_effect": 2,
    "has_property": 3,
    "belongs_to_meridian": 4,
}

REL_HH = 10
REL_SS = 11
TOTAL_RELATIONS = 12

MIN_COOC_HERB = 0.8
TOP_K_HERB = 10
MIN_COOC_DISEASE = 0.8
TOP_K_DISEASE = 15


def load_entities():
    with open(os.path.join(KGE_DIR, "entities.txt"), "r", encoding="utf-8") as f:
        ent_lines = [line.strip() for line in f if line.strip()]
    return ent_lines, {name: idx for idx, name in enumerate(ent_lines)}


def load_original_split():
    rec_data = torch.load(os.path.join(PAPER_DIR, "rec_data.pt"), map_location="cpu")
    return rec_data["train_dict"], rec_data["test_dict"], rec_data["herb_indices"]


def build_cooccurrence_graph(interaction_mat, global_ids, threshold, top_k, name):
    intersection = (interaction_mat @ interaction_mat.T).tocoo()
    degrees = interaction_mat.sum(axis=1).A1
    row_neighbors = defaultdict(list)

    print(f"   Building {name} from matrix {interaction_mat.shape}...")
    for i, j, val in tqdm(
        zip(intersection.row, intersection.col, intersection.data),
        total=intersection.nnz,
        desc=name,
    ):
        if i == j:
            continue
        union = degrees[i] + degrees[j] - val
        score = float(val / union) if union > 0 else 0.0
        if score >= threshold:
            row_neighbors[i].append((j, score))

    src_list, dst_list = [], []
    for i, neighbors in row_neighbors.items():
        neighbors.sort(key=lambda item: item[1], reverse=True)
        src_id = global_ids[i]
        for j, _ in neighbors[:top_k]:
            dst_id = global_ids[j]
            src_list.append(src_id)
            dst_list.append(dst_id)

    print(f"   -> {name}: Generated {len(src_list)} edges (Jaccard >= {threshold}, Top-{top_k})")
    return src_list, dst_list


def add_edge(edges_src, edges_dst, edges_type, src, dst, rel):
    edges_src.extend([src, dst])
    edges_dst.extend([dst, src])
    edges_type.extend([rel, rel + 5])


def process():
    ent_lines, ent2id = load_entities()
    train_dict, test_dict, herb_indices = load_original_split()
    train_treat_pairs = {
        (herb_id, disease_id)
        for disease_id, herbs in train_dict.items()
        for herb_id in herbs
    }

    edges_src, edges_dst, edges_type = [], [], []
    non_treat_relation_counts = defaultdict(int)
    skipped_test_treat_edges = 0

    print("1. Building no-leak paper graph from original paper split...")
    print(f"   Original split: train diseases={len(train_dict)}, test diseases={len(test_dict)}, herbs={len(herb_indices)}")

    for filename in ["train.tsv", "dev.tsv", "test.tsv"]:
        path = os.path.join(KGE_DIR, filename)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, sep="\t", header=None, names=["h", "r", "t"])
        for _, row in df.iterrows():
            h, r, t = row["h"], row["r"], row["t"]
            if r not in VALID_RELATIONS or h not in ent2id or t not in ent2id:
                continue
            h_idx, t_idx = ent2id[h], ent2id[t]
            r_id = REL_TYPE_MAP[r]

            if r == "treats_disease":
                if (h_idx, t_idx) not in train_treat_pairs:
                    skipped_test_treat_edges += 1
                    continue
            else:
                non_treat_relation_counts[r] += 1

            add_edge(edges_src, edges_dst, edges_type, h_idx, t_idx, r_id)

    print("2. Building no-leak H-H / D-D Jaccard graphs from train_dict only...")
    herb_global_list = sorted({herb for herbs in train_dict.values() for herb in herbs})
    disease_global_list = sorted(train_dict.keys())
    herb_local = {herb_id: idx for idx, herb_id in enumerate(herb_global_list)}
    disease_local = {disease_id: idx for idx, disease_id in enumerate(disease_global_list)}

    hd_rows, hd_cols = [], []
    for disease_id, herbs in train_dict.items():
        for herb_id in herbs:
            if herb_id in herb_local and disease_id in disease_local:
                hd_rows.append(herb_local[herb_id])
                hd_cols.append(disease_local[disease_id])

    h_d_mat = sparse.csr_matrix(
        (np.ones(len(hd_rows), dtype=np.float32), (hd_rows, hd_cols)),
        shape=(len(herb_global_list), len(disease_global_list)),
    )
    d_h_mat = h_d_mat.T

    hh_src, hh_dst = build_cooccurrence_graph(
        h_d_mat,
        herb_global_list,
        threshold=MIN_COOC_HERB,
        top_k=TOP_K_HERB,
        name="H-H no-leak",
    )
    edges_src.extend(hh_src)
    edges_dst.extend(hh_dst)
    edges_type.extend([REL_HH] * len(hh_src))

    ss_src, ss_dst = build_cooccurrence_graph(
        d_h_mat,
        disease_global_list,
        threshold=MIN_COOC_DISEASE,
        top_k=TOP_K_DISEASE,
        name="D-D no-leak",
    )
    edges_src.extend(ss_src)
    edges_dst.extend(ss_dst)
    edges_type.extend([REL_SS] * len(ss_src))

    edge_index = torch.tensor([edges_src, edges_dst], dtype=torch.long)
    edge_type = torch.tensor(edges_type, dtype=torch.long)
    data_dict = {
        "num_nodes": len(ent_lines),
        "num_relations": TOTAL_RELATIONS,
        "herb_indices": herb_indices,
        "train_dict": train_dict,
        "test_dict": test_dict,
        "source": "paper_graph_data split with no test/dev disease-herb edges in graph",
    }

    torch.save(edge_index, os.path.join(OUTPUT_DIR, "edge_index.pt"))
    torch.save(edge_type, os.path.join(OUTPUT_DIR, "edge_type.pt"))
    torch.save(data_dict, os.path.join(OUTPUT_DIR, "rec_data.pt"))

    relation_rows = []
    for rel, rel_id in REL_TYPE_MAP.items():
        relation_rows.append({"relation": rel, "type_id": rel_id})
        relation_rows.append({"relation": f"rev_{rel}", "type_id": rel_id + 5})
    relation_rows.extend(
        [
            {"relation": "herb_disease_jaccard", "type_id": REL_HH},
            {"relation": "disease_herb_jaccard", "type_id": REL_SS},
        ]
    )
    pd.DataFrame(relation_rows).sort_values("type_id").to_csv(
        os.path.join(OUTPUT_DIR, "relation_map.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    summary = [
        {"item": "num_nodes", "count": len(ent_lines), "note": ""},
        {"item": "num_relations", "count": TOTAL_RELATIONS, "note": ""},
        {"item": "edge_count", "count": int(edge_index.shape[1]), "note": ""},
        {"item": "train_treats_disease_edges_bidirectional", "count": len(train_treat_pairs) * 2, "note": "Only original rec train positives are inserted."},
        {"item": "skipped_non_train_treats_disease_rows", "count": skipped_test_treat_edges, "note": "Held-out disease-herb rows removed from graph."},
        {"item": "herb_disease_jaccard_edges", "count": len(hh_src), "note": "Built from train_dict only."},
        {"item": "disease_herb_jaccard_edges", "count": len(ss_src), "note": "Built from train_dict only."},
        {"item": "train_disease_count", "count": len(train_dict), "note": ""},
        {"item": "test_disease_count", "count": len(test_dict), "note": ""},
        {"item": "candidate_herb_count", "count": len(herb_indices), "note": ""},
    ]
    for rel, count in sorted(non_treat_relation_counts.items()):
        summary.append({"item": f"{rel}_rows_from_all_kge_splits", "count": count, "note": "Non-recommendation edges kept."})
    pd.DataFrame(summary).to_csv(os.path.join(OUTPUT_DIR, "graph_summary.csv"), index=False, encoding="utf-8-sig")

    print("3. Saved no-leak paper graph:")
    print(f"   nodes={len(ent_lines)}, relations={TOTAL_RELATIONS}, edges={edge_index.shape[1]}")
    print(f"   removed held-out treats_disease rows={skipped_test_treat_edges}")


if __name__ == "__main__":
    process()
