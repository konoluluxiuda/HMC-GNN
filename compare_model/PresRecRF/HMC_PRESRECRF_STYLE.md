# PresRecRF-style Baseline for HMC-GNN

This folder contains the original PresRecRF reference code and an HMC-GNN-adapted baseline:

```text
hmc_presrecrf_style.py
```

## Purpose

The original PresRecRF model is designed for symptom-set-to-herb-set prescription recommendation. Directly comparing its original results with HMC-GNN is not fair because HMC-GNN uses a disease-to-herb ranking task and a disease-label-disjoint protocol.

This adapted baseline keeps the core PresRecRF idea:

```text
semantic representation + structural representation -> fused representation -> herb ranking
```

but evaluates it on the same HMC-GNN disease-herb data split.

## What Is Kept From PresRecRF

- Two-tower disease/herb recommendation formulation.
- Semantic and structural representation fusion.
- Dot-product disease-herb scoring.

## What Is Changed For Fairness

- Symptoms are replaced by diseases.
- The input is a single disease node rather than a symptom set.
- Herb dosage prediction is removed because HMC-GNN has no dosage labels.
- The original random/symptom-prescription split is replaced by the HMC-GNN disease-label-disjoint split.
- The model does not use RGCN, gene-jaccard graph edges, local-global-semantic branches, graph SSL, cross-modal SSL, or property-chemical alignment.

The script also provides an optional fairness-enhanced diagnostic setting:

```text
--local-smoothing {interaction, cooccurrence, gene_jaccard, all_local}
```

This setting gives the PresRecRF-style baseline access to the same local graph edges through relation-agnostic LightGCN-style smoothing. It is useful for comparing the core representation-fusion idea under more similar side information, but it should not be described as a direct PresRecRF reproduction.

## Current Feature Sources

Structural representation:

```text
learnable node ID embedding
```

Semantic representation:

```text
node_attributes.pt
node_chem_multihot.pt
node_chem_dense.pt
node_chem_fingerprint.pt / .npy
node_disease_text.pt
node_gene_matrix.pt
```

The feature directory is automatically selected. If the disease-split graph directory does not contain dense semantic feature files, the script uses:

```text
dataset/NEWHERB/etcm_graph_data/g4_gene_bridge_chemical
```

Gene features are loaded from the disease-split graph directory to keep node alignment.

## Run

Use the same Python environment as the main HMC-GNN experiments:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/PresRecRF/hmc_presrecrf_style.py
```

Short smoke test:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/PresRecRF/hmc_presrecrf_style.py \
  --epochs 2 \
  --eval-interval 1 \
  --patience 2 \
  --save-path /tmp/best_presrecrf_style_smoke.pt
```

Fairness-enhanced local smoothing diagnostic:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/PresRecRF/hmc_presrecrf_style.py \
  --fusion-mode gate \
  --local-smoothing all_local \
  --smoothing-layers 1 \
  --smoothing-alpha 0.5 \
  --save-path checkpoints/best_presrecrf_style_gate_all_local.pt
```

Available local smoothing modes:

```text
none:
  no graph propagation

interaction:
  treats_disease + rev_treats_disease

cooccurrence:
  interaction + herb_disease_jaccard + disease_herb_jaccard

gene_jaccard:
  herb_gene_jaccard + disease_gene_jaccard

all_local:
  interaction + cooccurrence jaccard + gene-jaccard same-type edges
```

## Interpretation

This baseline should be reported as:

```text
PresRecRF-style semantic-structural fusion
```

not as a direct reproduction of PresRecRF.

It tests whether semantic-structural fusion is sufficient under the same disease-herb recommendation protocol. The strict version isolates PresRecRF-style fusion without graph propagation. The local-smoothing version tests whether giving a fusion baseline access to the same local edges can close the gap, while still excluding HMC-GNN's relation-aware RGCN, complementary local/global/semantic views, semantic residual design, and auxiliary alignment objectives.
