#!/usr/bin/env python3
"""Merge two ETCM disease fetch output directories.

Gene ids are local to each fetch run, so relations are remapped by gene symbol
while merging.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def gene_index_number(gene_id: str) -> int:
    match = re.search(r"_(\d+)$", gene_id)
    return int(match.group(1)) if match else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", required=True)
    parser.add_argument("--extra-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    extra_dir = Path(args.extra_dir)
    out_dir = Path(args.output_dir)

    base_diseases = read_csv(base_dir / "entities" / "disease_etcm_full.csv")
    extra_diseases = read_csv(extra_dir / "entities" / "disease_etcm_full.csv")
    base_genes = read_csv(base_dir / "entities" / "gene_etcm_full.csv")
    extra_genes = read_csv(extra_dir / "entities" / "gene_etcm_full.csv")
    base_rel = read_csv(base_dir / "relation" / "diseaseTOgene_etcm_full.csv")
    extra_rel = read_csv(extra_dir / "relation" / "diseaseTOgene_etcm_full.csv")
    base_failed = read_csv(base_dir / "failed_disease_ids_etcm_full.csv")
    extra_failed = read_csv(extra_dir / "failed_disease_ids_etcm_full.csv")

    disease_by_id: dict[str, dict[str, str]] = {}
    for row in [*base_diseases, *extra_diseases]:
        disease_by_id[row["id"]] = row
    diseases = sorted(disease_by_id.values(), key=lambda r: int(r["etcm_id"]))

    gene_symbol_to_id = {row["name"].strip().upper(): row["id"] for row in base_genes}
    gene_rows = list(base_genes)
    next_gene_idx = max([gene_index_number(row["id"]) for row in gene_rows] or [0]) + 1
    for row in extra_genes:
        symbol = row["name"].strip().upper()
        if not symbol or symbol in gene_symbol_to_id:
            continue
        gene_id = f"ETCM_Gene_{next_gene_idx}"
        next_gene_idx += 1
        gene_symbol_to_id[symbol] = gene_id
        gene_rows.append({"id": gene_id, "name": symbol})

    base_gene_id_to_symbol = {row["id"]: row["name"].strip().upper() for row in base_genes}
    extra_gene_id_to_symbol = {row["id"]: row["name"].strip().upper() for row in extra_genes}

    merged_rel: list[dict[str, str]] = []
    seen_rel: set[tuple[str, str, str]] = set()

    def add_relation(row: dict[str, str], gene_id_to_symbol: dict[str, str]) -> None:
        disease_id = row[":START_ID"]
        symbol = row.get("gene_symbol", "") or gene_id_to_symbol.get(row[":END_ID"], "")
        symbol = symbol.strip().upper()
        if disease_id not in disease_by_id or symbol not in gene_symbol_to_id:
            return
        source = row.get("source", "")
        key = (disease_id, gene_symbol_to_id[symbol], source)
        if key in seen_rel:
            return
        seen_rel.add(key)
        merged_rel.append(
            {
                ":START_ID": disease_id,
                ":END_ID": gene_symbol_to_id[symbol],
                "source": source,
                "gene_symbol": symbol,
            }
        )

    for row in base_rel:
        add_relation(row, base_gene_id_to_symbol)
    for row in extra_rel:
        add_relation(row, extra_gene_id_to_symbol)

    failed_by_id: dict[str, dict[str, str]] = {}
    for row in [*base_failed, *extra_failed]:
        failed_by_id[row["etcm_id"]] = row
    failed = sorted(failed_by_id.values(), key=lambda r: int(r["etcm_id"]))

    write_csv(out_dir / "entities" / "disease_etcm_full.csv", diseases, ["id", "name", "etcm_id"])
    write_csv(out_dir / "entities" / "gene_etcm_full.csv", gene_rows, ["id", "name"])
    write_csv(
        out_dir / "relation" / "diseaseTOgene_etcm_full.csv",
        merged_rel,
        [":START_ID", ":END_ID", "source", "gene_symbol"],
    )
    write_csv(out_dir / "failed_disease_ids_etcm_full.csv", failed, ["etcm_id", "reason"])

    print("Done.")
    print(f"Output: {out_dir}")
    print(f"Diseases: {len(diseases)}")
    print(f"Genes: {len(gene_rows)}")
    print(f"Disease-Gene edges: {len(merged_rel)}")
    print(f"Failed pages: {len(failed)}")


if __name__ == "__main__":
    main()
