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
OUTPUT_ROOT = os.path.join(DATA_ROOT, "disease_split_graph_data")

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
    "g0_herb_disease_only": {
        "description": "Disease-disjoint split with only disease/herb nodes; side information is feature-only.",
        "entity_types": ["disease", "herb"],
        "extra_relations": [],
        "exclude_base_relations": [filename for filename, _ in BASE_RELATIONS],
    },
    "g0_base": {
        "description": "Disease-disjoint split + train disease-herb labels + base TCM relations.",
        "extra_relations": [],
        "exclude_base_relations": [],
    },
    "g3_gene_no_chemical": {
        "description": "G3 gene bridge without herb-chemical graph relations.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
        ],
        "exclude_base_relations": ["herbTOchemical.csv"],
    },
    "g3_gene_bridge": {
        "description": "G0 + disease-gene + herb-gene side information.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
        ],
        "exclude_base_relations": [],
    },
    "g4_gene_bridge_chemical": {
        "description": "G3 + ETCM herb-chemical side information.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
            ("herbTOchemical_etcm_matched.csv", "has_component"),
        ],
        "exclude_base_relations": [],
    },
    "g4_gene_bridge_chemical_gene_jaccard": {
        "description": "G4 + same-type co-occurrence edges based on shared associated genes.",
        "extra_relations": [
            ("diseaseTOgene_etcm_matched.csv", "disease_associated_gene"),
            ("herbTOgene_etcm_matched.csv", "herb_associated_gene"),
            ("herbTOchemical_etcm_matched.csv", "has_component"),
        ],
        "exclude_base_relations": [],
        "use_gene_jaccard_edges": True,
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
        return pd.DataFrame(
            [
                {"relation": rel, "type_id": idx}
                for rel, idx in sorted(self.rel_to_idx.items(), key=lambda item: item[1])
            ]
        )


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


def register_known_nodes(node_registry, entity_types=None):
    allowed_types = set(entity_types) if entity_types is not None else set(ENTITY_FILES.keys())
    for node_type, filename in ENTITY_FILES.items():
        if node_type not in allowed_types:
            continue
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


def create_node_registry_for_variant(variant):
    node_registry = NodeRegistry()
    register_known_nodes(node_registry, entity_types=variant.get("entity_types"))

    relation_files = ["herbTOdisease.csv"]
    excluded_base_relations = set(variant.get("exclude_base_relations", []))
    relation_files.extend(
        filename
        for filename, _ in BASE_RELATIONS
        if filename not in excluded_base_relations
    )
    relation_files.extend(filename for filename, _ in variant["extra_relations"])
    register_relation_endpoints(node_registry, sorted(set(relation_files)))
    return node_registry


def split_by_disease(pairs, seed=42, train_ratio=0.8, val_ratio=0.1):
    disease_to_herbs = defaultdict(list)
    for herb_id, disease_id in sorted(set(pairs)):
        disease_to_herbs[disease_id].append(herb_id)

    disease_ids = np.array(sorted(disease_to_herbs.keys()), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(disease_ids)

    train_end = int(len(disease_ids) * train_ratio)
    val_end = train_end + int(len(disease_ids) * val_ratio)

    train_diseases = set(disease_ids[:train_end].tolist())
    val_diseases = set(disease_ids[train_end:val_end].tolist())
    test_diseases = set(disease_ids[val_end:].tolist())

    def make_dict(disease_set):
        return {
            disease_id: list(dict.fromkeys(disease_to_herbs[disease_id]))
            for disease_id in sorted(disease_set)
        }

    return (
        make_dict(train_diseases),
        make_dict(val_diseases),
        make_dict(test_diseases),
        {
            "train_diseases": sorted(train_diseases),
            "val_diseases": sorted(val_diseases),
            "test_diseases": sorted(test_diseases),
        },
    )


def build_jaccard_edges(train_dict, node_registry, threshold, top_k, mode):
    if mode == "herb":
        row_ids = sorted({herb for herbs in train_dict.values() for herb in herbs})
        col_ids = sorted(train_dict.keys())
        name = "Herb-Herb train-disease Jaccard"
        rows, cols = [], []
        row_index = {node_id: idx for idx, node_id in enumerate(row_ids)}
        col_index = {node_id: idx for idx, node_id in enumerate(col_ids)}
        for disease_id, herbs in train_dict.items():
            for herb_id in herbs:
                rows.append(row_index[herb_id])
                cols.append(col_index[disease_id])
    elif mode == "disease":
        row_ids = sorted(train_dict.keys())
        col_ids = sorted({herb for herbs in train_dict.values() for herb in herbs})
        name = "Disease-Disease train-herb Jaccard"
        rows, cols = [], []
        row_index = {node_id: idx for idx, node_id in enumerate(row_ids)}
        col_index = {node_id: idx for idx, node_id in enumerate(col_ids)}
        for disease_id, herbs in train_dict.items():
            for herb_id in herbs:
                rows.append(row_index[disease_id])
                cols.append(col_index[herb_id])
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
        src_idx = node_registry.add(row_ids[i])
        for j, score in items[:top_k]:
            dst_idx = node_registry.add(row_ids[j])
            edges.append((src_idx, dst_idx, score))

    print(f"   -> {name}: {len(edges)} directed edges (Jaccard >= {threshold}, Top-{top_k})")
    return edges


def build_gene_jaccard_edges(
    relation_filename,
    node_registry,
    threshold,
    min_shared,
    top_k,
    source_type,
):
    pairs = load_relation_pairs(os.path.join(RELATION_DIR, relation_filename))
    source_to_genes = defaultdict(set)
    for source_id, gene_id in pairs:
        source_to_genes[source_id].add(gene_id)

    known_sources = []
    for row in node_registry.rows:
        if row["node_type"] == source_type and row["node_id"] in source_to_genes:
            known_sources.append(row["node_id"])
    known_sources = sorted(set(known_sources))

    if not known_sources:
        print(f"   -> {source_type}-gene Jaccard: 0 directed edges (no gene annotations)")
        return []

    gene_ids = sorted({gene_id for source_id in known_sources for gene_id in source_to_genes[source_id]})
    row_index = {node_id: idx for idx, node_id in enumerate(known_sources)}
    col_index = {gene_id: idx for idx, gene_id in enumerate(gene_ids)}

    rows, cols = [], []
    for source_id in known_sources:
        for gene_id in source_to_genes[source_id]:
            rows.append(row_index[source_id])
            cols.append(col_index[gene_id])

    mat = sparse.csr_matrix(
        (np.ones(len(rows), dtype=np.float32), (rows, cols)),
        shape=(len(known_sources), len(gene_ids)),
    )
    intersection = (mat @ mat.T).tocoo()
    degrees = mat.sum(axis=1).A1
    neighbors = defaultdict(list)

    name = f"{source_type.capitalize()}-{source_type.capitalize()} shared-gene Jaccard"
    print(f"   Building {name} from matrix {mat.shape}...")
    for i, j, shared in tqdm(
        zip(intersection.row, intersection.col, intersection.data),
        total=intersection.nnz,
        desc=f"{source_type}-gene-jaccard",
    ):
        if i == j or shared < min_shared:
            continue
        union = degrees[i] + degrees[j] - shared
        score = float(shared / union) if union > 0 else 0.0
        if score >= threshold:
            neighbors[i].append((j, score, int(shared)))

    edges = []
    for i, items in neighbors.items():
        items.sort(key=lambda item: (item[1], item[2]), reverse=True)
        src_idx = node_registry.add(known_sources[i])
        for j, score, shared in items[:top_k]:
            dst_idx = node_registry.add(known_sources[j])
            edges.append((src_idx, dst_idx, score, shared))

    print(
        f"   -> {name}: {len(edges)} directed edges "
        f"(shared_genes >= {min_shared}, Jaccard >= {threshold}, Top-{top_k})"
    )
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


def convert_label_dict(node_registry, label_dict):
    return {
        node_registry.add(disease_id): [node_registry.add(herb_id) for herb_id in herbs]
        for disease_id, herbs in label_dict.items()
    }


def build_variant(variant_name, node_registry, args, train_dict_ids, val_dict_ids, test_dict_ids, split_ids):
    variant = VARIANTS[variant_name]
    output_dir = os.path.join(args.output_root, variant_name)
    os.makedirs(output_dir, exist_ok=True)

    relation_registry = RelationRegistry()
    edge_set = set()
    summary = []

    def add_summary(item, count, note=""):
        summary.append({"item": item, "count": count, "note": note})

    print(f"\n=== Building disease split {variant_name}: {variant['description']} ===")

    train_pairs = [
        (herb_id, disease_id)
        for disease_id, herbs in train_dict_ids.items()
        for herb_id in herbs
    ]
    added = add_relation_edges(edge_set, node_registry, relation_registry, train_pairs, "treats_disease")
    add_summary(
        "train_treats_disease_edges_bidirectional",
        added,
        "Only train diseases' herb labels are inserted into the graph.",
    )

    excluded_base_relations = set(variant.get("exclude_base_relations", []))
    for filename, relation in BASE_RELATIONS:
        if filename in excluded_base_relations:
            add_summary(f"{filename}:{relation}", 0, "Excluded for this variant.")
            continue
        pairs = load_relation_pairs(os.path.join(RELATION_DIR, filename))
        added = add_relation_edges(edge_set, node_registry, relation_registry, pairs, relation)
        add_summary(f"{filename}:{relation}", added, "Full side-information relation.")

    hh_edges = build_jaccard_edges(
        train_dict_ids,
        node_registry,
        threshold=args.herb_threshold,
        top_k=args.herb_topk,
        mode="herb",
    )
    hh_rel = relation_registry.add("herb_disease_jaccard")
    before = len(edge_set)
    for src_idx, dst_idx, _ in hh_edges:
        edge_set.add((src_idx, dst_idx, hh_rel))
    add_summary("herb_disease_jaccard_edges", len(edge_set) - before, "Built from train diseases only.")

    dd_edges = build_jaccard_edges(
        train_dict_ids,
        node_registry,
        threshold=args.disease_threshold,
        top_k=args.disease_topk,
        mode="disease",
    )
    dd_rel = relation_registry.add("disease_herb_jaccard")
    before = len(edge_set)
    for src_idx, dst_idx, _ in dd_edges:
        edge_set.add((src_idx, dst_idx, dd_rel))
    add_summary("disease_herb_jaccard_edges", len(edge_set) - before, "Built from train diseases only.")

    if variant.get("use_gene_jaccard_edges", False):
        herb_gene_edges = build_gene_jaccard_edges(
            "herbTOgene_etcm_matched.csv",
            node_registry,
            threshold=args.herb_gene_jaccard_threshold,
            min_shared=args.herb_gene_min_shared,
            top_k=args.herb_gene_topk,
            source_type="herb",
        )
        herb_gene_rel = relation_registry.add("herb_gene_jaccard")
        before = len(edge_set)
        for src_idx, dst_idx, _, _ in herb_gene_edges:
            edge_set.add((src_idx, dst_idx, herb_gene_rel))
        add_summary(
            "herb_gene_jaccard_edges",
            len(edge_set) - before,
            "Built from shared herb-associated ETCM genes.",
        )

        disease_gene_edges = build_gene_jaccard_edges(
            "diseaseTOgene_etcm_matched.csv",
            node_registry,
            threshold=args.disease_gene_jaccard_threshold,
            min_shared=args.disease_gene_min_shared,
            top_k=args.disease_gene_topk,
            source_type="disease",
        )
        disease_gene_rel = relation_registry.add("disease_gene_jaccard")
        before = len(edge_set)
        for src_idx, dst_idx, _, _ in disease_gene_edges:
            edge_set.add((src_idx, dst_idx, disease_gene_rel))
        add_summary(
            "disease_gene_jaccard_edges",
            len(edge_set) - before,
            "Built from shared disease-associated ETCM genes.",
        )

    for filename, relation in variant["extra_relations"]:
        pairs = load_relation_pairs(os.path.join(RELATION_DIR, filename))
        added = add_relation_edges(edge_set, node_registry, relation_registry, pairs, relation)
        add_summary(f"{filename}:{relation}", added, "Full side-information relation.")

    sorted_edges = sorted(edge_set)
    if sorted_edges:
        src, dst, rel = zip(*sorted_edges)
        edge_index = torch.tensor([src, dst], dtype=torch.long)
        edge_type = torch.tensor(rel, dtype=torch.long)
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)
        edge_type = torch.empty((0,), dtype=torch.long)

    train_dict = convert_label_dict(node_registry, train_dict_ids)
    val_dict = convert_label_dict(node_registry, val_dict_ids)
    test_dict = convert_label_dict(node_registry, test_dict_ids)

    all_label_dicts = [train_dict_ids, val_dict_ids, test_dict_ids]
    herb_indices = sorted(
        {
            node_registry.add(herb_id)
            for label_dict in all_label_dicts
            for herbs in label_dict.values()
            for herb_id in herbs
        }
    )

    data_dict = {
        "num_nodes": len(node_registry.rows),
        "num_relations": len(relation_registry.rel_to_idx),
        "herb_indices": herb_indices,
        "train_dict": train_dict,
        "val_dict": val_dict,
        "test_dict": test_dict,
        "split_protocol": "disease_disjoint",
        "variant": variant_name,
        "variant_description": variant["description"],
        "node_id_by_index": [row["node_id"] for row in node_registry.rows],
        "train_disease_ids": split_ids["train_diseases"],
        "val_disease_ids": split_ids["val_diseases"],
        "test_disease_ids": split_ids["test_diseases"],
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
    add_summary("val_disease_count", len(val_dict))
    add_summary("test_disease_count", len(test_dict))
    add_summary("candidate_herb_count", len(herb_indices))
    add_summary("train_label_edges", sum(len(v) for v in train_dict.values()))
    add_summary("val_label_edges", sum(len(v) for v in val_dict.values()))
    add_summary("test_label_edges", sum(len(v) for v in test_dict.values()))
    pd.DataFrame(summary).to_csv(os.path.join(output_dir, "graph_summary.csv"), index=False, encoding="utf-8-sig")

    print(
        f"Saved {variant_name}: nodes={data_dict['num_nodes']}, relations={data_dict['num_relations']}, "
        f"edges={edge_index.shape[1]}, train/val/test diseases="
        f"{len(train_dict)}/{len(val_dict)}/{len(test_dict)}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Build disease-disjoint graph variants for HMC-GNN.")
    parser.add_argument("--variant", choices=["all"] + list(VARIANTS.keys()), default="all")
    parser.add_argument("--output-root", default=OUTPUT_ROOT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--herb-threshold", type=float, default=0.8)
    parser.add_argument("--herb-topk", type=int, default=10)
    parser.add_argument("--disease-threshold", type=float, default=0.8)
    parser.add_argument("--disease-topk", type=int, default=15)
    parser.add_argument("--herb-gene-jaccard-threshold", type=float, default=0.2)
    parser.add_argument("--herb-gene-min-shared", type=int, default=5)
    parser.add_argument("--herb-gene-topk", type=int, default=10)
    parser.add_argument("--disease-gene-jaccard-threshold", type=float, default=0.2)
    parser.add_argument("--disease-gene-min-shared", type=int, default=5)
    parser.add_argument("--disease-gene-topk", type=int, default=15)
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output_root, exist_ok=True)

    disease_herb_pairs = load_relation_pairs(os.path.join(RELATION_DIR, "herbTOdisease.csv"))
    train_dict_ids, val_dict_ids, test_dict_ids, split_ids = split_by_disease(
        disease_herb_pairs,
        seed=args.seed,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )

    print(
        "Disease-disjoint split: "
        f"train diseases={len(train_dict_ids)}, val diseases={len(val_dict_ids)}, "
        f"test diseases={len(test_dict_ids)}, "
        f"train labels={sum(len(v) for v in train_dict_ids.values())}, "
        f"val labels={sum(len(v) for v in val_dict_ids.values())}, "
        f"test labels={sum(len(v) for v in test_dict_ids.values())}"
    )

    variants = list(VARIANTS.keys()) if args.variant == "all" else [args.variant]
    for variant_name in variants:
        node_registry = create_node_registry_for_variant(VARIANTS[variant_name])
        build_variant(
            variant_name,
            node_registry,
            args,
            train_dict_ids,
            val_dict_ids,
            test_dict_ids,
            split_ids,
        )


if __name__ == "__main__":
    main()
