#!/usr/bin/env python3
"""Fetch ETCM herb detail pages and build herb-gene CSV files.

ETCM herb pages use two useful source structures:
- bootstrapTable({ data: [...] }) stores herb metadata and component links.
- A later HTML table lists candidate target genes per component with scores.

This script keeps herb data separate from disease pages. It outputs herb,
chemical, gene entities plus herb-chemical, chemical-gene, and aggregated
herb-gene relations.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BASE_URL = "http://www.tcmip.cn/ETCM/index.php/Home/Index/yc_details.html?id={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://www.tcmip.cn/ETCM/index.php/Home/Index/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
NA_VALUES = {"", "NA", "N/A", "NULL", "NONE", "NAN"}


def clean_text(value: str | None) -> str:
    value = "" if value is None else str(value)
    value = html.unescape(value)
    value = value.replace("\ufeff", "").replace("\xa0", " ")
    value = value.replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n+", "\n", value)
    return value.strip()


def html_fragment_to_text(fragment: str) -> str:
    fragment = html.unescape(fragment or "")
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</(div|p|li|tr|td)>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return clean_text(fragment)


def parse_bootstrap_table_rows(page_html: str) -> dict[str, str]:
    pattern = re.compile(
        r'\{\s*"ID"\s*:\s*"(?P<id>.*?)"\s*,\s*'
        r'"Item Name"\s*:\s*"(?P<item>.*?)"\s*,?\s*\}',
        re.S,
    )
    rows: dict[str, str] = {}
    for match in pattern.finditer(page_html):
        row_id = html_fragment_to_text(match.group("id"))
        item_html = html.unescape(match.group("item")).strip()
        rows[row_id] = item_html
    return rows


def first_nonempty(*values: str) -> str:
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned.upper() not in NA_VALUES:
            return cleaned
    return ""


def extract_title(page_html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", page_html, re.I | re.S)
    return html_fragment_to_text(match.group(1)) if match else ""


def extract_cf_links(fragment: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*)href\s*=\s*['\"](?P<href>[^'\"]*cf_details\.html\?id=(?P<cf_id>\d+)[^'\"]*)['\"]"
        r"(?P<attrs2>[^>]*)>(?P<text>.*?)</a>",
        re.I | re.S,
    )
    for match in pattern.finditer(fragment or ""):
        cf_id = clean_text(match.group("cf_id"))
        name = html_fragment_to_text(match.group("text"))
        if not name or name.upper() in NA_VALUES:
            continue
        results.append(
            {
                "chemical_key": f"cf:{cf_id}" if cf_id else f"name:{name.upper()}",
                "chemical_etcm_id": cf_id,
                "chemical_name": name,
            }
        )

    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for item in results:
        if item["chemical_key"] not in seen:
            deduped.append(item)
            seen.add(item["chemical_key"])
    return deduped


def extract_gene_scores(fragment: str, min_score: float) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    pattern = re.compile(
        r"jyjb_details\.html\?gene=(?P<gene>[^'\"&>]+).*?"
        r">(?P<text>[^<]+?)\s*\((?P<score>[0-9]+(?:\.[0-9]+)?)\)\s*</a>",
        re.I | re.S,
    )
    for match in pattern.finditer(fragment or ""):
        gene_from_url = clean_text(urllib.parse.unquote(match.group("gene"))).upper()
        gene_from_text = clean_text(match.group("text")).upper()
        gene = gene_from_text or gene_from_url
        score = clean_text(match.group("score"))
        if not gene or gene in NA_VALUES:
            continue
        try:
            score_value = float(score)
        except ValueError:
            continue
        if score_value < min_score:
            continue
        results.append({"gene_symbol": gene, "score": f"{score_value:g}"})

    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, str]] = []
    for item in results:
        key = (item["gene_symbol"], item["score"])
        if key not in seen:
            deduped.append(item)
            seen.add(key)
    return deduped


def extract_chemical_gene_rows(page_html: str, min_score: float) -> list[dict[str, str]]:
    table_row_pattern = re.compile(
        r"<tr[^>]*>\s*<td[^>]*>\s*(?P<chemical>.*?cf_details\.html\?id=\d+.*?)</td>\s*"
        r"<td[^>]*>(?P<genes>.*?)</td>\s*</tr>",
        re.I | re.S,
    )
    rows: list[dict[str, str]] = []

    for match in table_row_pattern.finditer(page_html or ""):
        chemical_links = extract_cf_links(match.group("chemical"))
        if not chemical_links:
            continue
        chemical = chemical_links[0]
        for gene in extract_gene_scores(match.group("genes"), min_score=min_score):
            rows.append(
                {
                    **chemical,
                    "gene_symbol": gene["gene_symbol"],
                    "score": gene["score"],
                }
            )

    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        key = (row["chemical_key"], row["gene_symbol"], row["score"])
        if key not in seen:
            deduped.append(row)
            seen.add(key)
    return deduped


def fetch_page(etcm_id: int, timeout: int, retries: int) -> str:
    url = BASE_URL.format(etcm_id)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read()
            return raw.decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt >= retries:
                return ""
            time.sleep(1.0 + attempt)
    return ""


def parse_herb_page(
    etcm_id: int,
    page_html: str,
    min_score: float,
) -> dict | None:
    if not page_html or len(page_html) < 500:
        return None

    rows = parse_bootstrap_table_rows(page_html)
    if not rows:
        return None

    chinese_name = html_fragment_to_text(rows.get("Herb Name in Chinese", ""))
    pinyin_name = html_fragment_to_text(rows.get("Herb Name in Pinyin", ""))
    latin_name = html_fragment_to_text(
        first_nonempty(
            rows.get("Herb Name in Ladin", ""),
            rows.get("Herb Name in Latin", ""),
        )
    )
    herb_type = html_fragment_to_text(rows.get("Type", ""))
    title = extract_title(page_html)
    display_name = first_nonempty(chinese_name, pinyin_name, title)
    if not display_name:
        return None

    components = extract_cf_links(rows.get("Components", ""))
    chemical_gene_rows = extract_chemical_gene_rows(page_html, min_score=min_score)
    component_keys = {component["chemical_key"] for component in components}
    for row in chemical_gene_rows:
        if row["chemical_key"] not in component_keys:
            components.append(
                {
                    "chemical_key": row["chemical_key"],
                    "chemical_etcm_id": row["chemical_etcm_id"],
                    "chemical_name": row["chemical_name"],
                }
            )
            component_keys.add(row["chemical_key"])

    return {
        "etcm_id": etcm_id,
        "name": display_name,
        "chinese_name": chinese_name,
        "pinyin_name": pinyin_name,
        "latin_name": latin_name,
        "type": herb_type,
        "components": components,
        "chemical_gene_rows": chemical_gene_rows,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_gene(gene_symbol: str, gene_to_id: dict[str, str], gene_rows: list[dict]) -> str:
    if gene_symbol not in gene_to_id:
        gene_id = f"ETCM_Gene_{len(gene_to_id) + 1}"
        gene_to_id[gene_symbol] = gene_id
        gene_rows.append({"id": gene_id, "name": gene_symbol})
    return gene_to_id[gene_symbol]


def add_chemical(
    chemical: dict[str, str],
    chemical_to_id: dict[str, str],
    chemical_rows: list[dict],
) -> str:
    key = chemical["chemical_key"]
    if key not in chemical_to_id:
        cf_id = chemical["chemical_etcm_id"]
        chemical_id = f"ETCM_chemical_id_{cf_id}" if cf_id else f"ETCM_Chemical_{len(chemical_to_id) + 1}"
        chemical_to_id[key] = chemical_id
        chemical_rows.append(
            {
                "id": chemical_id,
                "name": chemical["chemical_name"],
                "etcm_id": cf_id,
            }
        )
    return chemical_to_id[key]


def build_from_items(items: list[dict], out_dir: Path) -> None:
    entities_dir = out_dir / "entities"
    relation_dir = out_dir / "relation"

    herb_rows: list[dict] = []
    chemical_rows: list[dict] = []
    gene_rows: list[dict] = []
    herb_chemical_rows: list[dict] = []
    chemical_gene_rows: list[dict] = []
    herb_gene_best: dict[tuple[str, str], dict] = {}

    chemical_to_id: dict[str, str] = {}
    gene_to_id: dict[str, str] = {}

    for item in items:
        herb_id = f"ETCM_herb_id_{item['etcm_id']}"
        herb_rows.append(
            {
                "id": herb_id,
                "name": item["name"],
                "chinese_name": item["chinese_name"],
                "pinyin_name": item["pinyin_name"],
                "latin_name": item["latin_name"],
                "type": item["type"],
                "etcm_id": item["etcm_id"],
            }
        )

        for component in item["components"]:
            chemical_id = add_chemical(component, chemical_to_id, chemical_rows)
            herb_chemical_rows.append(
                {
                    ":START_ID": herb_id,
                    ":END_ID": chemical_id,
                    "source": "ETCM_COMPONENT",
                    "chemical_name": component["chemical_name"],
                }
            )

        for row in item["chemical_gene_rows"]:
            chemical_id = add_chemical(row, chemical_to_id, chemical_rows)
            gene_id = add_gene(row["gene_symbol"], gene_to_id, gene_rows)
            chemical_gene_rows.append(
                {
                    ":START_ID": chemical_id,
                    ":END_ID": gene_id,
                    "source": "ETCM_CANDIDATE_TARGET",
                    "score": row["score"],
                    "chemical_name": row["chemical_name"],
                    "gene_symbol": row["gene_symbol"],
                }
            )

            herb_gene_key = (herb_id, gene_id)
            existing = herb_gene_best.get(herb_gene_key)
            score_value = float(row["score"])
            if existing is None:
                herb_gene_best[herb_gene_key] = {
                    ":START_ID": herb_id,
                    ":END_ID": gene_id,
                    "source": "ETCM_CANDIDATE_TARGET",
                    "max_score": row["score"],
                    "chemical_count": 1,
                    "gene_symbol": row["gene_symbol"],
                }
            else:
                existing["chemical_count"] += 1
                if score_value > float(existing["max_score"]):
                    existing["max_score"] = row["score"]

    herb_chemical_rows = list(
        {(
            row[":START_ID"],
            row[":END_ID"],
            row["source"],
        ): row for row in herb_chemical_rows}.values()
    )
    chemical_gene_rows = list(
        {(
            row[":START_ID"],
            row[":END_ID"],
            row["score"],
        ): row for row in chemical_gene_rows}.values()
    )
    herb_gene_rows = list(herb_gene_best.values())

    write_csv(
        entities_dir / "herb_etcm_full.csv",
        herb_rows,
        ["id", "name", "chinese_name", "pinyin_name", "latin_name", "type", "etcm_id"],
    )
    write_csv(entities_dir / "chemical_etcm_full.csv", chemical_rows, ["id", "name", "etcm_id"])
    write_csv(entities_dir / "gene_etcm_full.csv", gene_rows, ["id", "name"])
    write_csv(
        relation_dir / "herbTOchemical_etcm_full.csv",
        herb_chemical_rows,
        [":START_ID", ":END_ID", "source", "chemical_name"],
    )
    write_csv(
        relation_dir / "chemicalTOgene_etcm_full.csv",
        chemical_gene_rows,
        [":START_ID", ":END_ID", "source", "score", "chemical_name", "gene_symbol"],
    )
    write_csv(
        relation_dir / "herbTOgene_etcm_full.csv",
        herb_gene_rows,
        [":START_ID", ":END_ID", "source", "max_score", "chemical_count", "gene_symbol"],
    )

    print("Done.")
    print(f"Output: {out_dir}")
    print(f"Herbs: {len(herb_rows)}")
    print(f"Chemicals: {len(chemical_rows)}")
    print(f"Genes: {len(gene_rows)}")
    print(f"Herb-Chemical edges: {len(herb_chemical_rows)}")
    print(f"Chemical-Gene edges: {len(chemical_gene_rows)}")
    print(f"Herb-Gene edges: {len(herb_gene_rows)}")


def build_outputs(args: argparse.Namespace) -> None:
    out_dir = Path(args.output_dir)
    failed_rows: list[dict] = []
    items: list[dict] = []

    if args.input_html:
        page_html = Path(args.input_html).read_text(encoding="utf-8", errors="replace")
        item = parse_herb_page(args.start_id, page_html, min_score=args.min_score)
        if item is None:
            failed_rows.append({"etcm_id": args.start_id, "reason": "input_html_parse_failed"})
        else:
            items.append(item)
    else:
        consecutive_empty = 0
        for etcm_id in range(args.start_id, args.max_id + 1):
            page_html = fetch_page(etcm_id, timeout=args.timeout, retries=args.retries)
            item = parse_herb_page(etcm_id, page_html, min_score=args.min_score)

            if item is None:
                failed_rows.append({"etcm_id": etcm_id, "reason": "empty_or_parse_failed"})
                consecutive_empty += 1
                if consecutive_empty >= args.max_consecutive_empty:
                    print(
                        f"Stop: {args.max_consecutive_empty} consecutive empty pages "
                        f"ending at id={etcm_id}",
                        file=sys.stderr,
                    )
                    break
                time.sleep(args.sleep_seconds)
                continue

            consecutive_empty = 0
            items.append(item)
            if len(items) % args.progress_every == 0:
                total_chemical_gene = sum(len(row["chemical_gene_rows"]) for row in items)
                print(
                    f"parsed={len(items)} last_id={etcm_id} "
                    f"chemical_gene_edges={total_chemical_gene}",
                    flush=True,
                )
            time.sleep(args.sleep_seconds)

    build_from_items(items, out_dir)
    write_csv(out_dir / "failed_herb_ids_etcm_full.csv", failed_rows, ["etcm_id", "reason"])
    print(f"Failed pages: {len(failed_rows)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--max-id", type=int, default=10000)
    parser.add_argument("--max-consecutive-empty", type=int, default=100)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--progress-every", type=int, default=20)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument(
        "--input-html",
        help="Parse one saved yc_details HTML file instead of fetching pages.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/newherb_etcm_herb_gene",
        help="Directory that will receive entities/, relation/, and failed CSV files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    build_outputs(parse_args())
