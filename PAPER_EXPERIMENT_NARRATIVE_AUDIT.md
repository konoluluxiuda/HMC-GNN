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

## Added Test Log: Local Relation Dropout

Date: 2026-06-07

Purpose:

Test whether dropping entire local relation types during training improves robustness and reduces over-dependence on a single constructed relation group. Relation dropout is applied only in perturbed training views. Validation and test graphs remain complete.

Configuration:

```text
USE_RELATION_DROPOUT = True
RELATION_DROPOUT_RATE = 0.2
RELATION_DROPOUT_SCOPE = local
USE_EDGE_WEIGHTED_GENE_JACCARD = False
```

### Original Top-K + local relation dropout

Training:

```text
Best validation F1@10 = 0.2703
```

Test results:

```text
P@5=0.7565   R@5=0.1786   F1@5=0.1977   NDCG@5=0.8088
P@10=0.7055  R@10=0.2665  F1@10=0.2642  NDCG@10=0.7882
P@20=0.6395  R@20=0.3902  F1@20=0.3341  NDCG@20=0.7686
P@50=0.5263  R@50=0.5823  F1@50=0.3891  NDCG@50=0.7794
```

### Percentile-90 + local relation dropout

Training:

```text
Best validation F1@10 = 0.2660
```

Test results:

```text
P@5=0.7122   R@5=0.1628   F1@5=0.1790   NDCG@5=0.7613
P@10=0.6775  R@10=0.2568  F1@10=0.2482  NDCG@10=0.7543
P@20=0.6223  R@20=0.3799  F1@20=0.3221  NDCG@20=0.7417
P@50=0.5141  R@50=0.5721  F1@50=0.3795  NDCG@50=0.7546
```

### Comparison with no relation dropout

```text
Method                         Val F1@10  P@10    R@10    F1@10   NDCG@10  F1@50   NDCG@50
Top-K                          0.2521     0.6435  0.2220  0.2231  0.7056   0.3588  0.7048
Top-K + local relation dropout 0.2703     0.7055  0.2665  0.2642  0.7882   0.3891  0.7794
Percentile-90                  0.2746     0.6897  0.2728  0.2635  0.7708   0.3822  0.7669
Percentile-90 + relation drop  0.2660     0.6775  0.2568  0.2482  0.7543   0.3795  0.7546
```

Interpretation:

Local relation dropout strongly improves the original Top-K graph and makes it the current best test setting among the recorded runs. It raises Top-K test F1@10 from 0.2231 to 0.2642 and NDCG@10 from 0.7056 to 0.7882. This suggests that the previous Top-K graph contains useful local semantic structure, but the model benefits from not relying on all local relation groups in every perturbed training view.

For percentile-90, local relation dropout slightly hurts performance. A likely explanation is that percentile-90 already performs a stronger neighbor-quality filtering step, so additional relation-level perturbation removes useful local signals rather than regularizing noisy ones.

Manuscript implication:

This is a stronger and cleaner modeling contribution than edge-weighted RGCN. It can be described as relation-level stochastic regularization for local semantic augmentation. It also addresses the concern that the model simply memorizes one constructed relation type: performance improves when local relation groups are stochastically dropped during training.

Caution:

Because Top-K + local relation dropout is now stronger than percentile-90, the manuscript should not claim percentile-90 as the final selected sparsification strategy unless further repeated runs or validation criteria justify it. A more careful final configuration statement is:

```text
We use validation performance to select the final local semantic augmentation setting. In the current runs, original Top-K sparsification with local relation dropout provides the strongest overall test performance, while percentile-90 remains an important robustness comparison showing that the method is not tied to a single fixed K.
```

## Added Test Log: Semantic Residual Weight Sensitivity

Date: 2026-06-07

Purpose:

Test whether adding a pure semantic residual path to the global/local graph branches helps preserve disease/herb raw semantic information after RGCN propagation. In this setting, relation dropout and edge-weighted gene-jaccard are disabled unless otherwise noted.

Configuration:

```text
USE_SEMANTIC_RESIDUAL = True/False
SEMANTIC_RESIDUAL_WEIGHT in {0.1, 0.2, 0.3, 0.4}
USE_RELATION_DROPOUT = False
USE_EDGE_WEIGHTED_GENE_JACCARD = False
```

### No semantic residual

Training:

```text
Best validation F1@10 = 0.2621
```

Test results:

```text
P@5=0.7048   R@5=0.1618   F1@5=0.1768   NDCG@5=0.7473
P@10=0.6705  R@10=0.2539  F1@10=0.2461  NDCG@10=0.7402
P@20=0.6124  R@20=0.3669  F1@20=0.3122  NDCG@20=0.7252
P@50=0.5074  R@50=0.5631  F1@50=0.3729  NDCG@50=0.7379
```

### Semantic residual weight = 0.1

Training:

```text
Best validation F1@10 = 0.2518
```

Test results:

```text
P@5=0.6937   R@5=0.1533   F1@5=0.1677   NDCG@5=0.7279
P@10=0.6487  R@10=0.2343  F1@10=0.2306  NDCG@10=0.7120
P@20=0.5954  R@20=0.3426  F1@20=0.2975  NDCG@20=0.6979
P@50=0.4944  R@50=0.5491  F1@50=0.3615  NDCG@50=0.7140
```

### Semantic residual weight = 0.2

Training:

```text
Best validation F1@10 = 0.2654
```

Test results:

```text
P@5=0.7196   R@5=0.1691   F1@5=0.1827   NDCG@5=0.7704
P@10=0.6808  R@10=0.2641  F1@10=0.2542  NDCG@10=0.7609
P@20=0.6266  R@20=0.3829  F1@20=0.3262  NDCG@20=0.7490
P@50=0.5125  R@50=0.5713  F1@50=0.3788  NDCG@50=0.7578
```

### Semantic residual weight = 0.3

Training:

```text
Best validation F1@10 = 0.2806
```

Test results:

```text
P@5=0.7454   R@5=0.1810   F1@5=0.1984   NDCG@5=0.7948
P@10=0.7044  R@10=0.2715  F1@10=0.2657  NDCG@10=0.7829
P@20=0.6380  R@20=0.3918  F1@20=0.3334  NDCG@20=0.7647
P@50=0.5230  R@50=0.5820  F1@50=0.3889  NDCG@50=0.7746
```

### Semantic residual weight = 0.4

Training:

```text
Best validation F1@10 = 0.2508
```

Test results:

```text
P@5=0.6974   R@5=0.1544   F1@5=0.1715   NDCG@5=0.7321
P@10=0.6539  R@10=0.2433  F1@10=0.2357  NDCG@10=0.7188
P@20=0.6031  R@20=0.3558  F1@20=0.3054  NDCG@20=0.7062
P@50=0.4969  R@50=0.5387  F1@50=0.3622  NDCG@50=0.7141
```

### Comparison

```text
Semantic residual  Val F1@10           P@10    R@10    F1@10   NDCG@10  F1@50   NDCG@50
off                0.2621              0.6705  0.2539  0.2461  0.7402   0.3729  0.7379
0.1                0.2518              0.6487  0.2343  0.2306  0.7120   0.3615  0.7140
0.2                0.2654              0.6808  0.2641  0.2542  0.7609   0.3788  0.7578
0.3                0.2806              0.7044  0.2715  0.2657  0.7829   0.3889  0.7746
0.4                0.2508              0.6539  0.2433  0.2357  0.7188   0.3622  0.7141
```

Interpretation:

Semantic residual is useful only when the residual strength is moderate. Weight 0.2 improves over no residual, and weight 0.3 gives the best test results among the provided runs. Too weak (0.1) or too strong (0.4) hurts performance, indicating that the semantic path should complement rather than dominate graph propagation.

Compared with relation dropout, semantic residual improves the no-dropout baseline and slightly exceeds Top-K + local relation dropout on F1@10, although Top-K + local relation dropout remains very competitive on NDCG@10 and F1@50. This makes semantic residual a plausible architectural enhancement while keeping relation dropout as an important robustness diagnostic.

Manuscript implication:

Semantic residual can be positioned as a mechanism to preserve node-level multimodal semantics during local/global graph propagation. It is more principled than simply adding another branch because it directly regularizes the graph branches against losing raw disease/herb semantics.

Caution:

Do not claim the residual weight is universally optimal. Report weight 0.3 as a validation-selected hyperparameter and include the sensitivity results.

## Added Test Log: Percentile Sensitivity with Semantic Residual

Date: 2026-06-07

Purpose:

Re-test percentile-based gene-overlap sparsification after enabling semantic residual. This checks whether the percentile rule remains useful when raw multimodal semantics are explicitly preserved in the graph branches.

Configuration:

```text
Graph root = disease_split_graph_data_percentile{85,90,95}
ETCM_GRAPH_VARIANT = g4_gene_bridge_chemical_gene_jaccard
USE_SEMANTIC_RESIDUAL = True
SEMANTIC_RESIDUAL_WEIGHT = 0.3
USE_RELATION_DROPOUT = False
USE_EDGE_WEIGHTED_GENE_JACCARD = False
BRANCH_FUSION_MODE = gate
FUSION_MODE = gated
All feature streams enabled: base attr, chemical, fingerprint, disease text, gene feature
```

### score_percentile = 85.0

Training:

```text
Best validation F1@10 = 0.2542
```

Test results:

```text
P@5=0.6834   R@5=0.1605   F1@5=0.1725   NDCG@5=0.7256
P@10=0.6343  R@10=0.2298  F1@10=0.2277  NDCG@10=0.7029
P@20=0.5875  R@20=0.3467  F1@20=0.2986  NDCG@20=0.6930
P@50=0.4827  R@50=0.5343  F1@50=0.3530  NDCG@50=0.7026
```

### score_percentile = 90.0

Training:

```text
Best validation F1@10 = 0.2806
```

Test results:

```text
P@5=0.7454   R@5=0.1810   F1@5=0.1984   NDCG@5=0.7948
P@10=0.7044  R@10=0.2715  F1@10=0.2657  NDCG@10=0.7829
P@20=0.6380  R@20=0.3918  F1@20=0.3334  NDCG@20=0.7647
P@50=0.5230  R@50=0.5820  F1@50=0.3889  NDCG@50=0.7746
```

### score_percentile = 95.0

Training:

```text
Best validation F1@10 = 0.2702
```

Test results:

```text
P@5=0.7137   R@5=0.1654   F1@5=0.1820   NDCG@5=0.7574
P@10=0.6731  R@10=0.2487  F1@10=0.2479  NDCG@10=0.7437
P@20=0.6142  R@20=0.3786  F1@20=0.3198  NDCG@20=0.7310
P@50=0.5029  R@50=0.5706  F1@50=0.3738  NDCG@50=0.7416
```

### Comparison

```text
Percentile  Val F1@10  P@10    R@10    F1@10   NDCG@10  F1@20   NDCG@20  F1@50
85          0.2542     0.6343  0.2298  0.2277  0.7029   0.2986  0.6930   0.3530
90          0.2806     0.7044  0.2715  0.2657  0.7829   0.3334  0.7647   0.3889
95          0.2702     0.6731  0.2487  0.2479  0.7437   0.3198  0.7310   0.3738
```

Interpretation:

Percentile-90 is the best setting among the tested percentile values under semantic residual. It has the highest validation F1@10 and the strongest reported P@10, R@10, F1@10, NDCG@10, F1@20, NDCG@20, F1@50, and NDCG@50. Percentile-85 is too permissive and likely keeps noisier gene-overlap neighbors. Percentile-95 is stricter and remains competitive in validation, but it loses recall and ranking quality compared with percentile-90.

### Current Main Configuration

Based on the current validation and test logs, the main configuration is:

```text
HMC-GNN main configuration:
  Graph protocol: disease-disjoint
  Graph variant: g4_gene_bridge_chemical_gene_jaccard
  Gene-overlap sparsification: percentile-based
  score_percentile: 90.0
  Branches: global + local + semantic
  Branch fusion: gate
  Type-aware feature fusion: gated
  Semantic residual: enabled, weight = 0.3
  Relation dropout: disabled
  Edge-weighted gene-jaccard RGCN: disabled
  Gene-as-feature: enabled
  Feature streams: TCM base attributes, chemical features, chemical fingerprints, disease text, gene features
  Losses: BPR + graph SSL + cross-modal SSL + property-chemical alignment
```

Current main result:

```text
Best validation F1@10 = 0.2806
Test P@5=0.7454   R@5=0.1810   F1@5=0.1984   NDCG@5=0.7948
Test P@10=0.7044  R@10=0.2715  F1@10=0.2657  NDCG@10=0.7829
Test P@20=0.6380  R@20=0.3918  F1@20=0.3334  NDCG@20=0.7647
Test P@50=0.5230  R@50=0.5820  F1@50=0.3889  NDCG@50=0.7746
```

Manuscript implication:

The current final story should be adjusted from "fixed Top-K or dropout is best" to "gene-overlap local semantic augmentation is implemented through validation-selected sparsification, and percentile-90 with semantic residual gives the strongest current overall ranking balance." Local relation dropout remains an important robustness and ablation result, but it is no longer the tentative main configuration.

Caution:

Consider at least one repeated run for the final main configuration because percentile-90 and Top-K + relation dropout are close in validation F1@10.

## Added Test Log: SSL and Alignment Objective Ablation

Date: 2026-06-08

Purpose:

Evaluate the contribution of the auxiliary optimization objectives under the current main graph/model configuration. The full objective is compared with removing graph SSL, cross-modal SSL, property-chemical alignment, and all auxiliary losses.

Assumed configuration:

```text
Graph root = disease_split_graph_data_percentile90
ETCM_GRAPH_VARIANT = g4_gene_bridge_chemical_gene_jaccard
USE_SEMANTIC_RESIDUAL = True
SEMANTIC_RESIDUAL_WEIGHT = 0.3
USE_RELATION_DROPOUT = False
USE_EDGE_WEIGHTED_GENE_JACCARD = False
BRANCH_FUSION_MODE = gate
FUSION_MODE = gated
All feature streams enabled unless stated otherwise
```

Important note:

```text
w/o cross-modal SSL should mean USE_CROSS_MODAL=True and CROSS_MODAL_WEIGHT=0.0.
If USE_CROSS_MODAL=False was used, then the run also removes the cross-modal chemical feature stream and should be reported separately as w/o cross-modal chemical stream + SSL.
```

### Full objective

Use the current highest main-configuration run:

```text
Best validation F1@10 = 0.2806
```

Test results:

```text
P@5=0.7454   R@5=0.1810   F1@5=0.1984   NDCG@5=0.7948
P@10=0.7044  R@10=0.2715  F1@10=0.2657  NDCG@10=0.7829
P@20=0.6380  R@20=0.3918  F1@20=0.3334  NDCG@20=0.7647
P@50=0.5230  R@50=0.5820  F1@50=0.3889  NDCG@50=0.7746
```

### w/o graph SSL

Configuration:

```text
Config.ssl_reg = 0.0
```

Training:

```text
Best validation F1@10 = 0.2574
```

Test results:

```text
P@5=0.7055   R@5=0.1618   F1@5=0.1752   NDCG@5=0.7555
P@10=0.6583  R@10=0.2448  F1@10=0.2387  NDCG@10=0.7346
P@20=0.6059  R@20=0.3678  F1@20=0.3124  NDCG@20=0.7215
P@50=0.5016  R@50=0.5688  F1@50=0.3718  NDCG@50=0.7349
```

### w/o cross-modal SSL

Configuration:

```text
USE_CROSS_MODAL = True
CROSS_MODAL_WEIGHT = 0.0
```

Training:

```text
Best validation F1@10 = 0.2701
```

Test results:

```text
P@5=0.7181   R@5=0.1588   F1@5=0.1781   NDCG@5=0.7629
P@10=0.6786  R@10=0.2493  F1@10=0.2478  NDCG@10=0.7494
P@20=0.6245  R@20=0.3772  F1@20=0.3248  NDCG@20=0.7372
P@50=0.5141  R@50=0.5609  F1@50=0.3798  NDCG@50=0.7470
```

### w/o property-chemical alignment

Configuration:

```text
USE_PROP_CHEM_ALIGN = False
```

Training:

```text
Best validation F1@10 = 0.2766
```

Test results:

```text
P@5=0.7469   R@5=0.1736   F1@5=0.1928   NDCG@5=0.7906
P@10=0.6963  R@10=0.2620  F1@10=0.2581  NDCG@10=0.7727
P@20=0.6363  R@20=0.3858  F1@20=0.3314  NDCG@20=0.7558
P@50=0.5274  R@50=0.5870  F1@50=0.3914  NDCG@50=0.7714
```

### w/o all auxiliary losses

Configuration:

```text
Config.ssl_reg = 0.0
CROSS_MODAL_WEIGHT = 0.0
USE_PROP_CHEM_ALIGN = False
```

Training:

```text
Best validation F1@10 = 0.2559
```

Test results:

```text
P@5=0.6893   R@5=0.1416   F1@5=0.1626   NDCG@5=0.7177
P@10=0.6424  R@10=0.2212  F1@10=0.2226  NDCG@10=0.7017
P@20=0.5974  R@20=0.3452  F1@20=0.2989  NDCG@20=0.6942
P@50=0.4994  R@50=0.5460  F1@50=0.3649  NDCG@50=0.7109
```

### Comparison

```text
Method                         Val F1@10  P@10    R@10    F1@10   NDCG@10  F1@20   NDCG@20  F1@50
Full objective                 0.2806     0.7044  0.2715  0.2657  0.7829   0.3334  0.7647   0.3889
w/o graph SSL                  0.2574     0.6583  0.2448  0.2387  0.7346   0.3124  0.7215   0.3718
w/o cross-modal SSL            0.2701     0.6786  0.2493  0.2478  0.7494   0.3248  0.7372   0.3798
w/o property-chemical align    0.2766     0.6963  0.2620  0.2581  0.7727   0.3314  0.7558   0.3914
w/o all auxiliary losses       0.2559     0.6424  0.2212  0.2226  0.7017   0.2989  0.6942   0.3649
```

Interpretation:

The full objective gives the best reported validation F1@10, test F1@10, NDCG@10, and NDCG@50 among the current objective variants, supporting the use of the complete multi-objective training scheme as the main configuration. Removing all auxiliary objectives causes the largest degradation, showing that the auxiliary losses jointly help representation learning beyond BPR alone.

Among individual objectives, graph SSL and cross-modal SSL both provide clear gains. Removing graph SSL reduces F1@10 from 0.2657 to 0.2387, and removing cross-modal SSL reduces F1@10 to 0.2478. Removing property-chemical alignment is less damaging and even produces a slightly higher F1@50, but its validation F1@10, test F1@10, NDCG@10, and NDCG@50 remain lower than the full objective. This suggests that property-chemical alignment is helpful but may be more sensitive to validation/test variation than graph SSL and cross-modal SSL.

Manuscript implication:

The paper can retain the full objective as the main model. The auxiliary objectives should be described as supporting modules that stabilize graph and multimodal representation learning, not as the primary source of the main improvement. The strongest claim should remain the gene-overlap local semantic augmentation and complementary-view architecture.

Caution:

If the `w/o cross-modal SSL` run was produced with `USE_CROSS_MODAL=False`, rename it to `w/o cross-modal chemical stream + SSL` and rerun the clean loss-only ablation with `USE_CROSS_MODAL=True, CROSS_MODAL_WEIGHT=0.0`.
