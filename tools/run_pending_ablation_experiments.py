import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = os.environ.get("HMC_PYTHON", sys.executable)
OUT_DIR = ROOT / "experiment_outputs"
OUT_DIR.mkdir(exist_ok=True)


EXPERIMENTS = [
    {
        "name": "w_o_same_type_gene_overlap_edges",
        "title": "w/o same-type gene-overlap edges",
        "env": {"HMC_DROP_RELATION_IDS": "12,13"},
        "note": "Drop herb_gene_jaccard and disease_gene_jaccard edges only.",
    },
    {
        "name": "w_o_gene_relations_features",
        "title": "w/o gene relations/features",
        "env": {
            "HMC_DROP_RELATION_IDS": "12,13,14,15,16,17",
            "HMC_DISABLE_GENE_FEATURE": "1",
        },
        "note": "Drop gene-overlap edges, disease/herb-gene relations, and node_gene_matrix.",
    },
    {
        "name": "w_o_chemical_nodes_relations_features",
        "title": "w/o chemical nodes/relations/features",
        "env": {
            "HMC_DROP_RELATION_IDS": "2,3",
            "HMC_DISABLE_CHEM_FEATURES": "1",
        },
        "note": "Drop herb-chemical relations and disable chemical dense/fingerprint/cross-modal streams.",
    },
    {
        "name": "w_o_effect_relations",
        "title": "w/o effect relations",
        "env": {"HMC_DROP_RELATION_IDS": "4,5"},
        "note": "Drop herb-effect relations.",
    },
    {
        "name": "w_o_property_meridian_relations_features",
        "title": "w/o property + meridian relations/features",
        "env": {
            "HMC_DROP_RELATION_IDS": "6,7,8,9",
            "HMC_DISABLE_BASE_ATTR": "1",
        },
        "note": "Drop property/meridian relations and disable base attribute matrix.",
    },
    {
        "name": "local_semantic",
        "title": "local + semantic",
        "env": {"HMC_DISABLE_GLOBAL_BRANCH": "1"},
        "note": "Disable global branch; keep local and semantic branches.",
    },
    {
        "name": "local_only_at50",
        "title": "local only, @50 completed",
        "env": {
            "HMC_DISABLE_GLOBAL_BRANCH": "1",
            "HMC_DISABLE_SEMANTIC_BRANCH": "1",
        },
        "note": "Disable global and semantic branches; keep local branch only.",
    },
]


METRIC_RE = re.compile(
    r"P@(?P<k>\d+)=(?P<p>\d+\.\d+)\s+"
    r"R@\d+=(?P<r>\d+\.\d+)\s+"
    r"F1@\d+=(?P<f1>\d+\.\d+)\s+"
    r"NDCG@\d+=(?P<ndcg>\d+\.\d+)"
)
BEST_RE = re.compile(r"Training Finished\. Best F1@10:\s*(?P<best>\d+\.\d+)")


def run_experiment(spec):
    env = os.environ.copy()
    env.update(spec["env"])
    env["HMC_EXPERIMENT_NAME"] = spec["name"]
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-hmc")

    log_path = OUT_DIR / f"{spec['name']}.log"
    print(f"\n===== Running {spec['title']} =====")
    print(f"Log: {log_path}")

    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            [PYTHON, str(ROOT / "train.py")],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            log_file.write(line)
            log_file.flush()
        returncode = proc.wait()

    stdout = log_path.read_text(encoding="utf-8", errors="replace")
    metrics = {}
    best_val = None
    for line in stdout.splitlines():
        best_match = BEST_RE.search(line)
        if best_match:
            best_val = best_match.group("best")
        metric_match = METRIC_RE.search(line)
        if metric_match:
            k = metric_match.group("k")
            metrics[k] = {
                "P": metric_match.group("p"),
                "R": metric_match.group("r"),
                "F1": metric_match.group("f1"),
                "NDCG": metric_match.group("ndcg"),
            }

    return {
        "name": spec["name"],
        "title": spec["title"],
        "note": spec["note"],
        "env": spec["env"],
        "returncode": returncode,
        "log_path": log_path,
        "best_val": best_val,
        "metrics": metrics,
    }


def write_report(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = OUT_DIR / "PENDING_ABLATION_RESULTS_REVIEW.md"
    lines = [
        "# Pending Ablation Results For Review",
        "",
        f"Generated: {timestamp}",
        "",
        "This file is a temporary review artifact. Results here are not yet merged into `PAPER_EXPERIMENT_NARRATIVE_AUDIT.md`.",
        "",
        "## Summary Table",
        "",
        "| Experiment | Status | Val F1@10 | P@5 | R@5 | F1@5 | NDCG@5 | P@10 | R@10 | F1@10 | NDCG@10 | P@20 | R@20 | F1@20 | NDCG@20 | P@50 | R@50 | F1@50 | NDCG@50 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for result in results:
        status = "OK" if result["returncode"] == 0 else f"FAIL({result['returncode']})"
        row = [result["title"], status, result["best_val"] or "-"]
        for k in ["5", "10", "20", "50"]:
            metric = result["metrics"].get(k, {})
            row.extend([metric.get("P", "-"), metric.get("R", "-"), metric.get("F1", "-"), metric.get("NDCG", "-")])
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Run Details", ""])
    for result in results:
        lines.extend(
            [
                f"### {result['title']}",
                "",
                f"- Status: `{result['returncode']}`",
                f"- Best validation F1@10: `{result['best_val'] or '-'}`",
                f"- Log: `{result['log_path'].relative_to(ROOT)}`",
                f"- Note: {result['note']}",
                "- Environment overrides:",
                "",
                "```text",
            ]
        )
        for key, value in result["env"].items():
            lines.append(f"{key}={value}")
        lines.extend(["```", ""])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main():
    results = [run_experiment(spec) for spec in EXPERIMENTS]
    report_path = write_report(results)
    print(f"\n✅ Wrote review report: {report_path}")
    if any(result["returncode"] != 0 for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
