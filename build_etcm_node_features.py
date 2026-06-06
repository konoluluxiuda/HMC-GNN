import argparse
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm


CURRENT_DIR = Path(__file__).parent.resolve()
DATA_ROOT = CURRENT_DIR / "dataset" / "NEWHERB"
ENTITY_DIR = DATA_ROOT / "entities"
RELATION_DIR = DATA_ROOT / "relation"
FEATURE_DIR = DATA_ROOT / "features"
GRAPH_ROOT = DATA_ROOT / "etcm_graph_data"

DEFAULT_BERT_PATH = Path("/home/zry/workspace/mkgformer/MKG/models/bert-base-chinese")


def clean_id(value):
    return str(value).replace("\ufeff", "").strip()


def load_node_map(graph_dir):
    df = pd.read_csv(graph_dir / "node_map.csv", encoding="utf-8-sig")
    df.columns = [clean_id(c) for c in df.columns]
    node_to_idx = {
        clean_id(row["node_id"]): int(row["node_index"])
        for _, row in df.iterrows()
    }
    id_to_name = {
        clean_id(row["node_id"]): str(row.get("name", ""))
        for _, row in df.iterrows()
    }
    return df, node_to_idx, id_to_name


def load_entity_name_map(filename):
    path = ENTITY_DIR / filename
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [clean_id(c) for c in df.columns]
    return {
        clean_id(row["id"]): str(row.get("name", ""))
        for _, row in df.iterrows()
    }


def load_relation_pairs(filename):
    path = RELATION_DIR / filename
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [clean_id(c).upper() for c in df.columns]
    start_col = ":START_ID" if ":START_ID" in df.columns else df.columns[0]
    end_col = ":END_ID" if ":END_ID" in df.columns else df.columns[1]
    pairs = []
    for start_id, end_id in zip(df[start_col], df[end_col]):
        start_id = clean_id(start_id)
        end_id = clean_id(end_id)
        if start_id and end_id:
            pairs.append((start_id, end_id))
    return pairs


def load_text_map(filename):
    path = FEATURE_DIR / filename
    text_map = {}
    if not path.exists():
        return text_map
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) == 2:
                text_map[parts[0]] = parts[1]
    return text_map


def save_node_attributes(graph_dir, node_to_idx):
    property_map = load_entity_name_map("property.csv")
    meridian_map = load_entity_name_map("meridian.csv")
    attr_ids = sorted(property_map.keys()) + sorted(meridian_map.keys())
    attr_to_col = {attr_id: idx for idx, attr_id in enumerate(attr_ids)}
    matrix = np.zeros((len(node_to_idx), len(attr_ids)), dtype=np.float32)

    hit_edges = 0
    for filename in ["herbTOflavor.csv", "herbTOchannelTropism.csv"]:
        for herb_id, attr_id in load_relation_pairs(filename):
            row = node_to_idx.get(herb_id)
            col = attr_to_col.get(attr_id)
            if row is not None and col is not None:
                matrix[row, col] = 1.0
                hit_edges += 1

    torch.save(torch.from_numpy(matrix), graph_dir / "node_attributes.pt")
    pd.DataFrame(
        {
            "feature_index": range(len(attr_ids)),
            "feature_id": attr_ids,
            "feature_name": [property_map.get(a, meridian_map.get(a, "")) for a in attr_ids],
        }
    ).to_csv(graph_dir / "node_attributes_map.csv", index=False, encoding="utf-8-sig")
    return {"node_attributes_shape": tuple(matrix.shape), "node_attributes_edges": hit_edges}


def collect_herb_chemical_relations():
    herb_to_chemicals = defaultdict(set)
    for filename in ["herbTOchemical.csv", "herbTOchemical_etcm_matched.csv"]:
        if not (RELATION_DIR / filename).exists():
            continue
        for herb_id, chemical_id in load_relation_pairs(filename):
            herb_to_chemicals[herb_id].add(chemical_id)
    return herb_to_chemicals


def save_chemical_multihot(graph_dir, node_to_idx):
    chemical_map = load_entity_name_map("chemical_completed_etcm.csv")
    chemical_ids = sorted(chemical_map.keys())
    chemical_to_col = {chemical_id: idx for idx, chemical_id in enumerate(chemical_ids)}
    herb_to_chemicals = collect_herb_chemical_relations()

    matrix = np.zeros((len(node_to_idx), len(chemical_ids)), dtype=np.float32)
    hit_edges = 0
    for herb_id, chemical_ids_for_herb in herb_to_chemicals.items():
        row = node_to_idx.get(herb_id)
        if row is None:
            continue
        for chemical_id in chemical_ids_for_herb:
            col = chemical_to_col.get(chemical_id)
            if col is not None:
                matrix[row, col] = 1.0
                hit_edges += 1

    torch.save(torch.from_numpy(matrix), graph_dir / "node_chem_multihot.pt")
    pd.DataFrame(
        {
            "feature_index": range(len(chemical_ids)),
            "chemical_id": chemical_ids,
            "chemical_name": [chemical_map[cid] for cid in chemical_ids],
        }
    ).to_csv(graph_dir / "node_chem_multihot_map.csv", index=False, encoding="utf-8-sig")
    return {"node_chem_multihot_shape": tuple(matrix.shape), "node_chem_multihot_edges": hit_edges}


def save_etcm_herb_chemical_feature(graph_dir, node_to_idx):
    chemical_map = load_entity_name_map("chemical_completed_etcm.csv")
    chemical_ids = sorted(chemical_map.keys())
    chemical_to_col = {chemical_id: idx for idx, chemical_id in enumerate(chemical_ids)}

    matrix = np.zeros((len(node_to_idx), len(chemical_ids)), dtype=np.float32)
    hit_edges = 0
    for herb_id, chemical_id in load_relation_pairs("herbTOchemical_etcm_matched.csv"):
        row = node_to_idx.get(herb_id)
        col = chemical_to_col.get(chemical_id)
        if row is not None and col is not None:
            matrix[row, col] = 1.0
            hit_edges += 1

    torch.save(torch.from_numpy(matrix), graph_dir / "node_herb_chemical_etcm.pt")
    pd.DataFrame(
        {
            "feature_index": range(len(chemical_ids)),
            "chemical_id": chemical_ids,
            "chemical_name": [chemical_map[cid] for cid in chemical_ids],
        }
    ).to_csv(graph_dir / "node_herb_chemical_etcm_map.csv", index=False, encoding="utf-8-sig")
    return {
        "node_herb_chemical_etcm_shape": tuple(matrix.shape),
        "node_herb_chemical_etcm_edges": hit_edges,
    }


def load_maccs_by_name():
    path = FEATURE_DIR / "component2maccs.txt"
    comp_to_fp = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[1]:
                comp_to_fp[parts[0]] = np.array([float(bit) for bit in parts[1]], dtype=np.float32)
    return comp_to_fp


def save_chemical_fingerprint(graph_dir, node_to_idx):
    chemical_map = load_entity_name_map("chemical_completed_etcm.csv")
    comp_to_fp = load_maccs_by_name()
    fp_dim = len(next(iter(comp_to_fp.values()))) if comp_to_fp else 0
    matrix = np.zeros((len(node_to_idx), fp_dim), dtype=np.float32)
    herb_to_chemicals = collect_herb_chemical_relations()

    herb_hits = 0
    component_hits = []
    for herb_id, chemical_ids in herb_to_chemicals.items():
        row = node_to_idx.get(herb_id)
        if row is None:
            continue
        fps = []
        for chemical_id in chemical_ids:
            chemical_name = chemical_map.get(chemical_id, "")
            fp = comp_to_fp.get(chemical_name)
            if fp is not None:
                fps.append(fp)
        if fps:
            matrix[row] = np.mean(np.stack(fps), axis=0)
            herb_hits += 1
            component_hits.append(len(fps))

    torch.save(torch.from_numpy(matrix), graph_dir / "node_chem_fingerprint.pt")
    return {
        "node_chem_fingerprint_shape": tuple(matrix.shape),
        "fingerprint_herb_hits": herb_hits,
        "fingerprint_avg_components": float(np.mean(component_hits)) if component_hits else 0.0,
    }


def load_bert_model(bert_path):
    from transformers import AutoModel, AutoTokenizer

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(bert_path, local_files_only=True)
    model = AutoModel.from_pretrained(bert_path, local_files_only=True).to(device)
    model.eval()
    return tokenizer, model, device


@torch.no_grad()
def encode_texts(texts, tokenizer, model, device, batch_size=32, max_length=128):
    embeddings = []
    for start in tqdm(range(0, len(texts), batch_size), desc="BERT encoding"):
        batch_texts = texts[start : start + batch_size]
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
            padding=True,
        ).to(device)
        outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state[:, 0, :].cpu().numpy())
    if embeddings:
        return np.concatenate(embeddings, axis=0).astype(np.float32)
    return np.zeros((0, 768), dtype=np.float32)


def save_chemical_dense(graph_dir, node_to_idx, bert_path, batch_size):
    tokenizer, model, device = load_bert_model(bert_path)
    chemical_map = load_entity_name_map("chemical_completed_etcm.csv")
    comp_text = load_text_map("component2textlong.txt")
    herb_to_chemicals = collect_herb_chemical_relations()

    unique_chemical_ids = sorted({cid for cids in herb_to_chemicals.values() for cid in cids})
    chemical_texts = []
    chemical_ids_for_encoding = []
    for chemical_id in unique_chemical_ids:
        chemical_name = chemical_map.get(chemical_id, "")
        text = comp_text.get(chemical_name, "")
        if text:
            chemical_ids_for_encoding.append(chemical_id)
            chemical_texts.append(text)

    print(f"Encoding {len(chemical_texts)} component descriptions for herb chemical dense features...")
    encoded = encode_texts(chemical_texts, tokenizer, model, device, batch_size=batch_size)
    chemical_to_emb = {
        chemical_id: encoded[idx]
        for idx, chemical_id in enumerate(chemical_ids_for_encoding)
    }

    matrix = np.zeros((len(node_to_idx), 768), dtype=np.float32)
    herb_hits = 0
    component_hits = []
    for herb_id, chemical_ids in herb_to_chemicals.items():
        row = node_to_idx.get(herb_id)
        if row is None:
            continue
        embs = [chemical_to_emb[cid] for cid in chemical_ids if cid in chemical_to_emb]
        if embs:
            matrix[row] = np.mean(np.stack(embs), axis=0)
            herb_hits += 1
            component_hits.append(len(embs))

    torch.save(torch.from_numpy(matrix), graph_dir / "node_chem_dense.pt")
    return {
        "node_chem_dense_shape": tuple(matrix.shape),
        "chem_dense_encoded_components": len(chemical_texts),
        "chem_dense_herb_hits": herb_hits,
        "chem_dense_avg_components": float(np.mean(component_hits)) if component_hits else 0.0,
    }


def save_disease_text(graph_dir, node_map_df, bert_path, batch_size):
    tokenizer, model, device = load_bert_model(bert_path)
    disease_text = load_text_map("disease2textlong.txt")
    disease_rows = node_map_df[node_map_df["node_type"].eq("disease")]

    row_indices = []
    texts = []
    for _, row in disease_rows.iterrows():
        node_index = int(row["node_index"])
        name = str(row.get("name", ""))
        text = disease_text.get(name, "")
        if text:
            row_indices.append(node_index)
            texts.append(text)

    print(f"Encoding {len(texts)} disease descriptions...")
    encoded = encode_texts(texts, tokenizer, model, device, batch_size=batch_size)
    matrix = np.zeros((len(node_map_df), 768), dtype=np.float32)
    for idx, node_index in enumerate(row_indices):
        matrix[node_index] = encoded[idx]

    torch.save(torch.from_numpy(matrix), graph_dir / "node_disease_text.pt")
    return {
        "node_disease_text_shape": tuple(matrix.shape),
        "disease_text_hits": len(texts),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Build ETCM node-aligned optional feature matrices.")
    parser.add_argument("--variant", default="g4_gene_bridge_chemical")
    parser.add_argument("--graph-root", default=str(GRAPH_ROOT))
    parser.add_argument("--bert-path", default=str(DEFAULT_BERT_PATH))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--skip-bert", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    graph_dir = Path(args.graph_root) / args.variant
    if not graph_dir.exists():
        raise FileNotFoundError(f"Graph directory not found: {graph_dir}")

    node_map_df, node_to_idx, _ = load_node_map(graph_dir)
    summary = {}

    print(f"Building node-aligned features for {graph_dir}...")
    summary.update(save_node_attributes(graph_dir, node_to_idx))
    summary.update(save_chemical_multihot(graph_dir, node_to_idx))
    summary.update(save_etcm_herb_chemical_feature(graph_dir, node_to_idx))
    summary.update(save_chemical_fingerprint(graph_dir, node_to_idx))

    if args.skip_bert:
        print("Skipping BERT dense features.")
    else:
        summary.update(save_chemical_dense(graph_dir, node_to_idx, args.bert_path, args.batch_size))
        summary.update(save_disease_text(graph_dir, node_map_df, args.bert_path, args.batch_size))

    pd.DataFrame(
        [{"item": key, "value": value} for key, value in summary.items()]
    ).to_csv(graph_dir / "node_optional_feature_summary.csv", index=False, encoding="utf-8-sig")

    print("Done. Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
