# KDHR-style Baseline for HMC-GNN

This folder contains the original KDHR reference code and an HMC-GNN-adapted baseline:

```text
hmc_kdhr_style.py
```

## Purpose

The original KDHR model is designed for symptom-set-to-herb-set recommendation. It constructs three graphs:

```text
symptom-herb graph
symptom-symptom graph
herb-herb graph
```

Directly comparing the original KDHR result with HMC-GNN is not fair because HMC-GNN uses disease-to-herb ranking and a disease-label-disjoint split.

The adapted baseline keeps KDHR's core multi-graph GCN idea and maps it to:

```text
disease-herb graph
disease-disease graph
herb-herb graph
```

## Fairness Protocol

The adapted KDHR-style baseline uses:

```text
same disease-label-disjoint split
same candidate herb set
same P/R/F1/NDCG@K metrics
same train disease-herb labels for graph construction
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

By default, the adapted script uses a controlled-data setting:

```text
--global-context external
```

This gives KDHR-style the same external/global side-information edge pool used by HMC-GNN's global branch, but aggregates it with a plain relation-agnostic GCN layer. This controls for data availability while preserving the core architectural difference: ordinary KDHR-style multi-graph GCN fusion versus HMC-GNN's relation-aware local/global/semantic view learning.

To run a stricter KDHR-core-only variant without external/global context:

```text
--global-context none
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

The default setting uses both co-occurrence Jaccard and gene-Jaccard same-type edges:

```text
--same-type-mode both
```

Other modes:

```text
--same-type-mode cooccurrence
--same-type-mode gene_jaccard
```

## Feature Sources

The adapted baseline can use the same node-side information as HMC-GNN:

```text
node_attributes.pt
node_chem_multihot.pt
node_chem_dense.pt
node_chem_fingerprint.pt / .npy
node_disease_text.pt
node_gene_matrix.pt
```

These features are projected into the node input embedding and fused with the learnable structural embedding. This keeps side information comparable while preserving KDHR's core three-graph GCN structure.

## Run

Default fairness-enhanced KDHR-style baseline:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/KDHR/hmc_kdhr_style.py \
  --same-type-mode both \
  --global-context external \
  --save-path checkpoints/best_kdhr_style_both.pt
```

Co-occurrence-only variant:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/KDHR/hmc_kdhr_style.py \
  --same-type-mode cooccurrence \
  --global-context external \
  --save-path checkpoints/best_kdhr_style_cooccurrence.pt
```

Gene-Jaccard-only variant:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/KDHR/hmc_kdhr_style.py \
  --same-type-mode gene_jaccard \
  --global-context external \
  --save-path checkpoints/best_kdhr_style_gene_jaccard.pt
```

Strict KDHR-core-only variant:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/KDHR/hmc_kdhr_style.py \
  --same-type-mode gene_jaccard \
  --global-context none \
  --save-path checkpoints/best_kdhr_style_gene_jaccard_local_only.pt
```

Optional normalized scoring diagnostic:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/KDHR/hmc_kdhr_style.py \
  --same-type-mode both \
  --normalize-score \
  --save-path checkpoints/best_kdhr_style_both_norm.pt
```

## Interpretation

Report this model as:

```text
KDHR-style multi-graph GCN
```

not as a direct reproduction of KDHR.

This baseline tests whether a conventional three-graph GCN fusion strategy is sufficient when adapted to disease-herb recommendation. The comparison with HMC-GNN then isolates the additional value of relation-aware heterogeneous propagation, complementary local/global/semantic view learning, semantic residual preservation, and auxiliary alignment objectives.
