#!/usr/bin/env python3
"""Integrate fetched ETCM disease/herb data into dataset/NEWHERB.

The raw fetched files are copied into the normal entities/ and relation/
folders with source-specific names.  Matched/expanded entity and relation files
are then built without overwriting the existing core CSVs.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import unicodedata
from pathlib import Path


RAW_COPY_PLAN = [
    ("disease", "entities/disease_etcm_4539.csv", "entities/disease_etcm_full.csv"),
    ("disease", "entities/gene_etcm_from_disease.csv", "entities/gene_etcm_full.csv"),
    ("disease", "relation/diseaseTOgene_etcm_4539.csv", "relation/diseaseTOgene_etcm_full.csv"),
    ("disease", "intermediate/failed_disease_ids_etcm_4539.csv", "failed_disease_ids_etcm_full.csv"),
    ("herb", "entities/herb_etcm_full.csv", "entities/herb_etcm_full.csv"),
    ("herb", "entities/chemical_etcm_full.csv", "entities/chemical_etcm_full.csv"),
    ("herb", "entities/gene_etcm_from_herb.csv", "entities/gene_etcm_full.csv"),
    ("herb", "relation/herbTOchemical_etcm_full.csv", "relation/herbTOchemical_etcm_full.csv"),
    ("herb", "relation/chemicalTOgene_etcm_full.csv", "relation/chemicalTOgene_etcm_full.csv"),
    ("herb", "relation/herbTOgene_etcm_full.csv", "relation/herbTOgene_etcm_full.csv"),
    ("herb", "intermediate/failed_herb_ids_etcm_full.csv", "failed_herb_ids_etcm_full.csv"),
]


def norm(value: str | None) -> str:
    value = "" if value is None else str(value)
    value = value.replace("\ufeff", "")
    value = unicodedata.normalize("NFKC", value)
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = value.replace("’", "'").replace("`", "'")
    return value


def slug_gene(symbol: str) -> str:
    symbol = re.sub(r"[^A-Za-z0-9_.-]+", "_", symbol.strip().upper())
    return symbol.strip("_") or "UNKNOWN"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_raw_files(dataset_dir: Path, disease_dir: Path, herb_dir: Path) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    roots = {"disease": disease_dir, "herb": herb_dir}
    for source, dst_rel, src_rel in RAW_COPY_PLAN:
        src = roots[source] / src_rel
        dst = dataset_dir / dst_rel
        if not src.exists():
            copied.append({"source": str(src), "dest": str(dst), "status": "missing"})
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append({"source": str(src), "dest": str(dst), "status": "copied"})
    return copied


def index_by_name(rows: list[dict[str, str]], name_col: str = "name") -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = norm(row.get(name_col, ""))
        if key and key not in indexed:
            indexed[key] = row
    return indexed


def build_gene_maps(
    existing_genes: list[dict[str, str]],
    disease_genes: list[dict[str, str]],
    herb_genes: list[dict[str, str]],
) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]]]:
    symbol_to_id: dict[str, str] = {}
    completed: list[dict[str, str]] = []
    matches: list[dict[str, str]] = []

    for row in existing_genes:
        symbol = row.get("name", "").strip().upper()
        if not symbol:
            continue
        symbol_to_id[symbol] = row["id"]
        completed.append({"id": row["id"], "name": row["name"], "source": "existing"})

    for source_name, rows in (("disease", disease_genes), ("herb", herb_genes)):
        for row in rows:
            symbol = row.get("name", "").strip().upper()
            if not symbol:
                continue
            if symbol in symbol_to_id:
                matches.append(
                    {
                        "source": source_name,
                        "source_id": row["id"],
                        "source_name": row["name"],
                        "matched_id": symbol_to_id[symbol],
                        "matched_name": symbol,
                        "match_type": "gene_symbol",
                    }
                )
                continue
            new_id = f"ETCM_GeneSymbol_{slug_gene(symbol)}"
            symbol_to_id[symbol] = new_id
            completed.append({"id": new_id, "name": symbol, "source": f"etcm_{source_name}"})
            matches.append(
                {
                    "source": source_name,
                    "source_id": row["id"],
                    "source_name": row["name"],
                    "matched_id": new_id,
                    "matched_name": symbol,
                    "match_type": "new_gene_symbol",
                }
            )

    return symbol_to_id, completed, matches


def chemical_aliases(name: str) -> list[str]:
    aliases = [name]
    aliases.extend(part.strip() for part in name.split(","))
    return [alias for alias in aliases if alias]


def build_chemical_maps(
    existing_chemicals: list[dict[str, str]],
    etcm_chemicals: list[dict[str, str]],
) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]]]:
    alias_to_existing: dict[str, dict[str, str]] = {}
    for row in existing_chemicals:
        for alias in chemical_aliases(row.get("name", "")):
            key = norm(alias)
            if key and key not in alias_to_existing:
                alias_to_existing[key] = row

    key_to_id: dict[str, str] = {}
    completed = [{"id": r["id"], "name": r["name"], "source": "existing"} for r in existing_chemicals]
    matches: list[dict[str, str]] = []
    existing_ids = {row["id"] for row in existing_chemicals}

    for row in etcm_chemicals:
        matched = None
        for alias in chemical_aliases(row.get("name", "")):
            matched = alias_to_existing.get(norm(alias))
            if matched:
                break
        if matched:
            matched_id = matched["id"]
            match_type = "chemical_name_or_alias"
        else:
            matched_id = row["id"]
            match_type = "new_chemical"
            if matched_id not in existing_ids:
                completed.append({"id": matched_id, "name": row["name"], "source": "etcm_herb"})
                existing_ids.add(matched_id)

        key_to_id[row["id"]] = matched_id
        matches.append(
            {
                "source_id": row["id"],
                "source_name": row["name"],
                "matched_id": matched_id,
                "matched_name": matched["name"] if matched else row["name"],
                "match_type": match_type,
            }
        )

    return key_to_id, completed, matches


def build_name_entity_maps(
    existing_rows: list[dict[str, str]],
    etcm_rows: list[dict[str, str]],
    entity_kind: str,
    name_columns: list[str],
    new_id_prefix: str | None = None,
    include_new: bool = True,
) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, str]]]:
    existing_by_name = index_by_name(existing_rows)
    source_to_id: dict[str, str] = {}
    completed = [{"id": r["id"], "name": r["name"], "source": "existing"} for r in existing_rows]
    matches: list[dict[str, str]] = []
    existing_ids = {row["id"] for row in existing_rows}

    for row in etcm_rows:
        matched = None
        matched_col = ""
        for col in name_columns:
            key = norm(row.get(col, ""))
            if key in existing_by_name:
                matched = existing_by_name[key]
                matched_col = col
                break

        if matched:
            matched_id = matched["id"]
            match_type = f"{entity_kind}_{matched_col}"
        else:
            if include_new:
                if new_id_prefix:
                    source_suffix = row.get("etcm_id", "") or row["id"]
                    matched_id = f"{new_id_prefix}{source_suffix}"
                else:
                    matched_id = row["id"]
                    if matched_id in existing_ids:
                        source_suffix = row.get("etcm_id", "") or row["id"]
                        matched_id = f"ETCM_{entity_kind}_new_id_{source_suffix}"
                match_type = f"new_{entity_kind}"
                if matched_id not in existing_ids:
                    completed.append({"id": matched_id, "name": row.get("name", ""), "source": f"etcm_{entity_kind}"})
                    existing_ids.add(matched_id)
            else:
                matched_id = ""
                match_type = f"unmatched_{entity_kind}"

        if matched_id:
            source_to_id[row["id"]] = matched_id
        matches.append(
            {
                "source_id": row["id"],
                "source_name": row.get("name", ""),
                "source_etcm_id": row.get("etcm_id", ""),
                "matched_id": matched_id,
                "matched_name": matched["name"] if matched else row.get("name", ""),
                "match_type": match_type,
            }
        )

    return source_to_id, completed, matches


def map_relation_rows(
    rows: list[dict[str, str]],
    start_map: dict[str, str],
    end_map: dict[str, str],
    extra_fields: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    id_rows: list[dict[str, str]] = []
    full_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for row in rows:
        src_start = row[":START_ID"]
        src_end = row[":END_ID"]
        if src_start not in start_map or src_end not in end_map:
            continue
        start = start_map[src_start]
        end = end_map[src_end]
        key = (start, end)
        if key not in seen:
            id_rows.append({":START_ID": start, ":END_ID": end})
            seen.add(key)
        full_row = {
            ":START_ID": start,
            ":END_ID": end,
            "source_start_id": src_start,
            "source_end_id": src_end,
        }
        for field in extra_fields:
            full_row[field] = row.get(field, "")
        full_rows.append(full_row)

    return id_rows, full_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", default="dataset/NEWHERB")
    parser.add_argument("--disease-dir", default="/tmp/newherb_etcm_disease_gene_4539")
    parser.add_argument("--herb-dir", default="/tmp/newherb_etcm_herb_gene")
    parser.add_argument(
        "--keep-only-existing-diseases",
        action="store_true",
        help="Do not add unmatched ETCM diseases to disease_completed_etcm.csv or disease-gene matched relations.",
    )
    parser.add_argument(
        "--keep-only-existing-herbs",
        action="store_true",
        help="Do not add unmatched ETCM herbs to herb_completed_etcm.csv or herb matched relations.",
    )
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    disease_dir = Path(args.disease_dir)
    herb_dir = Path(args.herb_dir)
    entities_dir = dataset_dir / "entities"
    relation_dir = dataset_dir / "relation"
    match_dir = dataset_dir / "intermediate" / "etcm_entity_matches"
    match_dir.mkdir(parents=True, exist_ok=True)

    copied = copy_raw_files(dataset_dir, disease_dir, herb_dir)

    existing_diseases = read_csv(entities_dir / "disease.csv")
    existing_herbs = read_csv(entities_dir / "herb.csv")
    existing_genes = read_csv(entities_dir / "gene.csv")
    existing_chemicals = read_csv(entities_dir / "chemical.csv")

    etcm_diseases = read_csv(disease_dir / "entities" / "disease_etcm_full.csv")
    disease_genes = read_csv(disease_dir / "entities" / "gene_etcm_full.csv")
    etcm_herbs = read_csv(herb_dir / "entities" / "herb_etcm_full.csv")
    etcm_chemicals = read_csv(herb_dir / "entities" / "chemical_etcm_full.csv")
    herb_genes = read_csv(herb_dir / "entities" / "gene_etcm_full.csv")

    disease_map, disease_completed, disease_matches = build_name_entity_maps(
        existing_diseases,
        etcm_diseases,
        "disease",
        ["name"],
        new_id_prefix="ETCM_disease_new_id_",
        include_new=not args.keep_only_existing_diseases,
    )
    herb_map, herb_completed, herb_matches = build_name_entity_maps(
        existing_herbs,
        etcm_herbs,
        "herb",
        ["chinese_name", "name", "pinyin_name"],
        include_new=not args.keep_only_existing_herbs,
    )
    gene_symbol_to_id, gene_completed, gene_matches = build_gene_maps(
        existing_genes,
        disease_genes,
        herb_genes,
    )
    chemical_map, chemical_completed, chemical_matches = build_chemical_maps(
        existing_chemicals,
        etcm_chemicals,
    )

    disease_gene_id_to_symbol = {row["id"]: row["name"].strip().upper() for row in disease_genes}
    herb_gene_id_to_symbol = {row["id"]: row["name"].strip().upper() for row in herb_genes}
    disease_gene_map = {gid: gene_symbol_to_id[sym] for gid, sym in disease_gene_id_to_symbol.items() if sym}
    herb_gene_map = {gid: gene_symbol_to_id[sym] for gid, sym in herb_gene_id_to_symbol.items() if sym}

    write_csv(entities_dir / "disease_completed_etcm.csv", disease_completed, ["id", "name", "source"])
    write_csv(entities_dir / "herb_completed_etcm.csv", herb_completed, ["id", "name", "source"])
    write_csv(entities_dir / "gene_completed_etcm.csv", gene_completed, ["id", "name", "source"])
    write_csv(entities_dir / "chemical_completed_etcm.csv", chemical_completed, ["id", "name", "source"])

    write_csv(match_dir / "raw_file_copy_report.csv", copied, ["source", "dest", "status"])
    write_csv(match_dir / "disease_matches.csv", disease_matches, ["source_id", "source_name", "source_etcm_id", "matched_id", "matched_name", "match_type"])
    write_csv(match_dir / "herb_matches.csv", herb_matches, ["source_id", "source_name", "source_etcm_id", "matched_id", "matched_name", "match_type"])
    write_csv(match_dir / "gene_matches.csv", gene_matches, ["source", "source_id", "source_name", "matched_id", "matched_name", "match_type"])
    write_csv(match_dir / "chemical_matches.csv", chemical_matches, ["source_id", "source_name", "matched_id", "matched_name", "match_type"])

    relation_specs = [
        (
            disease_dir / "relation" / "diseaseTOgene_etcm_full.csv",
            relation_dir / "diseaseTOgene_etcm_matched.csv",
            relation_dir / "diseaseTOgene_etcm_matched_full.csv",
            disease_map,
            disease_gene_map,
            ["source", "gene_symbol"],
        ),
        (
            herb_dir / "relation" / "herbTOgene_etcm_full.csv",
            relation_dir / "herbTOgene_etcm_matched.csv",
            relation_dir / "herbTOgene_etcm_matched_full.csv",
            herb_map,
            herb_gene_map,
            ["source", "max_score", "chemical_count", "gene_symbol"],
        ),
        (
            herb_dir / "relation" / "herbTOchemical_etcm_full.csv",
            relation_dir / "herbTOchemical_etcm_matched.csv",
            relation_dir / "herbTOchemical_etcm_matched_full.csv",
            herb_map,
            chemical_map,
            ["source", "chemical_name"],
        ),
        (
            herb_dir / "relation" / "chemicalTOgene_etcm_full.csv",
            relation_dir / "chemicalTOgene_etcm_matched.csv",
            relation_dir / "chemicalTOgene_etcm_matched_full.csv",
            chemical_map,
            herb_gene_map,
            ["source", "score", "chemical_name", "gene_symbol"],
        ),
    ]

    relation_counts: list[dict[str, str]] = []
    for src, id_path, full_path, start_map, end_map, extras in relation_specs:
        rows = read_csv(src)
        id_rows, full_rows = map_relation_rows(rows, start_map, end_map, extras)
        write_csv(id_path, id_rows, [":START_ID", ":END_ID"])
        write_csv(
            full_path,
            full_rows,
            [":START_ID", ":END_ID", "source_start_id", "source_end_id", *extras],
        )
        relation_counts.append(
            {
                "relation_file": id_path.name,
                "source_rows": str(len(rows)),
                "matched_unique_edges": str(len(id_rows)),
                "matched_full_rows": str(len(full_rows)),
            }
        )
    write_csv(match_dir / "relation_match_counts.csv", relation_counts, ["relation_file", "source_rows", "matched_unique_edges", "matched_full_rows"])

    disease_existing_count = sum(
        1
        for row in disease_matches
        if not row["match_type"].startswith("new_")
        and not row["match_type"].startswith("unmatched_")
    )
    herb_existing_count = sum(
        1
        for row in herb_matches
        if not row["match_type"].startswith("new_")
        and not row["match_type"].startswith("unmatched_")
    )
    summary_rows = [
        {"item": "raw_files_copied", "count": str(sum(1 for row in copied if row["status"] == "copied"))},
        {"item": "disease_matches_existing", "count": str(disease_existing_count)},
        {"item": "disease_new", "count": str(sum(1 for row in disease_matches if row["match_type"].startswith("new_")))},
        {"item": "disease_unmatched_skipped", "count": str(sum(1 for row in disease_matches if row["match_type"].startswith("unmatched_")))},
        {"item": "herb_matches_existing", "count": str(herb_existing_count)},
        {"item": "herb_new", "count": str(sum(1 for row in herb_matches if row["match_type"].startswith("new_")))},
        {"item": "herb_unmatched_skipped", "count": str(sum(1 for row in herb_matches if row["match_type"].startswith("unmatched_")))},
        {"item": "gene_completed", "count": str(len(gene_completed))},
        {"item": "chemical_completed", "count": str(len(chemical_completed))},
    ]
    write_csv(match_dir / "integration_summary.csv", summary_rows, ["item", "count"])

    print("Done.")
    print(f"Dataset: {dataset_dir}")
    for row in summary_rows:
        print(f"{row['item']}: {row['count']}")
    for row in relation_counts:
        print(
            f"{row['relation_file']}: {row['matched_unique_edges']} unique edges "
            f"from {row['source_rows']} source rows"
        )


if __name__ == "__main__":
    main()
