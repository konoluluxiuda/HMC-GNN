#!/usr/bin/env python3
"""Refetch failed ETCM disease ids from a previous disease output."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

from fetch_etcm_disease_pages import parse_disease_page, write_csv


def read_failed_ids(path: Path) -> list[int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [int(row["etcm_id"]) for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failed-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--progress-every", type=int, default=25)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    disease_rows: list[dict] = []
    gene_rows: list[dict] = []
    relation_rows: list[dict] = []
    failed_rows: list[dict] = []
    gene_to_id: dict[str, str] = {}

    failed_ids = read_failed_ids(Path(args.failed_file))
    for index, etcm_id in enumerate(failed_ids, start=1):
        item = parse_disease_page(
            etcm_id,
            timeout=args.timeout,
            retries=args.retries,
            include_herbs=False,
        )
        if item is None:
            failed_rows.append({"etcm_id": etcm_id, "reason": "empty_or_parse_failed"})
        else:
            disease_id = f"ETCM_disease_id_{item['etcm_id']}"
            disease_rows.append(
                {"id": disease_id, "name": item["disease_name"], "etcm_id": item["etcm_id"]}
            )
            for gene_symbol, source in item["genes"]:
                if gene_symbol not in gene_to_id:
                    gene_id = f"ETCM_Gene_{len(gene_to_id) + 1}"
                    gene_to_id[gene_symbol] = gene_id
                    gene_rows.append({"id": gene_id, "name": gene_symbol})
                relation_rows.append(
                    {
                        ":START_ID": disease_id,
                        ":END_ID": gene_to_id[gene_symbol],
                        "source": source,
                        "gene_symbol": gene_symbol,
                    }
                )

        if index % args.progress_every == 0:
            print(
                f"checked={index}/{len(failed_ids)} recovered={len(disease_rows)} "
                f"still_failed={len(failed_rows)}",
                file=sys.stderr,
                flush=True,
            )
        time.sleep(args.sleep_seconds)

    write_csv(out_dir / "entities" / "disease_etcm_full.csv", disease_rows, ["id", "name", "etcm_id"])
    write_csv(out_dir / "entities" / "gene_etcm_full.csv", gene_rows, ["id", "name"])
    write_csv(
        out_dir / "relation" / "diseaseTOgene_etcm_full.csv",
        relation_rows,
        [":START_ID", ":END_ID", "source", "gene_symbol"],
    )
    write_csv(out_dir / "failed_disease_ids_etcm_full.csv", failed_rows, ["etcm_id", "reason"])

    print("Done.")
    print(f"Output: {out_dir}")
    print(f"Recovered diseases: {len(disease_rows)}")
    print(f"Genes: {len(gene_rows)}")
    print(f"Disease-Gene edges: {len(relation_rows)}")
    print(f"Still failed: {len(failed_rows)}")


if __name__ == "__main__":
    main()
