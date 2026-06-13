from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT_DIR = Path(__file__).resolve().parent


K_LABELS = ["5", "10", "20", "50"]
X = np.arange(len(K_LABELS))


MODELS = {
    "BPR-MF": {
        "P": [0.2982, 0.2790, 0.2672, 0.2401],
        "R": [0.0426, 0.0677, 0.1086, 0.2069],
        "F1": [0.0525, 0.0742, 0.1061, 0.1537],
        "NDCG": [0.3113, 0.3013, 0.2981, 0.3092],
    },
    "LightGCN": {
        "P": [0.2886, 0.2683, 0.2465, 0.2305],
        "R": [0.0431, 0.0727, 0.1149, 0.2202],
        "F1": [0.0584, 0.0843, 0.1122, 0.1579],
        "NDCG": [0.3034, 0.2917, 0.2810, 0.3047],
    },
    "PresRecRF-style": {
        "P": [0.5904, 0.5339, 0.4819, 0.4078],
        "R": [0.1012, 0.1511, 0.2302, 0.4209],
        "F1": [0.1200, 0.1672, 0.2198, 0.2898],
        "NDCG": [0.6116, 0.5785, 0.5511, 0.5641],
    },
    "KDHR-style": {
        "P": [0.6103, 0.5480, 0.4910, 0.4224],
        "R": [0.1060, 0.1561, 0.2375, 0.4235],
        "F1": [0.1270, 0.1752, 0.2264, 0.2988],
        "NDCG": [0.6321, 0.5954, 0.5663, 0.5825],
    },
    "BSGAM-style": {
        "P": [0.5970, 0.5491, 0.4792, 0.4225],
        "R": [0.1040, 0.1543, 0.2196, 0.4100],
        "F1": [0.1265, 0.1738, 0.2137, 0.2956],
        "NDCG": [0.6288, 0.5988, 0.5581, 0.5801],
    },
    "HMC-GNN": {
        "P": [0.7454, 0.7044, 0.6380, 0.5230],
        "R": [0.1810, 0.2715, 0.3918, 0.5820],
        "F1": [0.1984, 0.2657, 0.3334, 0.3889],
        "NDCG": [0.7948, 0.7829, 0.7647, 0.7746],
    },
}


STYLE = {
    "BPR-MF": {"color": "#9CA3AF", "marker": "o", "lw": 1.8, "alpha": 0.95},
    "LightGCN": {"color": "#6B7280", "marker": "s", "lw": 1.8, "alpha": 0.95},
    "PresRecRF-style": {"color": "#60A5FA", "marker": "^", "lw": 2.0, "alpha": 0.95},
    "KDHR-style": {"color": "#2563EB", "marker": "D", "lw": 2.0, "alpha": 0.95},
    "BSGAM-style": {"color": "#14B8A6", "marker": "P", "lw": 2.0, "alpha": 0.95},
    "HMC-GNN": {"color": "#B91C1C", "marker": "*", "lw": 3.0, "alpha": 1.0},
}


def setup_matplotlib():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


def plot_panel(ax, metric, title, ylabel, ylim):
    for model_name, metrics in MODELS.items():
        style = STYLE[model_name]
        ax.plot(
            X,
            metrics[metric],
            label=model_name,
            color=style["color"],
            marker=style["marker"],
            linewidth=style["lw"],
            markersize=8 if model_name == "HMC-GNN" else 5,
            alpha=style["alpha"],
            zorder=4 if model_name == "HMC-GNN" else 2,
        )

    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xticks(X)
    ax.set_xticklabels(K_LABELS)
    ax.set_xlabel("Top-K")
    ax.set_ylabel(ylabel)
    ax.set_ylim(*ylim)
    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.65)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main():
    setup_matplotlib()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.0), constrained_layout=False)
    panels = [
        ("P", "(a) Precision@K", "Precision", (0.20, 0.82)),
        ("R", "(b) Recall@K", "Recall", (0.00, 0.64)),
        ("F1", "(c) F1@K", "F1-score", (0.00, 0.43)),
        ("NDCG", "(d) NDCG@K", "NDCG", (0.25, 0.84)),
    ]

    for ax, (metric, title, ylabel, ylim) in zip(axes.flat, panels):
        plot_panel(ax, metric, title, ylabel, ylim)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=False,
        columnspacing=1.3,
        handlelength=2.2,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.0, h_pad=1.2)

    png_path = OUT_DIR / "Overall_Performance_Comparison_Current.png"
    pdf_path = OUT_DIR / "Overall_Performance_Comparison_Current.pdf"
    svg_path = OUT_DIR / "Overall_Performance_Comparison_Current.svg"
    fig.savefig(png_path, dpi=600, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")
    print(f"Saved {svg_path}")


if __name__ == "__main__":
    main()
