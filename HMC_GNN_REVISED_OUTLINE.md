# HMC-GNN Revised Manuscript Outline

## 0. Core Positioning

This manuscript should present HMC-GNN as a disease-driven herb recommendation framework built on a constructed multimodal heterogeneous disease-herb knowledge graph. The central problem is not merely that disease input is different from symptom-set input, but that disease-herb supervision is sparse and difficult to generalize from direct labels alone. The revised paper should therefore focus on how external biological and multimodal knowledge is converted into useful recommendation structure.

The final manuscript should retain only three main innovations:

1. Gene-overlap-guided local semantic graph augmentation.
2. Complementary local-global-semantic view learning.
3. Type-aware multimodal semantic fusion with contrastive alignment.

Disease-label-disjoint evaluation, threshold sensitivity, and leakage checks are important experimental rigor, but they should not be written as primary methodological innovations.

## 1. Main Work And Innovation Points

### 1.1 Gene-Overlap-Guided Local Semantic Graph Augmentation

This is the primary innovation of the revised paper.

The key idea is that gene associations should not be used only as node-side features or extra gene nodes. Instead, disease-gene and herb-gene associations can induce same-type semantic relations:

- diseases sharing associated genes may have related biological mechanisms;
- herbs sharing associated genes may have related therapeutic or molecular effects.

Therefore, HMC-GNN computes shared-gene similarity between same-type nodes and uses it to construct disease-disease and herb-herb local semantic edges. The similarity is computed as:

```text
J(i,j) = |G_i ∩ G_j| / |G_i ∪ G_j|
```

where `G_i` and `G_j` are the associated gene sets of two diseases or two herbs.

The graph augmentation pipeline is:

```text
disease-gene / herb-gene associations
-> shared gene filtering
-> Jaccard similarity computation
-> bounded-neighborhood sparsification
-> disease-disease and herb-herb local semantic edges
```

Current main configuration:

```text
Graph variant: g4_gene_bridge_chemical_gene_jaccard
Sparsification: percentile-based
score_percentile: 90.0
Semantic residual: enabled, weight = 0.3
Relation dropout: disabled
Edge-weighted gene-jaccard RGCN: disabled
```

Why this is innovative:

- It transforms gene associations from static side information into graph topology.
- It creates local same-type semantic neighborhoods that compensate for sparse disease-herb labels.
- It avoids relying only on direct disease-herb co-occurrence.
- It provides a biologically informed but still recommendation-oriented graph augmentation mechanism.

What not to overclaim:

- Do not claim causal biomedical mechanisms.
- Do not claim the selected percentile is universally optimal.
- Do not claim gene-overlap alone explains clinical efficacy.

Suggested manuscript phrasing:

```text
Rather than treating gene associations merely as auxiliary node attributes, we use gene overlap to induce local semantic neighborhoods among diseases and herbs. This transforms external biological annotations into recommendation-relevant same-type graph structures, enabling the model to propagate therapeutic signals beyond sparse disease-herb labels.
```

### 1.2 Complementary Local-Global-Semantic View Learning

This is the second main innovation.

The previous unified-graph framing is too simple for the current implementation. The final HMC-GNN should be described as a complementary-view model with three separated views:

1. Local view:
   Direct recommendation labels and local similarity relations.

```text
treats_disease
rev_treats_disease
herb_disease_jaccard
disease_herb_jaccard
herb_gene_jaccard
disease_gene_jaccard
```

2. Global view:
   External heterogeneous knowledge relations after removing local recommendation and similarity edges. These include herb-property, herb-meridian, herb-effect, herb-chemical, disease-gene, herb-gene, and related side-information relations.

3. Semantic view:
   Pure node-level multimodal semantic representation without graph propagation.

Why this is innovative:

- It avoids forcing therapeutic interactions, external knowledge, and raw semantic features into one unified propagation channel.
- It lets local disease/herb similarity and global heterogeneous knowledge contribute complementary information.
- It reduces semantic interference in a highly heterogeneous graph.
- It makes the model easier to explain than a single monolithic graph.

Current implementation:

```text
Global branch: RGCN over external knowledge edges
Local branch: RGCN over disease-herb and same-type local semantic edges
Semantic branch: projected multimodal node semantics without RGCN
Branch fusion: gate
Semantic residual: semantic branch is also injected into graph branches with weight 0.3
```

Semantic residual should be described as an extension of complementary-view learning:

```text
z_global = RGCN_global(x) + beta * z_semantic
z_local  = RGCN_local(x)  + beta * z_semantic
```

where `beta = 0.3` in the current main configuration.

Suggested manuscript phrasing:

```text
We decouple the heterogeneous graph into local, global, and semantic views. The local view captures recommendation-specific and gene-overlap-induced same-type relations, the global view captures external heterogeneous knowledge, and the semantic view preserves raw multimodal node information. A semantic residual path further injects node-level semantics back into graph-propagated representations to mitigate semantic dilution during multi-hop aggregation.
```

### 1.3 Type-Aware Multimodal Semantic Fusion And Contrastive Alignment

This is the third, supporting innovation.

The revised paper should emphasize that herb nodes and disease nodes do not share the same modality structure. Therefore, the model should not use a single shared fusion gate for all nodes.

Herb-side streams:

```text
structural embedding
TCM attribute features
chemical features
gene features
```

Disease-side streams:

```text
structural embedding
disease text features
gene features
```

Type-aware gated fusion:

```text
e_h = Gate_h(e_structure, e_attr, e_chem, e_gene)
e_d = Gate_d(e_structure, e_text, e_gene)
```

The optimization combines recommendation and auxiliary alignment objectives:

```text
L = L_BPR
  + lambda_g L_graph_SSL
  + lambda_c L_cross_modal
  + lambda_p L_property_chemical
```

Why this matters:

- Herb and disease nodes have asymmetric feature availability.
- Chemical signals are especially important for herb representation.
- Text and gene features help disease representation.
- Contrastive and alignment losses prevent graph embeddings from drifting away from meaningful modality-specific semantics.

Suggested manuscript phrasing:

```text
Because herbs and diseases are associated with different semantic modalities, HMC-GNN adopts type-aware multimodal fusion. Herb nodes integrate structural, traditional attribute, chemical, and gene signals, whereas disease nodes integrate structural, textual, and gene signals. The fused representations are further regularized through graph self-supervision and cross-modal semantic alignment objectives.
```

## 2. Revised Paper Structure

## 2.1 Abstract

The abstract should be rewritten around the following logic:

1. Disease-driven herb recommendation suffers from sparse disease-herb labels.
2. Existing methods often use external knowledge as side features or unified graph edges, but do not explicitly transform gene associations into local semantic topology.
3. HMC-GNN introduces gene-overlap-guided local semantic graph augmentation.
4. HMC-GNN learns complementary local, global, and semantic views with type-aware multimodal fusion.
5. Experiments under a disease-label-disjoint protocol show improved recommendation performance.

Suggested abstract skeleton:

```text
Disease-driven herb recommendation aims to rank candidate herbs for a given disease, but direct disease-herb supervision is sparse and difficult to generalize. To address this problem, we propose HMC-GNN, a gene-aware heterogeneous graph recommendation framework. Instead of using gene associations only as auxiliary features, HMC-GNN constructs disease-disease and herb-herb local semantic edges based on shared-gene overlap. The model further decomposes the graph into complementary local, global, and semantic views, and integrates asymmetric herb and disease modalities through type-aware fusion. A semantic residual path preserves raw multimodal semantics during graph propagation, while multi-objective self-supervised alignment improves representation consistency. Experiments on our constructed disease-herb dataset under a disease-label-disjoint protocol demonstrate that HMC-GNN improves top-K herb recommendation performance over internal variants and baselines. AUTHOR_INPUT_NEEDED: final overall comparison numbers.
```

## 2.2 Introduction

### 2.2.1 Background

Introduce disease-driven herb recommendation as an important recommendation task in computational traditional medicine. The input is a disease, and the output is a ranked list of candidate herbs.

The key challenge:

```text
Disease-herb labels are sparse, while useful knowledge is distributed across heterogeneous sources such as herb attributes, chemical information, disease text, and gene associations.
```

Do not frame the novelty mainly as "disease input instead of symptom input." A better framing is:

```text
The central challenge is how to transform sparse disease labels and external biomedical knowledge into effective recommendation structure.
```

### 2.2.2 Limitations Of Existing Work

Group previous methods into three limitations:

1. Co-occurrence and matrix-based methods:
   They capture direct statistical associations but struggle with high-order heterogeneous knowledge.

2. Unified KG/GNN methods:
   They aggregate heterogeneous information, but local recommendation interactions, external knowledge relations, and raw semantic features may interfere when propagated in a single graph.

3. Multimodal feature methods:
   They use chemical, textual, or biological features, but often treat gene associations as side information rather than converting them into local graph structures.

### 2.2.3 Proposed Idea

State the core insight:

```text
Gene overlap can provide local semantic neighborhoods among diseases and herbs. These local neighborhoods should be learned separately from global heterogeneous knowledge and raw node semantics.
```

### 2.2.4 Contributions

Use exactly three main contributions:

1. We propose a gene-overlap-guided local semantic graph augmentation strategy that constructs disease-disease and herb-herb same-type edges from shared gene associations.

2. We design a complementary local-global-semantic view learning framework that separates recommendation-specific local topology, external heterogeneous knowledge, and raw multimodal node semantics, with a semantic residual path to preserve node-level information during graph propagation.

3. We introduce type-aware multimodal semantic fusion with multi-objective contrastive alignment, enabling herbs and diseases to integrate asymmetric modality streams while maintaining graph, chemical, and attribute-level semantic consistency.

Then mention experimental rigor separately:

```text
We evaluate the model under a disease-label-disjoint protocol and conduct ablation, sensitivity, and diagnostic analyses to verify the contribution of each component.
```

Do not list disease-label-disjoint protocol as an innovation.

## 2.3 Related Work

### 2.3.1 Traditional Medicine Recommendation

Discuss PTM, KDHR, BSGAM, PresRecRF, SDPR, MRHAF, NFFGRAM and related prescription/herb recommendation models.

Focus on what they do:

- co-occurrence and topic modeling;
- symptom/syndrome/prescription process modeling;
- heterogeneous graph learning;
- multi-feature and attention-based fusion.

### 2.3.2 Knowledge-Aware Recommendation

Discuss two broad categories:

- KG embedding-based recommendation;
- graph representation learning-based recommendation.

Position HMC-GNN as a graph representation learning-based knowledge-aware recommender because it uses RGCN-style graph propagation over typed relations.

### 2.3.3 Multi-View And Multimodal Graph Learning

Use MRHAF, SDPR, and NFFGRAM as motivating references, but distinguish HMC-GNN clearly:

```text
HMC-GNN does not replicate the syndrome differentiation process or directly adopt a fixed multi-graph design. Instead, it constructs task-specific local semantic views from gene overlap and combines them with global heterogeneous knowledge and raw multimodal semantics.
```

## 2.4 Problem Formulation

Define:

- disease set `D`;
- herb set `H`;
- multimodal node attributes;
- heterogeneous graph `G = (V, E, R)`;
- disease-herb labels;
- top-K ranking objective.

Task:

```text
Given a disease d_i, rank candidate herbs h in H according to predicted relevance score s(d_i, h).
```

Clarify the protocol:

```text
We evaluate under a disease-label-disjoint protocol. Validation and test disease-herb labels are not inserted into the training graph. This is not a fully inductive unseen-node setting, because side information such as disease text and gene associations can still be available.
```

## 2.5 Methodology

### 2.5.1 Dataset And Heterogeneous Graph Construction

Use "our constructed multimodal heterogeneous disease-herb graph" rather than "ETCM-enhanced" as the primary name.

Node types:

```text
disease
herb
chemical
effect
property
meridian
gene
```

Relation types:

```text
treats_disease
has_component
has_effect
has_property
belongs_to_meridian
disease_associated_gene
herb_associated_gene
reverse relations
same-type Jaccard relations
```

Current statistics:

```text
nodes: 17683
relations: 18
edges: 724407
candidate herbs: 395
train/validation/test diseases: 2162 / 270 / 271
train/validation/test label edges: 203815 / 22547 / 22468
```

AUTHOR_INPUT_NEEDED:

- Confirm final edge count for percentile-90 graph if it differs from 724407.
- Fill final `graph_summary.csv` values for the exact main graph directory.

### 2.5.2 Gene-Overlap-Guided Local Semantic Augmentation

Describe the full construction:

1. Build herb-gene and disease-gene sets.
2. Compute shared genes.
3. Compute Jaccard similarity.
4. Apply filtering and sparsification.
5. Add same-type semantic edges.

Main setting:

```text
shared_genes >= 5
Jaccard >= 0.2
sparsification = percentile
score_percentile = 90.0
top-k cap retained after percentile filtering
```

Explain percentile:

```text
The percentile rule keeps high-scoring neighbors according to each node's similarity distribution and then applies a bounded-neighborhood cap. This avoids tying the method to a single fixed K while still controlling graph density.
```

### 2.5.3 Complementary Local-Global-Semantic Views

Local view:

```text
direct disease-herb labels from training diseases
disease/herb co-occurrence Jaccard
disease/herb gene-overlap Jaccard
```

Global view:

```text
external heterogeneous knowledge relations excluding local recommendation and similarity relations
```

Semantic view:

```text
projected multimodal features without graph propagation
```

### 2.5.4 Type-Aware Multimodal Fusion

Write herb and disease fusion separately.

Herb:

```text
structure + TCM attributes + chemical features + gene features
```

Disease:

```text
structure + disease text + gene features
```

Explain why:

```text
Herbs and diseases have asymmetric modality availability; therefore, a shared fusion function would mix incompatible semantics.
```

### 2.5.5 RGCN Encoding And Semantic Residual

Global and local views are encoded by separate RGCN stacks:

```text
z_global = RGCN_global(x, E_global)
z_local  = RGCN_local(x, E_local)
```

Semantic view:

```text
z_sem = MLP(x_semantic)
```

Semantic residual:

```text
z_global = z_global + beta * z_sem
z_local  = z_local  + beta * z_sem
beta = 0.3
```

Branch fusion:

```text
z = Gate(z_global, z_local, z_sem)
```

### 2.5.6 Multi-Objective Optimization

Use:

```text
L = L_BPR
  + lambda_g L_GraphSSL
  + lambda_c L_CrossModal
  + lambda_p L_PropertyChemical
```

Explain each:

- BPR: ranking objective;
- Graph SSL: consistency between perturbed graph views;
- Cross-modal SSL: align graph herb embeddings with chemical representations;
- Property-chemical alignment: align TCM attribute semantics and chemical semantics.

## 2.6 Experimental Setup

### 2.6.1 Dataset Split

Use disease-label-disjoint protocol:

```text
train diseases: 2162
validation diseases: 270
test diseases: 271
```

Important wording:

```text
Validation/test disease-herb labels are excluded from graph construction, while side information is retained as available external knowledge.
```

### 2.6.2 Metrics

Use:

```text
Precision@K
Recall@K
F1@K
NDCG@K
K = 5, 10, 20, 50
```

Clarify NDCG:

```text
Because herb labels are binary and do not contain graded clinical importance, NDCG is computed with binary relevance and evaluates whether true herbs are ranked earlier.
```

### 2.6.3 Implementation Details

Current configuration:

```text
embedding dim: 256
hidden dim: 256
batch size: 1024
learning rate: 1e-3
weight decay: 1e-5
dropout: 0.2
edge dropout: 0.1
epochs: 800
early stopping patience: 20
SSL temperature: 0.2
branch fusion: gate
semantic residual weight: 0.3
gene-overlap percentile: 90.0
```

## 2.7 Results

### 2.7.1 Main Result

Current main model:

```text
HMC-GNN main:
  percentile-90 gene-overlap local semantic graph
  local-global-semantic complementary views
  semantic residual weight 0.3
  type-aware multimodal gated fusion
  all auxiliary objectives enabled
```

Current main result:

```text
Best validation F1@10 = 0.2806
P@5=0.7454   R@5=0.1810   F1@5=0.1984   NDCG@5=0.7948
P@10=0.7044  R@10=0.2715  F1@10=0.2657  NDCG@10=0.7829
P@20=0.6380  R@20=0.3918  F1@20=0.3334  NDCG@20=0.7647
P@50=0.5230  R@50=0.5820  F1@50=0.3889  NDCG@50=0.7746
```

AUTHOR_INPUT_NEEDED:

- Confirm final repeated-run mean/std if required.
- Confirm whether all external baselines have been rerun under the same disease-label-disjoint protocol.

### 2.7.2 Comparison With Old HMC-GNN

Use an internal evolution table:

```text
Old HMC-GNN:
  unified graph
  disease/herb Jaccard co-occurrence
  no gene-overlap same-type semantic augmentation
  no complementary-view decomposition
  no semantic residual

Current HMC-GNN:
  gene-overlap local semantic graph
  local/global/semantic views
  type-aware multimodal fusion
  semantic residual
  multi-objective SSL/alignment
```

### 2.7.3 Gene-Overlap Analysis

Focus on:

- gene-overlap improves same-type local semantic structure;
- percentile sparsification is better than overly loose or overly strict settings;
- continuous edge weighting did not outperform sparse binary local semantic edges.

Do not claim:

- gene-overlap proves biological causality;
- the selected threshold is universal.

## 2.8 Ablation Studies

### 2.8.1 Graph Variant Ablation

```text
g0_base
g3_gene_bridge
g4_gene_bridge_chemical
g4_gene_bridge_chemical_gene_jaccard
```

Purpose:

Show how gene relations, chemical relations, and gene-overlap semantic edges affect performance.

### 2.8.2 Gene Mechanism Ablation

Required variants:

```text
w/o gene
gene-as-feature only
gene-as-node only
gene-jaccard only
all gene components
```

AUTHOR_INPUT_NEEDED:

- Confirm which of these have already been run.
- Mark missing ones as future work only if they cannot be completed.

### 2.8.3 Local Semantic Source Ablation

```text
herb_gene_jaccard only
disease_gene_jaccard only
herb + disease gene_jaccard
```

Purpose:

Separate herb-side and disease-side contribution.

### 2.8.4 Complementary View Ablation

```text
w/o local
w/o global
w/o semantic
local + global
local + global + semantic
branch sum vs branch gate
```

### 2.8.5 Fusion Ablation

```text
add fusion
shared gate
type-aware gate
```

### 2.8.6 Semantic Residual Ablation

Use current sensitivity:

```text
off
0.1
0.2
0.3
0.4
```

Current best:

```text
semantic residual weight = 0.3
```

### 2.8.7 Training Regularization And Edge Strategy Diagnostics

Use as diagnostic, not main innovation:

```text
relation dropout
edge-weighted gene-jaccard RGCN
Top-K / percentile / adaptive sparsification
```

Key conclusion:

```text
Neighbor selection and semantic residual are more important than continuous Jaccard edge weighting in the current model.
```

### 2.8.8 SSL And Alignment Ablation

```text
w/o graph SSL
w/o cross-modal SSL
w/o property-chemical alignment
w/o all auxiliary losses
```

## 2.9 Robustness And Diagnostic Analysis

### 2.9.1 Percentile Sensitivity

Current results:

```text
85: F1@10=0.2277, NDCG@10=0.7029
90: F1@10=0.2657, NDCG@10=0.7829
95: F1@10=0.2479, NDCG@10=0.7437
```

Interpretation:

```text
85 is too permissive, 95 is too strict, and 90 provides the best validation/test balance in the current runs.
```

### 2.9.2 Edge-Weighted Gene-Jaccard Diagnostic

Current conclusion:

```text
Jaccard edge weighting did not improve over sparse binary gene-overlap edges.
```

This supports the claim that the main value lies in constructing useful semantic neighborhoods, not simply scaling messages by similarity scores.

### 2.9.3 Leakage Diagnostic

Use only as rigor:

```text
old graph vs no-leak graph
disease-label-disjoint graph
```

Do not make leakage control a main innovation.

## 2.10 Discussion

Discuss four points:

1. Why gene-overlap local semantic edges improve sparse disease-herb recommendation.
2. Why local/global/semantic decoupling is better than a single unified graph.
3. Why semantic residual helps preserve raw node semantics during graph propagation.
4. Limitations and future work.

Limitations:

- gene overlap does not imply causal therapeutic mechanisms;
- thresholds/percentiles are validation-selected;
- binary disease-herb labels do not encode herb importance;
- external baselines must be rerun under the same protocol for strict comparison;
- only one dataset is currently used.

## 2.11 Conclusion

Conclusion should be compact:

```text
We proposed HMC-GNN, a disease-driven herb recommendation model that transforms gene associations into local semantic graph structure, learns complementary local/global/semantic views, and integrates asymmetric herb/disease modalities through type-aware fusion and contrastive alignment. Experiments under a disease-label-disjoint protocol show that gene-overlap-guided local semantic augmentation and semantic residual view learning improve top-K herb recommendation. Future work will extend the framework to multiple datasets, richer clinical labels, and more adaptive graph sparsification.
```

## 3. Final Contribution Statement For Manuscript

Use this version in the final paper:

```text
The main contributions of this work are summarized as follows.

First, we propose a gene-overlap-guided local semantic graph augmentation strategy for disease-driven herb recommendation. By computing shared-gene Jaccard similarity between same-type nodes, we construct disease-disease and herb-herb semantic edges that transform biological gene associations into recommendation-relevant local topology.

Second, we design a complementary local-global-semantic view learning framework. The local view captures disease-herb interactions and gene-overlap semantic neighborhoods, the global view captures heterogeneous external knowledge, and the semantic view preserves raw multimodal node information. A semantic residual path further mitigates semantic dilution during graph propagation.

Third, we introduce type-aware multimodal fusion and contrastive alignment for asymmetric herb and disease representations. Herbs integrate structural, traditional attribute, chemical, and gene features, whereas diseases integrate structural, textual, and gene features. The model is optimized with ranking, graph self-supervision, cross-modal chemical alignment, and property-chemical alignment objectives.
```

## 4. Terms To Use Consistently

Use:

- constructed multimodal heterogeneous disease-herb graph;
- gene-overlap-guided local semantic augmentation;
- local/global/semantic complementary views;
- type-aware multimodal fusion;
- semantic residual;
- disease-label-disjoint protocol.

Avoid:

- ETCM-enhanced as the main dataset name;
- disease-disjoint as a main innovation;
- Top-K pruning as the core method;
- edge-weighted RGCN as the main contribution;
- causal biological explanation.
