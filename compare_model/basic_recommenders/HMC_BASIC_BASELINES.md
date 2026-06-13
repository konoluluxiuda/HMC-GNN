# Basic Recommender Baselines for HMC-GNN

This folder contains two classic recommendation baselines adapted to the HMC-GNN disease-herb protocol:

```text
hmc_bpr_lightgcn.py
```

## Baselines

### BPR-MF

Core idea:

```text
learn disease and herb latent embeddings from implicit disease-herb interactions
optimize Bayesian Personalized Ranking loss
```

Paper support:

```text
Rendle et al., BPR: Bayesian Personalized Ranking from Implicit Feedback, UAI 2009.
Koren et al., Matrix Factorization Techniques for Recommender Systems, IEEE Computer 2009.
```

### LightGCN

Core idea:

```text
build a disease-herb bipartite graph
propagate embeddings through lightweight graph convolution
average layer-wise embeddings for ranking
```

Paper support:

```text
He et al., LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation, SIGIR 2020.
```

## Fairness Protocol

Both baselines use:

```text
same disease-label-disjoint split
same candidate herb set
same P/R/F1/NDCG@K metrics
same train disease-herb labels
```

They intentionally do not use:

```text
node-side semantic features
gene-overlap edges
external heterogeneous knowledge edges
RGCN
local/global/semantic branch decomposition
SSL/alignment losses
```

This keeps them faithful to their original collaborative-filtering assumptions. They should be interpreted as general recommendation baselines rather than knowledge-aware TCM baselines.

## Run

BPR-MF:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/basic_recommenders/hmc_bpr_lightgcn.py \
  --model bprmf \
  --save-path checkpoints/best_bprmf.pt
```

LightGCN:

```bash
/home/zry/.conda/envs/mkgformer/bin/python compare_model/basic_recommenders/hmc_bpr_lightgcn.py \
  --model lightgcn \
  --lightgcn-layers 3 \
  --save-path checkpoints/best_lightgcn.pt
```

## Interpretation

These baselines answer two basic questions:

```text
BPR-MF:
  Is latent collaborative filtering over disease-herb interactions sufficient?

LightGCN:
  Is high-order propagation over the disease-herb bipartite graph sufficient?
```

The comparison with HMC-GNN then shows whether external biomedical knowledge, relation-aware graph propagation, multimodal semantic fusion, and complementary view learning provide additional benefits beyond standard collaborative filtering.
