# BSGAM-style Baseline for HMC-GNN

This folder contains the original BSGAM reference code and an HMC-GNN-adapted baseline:

```text
hmc_bsgam_style.py
```

## Purpose

The original BSGAM model is designed for symptom-set-to-herb-set recommendation. It constructs three graph views and fuses the interaction view with the same-type view through multi-head attention.

Directly comparing the original BSGAM result with HMC-GNN is not fair because HMC-GNN uses disease-to-herb ranking and a disease-label-disjoint split.

The adapted baseline keeps BSGAM's core idea:

```text
multi-graph GCN view learning + multi-head view attention fusion
```

and maps it to:

```text
disease-herb graph
disease-disease graph
herb-herb graph
```

## Fairness Protocol

The adapted BSGAM-style baseline uses:

```text
same disease-label-disjoint split
same candidate herb set
same P/R/F1/NDCG@K metrics
same train disease-herb labels for graph construction
same node-side feature sources
```

It does not use:

```text
relation-aware RGCN
local/global/semantic branch decomposition
semantic residual
graph SSL
cross-modal SSL
property-chemical alignment
```

## Graph Mapping

D-H graph:

```text
treats_disease
rev_treats_disease
```

D-D graph:

```text
disease_herb_jaccard
disease_gene_jaccard
```

H-H graph:

```text
herb_disease_jaccard
herb_gene_jaccard
```

The default same-type setting uses gene-overlap edges:

```text
--same-type-mode gene_jaccard
```

Other modes:

```text
--same-type-mode cooccurrence
--same-type-mode both
```

## Controlled External Context

The script supports:

```text
--global-context external
```

This gives BSGAM-style the same external/global side-information edge pool used by HMC-GNN's global branch, but aggregates it with a plain relation-agnostic GCN and fuses it as an additional attention view. This controls for data availability while preserving the core architectural difference:

```text
BSGAM-style:
  ordinary graph convolution + multi-head view attention

HMC-GNN:
  relation-aware RGCN + complementary local/global/semantic views
```

## Feature Sources

The adapted baseline can use:

```text
node_attributes.pt
node_chem_multihot.pt
node_chem_dense.pt
node_chem_fingerprint.pt / .npy
node_disease_text.pt
node_gene_matrix.pt
```

## Run

Strict local BSGAM-style:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/BSGAM/hmc_bsgam_style.py \
  --same-type-mode gene_jaccard \
  --global-context none \
  --save-path checkpoints/best_bsgam_style_gene_jaccard_local_only.pt
```

Controlled external-data BSGAM-style:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/BSGAM/hmc_bsgam_style.py \
  --same-type-mode gene_jaccard \
  --global-context external \
  --save-path checkpoints/best_bsgam_style_gene_jaccard_controlled.pt
```

Co-occurrence diagnostic:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/BSGAM/hmc_bsgam_style.py \
  --same-type-mode cooccurrence \
  --global-context none \
  --save-path checkpoints/best_bsgam_style_cooccurrence.pt
```

## Interpretation

Report this model as:

```text
BSGAM-style multi-graph attention
```

not as a direct reproduction of BSGAM.

This baseline tests whether a conventional multi-graph attention fusion strategy is sufficient when adapted to disease-herb recommendation. The comparison with HMC-GNN then isolates the additional value of relation-aware heterogeneous propagation, complementary local/global/semantic view learning, semantic residual preservation, and auxiliary alignment objectives.
