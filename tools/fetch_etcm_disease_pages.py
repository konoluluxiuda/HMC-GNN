#!/usr/bin/env python3
"""Fetch ETCM disease detail pages and build disease-gene CSV files.

The ETCM disease detail pages embed their table rows directly in JavaScript:
bootstrapTable({ data: [...] }).  This script parses that source HTML instead
of using the truncated tableExport.csv view.

By default herb relations are intentionally skipped. ETCM has separate herb
detail pages, so herb-gene data should be fetched from yc_details pages.
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


BASE_URL = "http://www.tcmip.cn/ETCM/index.php/Home/Index/dis_details.html?id={}"
DEFAULT_MAX_ID = 4539
DEFAULT_OUTPUT_DIR = "/tmp/newherb_etcm_disease_gene_4539"
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
    fragment = re.sub(r"</(div|p|li|tr)>", "\n", fragment, flags=re.I)
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
        row_id = clean_text(match.group("id"))
        item_html = html.unescape(match.group("item")).strip()
        rows[row_id] = item_html
    return rows


def extract_gene_links(gene_html: str) -> list[tuple[str, str]]:
    if html_fragment_to_text(gene_html).upper() in NA_VALUES:
        return []

    results: list[tuple[str, str]] = []
    pattern = re.compile(
        r"jyjb_details\?gene=(?P<gene>[^'\"&>]+).*?"
        r">(?P<text>[^<]+)</a>\s*\((?P<source>[^)]+)\)",
        re.S,
    )
    for match in pattern.finditer(gene_html or ""):
        gene_from_url = clean_text(urllib.parse.unquote(match.group("gene"))).upper()
        gene_from_text = clean_text(match.group("text")).upper()
        source = clean_text(match.group("source")).upper()
        gene = gene_from_text or gene_from_url
        if gene and gene not in NA_VALUES:
            results.append((gene, source or "UNKNOWN"))

    if not results:
        text = html_fragment_to_text(gene_html).upper()
        text = text.replace("，", ",").replace("；", ";")
        text = text.replace("（", "(").replace("）", ")")
        fallback = re.compile(
            r"\b([A-Z0-9][A-Z0-9_.-]{1,40})\s*"
            r"\((HPO|TTD|OMIM|CTD|DISGENET|ETCM)\)"
        )
        for gene, source in fallback.findall(text):
            if gene not in {"NA", "HPO", "TTD"}:
                results.append((gene, source))

    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str]] = []
    for item in results:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def extract_herb_links(herb_html: str) -> list[dict[str, str]]:
    if html_fragment_to_text(herb_html).upper() in NA_VALUES:
        return []

    results: list[dict[str, str]] = []
    link_pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*)>(?P<text>.*?)</a>",
        re.I | re.S,
    )
    href_pattern = re.compile(r"href\s*=\s*['\"](?P<href>[^'\"]+)['\"]", re.I)

    for match in link_pattern.finditer(herb_html or ""):
        attrs = match.group("attrs")
        text = html_fragment_to_text(match.group("text"))
        href_match = href_pattern.search(attrs)
        href = html.unescape(href_match.group("href")) if href_match else ""
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        ywname = clean_text(qs.get("ywname", [""])[0])
        name = clean_text(text.lstrip(";").strip()) or ywname
        if name.upper() in NA_VALUES or ywname.upper() in NA_VALUES:
            continue
        results.append({"herb_name": name, "ywname": ywname or name})

    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for item in results:
        key = item["ywname"].upper()
        if key not in seen:
            deduped.append(item)
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


def parse_disease_page(
    etcm_id: int,
    timeout: int,
    retries: int,
    include_herbs: bool = False,
) -> dict | None:
    page_html = fetch_page(etcm_id, timeout=timeout, retries=retries)
    if not page_html or len(page_html) < 500:
        return None

    rows = parse_bootstrap_table_rows(page_html)
    if not rows:
        return None

    disease_name = html_fragment_to_text(rows.get("Disease Name", ""))
    if not disease_name:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", page_html, re.I | re.S)
        disease_name = html_fragment_to_text(title_match.group(1)) if title_match else ""
    if not disease_name:
        return None

    return {
        "etcm_id": etcm_id,
        "disease_name": disease_name,
        "genes": extract_gene_links(rows.get("Disease Genes (Reference)", "")),
        "herbs": (
            extract_herb_links(rows.get("Herbs Associated with This Disease", ""))
            if include_herbs
            else []
        ),
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs(args: argparse.Namespace) -> None:
    out_dir = Path(args.output_dir)
    entities_dir = out_dir / "entities"
    relation_dir = out_dir / "relation"

    disease_rows: list[dict] = []
    gene_rows: list[dict] = []
    herb_rows: list[dict] = []
    disease_gene_rows: list[dict] = []
    disease_herb_rows: list[dict] = []
    failed_rows: list[dict] = []

    gene_to_id: dict[str, str] = {}
    herb_to_id: dict[str, str] = {}
    consecutive_empty = 0

    for etcm_id in range(args.start_id, args.max_id + 1):
        item = parse_disease_page(
            etcm_id,
            timeout=args.timeout,
            retries=args.retries,
            include_herbs=args.include_herbs,
        )

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
        disease_id = f"ETCM_disease_id_{item['etcm_id']}"
        disease_rows.append(
            {
                "id": disease_id,
                "name": item["disease_name"],
                "etcm_id": item["etcm_id"],
            }
        )

        for gene_symbol, source in item["genes"]:
            if gene_symbol not in gene_to_id:
                gene_id = f"ETCM_Gene_{len(gene_to_id) + 1}"
                gene_to_id[gene_symbol] = gene_id
                gene_rows.append({"id": gene_id, "name": gene_symbol})
            disease_gene_rows.append(
                {
                    ":START_ID": disease_id,
                    ":END_ID": gene_to_id[gene_symbol],
                    "source": source,
                    "gene_symbol": gene_symbol,
                }
            )

        if args.include_herbs:
            for herb in item["herbs"]:
                herb_key = herb["ywname"].upper()
                if herb_key not in herb_to_id:
                    herb_id = f"ETCM_Herb_{len(herb_to_id) + 1}"
                    herb_to_id[herb_key] = herb_id
                    herb_rows.append(
                        {
                            "id": herb_id,
                            "name": herb["herb_name"],
                            "ywname": herb["ywname"],
                        }
                    )
                disease_herb_rows.append(
                    {
                        ":START_ID": disease_id,
                        ":END_ID": herb_to_id[herb_key],
                        "source": "ETCM",
                        "herb_ywname": herb["ywname"],
                    }
                )

        if len(disease_rows) % args.progress_every == 0:
            print(
                f"parsed={len(disease_rows)} last_id={etcm_id} "
                f"genes={len(gene_rows)} DG={len(disease_gene_rows)}"
                + (
                    f" herbs={len(herb_rows)} DH={len(disease_herb_rows)}"
                    if args.include_herbs
                    else ""
                ),
                flush=True,
            )

        time.sleep(args.sleep_seconds)

    # Stable dedupe.
    disease_gene_rows = list(
        {(
            r[":START_ID"],
            r[":END_ID"],
            r["source"],
        ): r for r in disease_gene_rows}.values()
    )
    if args.include_herbs:
        disease_herb_rows = list(
            {(
                r[":START_ID"],
                r[":END_ID"],
                r["source"],
            ): r for r in disease_herb_rows}.values()
        )

    write_csv(entities_dir / "disease_etcm_full.csv", disease_rows, ["id", "name", "etcm_id"])
    write_csv(entities_dir / "gene_etcm_full.csv", gene_rows, ["id", "name"])
    write_csv(
        relation_dir / "diseaseTOgene_etcm_full.csv",
        disease_gene_rows,
        [":START_ID", ":END_ID", "source", "gene_symbol"],
    )
    if args.include_herbs:
        write_csv(entities_dir / "herb_etcm_full.csv", herb_rows, ["id", "name", "ywname"])
        write_csv(
            relation_dir / "diseaseTOherb_etcm_full.csv",
            disease_herb_rows,
            [":START_ID", ":END_ID", "source", "herb_ywname"],
        )
    write_csv(out_dir / "failed_disease_ids_etcm_full.csv", failed_rows, ["etcm_id", "reason"])

    print("Done.")
    print(f"Output: {out_dir}")
    print(f"Diseases: {len(disease_rows)}")
    print(f"Genes: {len(gene_rows)}")
    print(f"Disease-Gene edges: {len(disease_gene_rows)}")
    if args.include_herbs:
        print(f"Herbs: {len(herb_rows)}")
        print(f"Disease-Herb edges: {len(disease_herb_rows)}")
    print(f"Failed pages: {len(failed_rows)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--max-id", type=int, default=DEFAULT_MAX_ID)
    parser.add_argument("--max-consecutive-empty", type=int, default=100)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--progress-every", type=int, default=50)
    parser.add_argument(
        "--include-herbs",
        action="store_true",
        help="Also parse disease-to-herb links from disease pages.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory that will receive entities/, relation/, and failed CSV files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    build_outputs(parse_args())
