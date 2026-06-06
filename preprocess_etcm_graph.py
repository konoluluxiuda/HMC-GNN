import argparse
import os
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
from scipy import sparse
from tqdm import tqdm


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(CURRENT_DIR, "dataset", "NEWHERB")
ENTITY_DIR = os.path.join(DATA_ROOT, "entities")
RELATION_DIR = os.path.join(DATA_ROOT, "relation")
OUTPUT_ROOT = os.path.join(DATA_ROOT, "etcm_graph_data")

ENTITY_FILES = {
    "disease": "disease_completed_etcm.csv",
    "herb": "herb_completed_etcm.csv",
    "gene": "gene_completed_etcm.csv",
    "chemical": "chemical_completed_etcm.csv",
    "effect": "effect.csv",
    "property": "property.csv",
    "meridian": "meridian.csv",
}

BASE_RELATIONS = [
    ("herbTOchemical.csv", "has_component"),
    ("herbTOeffect.csv", "has_effect"),
    ("herbTOflavor.csv", "has_property"),
    ("herbTOchannelTropism.csv", "belongs_to_meridian"),
]

VARIANTS = {
    "g0_base": {
        "description": "Original graph with train disease-herb edges and TCM/chemical relations.",
        "extra_relations": [],
    },
    "g1_disease_gene": {
        "description": "G0 + diseaseTOgene.",
        "extra_relations": [("diseaseTOgene_etcm_matched.csv", "disease_associated_gene")],
    },
    "g2_herb_gene": {
        "description": "G0 + herbTOgene.",
        "extra_relations": [("herbTOgene_etcm_matched.csv", "herb_associated_gene")],
    },
    "g3_gene_bridge": {
        "description": "G0 + diseaseTOgene + herbTOgene.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
        ],
    },
    "g4_gene_bridge_chemical": {
        "description": "G3 + ETCM herbTOchemical.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
            ("herbTOchemical_etcm_matched.csv", "has_component"),
        ],
    },
    "g5_component_gene_extension": {
        "description": "G4 + chemicalTOgene as an optional component-gene semantic extension.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
            ("herbTOchemical_etcm_matched.csv", "has_component"),
            ("chemicalTOgene_etcm_matched.csv", "chemical_associated_gene"),
        ],
    },
}


def clean_id(value):
    return str(value).replace("\ufeff", "").strip()


def normalize_header(name):
    return clean_id(name).upper()


class NodeRegistry:
    def __init__(self):
        self.node_to_idx = {}
        self.rows = []

    def add(self, node_id, node_type="unknown", name="", source="relation_only"):
        node_id = clean_id(node_id)
        if not node_id:
            return None
        if node_id not in self.node_to_idx:
            self.node_to_idx[node_id] = len(self.rows)
            self.rows.append(
                {
                    "node_id": node_id,
                    "node_index": self.node_to_idx[node_id],
                    "node_type": node_type,
                    "name": name,
                    "source": source,
                }
            )
        return self.node_to_idx[node_id]

    def to_frame(self):
        return pd.DataFrame(self.rows)


class RelationRegistry:
    def __init__(self):
        self.rel_to_idx = {}

    def add(self, relation):
        if relation not in self.rel_to_idx:
            self.rel_to_idx[relation] = len(self.rel_to_idx)
        return self.rel_to_idx[relation]

    def to_frame(self):
        rows = [
            {"relation": rel, "type_id": idx}
            for rel, idx in sorted(self.rel_to_idx.items(), key=lambda item: item[1])
        ]
        return pd.DataFrame(rows)


def load_entity_table(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [clean_id(c) for c in df.columns]
    if "id" not in df.columns:
        raise ValueError(f"Entity file missing id column: {path}")
    if "name" not in df.columns:
        df["name"] = ""
    if "source" not in df.columns:
        df["source"] = "existing"
    return df


def load_relation_pairs(path):
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


def register_known_nodes(node_registry):
    for node_type, filename in ENTITY_FILES.items():
        path = os.path.join(ENTITY_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing entity file: {path}")
        df = load_entity_table(path)
        for _, row in df.iterrows():
            node_registry.add(row["id"], node_type=node_type, name=row["name"], source=row["source"])


def register_relation_endpoints(node_registry, relation_files):
    for filename in relation_files:
        path = os.path.join(RELATION_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing relation file: {path}")
        for start_id, end_id in load_relation_pairs(path):
            node_registry.add(start_id)
            node_registry.add(end_id)


def split_disease_herb_pairs(pairs, seed=42, train_ratio=0.8):
    disease_to_herbs = defaultdict(list)
    for herb_id, disease_id in sorted(set(pairs)):
        disease_to_herbs[disease_id].append(herb_id)

    rng = np.random.default_rng(seed)
    train_dict_ids = {}
    test_dict_ids = {}

    for disease_id in sorted(disease_to_herbs):
        herbs = list(dict.fromkeys(disease_to_herbs[disease_id]))
        if len(herbs) < 2:
            train_dict_ids[disease_id] = herbs
            continue
        herbs = np.array(herbs, dtype=object)
        rng.shuffle(herbs)
        split = max(1, int(len(herbs) * train_ratio))
        train_dict_ids[disease_id] = herbs[:split].tolist()
        test_dict_ids[disease_id] = herbs[split:].tolist()

    return train_dict_ids, test_dict_ids


def build_jaccard_edges(train_dict, node_registry, threshold, top_k, mode="herb"):
    if mode == "herb":
        row_ids = sorted({herb for herbs in train_dict.values() for herb in herbs})
        col_ids = sorted(train_dict.keys())
        row_index = {node_id: idx for idx, node_id in enumerate(row_ids)}
        col_index = {node_id: idx for idx, node_id in enumerate(col_ids)}
        rows, cols = [], []
        for disease_id, herbs in train_dict.items():
            for herb_id in herbs:
                rows.append(row_index[herb_id])
                cols.append(col_index[disease_id])
        name = "Herb-Herb disease Jaccard"
    elif mode == "disease":
        row_ids = sorted(train_dict.keys())
        col_ids = sorted({herb for herbs in train_dict.values() for herb in herbs})
        row_index = {node_id: idx for idx, node_id in enumerate(row_ids)}
        col_index = {node_id: idx for idx, node_id in enumerate(col_ids)}
        rows, cols = [], []
        for disease_id, herbs in train_dict.items():
            for herb_id in herbs:
                rows.append(row_index[disease_id])
                cols.append(col_index[herb_id])
        name = "Disease-Disease herb Jaccard"
    else:
        raise ValueError(f"Unsupported Jaccard mode: {mode}")

    mat = sparse.csr_matrix(
        (np.ones(len(rows), dtype=np.float32), (rows, cols)),
        shape=(len(row_ids), len(col_ids)),
    )
    intersection = (mat @ mat.T).tocoo()
    degrees = mat.sum(axis=1).A1
    neighbors = defaultdict(list)

    print(f"   Building {name} from matrix {mat.shape}...")
    for i, j, val in tqdm(
        zip(intersection.row, intersection.col, intersection.data),
        total=intersection.nnz,
        desc=f"{mode}-jaccard",
    ):
        if i == j:
            continue
        union = degrees[i] + degrees[j] - val
        score = float(val / union) if union > 0 else 0.0
        if score >= threshold:
            neighbors[i].append((j, score))

    edges = []
    for i, items in neighbors.items():
        items.sort(key=lambda item: item[1], reverse=True)
        src_id = row_ids[i]
        src_idx = node_registry.add(src_id)
        for j, score in items[:top_k]:
            dst_id = row_ids[j]
            dst_idx = node_registry.add(dst_id)
            edges.append((src_idx, dst_idx, score))

    print(f"   -> {name}: {len(edges)} directed edges (Jaccard >= {threshold}, Top-{top_k})")
    return edges


def add_relation_edges(edge_set, node_registry, relation_registry, pairs, relation, add_reverse=True):
    rel_id = relation_registry.add(relation)
    rev_rel_id = relation_registry.add(f"rev_{relation}") if add_reverse else None
    before = len(edge_set)

    for start_id, end_id in pairs:
        start_idx = node_registry.add(start_id)
        end_idx = node_registry.add(end_id)
        if start_idx is None or end_idx is None:
            continue
        edge_set.add((start_idx, end_idx, rel_id))
        if add_reverse:
            edge_set.add((end_idx, start_idx, rev_rel_id))

    return len(edge_set) - before


def build_variant(variant_name, node_registry, args, train_dict_ids, test_dict_ids, all_dict_ids=None):
    variant = VARIANTS[variant_name]
    output_dir = os.path.join(args.output_root, variant_name)
    os.makedirs(output_dir, exist_ok=True)

    relation_registry = RelationRegistry()
    edge_set = set()
    summary = []

    def add_summary(item, count, note=""):
        summary.append({"item": item, "count": count, "note": note})

    print(f"\n=== Building {variant_name}: {variant['description']} ===")

    graph_dict_ids = all_dict_ids if args.leak_disease_herb else train_dict_ids
    graph_pairs = [
        (herb_id, disease_id)
        for disease_id, herbs in graph_dict_ids.items()
        for herb_id in herbs
    ]
    added = add_relation_edges(edge_set, node_registry, relation_registry, graph_pairs, "treats_disease")
    if args.leak_disease_herb:
        add_summary(
            "all_treats_disease_edges_bidirectional",
            added,
            "Leak diagnostic: train and held-out disease-herb positives are inserted into the graph.",
        )
    else:
        add_summary("train_treats_disease_edges_bidirectional", added, "Only train disease-herb positives are inserted into the graph.")

    for filename, relation in BASE_RELATIONS:
        pairs = load_relation_pairs(os.path.join(RELATION_DIR, filename))
        added = add_relation_edges(edge_set, node_registry, relation_registry, pairs, relation)
        add_summary(f"{filename}:{relation}", added)

    hh_edges = build_jaccard_edges(
        graph_dict_ids,
        node_registry,
        threshold=args.herb_threshold,
        top_k=args.herb_topk,
        mode="herb",
    )
    hh_rel = relation_registry.add("herb_disease_jaccard")
    before = len(edge_set)
    for src_idx, dst_idx, _ in hh_edges:
        edge_set.add((src_idx, dst_idx, hh_rel))
    add_summary("herb_disease_jaccard_edges", len(edge_set) - before)

    dd_edges = build_jaccard_edges(
        graph_dict_ids,
        node_registry,
        threshold=args.disease_threshold,
        top_k=args.disease_topk,
        mode="disease",
    )
    dd_rel = relation_registry.add("disease_herb_jaccard")
    before = len(edge_set)
    for src_idx, dst_idx, _ in dd_edges:
        edge_set.add((src_idx, dst_idx, dd_rel))
    add_summary("disease_herb_jaccard_edges", len(edge_set) - before)

    for filename, relation in variant["extra_relations"]:
        pairs = load_relation_pairs(os.path.join(RELATION_DIR, filename))
        added = add_relation_edges(edge_set, node_registry, relation_registry, pairs, relation)
        add_summary(f"{filename}:{relation}", added)

    sorted_edges = sorted(edge_set)
    if sorted_edges:
        src, dst, rel = zip(*sorted_edges)
        edge_index = torch.tensor([src, dst], dtype=torch.long)
        edge_type = torch.tensor(rel, dtype=torch.long)
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)
        edge_type = torch.empty((0,), dtype=torch.long)

    train_dict = {
        node_registry.add(disease_id): [node_registry.add(herb_id) for herb_id in herbs]
        for disease_id, herbs in train_dict_ids.items()
    }
    test_dict = {
        node_registry.add(disease_id): [node_registry.add(herb_id) for herb_id in herbs]
        for disease_id, herbs in test_dict_ids.items()
    }
    herb_indices = sorted({
        node_registry.add(herb_id)
        for herbs in list(train_dict_ids.values()) + list(test_dict_ids.values())
        for herb_id in herbs
    })

    data_dict = {
        "num_nodes": len(node_registry.rows),
        "num_relations": len(relation_registry.rel_to_idx),
        "herb_indices": herb_indices,
        "train_dict": train_dict,
        "test_dict": test_dict,
        "variant": variant_name,
        "variant_description": variant["description"],
        "node_id_by_index": [row["node_id"] for row in node_registry.rows],
    }

    torch.save(edge_index, os.path.join(output_dir, "edge_index.pt"))
    torch.save(edge_type, os.path.join(output_dir, "edge_type.pt"))
    torch.save(data_dict, os.path.join(output_dir, "rec_data.pt"))
    node_registry.to_frame().to_csv(os.path.join(output_dir, "node_map.csv"), index=False, encoding="utf-8-sig")
    relation_registry.to_frame().to_csv(os.path.join(output_dir, "relation_map.csv"), index=False, encoding="utf-8-sig")

    add_summary("num_nodes", data_dict["num_nodes"])
    add_summary("num_relations", data_dict["num_relations"])
    add_summary("edge_count", int(edge_index.shape[1]))
    add_summary("train_disease_count", len(train_dict))
    add_summary("test_disease_count", len(test_dict))
    add_summary("candidate_herb_count", len(herb_indices))
    pd.DataFrame(summary).to_csv(os.path.join(output_dir, "graph_summary.csv"), index=False, encoding="utf-8-sig")

    print(
        f"Saved {variant_name}: nodes={data_dict['num_nodes']}, "
        f"relations={data_dict['num_relations']}, edges={edge_index.shape[1]}, "
        f"train diseases={len(train_dict)}, test diseases={len(test_dict)}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Build ETCM-enhanced graph variants for HMC-GNN.")
    parser.add_argument(
        "--variant",
        choices=["all"] + list(VARIANTS.keys()),
        default="all",
        help="Graph variant to build.",
    )
    parser.add_argument("--output-root", default=OUTPUT_ROOT, help="Root directory for generated graph variants.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--herb-threshold", type=float, default=0.8)
    parser.add_argument("--herb-topk", type=int, default=10)
    parser.add_argument("--disease-threshold", type=float, default=0.8)
    parser.add_argument("--disease-topk", type=int, default=15)
    parser.add_argument(
        "--leak-disease-herb",
        action="store_true",
        help="Insert all disease-herb positives into graph and build Jaccard from all positives while keeping rec split unchanged.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output_root, exist_ok=True)

    node_registry = NodeRegistry()
    register_known_nodes(node_registry)

    all_relation_files = ["herbTOdisease.csv"]
    all_relation_files.extend(filename for filename, _ in BASE_RELATIONS)
    for variant in VARIANTS.values():
        all_relation_files.extend(filename for filename, _ in variant["extra_relations"])
    register_relation_endpoints(node_registry, sorted(set(all_relation_files)))

    disease_herb_pairs = load_relation_pairs(os.path.join(RELATION_DIR, "herbTOdisease.csv"))
    train_dict_ids, test_dict_ids = split_disease_herb_pairs(
        disease_herb_pairs,
        seed=args.seed,
        train_ratio=args.train_ratio,
    )
    all_dict_ids = defaultdict(list)
    for herb_id, disease_id in sorted(set(disease_herb_pairs)):
        all_dict_ids[disease_id].append(herb_id)
    print(
        f"Split disease-herb positives: diseases={len(train_dict_ids)}, "
        f"train pairs={sum(len(v) for v in train_dict_ids.values())}, "
        f"test pairs={sum(len(v) for v in test_dict_ids.values())}"
    )
    if args.leak_disease_herb:
        print(
            "Leak diagnostic enabled: graph disease-herb and Jaccard relations use "
            f"all pairs={sum(len(v) for v in all_dict_ids.values())}."
        )

    variants = list(VARIANTS.keys()) if args.variant == "all" else [args.variant]
    for variant_name in variants:
        build_variant(variant_name, node_registry, args, train_dict_ids, test_dict_ids, all_dict_ids=all_dict_ids)


if __name__ == "__main__":
    main()
