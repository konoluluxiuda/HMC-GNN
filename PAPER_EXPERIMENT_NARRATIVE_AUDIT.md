# HMC-GNN Paper Experiment Narrative Audit

Date: 2026-06-07

Purpose: answer key manuscript-positioning questions before rewriting the paper, with a focus on whether the current experimental narrative is logically defensible and aligned with the implemented HMC-GNN.

## 1. Main Configuration: Gate as Final Model, Sum as Ablation

Latest user decision:

```text
Final main configuration: gate
Sum result:
P@5=0.5786   R@5=0.0993   F1@5=0.1186   NDCG@5=0.6083
P@10=0.5465  R@10=0.1551  F1@10=0.1725  NDCG@10=0.5906
P@20=0.4810  R@20=0.2316  F1@20=0.2203  NDCG@20=0.5554
P@50=0.4008  R@50=0.3925  F1@50=0.2811  NDCG@50=0.5558
Best validation F1@10 = 0.1901
```

Important caveat:

The current manuscript narrative must distinguish between:

- branch fusion strategy: `sum` vs `gate`;
- feature fusion strategy: type-aware gate for herb/disease features;
- gene-jaccard graph construction.

If gate is the final main model, the paper should not use previous `sum` high-score logs as the main result unless that exact configuration is restored and rerun. The current `sum` result above is much lower than the earlier logged gene-jaccard-sum result, so the safest narrative is:

```text
Gate is the final architecture because it is more flexible and node-adaptive.
Sum is reported as an ablation or diagnostic baseline.
AUTHOR_INPUT_NEEDED: final gate test result table.
```

Risk:

If the final gate result is not clearly better than sum or simpler baselines, the paper should not overclaim branch-gate effectiveness. It can still claim the framework supports adaptive branch weighting, but the ablation must be reported honestly.

## 2. Dataset Naming: Avoid "ETCM-enhanced"

The dataset should be presented as the paper's own constructed dataset, not as merely "ETCM-enhanced."

Recommended wording:

```text
We construct a multimodal disease-herb recommendation dataset by integrating disease-herb labels, herb attributes, chemical information, disease textual semantics, and gene associations.
```

Avoid:

```text
ETCM-enhanced graph
ETCM-enhanced benchmark
```

Use instead:

```text
the constructed NEWHERB dataset
our multimodal disease-herb dataset
the proposed HMC-GNN dataset
```

ETCM can still be described as one data source for herb attributes, chemical relations, and gene associations. The paper should not make ETCM sound like the sole contribution or the whole dataset.

## 3. Gene Only as Co-occurrence Edge: Is the Innovation Sufficient?

Concern:

If gene only contributes through same-type co-occurrence edges, and this alone causes a large improvement, reviewers may argue that the method is a dataset-specific graph engineering trick rather than a substantial model innovation.

Assessment:

This concern is valid. Gene-overlap edges alone are not enough to support a broad "new model" claim unless they are embedded in a clearer methodological framework.

Defensible framing:

Do not present the contribution as "we add gene edges." Present it as:

```text
external biological associations are transformed into local semantic topology among diseases and herbs.
```

This is stronger because the work is not simply adding a new entity type. It converts cross-type biological annotations into same-type local smoothing structures:

- disease-gene associations -> disease-disease semantic proximity;
- herb-gene associations -> herb-herb semantic proximity.

Still, this needs supporting experiments:

- w/o gene-jaccard;
- herb-gene-jaccard only;
- disease-gene-jaccard only;
- gene-as-feature only;
- gene-as-node only;
- all gene mechanisms.

If these ablations are missing, the claim should be conservative:

```text
Gene-overlap provides an effective local semantic augmentation in our dataset.
```

Rather than:

```text
Gene-overlap is a general solution for disease-driven herb recommendation.
```

## 4. Is the Dataset Multimodal?

Yes, the dataset can be called multimodal, but the paper must define modalities carefully.

Valid modalities:

- graph topology: disease-herb and heterogeneous knowledge relations;
- TCM attributes: property, flavor, meridian/channel tropism;
- chemical semantics: chemical components, fingerprints, dense chemical embeddings;
- disease text semantics: disease textual embeddings;
- biological gene associations: disease-gene and herb-gene annotations.

Recommended wording:

```text
The dataset is multimodal in the sense that each disease or herb can be represented through heterogeneous graph structure, textual semantics, TCM attribute vectors, chemical descriptors, and gene-associated biological annotations.
```

Do not overstate:

- gene annotations are not omics measurements;
- chemical features are derived representations, not necessarily experimentally measured compound abundance;
- disease text and gene associations may have uneven coverage.

## 5. Fairness When Comparing Against Symptom-set Models

Concern:

Many baselines in the literature take symptom sets as input, while this project uses a single disease query. Direct comparison can be unfair.

Assessment:

The previous explanation is directionally correct but not sufficient by itself:

```text
Do not merely say symptom-driven vs disease-driven differs by input sparsity.
```

A fairer explanation is:

```text
Our task is not intended to reproduce symptom-set prescription generation. Instead, we study disease-query herb recommendation, where the input is a disease entity and the model must rely on structured side information to rank candidate herbs. Symptom-set models are included only when they can be adapted to the same disease-herb label space and evaluated under the same candidate herb set.
```

Rules for fair comparison:

1. If a baseline requires symptom sets and no comparable symptom input exists, do not present it as a strict baseline.
2. If adapted, state exactly how disease was converted into that baseline's input.
3. Use the same train/val/test split.
4. Use the same candidate herb list.
5. Use the same metrics.

Recommended paper structure:

- Main comparison: methods that can operate on disease-herb recommendation.
- Secondary comparison: adapted symptom-set models, explicitly labeled as adapted baselines.
- Discussion: disease-query recommendation is a different setting, not necessarily easier or harder in every metric.

The statement "disease labels are sparse and external biomedical knowledge must be transformed into recommendation structure" is good and should become the main motivation.

## 6. Is Top-K in Gene-overlap Augmentation Too Rigid?

Concern:

Fixed Top-K and threshold rules may look dataset-specific.

Assessment:

Yes, if presented as a fixed handcrafted trick. No, if presented as a general sparsification operator with sensitivity analysis.

Recommended framing:

```text
Top-K is not the innovation itself. It is a sparsification mechanism used to control graph density after computing gene-overlap similarity.
```

What to emphasize:

- shared-gene/Jaccard computes biological similarity;
- threshold removes weak/noisy overlaps;
- Top-K controls degree and prevents hub-like semantic edges;
- sensitivity analysis tests robustness.

Avoid claiming:

```text
K=10 or K=15 is universally optimal.
```

Use:

```text
The exact K is dataset-dependent; the method only requires a bounded-neighborhood sparsification step.
```

Potential improvement:

Instead of fixed Top-K, mention future or optional alternatives:

- validation-selected K;
- adaptive degree based on similarity distribution;
- percentile threshold;
- learnable edge weighting;
- degree-aware pruning.

For the current paper, fixed Top-K is acceptable if the threshold sensitivity section is honest and does not look like test-set tuning.

Implementation note:

`preprocess_disease_split_graph.py` now supports multiple gene-jaccard sparsification modes:

```text
--gene-jaccard-sparsify-mode topk       # historical default
--gene-jaccard-sparsify-mode percentile # keep per-source high-percentile scores, then cap by topk
--gene-jaccard-sparsify-mode adaptive   # keep scores above mean + alpha * std, then cap by topk
```

Additional controls:

```text
--gene-jaccard-score-percentile
--gene-jaccard-adaptive-alpha
--gene-jaccard-min-topk
```

The default remains `topk`, so existing graph construction is unchanged unless these options are explicitly used. The script also exports `gene_jaccard_edges.csv` with each selected edge's Jaccard score and shared-gene count, making sensitivity analysis more transparent.

Suggested manuscript wording:

```text
The proposed gene-overlap augmentation does not depend on a specific fixed K. In our implementation, Top-K is used as a bounded-neighborhood sparsification operator. We further examine percentile-based and adaptive score-based sparsification to verify that the improvement is not tied to a single dataset-specific threshold.
```

## 7. Is RGCN Encoding Too Simple? How to Improve It?

Concern:

RGCN is a standard encoder. If the whole model is just RGCN plus engineered graph edges, model novelty may look weak.

Assessment:

This is a real risk. RGCN itself should not be presented as the main innovation. It should be presented as the relation-aware backbone.

Possible improvements more aligned with this task:

1. Relation-level attention over RGCN messages
   - Learn which relation types matter more for a given node.
   - Especially useful because local, global, and gene relations are semantically different.

2. Type-aware relation aggregation
   - Separate herb-side and disease-side aggregation weights.
   - This matches current type-aware feature fusion.

3. Edge-weighted RGCN
   - Use Jaccard/gene-overlap values as edge weights instead of treating all semantic edges equally.
   - This would make gene-jaccard less like a binary handcrafted edge.

4. Local-global residual fusion
   - Add residual path from semantic branch to graph branches.
   - Prevent over-smoothing and preserve raw disease/herb semantics.

5. Relation dropout or relation gating
   - Randomly drop relation groups during training.
   - Helps show robustness and prevents dependence on one engineered relation.

Most practical near-term improvement:

```text
Use edge-weighted or relation-gated RGCN for gene-overlap edges.
```

This is the most aligned with the current paper because it turns gene-jaccard from binary graph construction into a more principled weighted semantic propagation mechanism.

## 8. Are the Three Non-BPR Losses Important Enough?

The three auxiliary losses are:

- graph SSL;
- cross-modal graph-chemical SSL;
- property-chemical alignment.

Assessment:

They are defensible because the previous TeX manuscript already built the paper around multimodal contrastive alignment. However, in the current version they should be secondary, not the central contribution.

Why they are still useful:

- BPR optimizes ranking only and may overfit observed disease-herb labels.
- graph SSL stabilizes graph representations under perturbation.
- cross-modal SSL keeps herb embeddings aligned with chemical semantics.
- property-chemical alignment supports the macro/micro TCM-biochemical narrative.

Risk:

If ablations show small gains, reviewers may question why these losses are central.

Recommended writing:

```text
The auxiliary objectives regularize representation learning and preserve multimodal consistency. They are not the primary source of improvement, but they support stable optimization under sparse disease-herb supervision.
```

Do not overstate:

```text
The three SSL losses are the main reason for performance improvement.
```

Required ablation:

- BPR only;
- BPR + graph SSL;
- BPR + cross-modal;
- BPR + property-chemical;
- full objective.

If the gains are minor, present them as regularization and interpretability support rather than core innovation.

## 9. Is NDCG Necessary Without Herb Importance Labels?

Concern:

Ground-truth herb sets do not contain internal importance levels.

Assessment:

NDCG is not strictly necessary, but it is still acceptable if binary relevance is clearly stated.

Why NDCG can be useful:

- The model outputs a ranked list.
- Even if all ground-truth herbs are equally relevant, ranking correct herbs earlier is still meaningful.
- Binary NDCG is common in top-K recommendation.

Limitation:

NDCG does not measure clinical priority among herbs.

Recommended wording:

```text
Because the dataset does not provide graded herb importance, NDCG is computed with binary relevance. It evaluates whether ground-truth herbs appear earlier in the recommendation list, but it should not be interpreted as modeling dosage or clinical priority within a prescription.
```

Recommendation:

- Keep NDCG as a supplementary ranking metric.
- Use F1@K and Recall@K as primary metrics.
- In the paper, do not over-interpret NDCG clinically.

## Final Positioning Recommendation

The new paper should not overclaim every component as a major innovation.

Main defensible contributions:

1. Gene-overlap-guided local semantic augmentation.
2. Complementary local/global/semantic view learning for disease-driven herb recommendation.
3. Type-aware multimodal fusion with auxiliary contrastive regularization.

Experimental/protocol contributions:

- disease-label-disjoint evaluation;
- leakage diagnostic;
- threshold sensitivity;
- NDCG as supplementary binary ranking evaluation.

Do not present as primary innovations:

- disease-disjoint split alone;
- fixed Top-K alone;
- RGCN backbone alone;
- gene-as-feature alone;
- NDCG metric;
- BPR + standard SSL losses without ablation support.

## Immediate Manuscript Actions

1. Decide and lock final main configuration:
   - user stated final main uses `gate`;
   - current `train.py` should be checked because it currently may still contain `BRANCH_FUSION_MODE='sum'`.

2. Rename dataset narrative:
   - avoid "ETCM-enhanced";
   - use "our constructed multimodal disease-herb dataset" or "NEWHERB".

3. Rewrite contribution list:
   - no disease-disjoint as main contribution;
   - no Top-K/Jaccard as main contribution;
   - emphasize gene-overlap local semantic structure.

4. Add caution statements:
   - gene-overlap is association-based, not causal proof;
   - disease-disjoint is not fully inductive unseen-node prediction;
   - NDCG uses binary relevance.

5. Add required ablation placeholders:
   - AUTHOR_INPUT_NEEDED: final gate main result;
   - AUTHOR_INPUT_NEEDED: gene-jaccard only / herb-only / disease-only ablations;
   - AUTHOR_INPUT_NEEDED: branch ablations;
   - AUTHOR_INPUT_NEEDED: SSL ablations under final graph.

## Added Test Log: Percentile/Adaptive Gene-Jaccard Sparsification

Date: 2026-06-07

Purpose:

Check whether gene-overlap augmentation is tied to a fixed Top-K rule or remains effective under alternative bounded-neighborhood sparsification strategies.

Critical comparability note:

Both runs below show:

```text
Warning: Gene feature enabled but file not found at the new disease_split graph directory.
Herb gated fusion streams: structure, attr, chem
Disease gated fusion streams: structure, disease_text
```

Therefore these are not fully comparable with an all-feature setting where `node_gene_matrix.pt` is loaded. They test the effect of alternative gene-jaccard graph edges, but gene-as-feature is absent. The results should be treated as preliminary sparsification diagnostics rather than final ablation results.

### Percentile-90 sparsification

Graph/view statistics:

```text
local branch edges = 431177 / 719081
global branch edges = 287904 / 719081
branch fusion = gate
gene feature = missing
```

Training:

```text
Best validation F1@10 = 0.1874
```

Test results:

```text
P@5=0.6125   R@5=0.1052   F1@5=0.1275   NDCG@5=0.6430
P@10=0.5461  R@10=0.1539  F1@10=0.1710  NDCG@10=0.6020
P@20=0.4697  R@20=0.2181  F1@20=0.2083  NDCG@20=0.5550
P@50=0.4106  R@50=0.4082  F1@50=0.2854  NDCG@50=0.5708
```

### Adaptive alpha=0.5 sparsification

Graph/view statistics:

```text
local branch edges = 432383 / 720287
global branch edges = 287904 / 720287
branch fusion = gate
gene feature = missing
```

Training:

```text
Best validation F1@10 = 0.1882
```

Test results:

```text
P@5=0.6148   R@5=0.1058   F1@5=0.1286   NDCG@5=0.6445
P@10=0.5458  R@10=0.1524  F1@10=0.1698  NDCG@10=0.6015
P@20=0.4720  R@20=0.2224  F1@20=0.2106  NDCG@20=0.5571
P@50=0.4140  R@50=0.4152  F1@50=0.2887  NDCG@50=0.5749
```

Interpretation:

The percentile and adaptive alternatives produce similar validation and test behavior. This supports the narrative that the gene-overlap augmentation is not dependent on one exact fixed Top-K edge count. However, because gene-as-feature was not loaded, these runs do not yet isolate the sparsification rule under the final all-feature configuration.

Next required check:

```text
Rerun percentile/adaptive after making node_gene_matrix.pt available to the new graph directories,
or modify train.py so gene_feature_data_dir falls back to the original compatible
g4_gene_bridge_chemical_gene_jaccard directory when node maps are identical.
```

## Updated Test Log: Sparsification with Gene Feature Restored

Date: 2026-06-07

Purpose:

Repeat the sparsification comparison after restoring the missing gene feature files. These runs are now comparable with the intended all-feature setting.

### Original Top-K sparsification

Training:

```text
Best validation F1@10 = 0.2521
```

Test results:

```text
P@5=0.6760   R@5=0.1330   F1@5=0.1548   NDCG@5=0.7151
P@10=0.6435  R@10=0.2220  F1@10=0.2231  NDCG@10=0.7056
P@20=0.5948  R@20=0.3458  F1@20=0.2992  NDCG@20=0.6946
P@50=0.4921  R@50=0.5346  F1@50=0.3588  NDCG@50=0.7048
```

### Percentile-90 sparsification

Training:

```text
Best validation F1@10 = 0.2746
```

Test results:

```text
P@5=0.7439   R@5=0.1851   F1@5=0.2020   NDCG@5=0.7905
P@10=0.6897  R@10=0.2728  F1@10=0.2635  NDCG@10=0.7708
P@20=0.6317  R@20=0.4015  F1@20=0.3347  NDCG@20=0.7593
P@50=0.5152  R@50=0.5810  F1@50=0.3822  NDCG@50=0.7669
```

### Adaptive alpha=0.5 sparsification

Training:

```text
Best validation F1@10 = 0.2597
```

Test results:

```text
P@5=0.7011   R@5=0.1547   F1@5=0.1731   NDCG@5=0.7389
P@10=0.6624  R@10=0.2408  F1@10=0.2389  NDCG@10=0.7284
P@20=0.6135  R@20=0.3691  F1@20=0.3141  NDCG@20=0.7204
P@50=0.5067  R@50=0.5577  F1@50=0.3715  NDCG@50=0.7321
```

### Comparison

```text
Method          Val F1@10  P@10    R@10    F1@10   NDCG@10  F1@50   NDCG@50
Top-K           0.2521     0.6435  0.2220  0.2231  0.7056   0.3588  0.7048
Percentile-90   0.2746     0.6897  0.2728  0.2635  0.7708   0.3822  0.7669
Adaptive-0.5    0.2597     0.6624  0.2408  0.2389  0.7284   0.3715  0.7321
```

Interpretation:

After restoring gene-as-feature, percentile-90 is the strongest sparsification strategy among the three tested settings. It improves validation F1@10 and all reported test metrics over the original Top-K setting. Adaptive-0.5 is also consistently stronger than the original Top-K setting, but weaker than percentile-90.

Manuscript implication:

These results make the fixed Top-K concern much easier to answer. The paper can state that gene-overlap augmentation is implemented as a bounded-neighborhood sparsification framework rather than a single fixed heuristic. Top-K, percentile, and adaptive strategies are all valid instantiations; in the current validation protocol, percentile-90 is selected as the final sparsification rule.

Caution:

The paper should explicitly say that percentile-90 is selected based on validation performance. Do not present percentile-90 as universally optimal, and do not imply that the test set was used to choose this setting.

## Added Test Log: Edge-Weighted Gene-Jaccard RGCN

Date: 2026-06-07

Purpose:

Test whether replacing binary gene-jaccard local edges with edge-weighted RGCN propagation improves the current disease-disjoint model. Only `herb_gene_jaccard` and `disease_gene_jaccard` edges in the local branch are reweighted; global branch remains the standard RGCN and semantic branch remains graph-free.

### one_plus_jaccard

Configuration:

```text
USE_EDGE_WEIGHTED_GENE_JACCARD = True
GENE_JACCARD_EDGE_WEIGHT_MODE = one_plus_jaccard
Weighted edge value = 1 + Jaccard
```

Training:

```text
Best validation F1@10 = 0.2307
```

Test results:

```text
P@5=0.6421   R@5=0.1211   F1@5=0.1406   NDCG@5=0.6718
P@10=0.6066  R@10=0.2008  F1@10=0.2022  NDCG@10=0.6587
P@20=0.5673  R@20=0.3103  F1@20=0.2740  NDCG@20=0.6500
P@50=0.4823  R@50=0.5118  F1@50=0.3444  NDCG@50=0.6706
```

### jaccard

Configuration:

```text
USE_EDGE_WEIGHTED_GENE_JACCARD = True
GENE_JACCARD_EDGE_WEIGHT_MODE = jaccard
Weighted edge value = Jaccard
```

Training:

```text
Best validation F1@10 = 0.2313
```

Test results:

```text
P@5=0.6524   R@5=0.1361   F1@5=0.1498   NDCG@5=0.6857
P@10=0.6052  R@10=0.2074  F1@10=0.2025  NDCG@10=0.6658
P@20=0.5637  R@20=0.3164  F1@20=0.2709  NDCG@20=0.6571
P@50=0.4790  R@50=0.5112  F1@50=0.3405  NDCG@50=0.6747
```

### Comparison

```text
Weight mode        Val F1@10  P@10    R@10    F1@10   NDCG@10  F1@50   NDCG@50
one_plus_jaccard   0.2307     0.6066  0.2008  0.2022  0.6587   0.3444  0.6706
jaccard            0.2313     0.6052  0.2074  0.2025  0.6658   0.3405  0.6747
Binary Top-K       0.2521     0.6435  0.2220  0.2231  0.7056   0.3588  0.7048
Percentile-90      0.2746     0.6897  0.2728  0.2635  0.7708   0.3822  0.7669
```

Interpretation:

The two edge-weighted modes are very close. `jaccard` is slightly better on recall and NDCG, while `one_plus_jaccard` is marginally better at F1@20 and F1@50. However, both are weaker than the binary gene-jaccard Top-K setting and much weaker than percentile-90 sparsification.

This suggests that the current gain comes more from selecting useful gene-overlap neighbors than from fine-grained continuous edge weighting. In the current implementation, weighted mean aggregation can also dilute the originally strong local same-type signal: raw Jaccard downweights all gene-overlap messages below 1.0, while `1 + Jaccard` changes the local branch distribution and does not preserve the behavior of PyG's original `RGCNConv` exactly.

Manuscript implication:

Edge weighting should not be used as the main result unless later variants recover or exceed the binary/percentile-90 result. It is still useful as a diagnostic ablation: continuous Jaccard weights are not automatically better than bounded sparse semantic edges. The stronger claim should remain gene-overlap-guided local semantic augmentation with validation-selected sparsification, not edge-weighted RGCN.
