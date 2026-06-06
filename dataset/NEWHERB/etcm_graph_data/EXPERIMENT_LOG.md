# ETCM Experiment Log

## 2026-06-04 HMC-GNN-ETCM-GeneFeature

### Configuration

Graph:

```text
USE_ETCM_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
USE_TFIDF_GRAPH = False
USE_FULL_GRAPH = False
USE_PAPER_GRAPH = False
USE_SEMANTIC_GRAPH = False
```

Features and SSL:

```text
FUSION_MODE = 'add'
USE_BASE_ATTR = False
USE_CROSS_MODAL = False
USE_PROP_CHEM_ALIGN = False
USE_CHEM_DENSE = False
USE_CHEM_FINGERPRINT = False
USE_DISEASE_TEXT = False
USE_GENE_FEATURE = True
```

Graph statistics:

```text
num_nodes = 17683
num_relations = 16
edge_count = 686925
candidate_herb_count = 395
train_disease_count = 2703
test_disease_count = 2581
```

Gene feature:

```text
node_gene_matrix.pt shape = 17683 × 5655
disease_gene_nnz = 68955
herb_gene_nnz = 46955
combined_gene_nnz = 115910
```

### Test Results

```text
P@5=0.1588   R@5=0.1621   F1@5=0.1151
P@10=0.1549  R@10=0.2691  F1@10=0.1434
P@20=0.1427  R@20=0.4127  F1@20=0.1625
P@50=0.1180  R@50=0.6058  F1@50=0.1624
```

## 2026-06-04 HMC-GNN-ETCM-AllSwitches

### Configuration

`train.py` was configured with the original optional switches enabled:

```text
USE_ETCM_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
```

Feature compatibility:

```text
ETCM g4 node count = 17683
old recommendation_data / paper_graph_data feature node count = 13596
```

Therefore, `train.py` loads optional non-gene features only from the active ETCM graph directory and checks `matrix.shape[0] == num_nodes`.

The optional feature matrices have now been rebuilt for `g4_gene_bridge_chemical/node_map.csv`:

```text
node_attributes.pt       17683 × 24
node_chem_multihot.pt    17683 × 7135
node_chem_fingerprint.pt 17683 × 167
node_chem_dense.pt       17683 × 768
node_disease_text.pt     17683 × 768
```

This all-switches-enabled run loaded graph, gene, attribute, chemical, fingerprint, and disease-text features from the same ETCM node space.

Loaded feature shapes:

```text
node_chem_dense.pt + node_chem_fingerprint.pt = 17683 × 935
node_attributes.pt = 17683 × 24
node_chem_multihot.pt = 17683 × 7135
final_attr_matrix = 17683 × 7159
node_disease_text.pt = 17683 × 768
node_gene_matrix.pt = 17683 × 5655, nnz = 115910
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1250
```

### Test Results

```text
P@5=0.1433   R@5=0.1150   F1@5=0.0912
P@10=0.1488  R@10=0.2323  F1@10=0.1314
P@20=0.1379  R@20=0.3704  F1@20=0.1529
P@50=0.1146  R@50=0.5695  F1@50=0.1562
```

### Compared With GeneFeature

```text
F1@5:  0.0912 vs 0.1151  (-0.0239)
F1@10: 0.1314 vs 0.1434  (-0.0120)
F1@20: 0.1529 vs 0.1625  (-0.0096)
F1@50: 0.1562 vs 0.1624  (-0.0062)
```

Observation: turning on all optional modalities and SSL losses did not improve this run. The most likely reasons to test next are feature noise / over-fusion, the large `node_chem_multihot` dimension, and SSL weight conflict with the gene-enhanced graph.

## 2026-06-04 HMC-GNN-ETCM-AllSwitches-NoGeneFeature

Purpose:

```text
Test whether the rebuilt non-gene .pt feature files introduce the performance drop.
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = False
```

Loaded non-gene feature files will be:

```text
node_attributes.pt
node_chem_dense.pt
node_chem_fingerprint.pt
node_chem_multihot.pt
node_disease_text.pt
```

Note:

```text
This disables Gene-as-feature only. Because the selected graph is still g4_gene_bridge_chemical,
disease-gene and herb-gene edges are still part of the graph structure. A completely no-gene
test requires either g0_base with rebuilt optional features or copying/rebuilding these features
for the g0_base node map.
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1158
```

### Test Results

```text
P@5=0.1388   R@5=0.1023   F1@5=0.0849
P@10=0.1393  R@10=0.1867  F1@10=0.1161
P@20=0.1283  R@20=0.3095  F1@20=0.1372
P@50=0.1117  R@50=0.5266  F1@50=0.1500
```

### Compared With Previous Runs

```text
GeneFeature F1@10:              0.1434
AllSwitches F1@10:              0.1314
AllSwitches-NoGeneFeature F1@10: 0.1161
```

Observation: disabling Gene-as-feature made the all-switches setting worse. This suggests the rebuilt non-gene optional features and/or their SSL losses are likely introducing noise, while gene features are at least partially compensating for that noise in the full setting.

## 2026-06-04 HMC-GNN-PaperGraph-OriginalPT-NoGene

Purpose:

```text
Return to the original paper_graph_data node space and use the original .pt feature files,
with gene data disabled, to compare against the ETCM rebuilt-feature runs.
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = False
USE_PAPER_GRAPH = True
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = False
```

Original paper graph / feature compatibility:

```text
paper_graph_data num_nodes = 13596
edge_count = 577509
num_relations = 12
candidate_herb_count = 395

node_attributes.pt       13596 × 24
node_chem_dense.pt       13596 × 768
node_chem_fingerprint.pt 13596 × 167
node_chem_multihot.pt    13596 × 6985
node_disease_text.pt     13596 × 768
```

## Result: Branch Evaluation Strict vs Fallback Diagnostic

Purpose:

```text
Check whether the historical high score for `g4_gene_bridge_chemical_gene_jaccard`
was caused by evaluation-time MRHAF local-branch fallback. In strict mode, validation
and test explicitly pass the local branch graph. In fallback_full mode, validation and
test intentionally omit local_edge_index/local_edge_type so the local branch falls back
to the provided edge_index, reproducing the older implicit behavior.
```

Shared configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical_gene_jaccard'
FUSION_MODE = 'gated'
feature_fusion_mode = legacy
USE_MRHAF_BRANCH_FUSION = True
BRANCH_FUSION_MODE = 'sum'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
```

### Strict branch evaluation

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1747
```

Test results:

```text
P@5=0.5838   R@5=0.0989   F1@5=0.1179   NDCG@5=0.6182
P@10=0.5258  R@10=0.1472  F1@10=0.1609  NDCG@10=0.5820
P@20=0.4738  R@20=0.2272  F1@20=0.2143  NDCG@20=0.5530
P@50=0.3996  R@50=0.4058  F1@50=0.2825  NDCG@50=0.5602
```

### Fallback-full branch evaluation

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1753
```

Test results:

```text
P@5=0.5904   R@5=0.1012   F1@5=0.1200   NDCG@5=0.6260
P@10=0.5373  R@10=0.1474  F1@10=0.1611  NDCG@10=0.5938
P@20=0.4915  R@20=0.2265  F1@20=0.2186  NDCG@20=0.5690
P@50=0.4237  R@50=0.3979  F1@50=0.2908  NDCG@50=0.5780
```

Analysis:

```text
Fallback-full evaluation does not reproduce the historical F1@10 = 0.2640 result.
It only gives a very small change over strict evaluation at K=10
(F1@10: 0.1609 -> 0.1611). Therefore the historical high score is unlikely to be
explained solely by missing local_edge_index/local_edge_type during evaluation.

The remaining likely causes are a different intermediate model implementation,
different saved checkpoint/state, or a different training/evaluation configuration
not captured by the later experiment log.
```

## Result: HMC-GNN-DiseaseHerbOnly-TypeAwareGate-GeneFeature

Purpose:

```text
Use a cleaner disease/herb-only graph as the main setting.
Gene, chemical, TCM attributes, and disease text are used as node-aligned features only,
not as graph nodes.
```

Graph:

```text
dataset/NEWHERB/disease_split_graph_data/g0_herb_disease_only
```

Graph statistics:

```text
node types:
  disease = 2703
  herb    = 406
num_nodes = 3109
num_relations = 4
edge_count = 426570
candidate_herb_count = 395
```

Relations:

```text
treats_disease
rev_treats_disease
herb_disease_jaccard
disease_herb_jaccard
```

Feature/fusion setting:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g0_herb_disease_only'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
FUSION_MODE = 'gated'

Herb gate:    structure / attr / chem / gene
Disease gate: structure / disease_text / gene
```

Node-aligned feature shapes:

```text
node_attributes.pt       3109 × 24
node_chem_multihot.pt    3109 × 7135
node_chem_fingerprint.pt 3109 × 167
node_chem_dense.pt       3109 × 768
node_disease_text.pt     3109 × 768
node_gene_matrix.pt      3109 × 5655
```

Training:

```text
Final test result was provided by user.
Best validation F1@10 was not included in the copied log.
```

Test results:

```text
P@5=0.5956   R@5=0.1008   F1@5=0.1235   NDCG@5=0.6306
P@10=0.5432  R@10=0.1583  F1@10=0.1727  NDCG@10=0.5985
P@20=0.4815  R@20=0.2352  F1@20=0.2213  NDCG@20=0.5618
P@50=0.4120  R@50=0.4123  F1@50=0.2877  NDCG@50=0.5728
```

Observation:

```text
Compared with the previous disease-split g4 mixed setting, the disease/herb-only graph with
type-aware gated feature fusion improves F1@10 and NDCG@10 while avoiding gene/chemical nodes
in graph propagation. This supports using gene and chemical information as features rather than
as graph nodes for the current main experiment.
```

## Result: HMC-GNN-G4-TypeAwareGate-AllFeature

Purpose:

```text
Evaluate the current manual train.py configuration after introducing type-aware gated fusion.
Unlike the disease/herb-only setting, this run uses the g4 graph, so gene nodes are still present
in graph propagation while gene is also injected as a node-aligned feature.
```

Graph:

```text
dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical
```

Configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
FUSION_MODE = 'gated'

Herb gate:    structure / attr / chem / gene
Disease gate: structure / disease_text / gene
```

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1952
```

Test results:

```text
P@5=0.6015   R@5=0.1036   F1@5=0.1241   NDCG@5=0.6330
P@10=0.5565  R@10=0.1580  F1@10=0.1782  NDCG@10=0.6054
P@20=0.4895  R@20=0.2333  F1@20=0.2233  NDCG@20=0.5682
P@50=0.4264  R@50=0.4196  F1@50=0.2998  NDCG@50=0.5867
```

Comparison with disease/herb-only type-aware run:

```text
Metric   DH-only     G4 current   Delta
P@10     0.5432      0.5565       +0.0133
R@10     0.1583      0.1580       -0.0003
F1@10    0.1727      0.1782       +0.0055
NDCG@10  0.5985      0.6054       +0.0069
P@50     0.4120      0.4264       +0.0144
F1@50    0.2877      0.2998       +0.0121
NDCG@50  0.5728      0.5867       +0.0139
```

Observation:

```text
With type-aware gated fusion, the g4 graph recovers and slightly exceeds the disease/herb-only
graph on top-rank precision, F1@10, and NDCG@10. The gain mainly comes from higher precision
and better ranking quality rather than recall, since R@10 is nearly unchanged. This suggests that
gene-node propagation may be useful when controlled by type-aware feature fusion, but it should
still be reported separately from the disease/herb-only feature-only setting because g4 uses gene
as both graph nodes and node features.
```

## Result: HMC-GNN-G4-MRHAFStyleBranchFusion-AllFeature

Purpose:

```text
Test a lightweight MRHAF-style extension on top of the current g4 configuration.
The model keeps the full g4 graph as a global knowledge branch, extracts a local
disease-herb/Jaccard interaction branch from the same graph, and uses type-aware fused
node semantics as a semantic branch. A branch-level gate learns how much each herb/disease
depends on global, local, and semantic representations.
```

Graph:

```text
dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical
```

Configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
FUSION_MODE = 'gated'
USE_MRHAF_BRANCH_FUSION = True

Node-level herb gate:    structure / attr / chem / gene
Node-level disease gate: structure / disease_text / gene
Branch-level gate:      global / local / semantic
```

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1907
```

Test results:

```text
P@5=0.6037   R@5=0.1060   F1@5=0.1276   NDCG@5=0.6197
P@10=0.5483  R@10=0.1555  F1@10=0.1735  NDCG@10=0.5897
P@20=0.4755  R@20=0.2396  F1@20=0.2203  NDCG@20=0.5526
P@50=0.4142  R@50=0.4148  F1@50=0.2919  NDCG@50=0.5711
```

Comparison with previous g4 type-aware single-branch run:

```text
Metric   G4 single   G4 MRHAF-style   Delta
P@5      0.6015      0.6037           +0.0022
R@5      0.1036      0.1060           +0.0024
F1@5     0.1241      0.1276           +0.0035
NDCG@5   0.6330      0.6197           -0.0133
P@10     0.5565      0.5483           -0.0082
R@10     0.1580      0.1555           -0.0025
F1@10    0.1782      0.1735           -0.0047
NDCG@10  0.6054      0.5897           -0.0157
P@20     0.4895      0.4755           -0.0140
R@20     0.2333      0.2396           +0.0063
F1@20    0.2233      0.2203           -0.0030
NDCG@20  0.5682      0.5526           -0.0156
P@50     0.4264      0.4142           -0.0122
R@50     0.4196      0.4148           -0.0048
F1@50    0.2998      0.2919           -0.0079
NDCG@50  0.5867      0.5711           -0.0156
```

Observation:

```text
The MRHAF-style branch fusion improves the very small-K hit balance at F1@5, but it reduces
the main ranking metrics at K=10/20/50. Compared with the simpler g4 type-aware single-branch
model, the added local/global/semantic branch gate introduces extra parameters and a second
RGCN pass without improving the primary metrics. This suggests that the current data does not
yet provide enough independent branch-specific signal to justify the more complex MRHAF-style
architecture as the main model. It is better kept as an ablation/negative result unless additional
branch supervision, attention regularization, or branch-specific pretraining is introduced.
```

## Result: HMC-GNN-G4-MRHAFStyleComplementaryViews-SumVsGate

Purpose:

```text
Retest the MRHAF-style design after making the three views genuinely complementary.
Compared with the previous branch-fusion run, the global branch no longer uses the full g4 graph.
Instead, g4 is split into:

local branch:
  treats_disease / rev_treats_disease / herb_disease_jaccard / disease_herb_jaccard

global branch:
  external ETCM knowledge edges only, with local recommendation interaction edges removed

semantic branch:
  pure node semantics without random structural embedding or graph propagation
```

Graph/view statistics:

```text
source graph = dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical
total edges  = 714474
local edges  = 426570
global external edges = 287904
```

Shared configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
FUSION_MODE = 'gated'
USE_MRHAF_BRANCH_FUSION = True

Node-level herb semantic gate:    attr / chem / gene
Node-level disease semantic gate: disease_text / gene
Branches:                        global / local / semantic
```

### Branch fusion = sum

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1926
```

Test results:

```text
P@5=0.6030   R@5=0.1002   F1@5=0.1222   NDCG@5=0.6328
P@10=0.5616  R@10=0.1578  F1@10=0.1737  NDCG@10=0.6090
P@20=0.5151  R@20=0.2544  F1@20=0.2360  NDCG@20=0.5891
P@50=0.4421  R@50=0.4508  F1@50=0.3099  NDCG@50=0.6046
```

### Branch fusion = gate

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.1769
```

Test results:

```text
P@5=0.5808   R@5=0.0965   F1@5=0.1162   NDCG@5=0.6091
P@10=0.5273  R@10=0.1428  F1@10=0.1601  NDCG@10=0.5756
P@20=0.4836  R@20=0.2254  F1@20=0.2187  NDCG@20=0.5525
P@50=0.4184  R@50=0.4200  F1@50=0.2929  NDCG@50=0.5709
```

Comparison:

```text
Metric   G4 single   Complementary-sum   Complementary-gate
P@10     0.5565      0.5616              0.5273
R@10     0.1580      0.1578              0.1428
F1@10    0.1782      0.1737              0.1601
NDCG@10  0.6054      0.6090              0.5756
P@20     0.4895      0.5151              0.4836
R@20     0.2333      0.2544              0.2254
F1@20    0.2233      0.2360              0.2187
NDCG@20  0.5682      0.5891              0.5525
P@50     0.4264      0.4421              0.4184
R@50     0.4196      0.4508              0.4200
F1@50    0.2998      0.3099              0.2929
NDCG@50  0.5867      0.6046              0.5709
```

Observation:

```text
After separating local recommendation interactions from global external ETCM knowledge, the
MRHAF-style sum fusion becomes useful. It improves NDCG@10 and substantially improves K=20/50
precision, recall, F1, and NDCG compared with the previous g4 single-branch model. The main
trade-off is that F1@10 is slightly lower because R@10 is almost unchanged and the gain is stronger
at larger K.

The branch-level gate performs worse than both the sum version and the single-branch g4 model.
This indicates that the current training signal is not sufficient for learning reliable per-node
global/local/semantic weights. The simpler MRHAF-style summation is more stable and better aligned
with the original MRHAF final fusion equations.

Current recommendation: keep Complementary-sum as the strongest MRHAF-style candidate, keep
Complementary-gate as a negative fusion ablation, and use G4 single-branch as the simpler strong
baseline.
```

## Result: HMC-GNN-G4-MRHAFStyleComplementaryViews-GeneJaccard-Sum

Purpose:

```text
Test whether adding same-type gene co-occurrence edges improves the complementary MRHAF-style
views. Compared with Complementary-sum, this run uses a new graph variant:

g4_gene_bridge_chemical_gene_jaccard

The local branch now includes both disease-herb interaction edges and same-type gene-similarity
edges:

local branch:
  treats_disease / rev_treats_disease
  herb_disease_jaccard / disease_herb_jaccard
  herb_gene_jaccard / disease_gene_jaccard

global branch:
  external ETCM knowledge edges after removing all local branch relations

semantic branch:
  pure node semantics without graph propagation
```

Gene co-occurrence construction:

```text
herb_gene_jaccard:
  source = herbTOgene_etcm_matched.csv
  shared_genes >= 5
  Jaccard >= 0.2
  Top-K = 10

disease_gene_jaccard:
  source = diseaseTOgene_etcm_matched.csv
  shared_genes >= 5
  Jaccard >= 0.2
  Top-K = 15
```

Graph/view statistics:

```text
source graph = dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical_gene_jaccard
total edges  = 724407
local edges  = 436503
global external edges = 287904

herb_gene_jaccard_edges    = 3620
disease_gene_jaccard_edges = 6313
num_relations = 18
```

Configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical_gene_jaccard'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
FUSION_MODE = 'gated'
USE_MRHAF_BRANCH_FUSION = True
BRANCH_FUSION_MODE = 'sum'
```

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.2770
```

Test results:

```text
P@5=0.7594   R@5=0.1833   F1@5=0.2017   NDCG@5=0.8042
P@10=0.7018  R@10=0.2689  F1@10=0.2640  NDCG@10=0.7840
P@20=0.6323  R@20=0.3847  F1@20=0.3299  NDCG@20=0.7625
P@50=0.5165  R@50=0.5695  F1@50=0.3817  NDCG@50=0.7698
```

Comparison with previous complementary-sum run:

```text
Metric   Complementary-sum   + Gene-Jaccard   Delta
P@5      0.6030              0.7594           +0.1564
R@5      0.1002              0.1833           +0.0831
F1@5     0.1222              0.2017           +0.0795
NDCG@5   0.6328              0.8042           +0.1714
P@10     0.5616              0.7018           +0.1402
R@10     0.1578              0.2689           +0.1111
F1@10    0.1737              0.2640           +0.0903
NDCG@10  0.6090              0.7840           +0.1750
P@20     0.5151              0.6323           +0.1172
R@20     0.2544              0.3847           +0.1303
F1@20    0.2360              0.3299           +0.0939
NDCG@20  0.5891              0.7625           +0.1734
P@50     0.4421              0.5165           +0.0744
R@50     0.4508              0.5695           +0.1187
F1@50    0.3099              0.3817           +0.0718
NDCG@50  0.6046              0.7698           +0.1652
```

Observation:

```text
Adding gene-derived same-type co-occurrence edges produces a very large improvement across all
metrics and all K values. Unlike previous variants where gains were concentrated at larger K,
this run improves both top-rank precision and recall. This suggests that gene-overlap similarity
provides a strong local smoothing signal for both diseases and herbs, allowing the local branch
to propagate information between biologically related diseases/herbs before combining with global
ETCM knowledge and pure semantic features.

This result is strong enough to become the current main candidate, but it also requires careful
validation because the improvement is unusually large. The gene-jaccard edges are external
side-information edges, not disease-herb label leakage, but the paper should explicitly state
that disease/herb gene annotations are assumed available at inference time. Additional checks
should include threshold sensitivity, removal of disease_gene_jaccard, removal of herb_gene_jaccard,
and comparison against gene-as-feature only.
```

## Result: Disease-Gene-Jaccard Threshold Sensitivity with Fixed Herb-Gene-Jaccard

Purpose:

```text
Analyze the effect of disease_gene_jaccard edges under different shared-gene/Jaccard thresholds.
These runs keep the herb_gene_jaccard configuration fixed and only change the disease_gene_jaccard
thresholds, testing how disease-side gene-aware smoothing affects performance under a stable
herb-side setting.
```

Assumption:

```text
The following runs are not disease-only ablations. They retain the herb_gene_jaccard setting and
only vary disease_gene_jaccard. The reported disease_gene_jaccard edge counts are estimated from
the current construction rule with Top-K = 15.
```

### disease_gene_jaccard: shared_genes >= 10, Jaccard >= 0.2

Graph change:

```text
disease_gene_jaccard_edges = 4266
```

Test results:

```text
P@5=0.7100   R@5=0.1580   F1@5=0.1761   NDCG@5=0.7498
P@10=0.6605  R@10=0.2365  F1@10=0.2357  NDCG@10=0.7307
P@20=0.6046  R@20=0.3633  F1@20=0.3085  NDCG@20=0.7172
P@50=0.5052  R@50=0.5673  F1@50=0.3725  NDCG@50=0.7350
```

### disease_gene_jaccard: shared_genes >= 5, Jaccard >= 0.3

Graph change:

```text
disease_gene_jaccard_edges = 2973
```

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.2575
```

Test results:

```text
P@5=0.6945   R@5=0.1503   F1@5=0.1690   NDCG@5=0.7346
P@10=0.6557  R@10=0.2353  F1@10=0.2345  NDCG@10=0.7220
P@20=0.5991  R@20=0.3551  F1@20=0.3049  NDCG@20=0.7068
P@50=0.4914  R@50=0.5526  F1@50=0.3617  NDCG@50=0.7172
```

### disease_gene_jaccard: shared_genes >= 20, Jaccard >= 0.3

Graph change:

```text
disease_gene_jaccard_edges = 530
```

Training:

```text
Early stopping triggered after 40 epochs without improvement.
Best validation F1@10 = 0.2750
```

Test results:

```text
P@5=0.7432   R@5=0.1821   F1@5=0.1964   NDCG@5=0.7944
P@10=0.6908  R@10=0.2662  F1@10=0.2574  NDCG@10=0.7747
P@20=0.6273  R@20=0.3838  F1@20=0.3248  NDCG@20=0.7560
P@50=0.5179  R@50=0.5841  F1@50=0.3831  NDCG@50=0.7706
```

Comparison:

```text
Setting             Edges   P@10    R@10    F1@10   NDCG@10   F1@50   NDCG@50
fixed herb + disease 10 / 0.2    disease=4266    0.6605  0.2365  0.2357  0.7307    0.3725  0.7350
fixed herb + disease 5 / 0.3     disease=2973    0.6557  0.2353  0.2345  0.7220    0.3617  0.7172
fixed herb + disease 20 / 0.3    disease=530     0.6908  0.2662  0.2574  0.7747    0.3831  0.7706
fixed herb + disease 5 / 0.2     disease=6313    0.7018  0.2689  0.2640  0.7840    0.3817  0.7698
```

Observation:

```text
With the herb_gene_jaccard setting fixed, stricter disease-side thresholds can still preserve most
of the improvement. The strictest tested disease setting, shared_genes >= 20 and Jaccard >= 0.3,
adds only 530 disease_gene_jaccard edges but remains close to the default disease 5/0.2 setting
on NDCG@10 and is slightly higher on F1@50/NDCG@50. This suggests that high-confidence disease-gene
similarity edges are more valuable than denser but noisier disease similarity graphs.

Because herb_gene_jaccard is retained in all these runs, these results cannot be interpreted as
disease-only ablations. They show disease-threshold sensitivity under a fixed herb-side gene
smoothing configuration. Next checks should isolate herb_gene_jaccard-only and disease_gene_jaccard-only
under the same random seed.
```

## Next: HMC-GNN-ETCM-DiseaseSplit-G4-GeneFeature

Purpose:

```text
Use a disease-disjoint split so train/val/test are separated by disease ID rather than
random disease-herb edges. This tests generalization to diseases whose herb labels are not
used for graph construction.
```

Generated graph:

```text
dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical
```

Construction:

```text
Target label triples: herbTOdisease.
Split unit: disease ID.
Only train diseases' herb labels are inserted as treats_disease graph edges.
H-H and D-D Jaccard edges are built from train diseases only.
Validation/test disease-herb labels are stored only in rec_data.pt as val_dict/test_dict.
External side-information relations are kept because they are assumed available at inference time.
```

Graph statistics:

```text
num_nodes = 17683
num_relations = 16
edge_count = 714474
train_disease_count = 2162
val_disease_count = 270
test_disease_count = 271
candidate_herb_count = 395
train_label_edges = 203815
val_label_edges = 22547
test_label_edges = 22468
herb_disease_jaccard_edges = 969
disease_herb_jaccard_edges = 17971
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = False
USE_ETCM_LEAK_GRAPH = False
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
```

Feature source:

```text
Graph directory:   dataset/NEWHERB/disease_split_graph_data/g4_gene_bridge_chemical
Feature directory: dataset/NEWHERB/etcm_graph_data/g4_gene_bridge_chemical

node_attributes.pt       17683 × 24
node_chem_dense.pt       17683 × 768
node_chem_fingerprint.pt 17683 × 167
node_chem_multihot.pt    17683 × 7135
node_disease_text.pt     17683 × 768
node_gene_matrix.pt      17683 × 5655
```

Note:

```text
The node_map.csv files for disease_split_graph_data/g4_gene_bridge_chemical and
etcm_graph_data/g4_gene_bridge_chemical are identical, so feature reuse is safe.
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1824
```

### Test Results

```text
P@5=0.5845   R@5=0.1010   F1@5=0.1197
P@10=0.5332  R@10=0.1558  F1@10=0.1701
P@20=0.4550  R@20=0.2344  F1@20=0.2120
P@50=0.3880  R@50=0.4198  F1@50=0.2793
```

### Diagnostic Summary

```text
DiseaseSplit-G4-GeneFeature:        F1@10 = 0.1701
ETCM-Leak-NewPT-NoGeneFeature:      F1@10 = 0.1641
PaperGraph-OriginalPT-NoGene:       F1@10 = 0.1788
PaperGraph-NoLeak-OriginalPT-NoGene:F1@10 = 0.1191
```

Observation: the disease-disjoint protocol gives much higher precision than previous edge-split no-leak runs. This indicates that the new protocol is not simply harder in every metric; it changes the task to ranking herbs for unseen diseases using side information. Recall is lower at small K because each held-out disease can have many relevant herbs, while top-K precision is strong.

## 2026-06-05 HMC-GNN-ETCM-DiseaseSplit-G4-ChemicalNoGeneChemical

Purpose:

```text
Use chemical information while avoiding direct chemical-gene relations.
```

Configuration:

```text
USE_DISEASE_SPLIT_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = True
```

Relation check:

```text
Included: herbTOchemical, diseaseTOgene, herbTOgene
Excluded: chemicalTOgene / chemical_associated_gene
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1825
```

### Test Results

```text
P@5=0.5860   R@5=0.1011   F1@5=0.1197
P@10=0.5339  R@10=0.1559  F1@10=0.1703
P@20=0.4559  R@20=0.2348  F1@20=0.2125
P@50=0.3885  R@50=0.4199  F1@50=0.2795
```

Observation: this result is almost identical to the previous disease-split G4 run (`F1@10 = 0.1701`). This confirms that the current G4 setting already avoids direct chemical-gene edges; chemical information is coming from herb-chemical relations and chemical feature matrices, not from `chemicalTOgene`.

## Next: Gene-as-node vs Gene-as-feature

Purpose:

```text
Test whether gene information works better as node-level graph propagation, feature-level semantic injection, or both.
```

`train.py` now supports `EXPERIMENT_PRESET`:

```text
gene_feature_only:
  graph = disease_split_graph_data/g0_base
  gene graph edges = no
  node_gene_matrix.pt = yes
  other optional features = no

gene_node_only:
  graph = disease_split_graph_data/g3_gene_bridge
  gene graph edges = yes
  node_gene_matrix.pt = no
  other optional features = no

gene_hybrid:
  graph = disease_split_graph_data/g3_gene_bridge
  gene graph edges = yes
  node_gene_matrix.pt = yes
  other optional features = no
```

Run commands:

```bash
EXPERIMENT_PRESET=gene_feature_only /home/zry/.conda/envs/mkgformer/bin/python /home/zry/workspace/HMC-GNN/train.py
EXPERIMENT_PRESET=gene_node_only /home/zry/.conda/envs/mkgformer/bin/python /home/zry/workspace/HMC-GNN/train.py
EXPERIMENT_PRESET=gene_hybrid /home/zry/.conda/envs/mkgformer/bin/python /home/zry/workspace/HMC-GNN/train.py
```

Important:

```text
Current default is gene_feature_only.
The previous disease-split G4 result used both gene graph edges and gene features, plus chemical/TCM/disease-text features.
These new presets isolate gene information by disabling chemical, TCM attribute, disease text, cross-modal loss, and property-chemical alignment.
```

Recorded results:

```text
1) Gene-as-feature only
Preset: gene_feature_only
Graph: disease_split_graph_data/g0_base
Gene as node: no
Gene as feature: yes
Other optional features/losses: off
Best validation F1@10: 0.1836
Test:
  P@5=0.6118  R@5=0.1057  F1@5=0.1279  NDCG@5=0.6403
  P@10=0.5454  R@10=0.1514  F1@10=0.1667  NDCG@10=0.6008
  P@20=0.4893  R@20=0.2287  F1@20=0.2211  NDCG@20=0.5681
  P@50=0.4184  R@50=0.4111  F1@50=0.2909  NDCG@50=0.5798

2) Gene-as-node only
Preset: gene_node_only
Graph: disease_split_graph_data/g3_gene_bridge
Gene as node: yes
Gene as feature: no
Other optional features/losses: off
Best validation F1@10: 0.1817
Test:
  P@5=0.5845  R@5=0.1025  F1@5=0.1221  NDCG@5=0.6215
  P@10=0.5247  R@10=0.1483  F1@10=0.1613  NDCG@10=0.5838
  P@20=0.4642  R@20=0.2328  F1@20=0.2107  NDCG@20=0.5525
  P@50=0.4130  R@50=0.4450  F1@50=0.2989  NDCG@50=0.5823

3) Gene hybrid
Preset: gene_hybrid
Graph: disease_split_graph_data/g3_gene_bridge
Gene as node: yes
Gene as feature: yes
Other optional features/losses: off
Best validation F1@10: 0.1787
Test:
  P@5=0.5734  R@5=0.0952  F1@5=0.1155  NDCG@5=0.6011
  P@10=0.5269  R@10=0.1458  F1@10=0.1629  NDCG@10=0.5721
  P@20=0.4721  R@20=0.2237  F1@20=0.2128  NDCG@20=0.5416
  P@50=0.3967  R@50=0.4021  F1@50=0.2772  NDCG@50=0.5489
```

Conclusion:

```text
Under isolated gene-information settings, Gene-as-feature is currently the strongest on validation F1@10, test P@5/P@10, test F1@10, and NDCG@5/10/20.
Gene-as-node improves recall at K=50 in this run, but it is weaker at the top-rank metrics used by the main recommendation setting.
The train.py default is therefore set to gene_feature_only for the next focused test.
```

### Test Results

```text
P@5=0.1303   R@5=0.1000   F1@5=0.0797
P@10=0.1368  R@10=0.2040  F1@10=0.1191
P@20=0.1349  R@20=0.3427  F1@20=0.1475
P@50=0.1137  R@50=0.5480  F1@50=0.1543
```

Observation: removing held-out disease-herb edges from the original paper graph drops F1@10 from `0.1788` to `0.1191`. This strongly supports the leakage hypothesis: the original paper graph result was substantially boosted by test disease-herb edges being present in graph propagation.

## Next: HMC-GNN-ETCM-Leak-AllSwitches-NewPT-NoGeneFeature

Purpose:

```text
Use the rebuilt ETCM .pt feature files under a leak diagnostic graph to determine whether
the low ETCM results are mainly caused by stricter no-leak graph construction or by the new
feature files themselves.
```

Generated graph:

```text
dataset/NEWHERB/etcm_graph_leak_data/g4_gene_bridge_chemical
```

Construction:

```text
The recommendation train/test split is unchanged.
All disease-herb positives, including held-out positives, are inserted into the graph.
H-H and D-D Jaccard edges are rebuilt from all disease-herb positives.
```

Graph statistics:

```text
num_nodes = 17683
num_relations = 16
edge_count = 810855
all_treats_disease_edges_bidirectional = 497660
herb_disease_jaccard_edges = 899
disease_herb_jaccard_edges = 24392
candidate_herb_count = 395
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = False
USE_ETCM_LEAK_GRAPH = True
ETCM_GRAPH_VARIANT = 'g4_gene_bridge_chemical'
USE_PAPER_NOLEAK_GRAPH = False
USE_PAPER_GRAPH = False
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = False
```

Feature source:

```text
Graph directory:   dataset/NEWHERB/etcm_graph_leak_data/g4_gene_bridge_chemical
Feature directory: dataset/NEWHERB/etcm_graph_data/g4_gene_bridge_chemical

node_attributes.pt       17683 × 24
node_chem_dense.pt       17683 × 768
node_chem_fingerprint.pt 17683 × 167
node_chem_multihot.pt    17683 × 7135
node_disease_text.pt     17683 × 768
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1685
```

### Test Results

```text
P@5=0.1851   R@5=0.2179   F1@5=0.1404
P@10=0.1723  R@10=0.3262  F1@10=0.1641
P@20=0.1589  R@20=0.4658  F1@20=0.1816
P@50=0.1268  R@50=0.6413  F1@50=0.1741
```

### Diagnostic Summary

```text
PaperGraph-OriginalPT-NoGene:        F1@10 = 0.1788
PaperGraph-NoLeak-OriginalPT-NoGene: F1@10 = 0.1191
ETCM-Leak-NewPT-NoGeneFeature:       F1@10 = 0.1641
ETCM-AllSwitches-NoGeneFeature:      F1@10 = 0.1161
```

Observation: the rebuilt ETCM `.pt` feature files are not the main cause of the low ETCM no-leak results. When held-out disease-herb edges and full H-H / D-D Jaccard edges are added back into the ETCM graph, performance recovers close to the original paper graph baseline. The dominant factor is graph leakage / graph density, especially the disease-herb and Jaccard construction.

## Next: HMC-GNN-ETCM-ChemFeature

Purpose:

```text
Plan3: test ETCM herb-chemical information explicitly as herb chemical semantic features.
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = True
ETCM_GRAPH_VARIANT = 'g0_base'
USE_PAPER_GRAPH = False
FUSION_MODE = 'add'
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_herb_chemical_etcm.pt'
USE_BASE_ATTR = False
USE_PROP_CHEM_ALIGN = False
USE_CHEM_DENSE = False
USE_CHEM_FINGERPRINT = False
USE_DISEASE_TEXT = False
USE_GENE_FEATURE = False
```

Feature:

```text
node_herb_chemical_etcm.pt = 17683 × 7135
nonzero herb-chemical entries = 10203
source = relation/herbTOchemical_etcm_matched.csv
```

Note:

```text
This is a no-gene Plan3 test. It uses g0_base rather than g4 so gene edges are not present in the graph.
```

Training:

```text
Early stopping triggered after 100 epochs without improvement.
Best validation F1@10 = 0.1169
```

### Test Results

```text
P@5=0.1190   R@5=0.1092   F1@5=0.0853
P@10=0.1226  R@10=0.2004  F1@10=0.1129
P@20=0.1201  R@20=0.3340  F1@20=0.1355
P@50=0.1054  R@50=0.5337  F1@50=0.1440
```

### Current F1@10 Summary

```text
PaperGraph-OriginalPT-NoGene:       0.1788
ETCM-GeneFeature:                   0.1434
ETCM-AllSwitches:                   0.1314
ETCM-AllSwitches-NoGeneFeature:     0.1161
ETCM-ChemFeature:                   0.1129
```

Observation: Plan3 did not improve performance in this isolated setting. The ETCM herb-chemical feature alone is weaker than the gene-feature run and also weaker than the original paper graph baseline.

## Next: HMC-GNN-PaperGraph-NoLeak-OriginalPT-NoGene

Purpose:

```text
Test whether the original paper_graph_data result is inflated because held-out disease-herb
edges were inserted into the graph before the recommendation train/test split.
```

Generated graph:

```text
dataset/NEWHERB/paper_graph_noleak_data
```

Construction:

```text
The train/test split is reused from paper_graph_data/rec_data.pt.
Only train_dict disease-herb positives are inserted as treats_disease graph edges.
H-H and D-D Jaccard edges are rebuilt from train_dict only.
Non-recommendation TCM relation edges are kept from the original KGE splits.
```

Graph statistics:

```text
num_nodes = 13596
num_relations = 12
edge_count = 453552
train_treats_disease_edges_bidirectional = 396130
skipped_non_train_treats_disease_rows = 50765
herb_disease_jaccard_edges = 0
disease_herb_jaccard_edges = 2864
candidate_herb_count = 395
```

Configuration prepared in `train.py`:

```text
USE_ETCM_GRAPH = False
USE_PAPER_NOLEAK_GRAPH = True
USE_PAPER_GRAPH = False
FUSION_MODE = 'gated'
USE_BASE_ATTR = True
USE_CROSS_MODAL = True
CHEM_MATRIX_FILENAME = 'node_chem_dense.pt'
USE_PROP_CHEM_ALIGN = True
USE_CHEM_DENSE = True
USE_CHEM_FINGERPRINT = True
USE_DISEASE_TEXT = True
USE_GENE_FEATURE = False
```

Feature source:

```text
Graph directory:   dataset/NEWHERB/paper_graph_noleak_data
Feature directory: dataset/NEWHERB/paper_graph_data

node_attributes.pt       13596 × 24
node_chem_dense.pt       13596 × 768
node_chem_fingerprint.pt 13596 × 167
node_chem_multihot.pt    13596 × 6985
node_disease_text.pt     13596 × 768
```
