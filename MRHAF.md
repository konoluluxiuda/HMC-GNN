This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
|        |        |     |                  |           |     |                 |           |               | IEEETRANSACTIONSANDJOURNALSTEMPLATE |      |             |           |     |     | 1   |
| ------ | ------ | --- | ---------------- | --------- | --- | --------------- | --------- | ------------- | ----------------------------------- | ---- | ----------- | --------- | --- | --- | --- |
| MRHAF: |        |     | Multi-Relational |           |     |                 |           | Hierarchical  |                                     |      |             | Attention |     |     |     |
| with   | Hybrid |     |                  | Knowledge |     |                 |           | Fusion        |                                     | for  | Explainable |           |     |     |     |
|        |        |     |                  | Herb      |     | Recommendations |           |               |                                     |      |             |           |     |     |     |
|        |        |     |                  | Xiaoyan   |     | Yang,           | Yiyu Luo, | and Changsong |                                     | Ding |             |           |     |     |     |
Abstract〞TraditionalChinesemedicine(TCM)herbrec- Index Terms〞Traditional Chinese medicine, herb rec-
ommendations aim to personalize herb combinations for ommendations, multi-head attention, knowledge graphs,
specific symptom profiles in accordance with TCM com- hybridfeaturefusion
| patibility | principles, | thereby  |           | ensuring   | optimal |                  | therapeutic |     |     |     |              |     |     |     |     |
| ---------- | ----------- | -------- | --------- | ---------- | ------- | ---------------- | ----------- | --- | --- | --- | ------------ | --- | --- | --- | --- |
| efficacy.  | However,    | existing |           | approaches |         | often            | fail to ac- |     |     |     |              |     |     |     |     |
|            |             |          |           |            |         |                  |             |     |     | I.  | INTRODUCTION |     |     |     |     |
| count for  | the varying |          | intensity | of         | complex | multi-relational |             |     |     |     |              |     |     |     |     |
TRADITIONAL
interactions among herbs, therapeutic effects, and symp- Chinese medicine (TCM) has served as
toms. This limitation hampers effective hybrid feature fu- a primary healthcare approach for millennia[1], with
sionacrossmulti-sourceherbalknowledgeandconstrains
|                        |     |         |                  |     |     |              |       | TCM prescriptions |               | (TCMPs) | constituting |       | its       | core therapeutic |        |
| ---------------------- | --- | ------- | ---------------- | --- | --- | ------------ | ----- | ----------------- | ------------- | ------- | ------------ | ----- | --------- | ---------------- | ------ |
| overall recommendation |     |         | performance.     |     |     | To address   | these |                   |               |         |              |       |           |                  |        |
|                        |     |         |                  |     |     |              |       | practice.         | Practitioners |         | formulate    | TCMPs | according |                  | to the |
| challenges,            | we  | propose | Multi-Relational |     |     | Hierarchical | At-   |                   |               |         |              |       |           |                  |        |
Monarch-Minister-Assistant-Messengerframework,whichop-
| tention | with Hybrid | Knowledge |     | Fusion |     | (MRHAF), | a novel |     |     |     |     |     |     |     |     |
| ------- | ----------- | --------- | --- | ------ | --- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
framework designed to improve both predictive accuracy timizes both efficacy and safety[2]. In this hierarchy, the
andinterpretabilitybymodelinglatentrelationshipsamong Monarch herb addresses the main condition, the Minister
therapeutic effects, herbs, and symptoms, as well as the supports it, the Assistant harmonizes the effects or reduces
| material | basis | underlying |     | herbal | efficacy. | MRHAF | con- |               |     |               |     |        |             |     |          |
| -------- | ----- | ---------- | --- | ------ | --------- | ----- | ---- | ------------- | --- | ------------- | --- | ------ | ----------- | --- | -------- |
|          |       |            |     |        |           |       |      | side effects, | and | the Messenger |     | guides | the formula | to  | specific |
sistsofthreecorecomponents:(1)aglobalHerb-Efficacy-
|     |     |     |     |     |     |     |     | organs | or functions. | While | historical |     | case | studies | provide |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------------- | ----- | ---------- | --- | ---- | ------- | ------- |
SymptomKnowledgeGraph(HESKG),whichappliesmulti-
headattentiontocaptureglobalsemanticinformation;(2)a valuableinsightsintoherbalcompatibility,prescriptionformu-
Herb-Symptom Interaction Graph (HSIG), which leverages lation remains challenging for novice practitioners, as it relies
self-attentiontomodeldirecttherapeuticassociations;and heavily on clinical experience. Thus, analyzing prescription
(3)amolecular-levelHerb-Attribute-ComponentKnowledge
|                |             |       |             |     |           |            |              | patterns    | and developing |          | intelligent     | herb | recommendations |         | are  |
| -------------- | ----------- | ----- | ----------- | --- | --------- | ---------- | ------------ | ----------- | -------------- | -------- | --------------- | ---- | --------------- | ------- | ---- |
| Graph (HACKG), |             | which | integrates  |     | explicit  | attributes | and          |             |                |          |                 |      |                 |         |      |
|                |             |       |             |     |           |            |              | crucial for | supporting     | clinical | decision-making |      |                 | in TCM. | With |
| implicit       | biochemical |       | information | to  | establish |            | the material |             |                |          |                 |      |                 |         |      |
basis of efficacy. Additionally, we integrate global seman- advances in artificial intelligence (AI), applying AI to TCM
tic features and local interaction features through a dual- diagnosis and prescription design has become both feasible
branch attention architecture. Extensive experiments on and essential[3], representing an important step toward the
| two benchmark          |           | datasets | demonstrate      |           | that | MRHAF         | outper- |               |     |            |            |          |                  |             |         |
| ---------------------- | --------- | -------- | ---------------- | --------- | ---- | ------------- | ------- | ------------- | --- | ---------- | ---------- | -------- | ---------------- | ----------- | ------- |
|                        |           |          |                  |           |      |               |         | modernization |     | of TCM     | practice.  | Existing | herb             | recommenda- |         |
| forms state-of-the-art |           |          | baselines,       | achieving |      | improvements  |         |               |     |            |            |          |                  |             |         |
|                        |           |          |                  |           |      |               |         | tion methods  |     | span topic | models[4], |          | [5], traditional |             | machine |
| of 9.75%               | and 22.3% |          | in Precision@10, |           |      | respectively. | Clini-  |               |     |            |            |          |                  |             |         |
cal evaluations confirm that MRHAF effectively captures learning[6], [7], and deep learning[8], [9] approaches. For
TCM formulation principles and delivers reliable recom- instance, Yao et al.[4] embedded TCM principles into topic
mendation outcomes, while network pharmacology anal- models to simulate TCM pattern identification and generate
| yses further    | validate |            | the rationality |     | of    | the recommended |     |                      |     |            |               |        |          |           |       |
| --------------- | -------- | ---------- | --------------- | --- | ----- | --------------- | --- | -------------------- | --- | ---------- | ------------- | ------ | -------- | --------- | ----- |
|                 |          |            |                 |     |       |                 |     | prescriptions,       |     | while Wang | et            | al.[5] | enhanced | topic     | model |
| herbs. Overall, |          | this study | provides        |     | a new | perspective     | on  |                      |     |            |               |        |          |           |       |
|                 |          |            |                 |     |       |                 |     | entity relationships |     | by         | incorporating |        | TCM      | knowledge | via a |
herbalcompatibilityandoffersvaluableguidanceforclini-
|     |     |     |     |     |     |     |     | knowledge | graph. | Although | such | models | improve |     | the repre- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------ | -------- | ---- | ------ | ------- | --- | ---------- |
caldecision-makinginTCM.
|     |     |     |     |     |     |     |     | sentation | of TCM | medication | patterns, |     | they | remain | limited in |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------ | ---------- | --------- | --- | ---- | ------ | ---------- |
capturinghigh-ordercorrelationsamongfrequentlyusedherbs
| This work       | was | supported | in    | part by | the       | National | Natural Sci- |                   |     |         |          |     |         |      |           |
| --------------- | --- | --------- | ----- | ------- | --------- | -------- | ------------ | ----------------- | --- | ------- | -------- | --- | ------- | ---- | --------- |
|                 |     |           |       |         |           |          |              | and symptoms[10]. |     | Machine | learning |     | methods | have | also been |
| ence Foundation |     | of China  | under | grant   | 82474352, | Hunan    | Provin-      |                   |     |         |          |     |         |      |           |
explored.Qinetal.[6]appliedclusteringalgorithmstoanalyze
| cial Administration |     | of Traditional |     | Chinese | Medicine |     | under grant |         |              |     |           |     |                      |     |     |
| ------------------- | --- | -------------- | --- | ------- | -------- | --- | ----------- | ------- | ------------ | --- | --------- | --- | -------------------- | --- | --- |
|                     |     |                |     |         |          |     |             | symptom | correlations | and | generated |     | herb recommendations |     |     |
A2024011,NaturalScienceFoundationofHunanProvinceundergrant
2023JJ60124,HunanProvincialDepartmentofEducationundergrant basedonretrievalresults.Peietal.[7]reformulatedtherecom-
22A0255.(Correspondingauthor:ChangsongDing.)
|         |         |      |            |     |              |       |         | mendation | task | as a multi-label |     | classification |     | problem, | using |
| ------- | ------- | ---- | ---------- | --- | ------------ | ----- | ------- | --------- | ---- | ---------------- | --- | -------------- | --- | -------- | ----- |
| Xiaoyan | Yang is | with | the School | of  | Informatics, | Hunan | Univer- |           |      |                  |     |                |     |          |       |
sity of Chinese Medicine, Changsha 410208, China (e-mail: YangXi- Bayesianclassifierstorepresentherbsandproducerecommen-
aoyan6t5@163.com). dations. However, most machine learning-based approaches
YiyuLuoiswiththeSchoolofInformatics,HunanUniversityofChi-
|     |     |     |     |     |     |     |     | primarily | emphasize | symptom-herb |     | associations, |     | while | over- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --------- | ------------ | --- | ------------- | --- | ----- | ----- |
neseMedicine,Changsha410208,China(e-mail:luoyiyu00@126.com).
ChangsongDingiswiththeSchoolofInformatics,HunanUniversity looking the critical compatibility relationships among herbs,
of Chinese Medicine, Changsha 410208, China, and also with the which are fundamental to TCM prescription principles.
| Big Data | Analysis | Laboratory | of Traditional |     | Chinese | Medicine, | Hunan |     |     |     |     |     |     |     |     |
| -------- | -------- | ---------- | -------------- | --- | ------- | --------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
University of Chinese Medicine, Changsha 410208, China (e-mail: Deep learning methods can effectively extract information
dingcs1975@hnucm.edu.cn). from high-dimensional multimodal data[11], particularly ex-
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
| 2   |     |     |     |     |     |     |     |     |     | IEEETRANSACTIONSANDJOURNALSTEMPLATE |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- |
cellingatmodelingnonlinearrelationships,whichmakesthem novel herb recommendation model. Experimental results
highly valuable for TCM research. For instance, Liu et al.[8] demonstratethatMRHAFsignificantlyoutperformsbase-
pretrained word embeddings from a large corpus of classi- line methods. Ablation studies further validate the effec-
cal Chinese medical texts and fine-tuned them via transfer tiveness of each module, while clinical evaluations and
learning to support herb recommendation in clinical cases. network pharmacology analyses confirm the rationality
However, TCM datasets are often characterized by short text, and interpretability of the recommended results.
| sparsity,         | and semantic  |       | ambiguity[12], |         | which     | pose      | challenges  |                   |       |             |            |              |            |           |          |
| ----------------- | ------------- | ----- | -------------- | ------- | --------- | --------- | ----------- | ----------------- | ----- | ----------- | ---------- | ------------ | ---------- | --------- | -------- |
|                   |               |       |                |         |           |           |             | The remainder     |       | of this     | paper      | is organized | as         | follows.  | Sec-     |
| to sequence-based |               | deep  | learning       | models. |           | To better | capture     |                   |       |             |            |              |            |           |          |
|                   |               |       |                |         |           |           |             | tion II overviews |       | the related | works.     | Section      | III        | outlines  | the      |
| the complex       | relationships |       | among          | TCM     | entities, |           | researchers |                   |       |             |            |              |            |           |          |
|                   |               |       |                |         |           |           |             | proposed          | MRHAF | model       | in detail. | Section      | IV         | describes | the      |
| have turned       | to            | graph | representation |         | learning. | This      | approach    |                   |       |             |            |              |            |           |          |
|                   |               |       |                |         |           |           |             | experimental      | setup | and         | reports    | extensive    | evaluation |           | results. |
offers a promising framework by mapping entities and their SectionVconcludesthepaper.Theoverallresearchframework
| relationships  | into          | nodes           | and           | edges, thereby   |                       | enabling      | the joint |                                   |     |                |         |      |         |          |     |
| -------------- | ------------- | --------------- | ------------- | ---------------- | --------------------- | ------------- | --------- | --------------------------------- | --- | -------------- | ------- | ---- | ------- | -------- | --- |
|                |               |                 |               |                  |                       |               |           | is illustrated                    | in  | Fig.1.         |         |      |         |          |     |
| learning       | of entity     | embeddings      |               | and their        | interconnections[13]. |               |           |                                   |     |                |         |      |         |          |     |
| For example,   | Jin           | et al.[9]       | constructed   |                  | a heterogeneous       |               | infor-    |                                   |     |                |         |      |         |          |     |
| mation network |               | by thresholding |               | symptom-herb     |                       | co-occurrence |           |                                   |     |                |         |      |         |          |     |
|                |               |                 |               |                  |                       |               |           |                                   |     | II.            | RELATED | WORK |         |          |     |
| patterns       | and then      | employed        |               | graph            | convolutional         |               | networks  |                                   |     |                |         |      |         |          |     |
| (GCN) to       | learn         | entity          | features.     | Yang             | et al.[14]            | developed     |           | a                                 |     |                |         |      |         |          |     |
|                |               |                 |               |                  |                       |               |           | A. Knowledge-awarerecommendations |     |                |         |      |         |          |     |
| TCM knowledge  |               | graph           | incorporating |                  | external              | knowledge     |           | to                                |     |                |         |      |         |          |     |
|                |               |                 |               |                  |                       |               |           | Knowledge-aware                   |     | recommendation |         |      | methods | leverage |     |
| alleviate      | data sparsity |                 | in herb       | recommendations. |                       | Furthermore,  |           |                                   |     |                |         |      |         |          |     |
acknowledging that herbs exert varying effects on different knowledge graphs (KGs) to capture semantic relationships
symptoms, Yang et al.[15] introduced a residual attention and user preferences [16]. These approaches generally fall
network that integrates semantic knowledge of symptoms to into two categories: KG embedding-based methods and graph
enhance representation learning. While graph-based learning representation learning-based methods (e.g., GCN) [17].
|     |     |     |     |     |     |     |     | Embedding-based |     | approaches | incorporate |     | external | knowledge |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | ---------- | ----------- | --- | -------- | --------- | --- |
methodshavedemonstratedeffectivenessinaggregatingstruc-
turalinformationforherbrecommendation,severalchallenges from KGs into user and item representations, which are then
remain: (1) inadequate differentiation of the varying impor- mappedtopreferencescoresfordownstreamrecommendation
tanceofrelationsamongherbs,therapeuticeffects,andsymp- tasks. For instance, Zhang et al. [18] constructed an item
toms, leading to overlooked hidden associations; (2) limited KG and applied a heterogeneous network with TransR to
|             |     |                 |     |                 |     |             |     | represent | item | features. | Similarly, | other | studies | [19] | built |
| ----------- | --- | --------------- | --- | --------------- | --- | ----------- | --- | --------- | ---- | --------- | ---------- | ----- | ------- | ---- | ----- |
| integration | of  | herb attributes |     | and biochemical |     | components, |     |           |      |           |            |       |         |      |       |
resulting ininsufficient knowledge representationand reduced user-item graphs and employed TransH to extract knowledge
interpretability. as auxiliary information, thereby directly modeling user
| Therefore, | we     | propose   | Multi-Relational |        | Hierarchical |     | Atten-     | preferences. |                |     |                |                 |     |     |      |
| ---------- | ------ | --------- | ---------------- | ------ | ------------ | --- | ---------- | ------------ | -------------- | --- | -------------- | --------------- | --- | --- | ---- |
|            |        |           |                  |        |              |     |            | Graph        | representation |     | learning-based | recommendations |     |     | typ- |
| tion with  | Hybrid | Knowledge |                  | Fusion | (MRHAF)      |     | to address |              |                |     |                |                 |     |     |      |
these challenges and advance clinically interpretable herb ically adopt GCN to aggregate information from neighboring
|                 |     |     |      |               |     |            |        | nodes in   | heterogeneous |           | graphs, | thereby generating |          | expressive |     |
| --------------- | --- | --- | ---- | ------------- | --- | ---------- | ------ | ---------- | ------------- | --------- | ------- | ------------------ | -------- | ---------- | --- |
| recommendation. |     | The | main | contributions | of  | this study | are as |            |               |           |         |                    |          |            |     |
|                 |     |     |      |               |     |            |        | embeddings | for           | users and | items.  | For                | example, | RAAGCN     |     |
follows:
|     |     |     |     |     |     |     |     | [16] applied | GCN | to aggregate |     | latent interaction |     | information |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------------ | --- | ------------------ | --- | ----------- | --- |
Multi-Relational Hierarchical Attention Feature Fusion. between entities for user preference modeling, while KGCN
?
We design a hierarchical attention framework that dy- [20] constructed a user-item graph and utilized multi-hop in-
namically evaluates the importance of different relation formationtoenrichentityfeatures.Extendingthislineofwork,
types using Graph Attention Networks (GAT), enabling somescholarshaveintegratedattentionmechanismsintoGCN
targeted neighborhood aggregation. A multi-head atten- to better aggregate neighbor information and capture higher-
tion mechanism enriches global semantic representations order dependencies. For instance, KGAT [21] introduced
while hierarchically filtering noise. In addition, local attention mechanisms to weight neighboring node features,
attention features are decoupled by explicitly modeling therebyfocusingoncrucialattributesanddemonstratingstrong
symptom-herb interactions. This framework effectively capabilities in modeling node information. In addition, path-
suppressesspuriousdependencypropagation,therebyen- based recommendation methods represent another important
hancing entity interaction modeling and improving inter- paradigm for exploiting graph structural information. By con-
pretability. structing user-item graphs and computing connections among
? Multi-Dimensional Herb Representation Learning. We entities, Troussas et al. [17] measured similarity between
construct a pharmacological knowledge graph that inte- entities to generate recommendations. However, path-based
grates herb attributes with chemical components. Lever- methods often overlook fine-grained graph structures when
aging a GAT-based aggregation mechanism, this module tracing multi-hop paths, and they typically fail to generate
bridges biochemical properties with traditional pharma- explicit reasoning paths as recommendation rationales, thus
cological knowledge to generate highly expressive mul- limitinginterpretability[22].Meta-path-basedapproachespar-
timodal herb embeddings. tially address this but rely heavily on predefined meta-paths,
? Comprehensive Knowledge Fusion for Herb Recommen- the design of which requires domain expertise and is often
| dation. | By  | fusing | multi-source |     | knowledge, | we  | build | a labor-intensive. |     |     |     |     |     |     |     |
| ------- | --- | ------ | ------------ | --- | ---------- | --- | ----- | ------------------ | --- | --- | --- | --- | --- | --- | --- |
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS3
Fig.1. Theworkflowofthewholeresearch.MRHAFcomprisesthreeparts:(A)constructingthreegraphs;(B)propagatingfeaturesviahierarchical
attention to extract entity features and edge importance; and (C) fusing hybrid features for herb recommendation. Additionally, we provide (D)
explainabilityanalysisviagraphstructureandcorrelationcoefficients,and(E)GO/KEGGenrichmentanalysistovalidatetherapeuticmechanisms.
B. Explanationofrecommendation attention during formulation generation. However, meta-path-
based methods can be time-consuming and require extensive
Despite their success in many practical scenarios, most
domain-specific prior knowledge. In contrast, our model em-
recommendation models remain black boxes and cannot ex-
phasizes entity-specific attention over diverse edge types and
plaintheiroutputs[23].Accordingly,researchhasincreasingly
incorporates hierarchical attention to deliver interpretability,
emphasized interpretability to promote transparency and user
while employing hybrid feature fusion to mitigate data spar-
trust [24]. Explainable recommendation methods typically
sity.
leverage rich side information to clarify why specific items
are suggested to users [25]. For example, Zheng et al. [26]
exploited direct and indirect user-user similarities by inte- III. METHODS
grating contextual information from a heterogeneous graph to A. Problemformulation
achieve interpretable friend-link recommendation. Boughareb
Unlike traditional recommendation systems that rely on
et al. [27] proposed a model that highlights semantic feature
user-item interactions, TCM herb recommendation follows
characterization and message propagation to explore the in-
a two-step clinical workflow. First, symptoms are analyzed
terpretability of latent user preferences through higher-order
to identify underlying syndrome patterns, which represent
connectivity. Incorporating KGs can simultaneously alleviate
holistic pathological states in TCM. Herbs are then combined
cold-startissuesandenhanceinterpretability[28].KGTN[23]
accordingtoTCMprinciplestotreatthediagnosedsyndrome,
integrated product attribute data via KGs to provide inter-
rather than just individual symptoms. Mathematically, this
pretable recommendations across multiple product categories.
workflow can be formalized as follows:
Attention mechanisms have also been used to emphasize the
Given symptom set S and herb set H, we define symptom
most relevant aspects of side information, further improving
subsets Syn. Each subset Syn ={s ,s ,...,s , 1 ≒ k ≒ |S|},
i 1 2 k
user confidence and satisfaction. Yang et al. [29] integrated
where k indicates the number of symptoms in Syn . Each
i
attention to select pertinent neighboring entities, thereby en-
symptom variable is binary: s ﹋ {0,1}, s = 1 if the
k k
hancing interpretability through knowledge-aware connectiv-
symptom is present in the diagnosis, and 0 otherwise. The
ity, while Zhang et al. [30] employed multi-head attention to
recommendation task computes:
learn initial news embeddings and used hierarchical gating to
fuse diverse side information.
y =耳 (Syn|H) (1)
For TCM herb recommendations, providing sufficient rea-
(cid:98)SynH ?
soningisessentialtoestablishclinicalcredibility.Somestudies Here, y represents the probability that herbs can treat
(cid:98)SynH
[31] introduced interpretability via meta-paths combined with Syn, 耳(﹞) is the recommendation function, and ? denotes
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
4 IEEETRANSACTIONSANDJOURNALSTEMPLATE
learnable hyperparameters. The model ranks all candidate
herbs based on their computed probabilities y? and se-
SynH
lects the top-N herbs with the highest scores, where N ﹋
{5,10,20}.
B. DesignofMRHAF
TheoverallworkflowoftheproposedMRHAFisillustrated
in Fig.1A,B,C. The model consists of three sequential phases:
(1)Firstly,weconstructthreecomplementarygraphs:aglobal
Herb-Efficacy-SymptomKnowledgeGraph(HESKG),aHerb-
Symptom Interaction Graph (HSIG), and a molecular-level
Herb-Attribute-Component Knowledge Graph (HACKG). (2)
Secondly,weapplyagraphattentionmechanismtoextracten-
tityembeddingsfromeachgraph.Specifically,intheHESKG,
we compute the importance of different edge types and use
these as weights for entity features. A multi-head attention
mechanism is then employed to capture global dependen-
cies, thereby enriching global semantic representations. (3)
Finally, we integrate the hybrid features derived from the
threegraphstogenerateherbrecommendations.Bycombining
implicitrelationalinformationwithexplicitherbalknowledge,
the model not only improves predictive accuracy but also
providesinterpretableexplanationsforitsrecommendedherbal
combinations. Fig. 2. Architecture of the multi-relational global attention feature
learningmodule.
TABLEI
SEVENRELATIONTYPESINHESKG
and herb nodes. E represents the edge set, comprising two
hs
relationlabel head rel tail kinds of edges: coexistence edges (Ec ) between symptoms
hs
sh0 symptom co-occur herb andherbs,andtherapeuticedges(Et )representingtreatment
hs
sh1 symptom treat herb relationships. The construction of HSIG is expressed as:
se2 symptom function efficacy
he3 herb function efficacy (cid:40)
1, if C(s ,h ) or T(s ,h ) is observed
hh4 herb combine herb HSIG= i j i j (3)
ss5 symptom co-occur symptom 0, otherwise
hh6 herb co-occur herb
Where C(s ,h ) denotes the coexistence of relationships
i j
involving symptoms and herbs, while T(s ,h ) represents
1) Graphconstruction: We construct three graphs, HESKG, i j
therapeutic treatment relationships between them.
HACKG, and HSIG, to enhance the extraction of features
HACKG Construction: We define HACKG as
related to herbs and symptoms.
G = (V ,R ,T ), where V =
HESKGConstruction:WedefineHESKGasG = HACKG hac hac hac hac
HESKG {Vh,...,Vh ,Va,...,Va ,Vc,...,Vc } is the set of
(V ,R ,T ), where V ={Vh,...,Vh ,Ve,...,Ve , 1 |h| 1 |a| 1 (|c|)
hes hes hes hes 1 |h| 1 |e| entities, including herbs, their attributes, and their chemical
Vs,...,Vs }isthesetofentities,includingherbs,efficacies,
1 (|s|) components. Specifically, herb attributes consist of four
and symptoms. R = {r ,r ,...,r } is the set of edges,
hes 1 2 |R| natures (cold, hot, warm, and cool), five flavors (sour,
representing interactions among the three types of nodes.
bitter, sweet, spicy, and salty), meridian tropism (lung,
T ?V ℅R ℅V denotes the triplets in G .
hes hes hes hes HESKG pericardium, heart, large intestine, triple energizer, small
Eachtripletisexpressedas(h,r,t),wherehistheheadentity,
intestine, stomach, gallbladder, bladder, spleen, liver, kidney),
tisthetailentity,andristherelationtype.G includes
HESKG and toxicity. Chemical components, such as alkaloids,
7 different edge types, as shown in Table I. For example, the
flavonoids, saponins, volatile oils, and polysaccharides, reflect
triplet (Herba Ephedrae, function, Induce sweating) consists
biochemicalproperties.R ={r ,r ,...,r }isthesetof
of the entities Herba Ephedrae and Induce sweating, with hac 1 2 |R|
edges, representing interactions among these types of nodes.
functionastherelationbetweenthem.Thecalculationformula
T ?V ℅R ℅V denotes the triplets in G .
is defined as: hac hac hac hac HACKG
The construction is formulated as:
(cid:40) (cid:40)
1, if h,t appear in T 1, if h,t appear in T
HESKG= hes (2) HACKG= hac (4)
0, otherwise 0, otherwise
HSIG Construction: The HSIG is denoted as G HSIG = 2) Hierarchical attention feature learning: This layer com-
(V ,E ), where V includes entities related to symptom prises three modules: (a) a multi-relational global attention
hs hs hs
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS5
feature extraction module, (b) a decoupled local attention embeddings. f(﹞) is the graph attention process. 考 is the
feature extraction module, and (c) a herb attribute and biolog- activation function. mm represents matrix multiplication.
ical information extraction module. Together, these modules
are designed to capture distinct entity features. Specifically, f(﹞)=GATConv(X(L?1),A?) (9)
hes
entity representations incorporate weighted importance from
differentedgetypesintheHESKG.Herbalfeaturesarefurther Here, A? is the adjacency matrix with self-loops, and
refined by integrating biochemical and therapeutic properties GATConv represents the graph attention layer. The infor-
from the HACKG. Additionally, interactional characteristics mation aggregation formula for each node h i in the graph
between symptoms and herbs are derived from the HSIG. attention mechanism is expressed as:
(a) Multi-relational Global Attention Feature Learning ? ?
M qu o e d n u c l y e: m T at h r i i s x m fro o m dul m e u b lt e i- g r i e n l s ati b o y na c l o d n a s t t a r , uc w ti h n i g ch a i n s t e h d e g n e u f s r e e d - X h (L i ) =考? (cid:88) 汐 hihj WX j (L?1) ? (10)
to weight and generate the input features. Subsequently, a
hj﹋N(hi)
graphattentionmechanismisutilizedtoextractentityfeatures. Where X(L?1) denotes the feature representation of node h
j j
Finally, a global attention aggregation operation is applied. at the (L?1)-th layer. N(h ) is the set of neighboring nodes
i
It models long-range dependencies and captures global con- of node h , and W is the learnable weight matrix. 汐 is
i hihj
textual features. The overall framework of this module is theattentioncoefficient,whichmeasurestheimportanceofh
i
illustrated in Fig.2. to h . The attention coefficient is calculated as:
j
Weighted Feature Fusion: The diverse edge-type frequen-
cies in HESKG reflect the varying strengths of association exp (cid:0) LeakyReLU (cid:0) 汐T[WX ﹡WX ] (cid:1)(cid:1)
between herbs and symptoms. This facilitates semantic fea- 汐 = hi hj
hihj (cid:80) exp(LeakyReLU(汐T[WX ﹡WX ]))
ture extraction. We employ the TF-IDF algorithm to achieve hk﹋N(hi) hi hk
(11)
effectiveinformationfusionacrossdifferentedgetypes.Inthis
Finally, the deep features extracted through multiple con-
formulation, nodes correspond to documents, and the edges
connected to each node correspond to terms. Let m and n volutional layers are fused with the initial features. They are
denotetwonodesinHESKG.ThefunctionF(m,n)represents further enhanced via a fully connected layer:
the frequency of the edge formed by node m and its neighbor
node n in the dataset (i.e., the edge frequency). F(n) denotes X(fe) =tanh (cid:16) BN (cid:16) W ﹞ (cid:16) Avg(X(0),X(L)) (cid:17) +b (cid:17)(cid:17) (12)
the total number of edges connected to node n. |V | is hes hes hes
hes
the total number of nodes in HESKG. F(m) is the number Followingthestepsabove,weobtainthesymptomembedding
of nodes connected to node m. Accordingly, the normalized matrix Xs and herb embedding matrix Xh . Both incorpo-
hes hes
weight of each edge is defined as: rate edge-importance characteristics.
F(m,n) (cid:18) |V | (cid:19) Global Attention Aggregation: This module consists of
EW (m,n) = F(n) ﹞log 1+F he ( s m) (5) two processes, denoted as 朴 羽 (﹞): multi-head attention feature
extraction and attention propagation. We utilize the weighted
Then, we represent all edge importance values within an
features obtained from HESKGAT to extract multi-relational
adjacency matrix and use them to weight the initial features.
attention. Multi-head attention emphasizes the relative impor-
The elements of the edge weight matrix RM℅M are denoted
tanceofdifferentedgetypes.Thisenablesthemodeltocapture
as:
global attention patterns and determine how entities prioritize
diverse relational contexts. Through this mechanism, entities
(cid:40)
EW , if (m,n) exist in HESKG aggregate neighboring node features associated with distinct
w = (m,n) (6)
mn edge types according to their learned attention weights.
0, otherwise
Multi-head attention: First, we calculate the multi-head
HESKGAT Feature Extraction: At each layer of the attention features. The attention coefficients are computed as
graph attention network, we apply a convolution operation follows:
withresidualconnectionstoupdatenoderepresentations.This (cid:18) (cid:18) Q ?KT (cid:19) (cid:19)
allows information aggregation from neighboring nodes while Y(0) =MLP softmax hes﹟ hes ?V (13)
hes d hes
simultaneously enhancing feature quality. The update rule is
formulated as: (cid:16) (cid:17)
Q =考 MLP(X(fe)) (14)
hes hes
X h (L es ?1) =考 (cid:16) f (cid:16) mm(X h (0 e ) s ,RM℅M),G HESKG (cid:17)(cid:17) (7) K hes =考 (cid:16) MLP(X h (f es e)) (cid:17) (15)
(cid:16) (cid:17)
X(L) =考 (cid:16) f (cid:16) (X(L?1)+FC(X(0))),G (cid:17)(cid:17) (8) V hes =考 MLP(X h (f es e)) (16)
hes hes hes HESKG
Here, Q , K , and V are the query, key, and value
hes hes hes
Where X(L?1) is the representation of symptoms and herbs representations of X(fe), respectively. Y(0) is the final repre-
hes hes hes
on the (L?1)-th layer. X(L) is the final output layer＊s entity sentation of the multi-head attention features.
hes
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
6 IEEETRANSACTIONSANDJOURNALSTEMPLATE
Fig. 4. Architecture of the herb attributes and biological information
Fig. 3. Architecture of decoupling local attention feature learning fusionmodule.
module.
Attention propagation: After obtaining the multi-head at- X(L) =考 (cid:16) f (cid:16)(cid:16) X(L?1)+FC(X(0)) (cid:17) ,G (cid:17)(cid:17) (21)
tentionfeatures,weapplymultiplelayersoflineartransforma- hs hs hs HSIG
tion to propagate the attention features forward. This process Here, X(L?1) represents the feature matrices at the (L?1)-
recursively iterates through the linear stack, progressively th layer o hs f HSIGAT. X(L) denotes the output feature matrices
extracting deeper representations. The propagation process is hs
afterinformationaggregationineachlayer.f(﹞)representsthe
defined as follows:
GATConv operation as defined in (9), and (10).
(cid:16) (cid:16) (cid:17)(cid:17)
Y(L?1) =ReLU MLP LayerNorm(Y(0)+X(fe)) Subsequently, the initial features X(0) and the convolution-
hes hes hes hs
(17) ally aggregated features X(L) are combined through average
hs
Y(L) =MLP(Y(L?1)) (18) pooling. They are then passed through a fully connected layer
hes hes
to enhance the representations further :
Y(L)∩ =LayerNorm(Y(L)+Y(0)) (19)
hes hes hes X(fe) =tanh (cid:16) BN (cid:16) W ﹞ (cid:16) Avg(X(0),X(L)) (cid:17) +b (cid:17)(cid:17) (22)
Where Y(L) denotes the amplified output from the fully hs hs hs
hes
connected layer. We then fuse this output with the extracted In addition, HSIGAT generates the symptom features Xs
hs
multi-head attention features to obtain a single-layer linear capturing interactional details, and the herbal features Xh .
hs
propagation feature
Y(L)∩
.
(c) Herb Attributes and Biological Information Fusion
hes
Module: This module enhances the feature representations of
Subsequently, we perform iterative operations within the
herbs by constructing a HACKG. HACKG integrates herbs＊
attention propagation layer to derive deeper-level entity repre-
intrinsic properties with their biological information as exter-
sentations. This process is defined as:
nal knowledge. This module provides a more comprehensive
Z(L) =朴(Z(L?1),Y(L)∩ ,羽) (20) and expressive embedding of herbs by bridging traditional
hes hes hes
Here, Z(L?1) refers to features from the (L?1)-th layer of pharmacological attributes with biochemical characteristics.
hes Importantly, it also helps elucidate the material basis underly-
the attention aggregation process. 羽 denotes the trainable pa-
ing the therapeutic effects of TCM. The detailed architecture
rameters utilized throughout the computational process. Con-
of this module is presented in Fig.4.
sequently, we obtain relationship-attentive enhanced features
HACKGAT Feature Extraction: We employ SMILES
for herbs and symptoms, denoted as Zh and Zs .
hes hes sequences to represent the chemical components of herbs.
(b) Decoupling the Local Attention Feature Learning Mod-
RDKitisusedtogeneratemolecularfingerprintsascomponent
ule: This module is designed to decouple herb-symptom in-
features [32], denoted as XECFP. To improve the quality of
teractions from other herb-related relationships, such as herb- c
input representations, we apply a weighted fusion of XECFP
efficacy and herb-herb relationships. The module can focus c
with automatically generated features X(0). Then, the fused
exclusivelyonmodelingdirectherb-symptomrelationshipsby c
features X(input) are used as the component feature input for
isolating these interactions. Meanwhile, this extracts precise c
downstream tasks, formulated as:
localattentionfeatureswhileminimizingnoisefromirrelevant
orindirectinformation.Theoverallarchitectureofthismodule
X(input) =X(0)+汐﹞XECFP (23)
is illustrated in Fig.3. c c c
HSIGATFeatureExtraction:Weimplementagraphatten- Where 汐 is a weighted fusion parameter that controls the
tion mechanism on the HSIG. Convolutional operations with contribution ratio of X(0) and XECFP.
c c
residual connections are employed to embed entity features. The fused features are then fed into HACKGAT to obtain
This approach effectively integrates graph structural infor- the molecular-level feature representation X(L), expressed as:
hac
mation and enhances entity representations. The aggregation (cid:16) (cid:16) (cid:17)(cid:17)
formula is defined as: X h (L ac ) =考 f (X h (L ac ?1)+FC(X h (0 a ) c )),G HACKG (24)
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS7
Here,X(L?1)
representsthefeaturematricesatthe(L?1)-th results.Ourexperimentsaimtoaddressthefollowingresearch
hac
| layerofHACKGAT.X(L) |     |     | denotestheoutputfeaturematrices |     |     |     |     | questions | (RQs): |     |     |     |     |     |     |
| ------------------- | --- | --- | ------------------------------- | --- | --- | --- | --- | --------- | ------ | --- | --- | --- | --- | --- | --- |
hac
afterinformationaggregationineachlayer.f(﹞)representsthe ? RQ1: Can MRHAF outperform current state-of-the-art
GATConv operation, as defined in (9), and (10). graph neural network-based and KG-based recommenda-
Toenhancetherepresentations,theinitialfeaturesX(0)
|     |     |     |     |     |     |     | and | tion | methods? |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | -------- | --- | --- | --- | --- | --- | --- |
hac
the aggregated features X(L) are first averaged. Subsequently, ? RQ2: How effective are the key modules proposed in
hac
MRHAF?
| this fused | result | is fed | into a | fully connected |     | layer | for further |     |     |     |     |     |     |     |     |
| ---------- | ------ | ------ | ------ | --------------- | --- | ----- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
processing: ? RQ3:Howdodifferenthyperparametersinfluencemodel
performance?
|          |       | (cid:16) | (cid:16) (cid:16) |       |         | (cid:17) | (cid:17)(cid:17) |     |     |     |     |     |     |     |     |
| -------- | ----- | -------- | ----------------- | ----- | ------- | -------- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| X (f e ) | =tanh | BN       | W ﹞               | Avg(X | (0 ) ,X | (L ))    | +b (25)          |     |     |     |     |     |     |     |     |
h a c h a c h ac ? RQ4: Are the herb combinations generated by MRHAF
|     |     |     |     |     |     |     |     | clinically | appropriate? |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------------ | --- | --- | --- | --- | --- | --- |
Thus,HACKGATproducestheherbalfeaturesXh
|           |      |                   |     |     |             |     | ,which      | RQ5: | Is the | recommended |     | herb | set | reasonable | in prac- |
| --------- | ---- | ----------------- | --- | --- | ----------- | --- | ----------- | ---- | ------ | ----------- | --- | ---- | --- | ---------- | -------- |
|           |      |                   |     |     |             |     | hac         | ?    |        |             |     |      |     |            |          |
| integrate | both | herbal attributes |     | and | biochemical |     | components. |      |        |             |     |      |     |            |          |
tice?
3) Hybrid feature fusion and herb recommendation: This RQ6: Are the recommendation results supported by
?
| layer focuses |     | on merging | entity | features |     | derived | from the |             |     |          |     |        |         |     |     |
| ------------- | --- | ---------- | ------ | -------- | --- | ------- | -------- | ----------- | --- | -------- | --- | ------ | ------- | --- | --- |
|               |     |            |        |          |     |         |          | mechanistic |     | evidence | of  | herbal | action? |     |     |
threeKGs:multi-relationalattentionfeaturesfromHESKGAT,
| herbal characteristics |     | from | HACKGAT, |     | and | relationship | fea- |     |     |     |     |     |     |     |     |
| ---------------------- | --- | ---- | -------- | --- | --- | ------------ | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
A. Experimentalsetup
| tures from | HSIGAT.   |           | Through | this      | process,   | hybrid | feature  |              |     |            |     |               |     |             |     |
| ---------- | --------- | --------- | ------- | --------- | ---------- | ------ | -------- | ------------ | --- | ---------- | --- | ------------- | --- | ----------- | --- |
|            |           |           |         |           |            |        |          | 1) Datasets: |     | We conduct |     | comprehensive |     | experiments | on  |
| fusion is  | achieved, | producing |         | the final | embeddings |        | for both |              |     |            |     |               |     |             |     |
herb and symptom entities. The given set of symptoms is two TCM prescription datasets to evaluate the effectiveness
subsequently represented as syndrome features, derived from of the proposed model. To ensure feature completeness and
|             |     |             |      |                |     |     |             | pharmacological |     | consistency, |     | herbs | lacking | component | in- |
| ----------- | --- | ----------- | ---- | -------------- | --- | --- | ----------- | --------------- | --- | ------------ | --- | ----- | ------- | --------- | --- |
| the symptom |     | embeddings. | This | representation |     |     | enables the |                 |     |              |     |       |         |           |     |
generation of a corresponding herb set for the given symptom formation were excluded based on the TCMSP1 database.
collection, thereby supporting herb recommendation. To inte- Consequently, prescriptions containing any of the removed
grate features across graphs, we employ a summation-based herbs were also filtered out to maintain reproducibility and
fusionstrategy.Specifically,theembeddingsobtainedfromthe ensure fair comparisons. To evaluate MRHAF＊s performance,
|               |     |                |     |         |     |              |         | each dataset | was | divided | into | training | and | testing | sets with an |
| ------------- | --- | -------------- | --- | ------- | --- | ------------ | ------- | ------------ | --- | ------- | ---- | -------- | --- | ------- | ------------ |
| three modules |     | are aggregated |     | to form | the | final hybrid | feature |              |     |         |      |          |     |         |              |
representations of herbs and symptoms. The computations of 8:2ratio.Furthermore,20%ofthetrainingdatawasrandomly
the final embeddings are expressed as: selected as a validation set for hyperparameter tuning. Table
|     |     |     |     |     |     |     |     | II summarizes | the | dataset | statistics, |     | while | Fig.5 illustrates | the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------- | ----------- | --- | ----- | ----------------- | --- |
e =sum(Xs ,Zs ) (26) distribution patterns of herbs across the two datasets.
|     |     | s         |     | hs     | hes |     |      |     |     |     |         |     |     |     |     |
| --- | --- | --------- | --- | ------ | --- | --- | ---- | --- | --- | --- | ------- | --- | --- | --- | --- |
|     |     | e =sum(Xh |     | ,Xh    | ,Zh | )   | (27) |     |     |     |         |     |     |     |     |
|     |     | h         |     | hs hac | hes |     |      |     |     |     | TABLEII |     |     |     |     |
STATISTICSOFTCM-33KANDTCM-9KDATASETS
| After | obtaining | the | final | embeddings |     | of symptoms | and |     |     |     |     |     |     |     |     |
| ----- | --------- | --- | ----- | ---------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
herbs, we compute herb preferences for each symptom set TCM-33k TCM-9k
as:
HESKG
|     | y?  | =ReLU(MLP(e |     |     | ))?e |     | (28) | #Entities  |     |     |     | 1,637 |     |     | 3,324 |
| --- | --- | ----------- | --- | --- | ---- | --- | ---- | ---------- | --- | --- | --- | ----- | --- | --- | ----- |
|     |     | SynH        |     |     | s    | h   |      |            |     |     |     |       |     |     |       |
|     |     |             |     |     |      |     |      | #Relations |     |     |     | 7     |     |     | 7     |
Where y? is the probability matrix of herbs for curing #Triplets 97,681 150,601
SynH
| the given       | set | of symptoms, |     | the operator |     | ? denotes | matrix | HSIG      |     |     |     |     |     |     |       |
| --------------- | --- | ------------ | --- | ------------ | --- | --------- | ------ | --------- | --- | --- | --- | --- | --- | --- | ----- |
| multiplication. |     |              |     |              |     |           |        | #Symptoms |     |     |     | 388 |     |     | 1,389 |
|                 |     |              |     |              |     |           |        | #Herbs    |     |     |     | 758 |     |     | 962   |
To train the model, we employ the Binary Cross-Entropy #Interactions 34,241 65,654
| Loss (BCELoss), |     | formulated |     | as: |     |     |     |     |     |     |     |     |     |     |     |
| --------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
HACKG
|     |     | N   |     |     |     |     |     | #Entities |     |     |     | 16,194 |     |     | 17,501 |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | ------ | --- | --- | ------ |
1 (cid:88)
| L=? |     | [y  | logp +(1?y |     | )log(1?p |     | )] (29) | #Relations |     |     |     | 2       |     |     | 2       |
| --- | --- | --- | ---------- | --- | -------- | --- | ------- | ---------- | --- | --- | --- | ------- | --- | --- | ------- |
|     |     | i   | i          |     | i        |     | i       |            |     |     |     |         |     |     |         |
|     | N   |     |            |     |          |     |         | #Triplets  |     |     |     | 770,807 |     |     | 829,206 |
i=1
DatasetSplit
Where N represents the number of recommended herbs, y i = #Train 19,324 4,719
y is the ground truth label, p = 考(y? ), 考(﹞) is #Dev 6,442 1,573
| SynHi    |     |       |                  |     | i       | SynHi |        |       |     |     |     |       |     |     |       |
| -------- | --- | ----- | ---------------- | --- | ------- | ----- | ------ | ----- | --- | --- | --- | ----- | --- | --- | ----- |
|          | y?  |       |                  |     |         |       |        | #Test |     |     |     | 6,442 |     |     | 1,573 |
| Sigmoid, | and | SynHi | is the predicted |     | ranking | of    | herbs. |       |     |     |     |       |     |     |       |
?TCM-33kdataset[4]originallycontained33,765prescrip-
|         |          | IV. | EXPERIMENTS |       |     |       |         |            |           |              |         |        |         |          |            |
| ------- | -------- | --- | ----------- | ----- | --- | ----- | ------- | ---------- | --------- | ------------ | ------- | ------ | ------- | -------- | ---------- |
|         |          |     |             |       |     |       |         | tions, 390 | symptoms, |              | and 805 | herbs. | After   | removing | herbs      |
| In this | section, | we  | evaluate    | MRHAF |     | using | two TCM |            |           |              |         |        |         |          |            |
|         |          |     |             |       |     |       |         | without    | component | information, |         | the    | dataset | was      | reduced to |
prescriptiondatasets.Webeginbydescribingtheexperimental
|     |     |     |     |     |     |     |     | 32,208 prescriptions, |     | 388 | symptoms, |     | and | 758 herbs. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --------- | --- | --- | ---------- | --- |
setup, followed by a comparative analysis of MRHAF against ? TCM-9k dataset [15] initially consisted of 9,196 pre-
| existing | methods.          | An  | ablation | study      | is  | then conducted |            | to          |       |           |     |           |        |           |     |
| -------- | ----------------- | --- | -------- | ---------- | --- | -------------- | ---------- | ----------- | ----- | --------- | --- | --------- | ------ | --------- | --- |
|          |                   |     |          |            |     |                |            | scriptions, | 1,448 | symptoms, |     | and 1,919 | herbs. | Following | the |
| validate | the effectiveness |     | of       | individual |     | model          | components |             |       |           |     |           |        |           |     |
and hyperparameters. Finally, we provide a discussion of the 1(https://www.91tcmsp.com/)
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
| 8   |     |     |     |     |     |     |     |     |     | IEEETRANSACTIONSANDJOURNALSTEMPLATE |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------- | --- | --- | --- | --- |
|GN(herbs|syms)﹎T(syms)|
|     |     |     |     |     |     |     | Precision@N |     | =   |     |     |     |     | (30) |
| --- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | ---- |
|N|
|GN(herbs|syms)﹎T(syms)|
|     |     |     |     |     |     |     | Recall@N |     | =   |     |     |     |     | (31) |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | ---- |
|T(syms)|
|     |     |     |     |     |     |     |     |        |     |     | (cid:80)N     | reli      |     |      |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | ------------- | --------- | --- | ---- |
|     |     |     |     |     |     |     |     | NDCG@N |     |     | = i=1         | log(i+1)  |     | (32) |
|     |     |     |     |     |     |     |     |        |     |     | (cid:80)|REL| | 2reli?1   |     |      |
|     |     |     |     |     |     |     |     |        |     |     | i=1           | log (i+1) |     |      |
2
|     |     |     |     |     |     |     | Where            | GN(herbs|syms) |            |                  | is the    | generated    | top-N   | herbs        |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | -------------- | ---------- | ---------------- | --------- | ------------ | ------- | ------------ |
|     |     |     |     |     |     |     | according        | to a           | collection | of               | symptoms, | and          | T(syms) | denotes      |
|     |     |     |     |     |     |     | the ground-truth |                | herb       | set. Precision@N |           | measures     |         | the prob-    |
|     |     |     |     |     |     |     | ability of       | correctly      |            | recommended      |           | herbs in     | the     | top-N herb   |
|     |     |     |     |     |     |     | suggestions.     | Recall@N       |            | evaluates        |           | the coverage |         | of correctly |
|     |     |     |     |     |     |     | recommended      |                | herbs      | among            | the top-N | herbs.       |         | NDCG@N       |
considersboththepositionandrelevanceoftherecommended
|     |     |     |     |     |     |     | herbs, which | is  | particularly |     | important | for | TCM prescriptions |     |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------------ | --- | --------- | --- | ----------------- | --- |
Fig.5. Thedistributionpatternsofherbsacrossthetwodatasets.
|     |     |     |     |     |     |     | where the           | order | and       | reference | value        | of herbs | play  | a crucial |
| --- | --- | --- | --- | --- | --- | --- | ------------------- | ----- | --------- | --------- | ------------ | -------- | ----- | --------- |
|     |     |     |     |     |     |     | role in formulating |       | effective |           | treatments.  |          |       |           |
|     |     |     |     |     |     |     |                     |       |           |           | We implement |          | MRHAF | using     |
same screening process, the final dataset contained 7,865 3) Implementation details:
prescriptions, 1,389 symptoms, and 962 herbs. PyTorch.Thelearningrateistunedwithintherangeof0.0001-
|                      |     |     |             |                   |     |        | 0.001 for | both | datasets. | For | the TCM-9k |     | dataset, | the input |
| -------------------- | --- | --- | ----------- | ----------------- | --- | ------ | --------- | ---- | --------- | --- | ---------- | --- | -------- | --------- |
| 2) Comparisonmodels: |     |     | To validate | the effectiveness |     | of the |           |      |           |     |            |     |          |           |
proposedMRHAFmodel,wecompareitagainstseveralstate- and hidden layer dimensions are set to 512. For the TCM-
|     |     |     |     |     |     |     | 33k dataset, | the | input | dimension |     | is fixed | at 512, | while the |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ----- | --------- | --- | -------- | ------- | --------- |
of-the-artbaselines.ThecomparedmethodsincludeKG-based
|                |                  |                |                |             |               |           | hidden layer | dimension |             | is reduced |            | to 256. | The overall | model       |
| -------------- | ---------------- | -------------- | -------------- | ----------- | ------------- | --------- | ------------ | --------- | ----------- | ---------- | ---------- | ------- | ----------- | ----------- |
| recommendation | models,          |                | relation-aware | graph       | learning      | mod-      |              |           |             |            |            |         |             |             |
|                |                  |                |                |             |               |           | architecture | consists  |             | of two     | GAT        | layers  | and four    | attention   |
| els, and       | herb-specific    | recommendation |                | models.     | Specifically, |           |              |           |             |            |            |         |             |             |
|                |                  |                |                |             |               |           | aggregation  | layers    | (with       | four       | heads      | per     | layer).     | Training is |
| we evaluate    | the following    |                | methods:       |             |               |           |              |           |             |            |            |         |             |             |
|                |                  |                |                |             |               |           | performed    | for       | 200 epochs, |            | with batch | sizes   | of 256      | for TCM-    |
| ? KGCN         | [20] constructed |                | a user-item    | interaction |               | graph and |              |           |             |            |            |         |             |             |
|                |                  |                |                |             |               |           | 33k and      | 128 for   | TCM-9k.     |            |            |         |             |             |
| item KGs.      | It expanded      | each           | entity＊s       | receptive   | field         | in the KG |              |           |             |            |            |         |             |             |
tocapturehigh-orderuserpreferencestowarddifferententities,
thereby predicting user-item correlations. B. Performancecomparisonandanalysis
?KGAT[21]extendedKGCNbyintroducingaknowledge-
|     |     |     |     |     |     |     | 1) Comparisonwithbaselines(RQ1): |     |     |     |     | Experiments |     | are con- |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | ----------- | --- | -------- |
aware attention mechanism that incorporates users＊ varying ducted on both datasets to evaluate MRHAF against baseline
| attention | across diverse | entity | relationships. |     |     |     |         |     |         |     |            |     |       |            |
| --------- | -------------- | ------ | -------------- | --- | --- | --- | ------- | --- | ------- | --- | ---------- | --- | ----- | ---------- |
|           |                |        |                |     |     |     | models. | The | results | are | summarized | in  | Table | III, where |
?RGCN[33]enhancedtheconventionalGCNbyassigning Precision@N, Recall@N, and NDCG@N are reported.
distinct weights to different edge types, thereby effectively Furthermore, paired t-tests were performed between the
| modeling | multi-relational |     | structures. |     |     |     |       |     |          |        |                |     |     |            |
| -------- | ---------------- | --- | ----------- | --- | --- | --- | ----- | --- | -------- | ------ | -------------- | --- | --- | ---------- |
|          |                  |     |             |     |     |     | MRHAF | and | baseline | models | (Supplementary |     |     | Table S1). |
? KDHR [14] applied GCN for multi-layer information fu- All improvements of MRHAF over the baselines are sta-
sionwhileincorporatingherbknowledgetostrengthenfeature
|     |     |     |     |     |     |     | tistically | significant |     | (p < | 0.05). | It is | evident | from the |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ----------- | --- | ---- | ------ | ----- | ------- | -------- |
representations and reduce noise. results that MRHAF consistently outperforms all baseline
? SMGCN [9] constructed three subgraphs describing methods across evaluation metrics. On the TCM-33k dataset,
symptom-herb interactions. GCN was employed to learn node MRHAF achieves improvements of 0.5963 in Precision@10
featurerepresentationsonthesesubgraphs,whileanMLPwas and 0.6719 in Recall@10 compared to the advanced KG
| used to | represent syndrome |     | features. |     |     |     |                |     |       |       |     |            |     |              |
| ------- | ------------------ | --- | --------- | --- | --- | --- | -------------- | --- | ----- | ----- | --- | ---------- | --- | ------------ |
|         |                    |     |           |     |     |     | recommendation |     | model | KGAT. | On  | the TCM-9k |     | dataset, the |
?SMRGAT[15]builtmulti-graphsbasedonsymptom-herb gainsare0.4487inPrecision@10and0.5556inRecall@10.
co-occurrence. GAT was then applied to capture the varying Furthermore, when compared with the advanced herb rec-
influence of herbs on symptoms, while residual connections ommendation model SMRGAT, MRHAF achieves a 0.0975
enhance feature learning. In addition, the semantic features of improvement in Precision@10 and a 0.1235 increase in
| symptoms | were integrated |     | with herbal | attribute | information. |     |           |     |          |       |     |              |     |         |
| -------- | --------------- | --- | ----------- | --------- | ------------ | --- | --------- | --- | -------- | ----- | --- | ------------ | --- | ------- |
|          |                 |     |             |           |              |     | Recall@10 | on  | TCM-33k, | while | the | improvements |     | on TCM- |
The effectiveness of MRHAF and comparison models is 9k reach 0.2230 in Precision@10 and 0.2766 in Recall@10.
| evaluated | on both | datasets | using | three | standard | metrics: |     |     |     |     |     |     |     |     |
| --------- | ------- | -------- | ----- | ----- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
Precision@N, Recall@N, and NDCG@N , which are The relatively poor performance of KGAT and KGCN can
widelyappliedinrecommendationtasks.Here,N denotesthe be attributed to limitations in KG structures, where multi-
numberofrecommendedherbsaccordingtoSyn
|     |     |     |     |     | i ,withvalues |     | hop propagation |     | is required |     | for certain | relationships |     | to reach |
| --- | --- | --- | --- | --- | ------------- | --- | --------------- | --- | ----------- | --- | ----------- | ------------- | --- | -------- |
set as {5,10,20}. The metrics are defined as follows: relevant entities, making it difficult to fully capture complex
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS9
TABLEIII
PERFORMANCEASSESSMENTOFMRHAFANDBASELINESONTCM-33KANDTCM-9K.THEOPTIMALRESULTSAREDISPLAYEDINBOLD
Precision Recall NDCG
P@5 P@10 P@20 R@5 R@10 R@20 N@5 N@10 N@20
TCM-33k
KGCN 0.1813 0.1100 0.0737 0.1345 0.1612 0.2152 0.3875 0.4221 0.4787
KGAT 0.2059 0.1417 0.1030 0.1493 0.2024 0.2912 0.3610 0.4159 0.4958
RGCN 0.2201 0.1647 0.1218 0.1568 0.2349 0.3460 0.3467 0.4164 0.5072
KDHR 0.2573 0.1991 0.1469 0.1949 0.2940 0.4304 0.3694 0.4442 0.5424
SMGCN 0.2479 0.1900 0.1385 0.1793 0.2717 0.3958 0.3684 0.4404 0.5335
SMRGAT 0.2624 0.2061 0.1490 0.1947 0.3012 0.4311 0.3752 0.4543 0.5483
MRHAF 0.2871 0.2262 0.1657 0.2182 0.3384 0.4870 0.3941 0.4717 0.5733
TCM-9k
KGCN 0.1972 0.1324 0.0846 0.1140 0.1491 0.1924 0.3850 0.4380 0.4873
KGAT 0.2309 0.1821 0.1325 0.1286 0.2086 0.3074 0.3503 0.4270 0.5167
RGCN 0.2343 0.1877 0.1276 0.1314 0.2101 0.2877 0.3602 0.4422 0.5161
KDHR 0.2626 0.2098 0.1547 0.1611 0.2501 0.3637 0.3657 0.4419 0.5404
SMGCN 0.2450 0.1951 0.1433 0.1377 0.2206 0.3307 0.3484 0.4238 0.5222
SMRGAT 0.2734 0.2157 0.1573 0.1647 0.2542 0.3702 0.3803 0.4572 0.5557
MRHAF 0.3308 0.2638 0.1931 0.2088 0.3245 0.4634 0.4220 0.4962 0.6050
TABLEIV
ABLATIONANALYSESARECONDUCTEDONTHETWODATASETS.THESUPERIOROUTCOMESAREHIGHLIGHTEDINBOLD.THEABBREVIATION＆W/O＊
DENOTES＆WITHOUT＊
Precision Recall NDCG
P@5 P@10 P@20 R@5 R@10 R@20 N@5 N@10 N@20
TCM-33k
w/o-HACKGAT 0.2767 0.2198 0.1611 0.2108 0.3298 0.4758 0.3843 0.4635 0.5642
w/o-HSIGAT 0.2744 0.2179 0.1592 0.2110 0.3291 0.4717 0.3804 0.4600 0.5591
w/o-HESKGAT 0.2724 0.2167 0.1602 0.2070 0.3243 0.4721 0.3769 0.4557 0.5579
MRHAF 0.2871 0.2262 0.1657 0.2182 0.3384 0.4870 0.3941 0.4717 0.5733
TCM-9k
w/o-HACKGAT 0.3200 0.2537 0.1886 0.1997 0.3097 0.4501 0.4147 0.4868 0.5969
w/o-HSIGAT 0.3190 0.2552 0.1861 0.1915 0.3051 0.4407 0.4155 0.4918 0.5974
w/o-HESKGAT 0.3036 0.2476 0.1828 0.1974 0.3117 0.4461 0.3955 0.4758 0.5838
MRHAF 0.3308 0.2638 0.1931 0.2088 0.3245 0.4634 0.4220 0.4962 0.6050
correlations and semantic information. Traditional TCM rec- TCM-33k and TCM-9k datasets are summarized in Table IV.
ommendation models demonstrate stronger performance in Meanwhile, paired t-tests were performed between MRHAF
this domain but still fall short of MRHAF. For instance, and its variants. All improvements of MRHAF over the
SMGCN focuses only on herb-symptom associations while ablated versions are statistically significant (p < 0.001),
ignoringthestrengthofinteractions.KDHRincorporatesTCM confirming that each module contributes positively to overall
knowledge but fails to integrate compound-level information performance (Supplementary Table S2). Based on Table IV,
or quantify relation intensity. SMRGAT leverages GAT to several conclusions can be drawn: (i) On both datasets, w/o-
modelherb-symptominfluencestrengths.However,itneglects HACKGAT, w/o-HESKGAT, and w/o-HSIGAT all perform
globalattentionandinformationonherbalcomponents.Incon- worse than MRHAF. This demonstrates the necessity of
trast, MRHAF integrates multi-relational hierarchical atten- incorporating herbal attributes and biochemical components,
tion with hybrid knowledge fusion, simultaneously capturing modeling global relationships through attention mechanisms,
global semantic dependencies, local interaction features, and and enhancing feature representation via symptom-herb in-
biochemical knowledge. This design explains its consistent teraction learning. (ii) The removal of HESKGAT results in
superiority over both KG-based and herb-specific baselines the most pronounced performance degradation, highlighting
across the two datasets. its central role in MRHAF. This finding underscores the
2) Ablation study (RQ2): To evaluate the contribution of importance of modeling multi-relational connections among
each module, we conduct ablation experiments by designing symptoms, efficacies, and herbs, which enables the model
three model variants: to better capture holistic TCM formulation principles and
?w/o-HACKGAT:RemovestheHACKGATmodulerespon- improve recommendation accuracy.
sible for extracting herbal attribute and component features. 3) Hyperparameter analysis (RQ3): To investigate the im-
? w/o-HSIGAT: Removes the HSIGAT module, capturing pact of hyperparameters on model performance, we employ a
local attention features. variable control methodology. The analysis primarily focuses
? w/o-HESKGAT: Removes the HESKGAT module that on input dimensions and hidden layer depths.
models multi-relational global attention features. Inputdimensions:Wevarytheembeddingdimensionofthe
The results of MRHAF and its ablated variants on the input layer over {64, 128, 256, 512}. As depicted in Fig.6,
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
10 IEEETRANSACTIONSANDJOURNALSTEMPLATE
experience,asTCMprescriptionstypicallycontain8-12herbs.
This finding indicates that MRHAF successfully models the
formulation principles of TCM. In contrast, the Top 5 recom-
mendations scored relatively lower, reflecting that a limited
number of herbs may not ensure prescription completeness.
Meanwhile, the stable scores observed for Top-20 recommen-
dations reflect the robustness of MRHAF in large-scale herb
candidate screening. Expert consistency was verified through
Cohen＊s Kappa, Kendall＊s W, and ICC analyses, showing
a significant and reliable overall consensus (Supplementary
TableS3-S6).Overall,theseresultsvalidateMRHAF＊sclinical
reliability and highlight potential directions for future opti-
mization. For example, future work could develop dynamic
Fig. 6. The Precision@N, Recall@N, and NDCG@N under different
inputdimensionsonthetwodatasets,withNsetto5,10,and20. recommendation strategies tailored to specific clinical needs
to enhance precision.
TABLEV
CLINICALEXPERTEVALUATIONOFMRHAFRECOMMENDEDRESULTS
doctor1 doctor2 doctor3 doctor4 doctor5 doctor6 mean
TCM-33k
Top5 3.792 3.361 2.426 3.139 3.755 3.815 3.381
Top10 3.806 3.227 3.477 3.574 3.931 3.949 3.660
Top20 3.806 2.931 4.074 3.769 4.051 3.657 3.715
TCM-9k
Fig. 7. The Precision@N, Recall@N, and NDCG@N under different Top5 3.951 3.543 2.963 4.062 3.259 3.877 3.605
hiddenlayerdepthsonthetwodatasets,withNsetto5,10,and20. Top10 3.938 3.210 3.506 4.086 4.296 4.111 3.858
Top20 3.963 2.914 4.136 4.086 3.432 4.099 3.772
MRHAF achieves optimal performance at 512 dimensions
across both datasets. This improvement arises because larger C. Casestudyofexplainability(RQ5)
dimensions allow the model to capture richer entity informa-
To further evaluate the performance and interpretability of
tion. However, excessively large embeddings introduce noise,
MRHAF, we conduct a case study using a randomly selected
leading to performance degradation.
sample from the test results, as illustrated in Fig.8. The anal-
Hidden layer depths: We further analyze the influence of ysis shows that seven of the ten recommended herbs overlap
hidden layer depth, varying the number of layers from {2, 3, with those in the original prescription. The symptom set iden-
4}.AsshowninFig.7,MRHAFachievesthebestperformance tifies the underlying TCM pattern as summer-dampness syn-
with two hidden layers across both datasets. While increas- drome.Therecommendedherbsdemonstratetherapeuticfunc-
ing the number of layers enables modeling of longer-range tions such as resolving the exterior with coolness and acridity
relationships, it also introduces redundant information. Such and clearing heat with wind coursing. MRHAF＊s ability to
redundancy may propagate noise and adversely affect model suggest these herbs stems from its integration of symptom-
performance. herb interactions with herbal efficacy knowledge. For exam-
4) Clinicalexpertevaluation(RQ4): To further evaluate the ple, Platycodon grandifloras resolves phlegm and suppresses
clinical applicability of MRHAF, we adopt the evaluation cough, addressing dampness associated with throat dryness.
procedures described in [34] and [8], adapting them to the Poriacocosdispelsdampness,relievingthroatswellingcaused
requirements of this study. Specifically, 5% of the recommen- by wind-heat colds. Angelica dahurica alleviates spasms and
dation results from the TCM-9k and TCM-33k datasets were pain while nourishing yin; when combined with other herbs,
randomly selected as evaluation samples. Six clinical experts, it prevents excessive sweating. This case study illustrates that
each holding the title of associate chief physician or above, MRHAF delivers high accuracy and clinically interpretable
independently assessed these samples under a double-blind herb recommendations aligned with TCM principles, offering
protocol. A five-point scale was employed, where a score of valuable support for symptom management.
1 indicates the least appropriate recommendation and a score Additionally, to investigate the mechanistic rationality of
of 5 represents the most suitable. The evaluation results are MRHAF＊s recommendations further, we extract symptom-
summarized in Table V. related triples from HESKG. Then, we compute inter-entity
For both datasets, the average expert ratings of all recom- correlations using learned features, and construct a subgraph
mendedsetsexceeded3.3points,confirmingthatMRHAFcan KG by filtering out negative-weight triples (Fig.9). A node
effectively capture expert knowledge and generate clinically degree analysis reveals that Glycyrrhiza uralensis, Angel-
valuable recommendations. Notably, the Top 10 recommen- ica dahurica, and Bupleurum chinense exhibit the highest
dations performed the best, which aligns well with clinical degree of 15, reflecting their extensive direct connections
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS
11
|     |     |     |     |     |     | respectively, | partially  | explaining |             | why | the model | recommends    |     |
| --- | --- | --- | --- | --- | --- | ------------- | ---------- | ---------- | ----------- | --- | --------- | ------------- | --- |
|     |     |     |     |     |     | this herb.    | Similarly, | the        | correlation |     | between   | Notopterygium |     |
incisumandSaposhnikoviadivaricatereaches0.64aftertrain-
|     |     |     |     |     |     | ing. Notopterygium |               | incisum       | is  | effective  | in      | dispelling | wind,     |
| --- | --- | --- | --- | --- | --- | ------------------ | ------------- | ------------- | --- | ---------- | ------- | ---------- | --------- |
|     |     |     |     |     |     | relieving          | the exterior, | alleviating   |     | pain,      | and     | treating   | wind-     |
|     |     |     |     |     |     | dampness,          | while         | Saposhnikovia |     | divaricate | dispels |            | wind-cold |
andwind-dampnesswhilereducingpain.Theircomplementary
pharmacologicalactionsexplainwhytheyareoftenprescribed
togetherforwind-coldarthralgia,illustratingmutualreinforce-
|     |     |     |     |     |     | ment in | TCM | compatibility. |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------- | --- | -------------- | --- | --- | --- | --- | --- |
TABLEVI
MOLECULARDOCKINGAFFINITY(KCAL/MOL)BETWEENMAINACTIVE
Fig.8. AcasestudyofMRHAF.Theherbsmarkedinredarecorrectly
| recommended. |     |     |     |     |     |                                     |              | COMPONENTSANDCORETARGETS |            |               |         |              |          |
| ------------ | --- | --- | --- | --- | --- | ----------------------------------- | ------------ | ------------------------ | ---------- | ------------- | ------- | ------------ | -------- |
|              |     |     |     |     |     | Component                           | Target       | Affinity                 |            | Component     |         | Target       | Affinity |
|              |     |     |     |     |     | quercetin                           | TNF          |                          | -8.7       | puerarin      |         | STAT3        | -7.2     |
|              |     |     |     |     |     | luteolin                            | TNF          |                          | -8.6       | puerarin      |         | TNF          | -7.1     |
|              |     |     |     |     |     | kaempferol                          | TNF          |                          | -8.6       | quercetin     |         | IL6          | -6.9     |
|              |     |     |     |     |     | rutin                               | IL1B         |                          | -8.1       | oroxylina     |         | IL6          | -6.9     |
|              |     |     |     |     |     | wogonin                             | TNF          |                          | -7.8       | rutin         |         | IL6          | -6.7     |
|              |     |     |     |     |     | rutin                               | TNF          |                          | -7.4       | paeoniflorin  |         | TNF          | -6.4     |
|              |     |     |     |     |     | quercetin                           | IL1B         |                          | -7.3       | licochalconea |         | STAT3        | -6.4     |
|              |     |     |     |     |     | luteolin                            | IFNG         |                          | -7.3       | wogonin       |         | IL6          | -6.4     |
|              |     |     |     |     |     | luteolin                            | IL6          |                          | -7.2       | paeoniflorin  |         | IL6          | -6.1     |
|              |     |     |     |     |     | quercetin                           | IFNG         |                          | -7.2       |               |         |              |          |
|              |     |     |     |     |     | D. Networkpharmacologyanalysis(RQ6) |              |                          |            |               |         |              |          |
|              |     |     |     |     |     | Network                             | pharmacology |                          | integrates |               | herbal  | components,  |          |
|              |     |     |     |     |     | molecular                           | targets,     | and biological           |            | pathways      |         | to elucidate | drug     |
|              |     |     |     |     |     | action mechanisms                   |              | systematically.          |            | Its           | central | hypothesis   | is       |
Fig.9. Subgraphsgeneratedbytherecommendedherbs. that TCM exerts therapeutic effects through multi-component
|     |     |     |     |     |     | synergy | acting | on multiple | targets[35], |     | thereby | modulating |     |
| --- | --- | --- | --- | --- | --- | ------- | ------ | ----------- | ------------ | --- | ------- | ---------- | --- |
disease-relatednetworks.Tofurthervalidatetherationalityand
within the symptom-herb association subgraph. The high interpretability of MRHAF＊s recommendations, we perform a
co-occurrence frequency between Glycyrrhiza uralensis and post-hocinterpretabilityanalysisonarepresentativecasefrom
Angelica dahurica corresponds to the classical herbal pair Fig.8.Specifically,weemploynetworkpharmacologytoinves-
|                |            |       |         |             |     | tigate the | potential | mechanisms |     | underlying | the | recommended |     |
| -------------- | ---------- | ----- | ------- | ----------- | --- | ---------- | --------- | ---------- | --- | ---------- | --- | ----------- | --- |
| ShaoYao-GanCao | Decoction, | known | for its | spasmolytic | and |            |           |            |     |            |     |             |     |
analgesic effects. Although Platycodon grandifloras shows a herb set (Fig.1E), thereby providing additional evidence for
slightly lower degree of 13, its frequent co-occurrence with MRHAF＊sexplanatorycapability.Followingtheframeworkof
multiplesymptomsvalidatesitsrolein※dispersinglungqiand ※using symptom phenotypes to characterize TCM indications
relievingsorethroat,§makingitasuitablesynergistictreatment and therapeutic effects§ proposed in [36], we extract all
for conditions such as dry throat and headache. Poria cocos associated genes for the target symptom set from SymMap2.
effectively alleviates dampness-related symptoms, including Simultaneously, we identify 889 disease-related targets by
cough,excessivephlegm,anddrythroat,bypromotingdiuresis integrating data from GeneCards3 (relevance score≡ 5), Dis-
GeNET4,andOMIM5.UsingtheTCMSPdatabase,wefurther
toeliminatedampnesswhilealsostrengtheningthespleenand
calming the mind. These findings demonstrate the effective- identify 197 bioactive components (oral bioavailability≡ 0.3,
ness of MRHAF. The model leverages structural knowledge drug-likeness≡ 0.18) and their 309 corresponding targets
graphinformation.Consequently,itgeneratesherbrecommen- across the ten recommended herbs. This analysis reveals 107
dations that are consistent with TCM pharmacodynamics and overlapping targets, suggesting that the herbal formula may
the principles of herbal compatibility. exert therapeutic effects through multi-target modulation of
Furthermore,correlationcoefficientsbetweensymptomem- inflammatory and immune-related pathways.
|          |                     |         |         |       |     | 1) Functional |     | enrichment | analysis: |     | Gene | Ontology | (GO) |
| -------- | ------------------- | ------- | ------- | ----- | --- | ------------- | --- | ---------- | --------- | --- | ---- | -------- | ---- |
| beddings | and herb embeddings | learned | through | MRHAF | are |               |     |            |           |     |      |          |      |
presented in Fig.10, providing a quantitative explanation of and Kyoto Encyclopedia of Genes and Genomes (KEGG)
therecommendationprocess.Significantshiftsareobservedin enrichment analyses of the overlapping targets identify 2,215
| correlations | among herb-herb, | symptom-herb, |     | and symptom- |     |     |     |     |     |     |     |     |     |
| ------------ | ---------------- | ------------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2http://www.symmap.org/
| symptom | pairs before | and after | training. | For example, | the |     |     |     |     |     |     |     |     |
| ------- | ------------ | --------- | --------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
3https://www.genecards.org/
correlations between ※aversion to cold§ and ※aversion to cold 4https://www.disgenet.org/
with fever§ with Platycodon grandifloras are 0.27 and 0.35, 5https://www.omim.org/
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
12 IEEETRANSACTIONSANDJOURNALSTEMPLATE
Fig.10. Correlationcoefficienttransformationheatmap.
the exterior, antiviral activity, and analgesia. Binding energy
is a key indicator of conformational stability between active
components and target proteins, with values lower than -5.0
kcal/molgenerallyindicatingstrongbindingaffinity.Asshown
in Table VI, quercetin exhibits strong affinity with TNF (-
8.7 kcal/mol), while luteolin binds to TNF (-8.6 kcal/mol)
with similarly high stability. Network analysis (Fig.11) re-
veals that the herb set modulates 107 target proteins, among
which IL1B, IL6, IFNG, TNF, and STAT3 constitute the core
regulatory hub of inflammation每immune interactions. Rep-
resentative docking conformations for these five key targets
are shown in Fig.12. Notably, Quercetin demonstrates broad-
Fig.11. PPInetworkoftargetsassociatedwiththesymptomsettreated spectrumanti-inflammatoryactivity[37]bytargetingmultiple
bytherecommendedherbset.
proteins, including TNF, IL1B, and IL6, while luteolin shows
high specificity toward TNF [38]. Licochalcone A selectively
GO terms (2,016 in Biological Process, 162 in Molecular regulates the STAT3 pathway (binding energy -6.4 kcal/mol),
Function,and37inCellularComponent)and163KEGGpath- exerting immunomodulatory effects [39]. Collectively, these
ways (Fig.11). These results highlight significant enrichment active components act synergistically to regulate inflamma-
in immune-inflammatory regulation, metabolic processes, and tory responses, immune modulation, and pathological repair.
infection responses, demonstrating the herb set＊s broad regu- This establishes the multi-target therapeutic mechanism of
latory effects across interconnected biological systems. the recommended herb set. Importantly, these molecular find-
2) Identificationofkeytargets: The 107 overlapping targets ings align with the traditional TCM therapeutic principles of
areimportedintotheSTRING6databasetoconstructahuman ※dispersing wind-cold from the exterior and clearing heat to
protein-protein interaction (PPI) network with a confidence relievesorethroat,§therebyconfirmingboththerationalityand
score threshold of 0.9. After the removal of isolated nodes, interpretability of MRHAF＊s herb recommendations.
86 targets remain. Topological analysis is conducted using
Cytoscape3.9.1,withmedianvaluesusedascutoffthresholds. V. CONCLUSION
Targets satisfying all three centrality criteria〞betweenness
This study proposes MRHAF, recommending optimal herb
centrality (BC), closeness centrality (CC), and degree central-
combinationsforgivensymptomsetsbasedonTCMcompati-
ity (DC)〞are identified as core targets, yielding 25 candidate
bilityprinciples.MRHAFintegratesheterogeneousknowledge
coregenes.Furtherscreeningnarrowsthissettofivefinalkey
by modeling the co-occurrence and therapeutic correlations
targets, as illustrated in Fig.12.
betweensymptomsandherbswithinamulti-graphframework.
3) Molecular docking: Building on the network pharma-
Specifically,MRHAFemploysGAT-basedencodingtoextract
cology analysis, we further explore the potential molecular
local attention features while distinguishing the relational im-
mechanisms of the top 10 recommended TCM herbs in
portanceofheterogeneousentities.AnHESKGisconstructed,
treating the selected symptom set. The herbal combination
using TF-IDF weighting and multi-head attention to capture
may exert therapeutic effects through multiple pathways, in-
multi-relationalglobaldependenciesandenhanceinterpretabil-
cluding anti-inflammatory actions, dispersing cold to relieve
ity. In addition, a HACKG is introduced to incorporate herb
6https://cn.string-db.org/ properties and biochemical information, thereby generating
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
YANGetal.:MRHAF:MULTI-RELATIONALHIERARCHICALATTENTIONWITHHYBRIDKNOWLEDGEFUSIONFOREXPLAINABLEHERBRECOMMENDATIONS
13
Fig.12. GOandKEGGenrichmentanalyses.Largerbubblesindicatemoreenrichedgenesinthecorrespondingpathway,whilereddercolors
representsmallerp-values,suggestinghigherenrichmentsignificanceandmorereliableresults.
Fig.13. Moleculardockingexamplesoffivekeytargets.
multi-dimensionalherbembeddings.Byfusingfeaturesacross but also aligns with TCM＊s holistic, synergistic therapeutic
these graphs, MRHAF achieves a comprehensive representa- philosophy.
tion of herbs and symptoms.
Despite these promising outcomes, several limitations re-
Extensive experiments on the TCM-33k and TCM-9k main.First,dosageinformationhasnotyetbeenincorporated;
datasets show that MRHAF consistently outperforms state-of- more precise dose-response modeling may further improve
the-artbaselines.Ablationandhyperparameterstudiesvalidate clinical applicability. Second, interactions among herbal com-
thecontributionofeachmoduleandthemodel＊sstability.Clin- ponentsarenotexplicitlymodeled,andfutureworkshouldex-
ical evaluations confirm its practical applicability and ability ploremechanismsunderlyingtheseinteractionstorecommend
tocapturespecialistknowledgeforvaluablerecommendations. combinations with stronger synergistic therapeutic potential.
Beyond accuracy, MRHAF offers multi-level interpretability: Additionally, filtering out herbs without chemical components
(i) subgraph tracing reveals meaningful associations between may bias the dataset toward well-studied herbs. Further work
recommendedherbsandsymptoms,(ii)embeddingcorrelation will expand the dataset and leverage existing information to
analysis shows strengthened semantic alignment after multi- infer latent components for missing herbs, thereby increasing
relational attention learning, and (iii) network pharmacology thebreadthofherbsthemodelcanpredict.Moreover,wewill
and molecular docking validate the pharmacodynamic plau- incorporate network pharmacology results into the model＊s
sibility of the recommendations. These results confirm that standardizedpipeline.Forinstance,wewillutilizethedocking
MRHAF not only captures clinical prescription principles scores to enrich herb embeddings or include them as training
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for publication in IEEE Journal of Biomedical and Health Informatics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JBHI.2025.3644489
14 IEEETRANSACTIONSANDJOURNALSTEMPLATE
constraints to ensure recommendations align more closely [19] Y.Cao,X.Wang,X.He,Z.Hu,andT.-S.Chua,※Unifyingknowledge
with established pharmacological evidence. Addressing these graphlearningandrecommendation:Towardsabetterunderstandingof
user preferences,§ in The world wide web conference, 2019, pp. 151每
challenges will enhance the accuracy and clinical reliability
161.
of herb recommendations, contributing to more scientific and [20] H. Wang, M. Zhao, X. Xie, W. Li, and M. Guo, ※Knowledge graph
effective decision-making in prescribing. convolutional networks for recommender systems,§ in The world wide
webconference,2019,pp.3307每3313.
[21] X. Wang, X. He, Y. Cao, M. Liu, and T.-S. Chua, ※Kgat: Knowledge
REFERENCES
graphattentionnetworkforrecommendation,§inProceedingsofthe25th
ACMSIGKDDinternationalconferenceonknowledgediscovery&data
mining,2019,pp.950每958.
[1] Q.Sun,M.He,M.Zhang,S.Zeng,L.Chen,H.Zhao,H.Yang,M.Liu, [22] T.Ma,L.Huang,Q.Lu,andS.Hu,※Kr-gcn:Knowledge-awarereason-
S.Ren,andH.Xu,※Traditionalchinesemedicineandcolorectalcancer: ing with graph convolution network for explainable recommendation,§
implicationsfordrugdiscovery,§FrontiersinPharmacology,vol.12,p. ACM Transactions on Information Systems, vol. 41, no. 1, pp. 1每27,
685002,2021. 2023.
[2] X. Su, Z. Yao, S. Li, H. Sun et al., ※Synergism of chinese herbal [23] C.Chang,J.Zhou,Y.Weng,X.Zeng,Z.Wu,C.-D.Wang,andY.Tang,
medicine: illustrated by danshen compound,§ Evidence-based Comple- ※Kgtn: Knowledge graph transformer network for explainable multi-
mentaryandAlternativeMedicine,vol.2016,2016. category item recommendation,§ Knowledge-Based Systems, vol. 278,
[3] Z.Zhao,Y.Qiang,F.Yang,X.Hou,J.Zhao,andK.Song,※Two-stream p.110854,2023.
vision transformer based multi-label recognition for tcm prescriptions [24] Y. Hou, N. Yang, Y. Wu, and P. S. Yu, ※Explainable recommendation
construction,§ComputersinBiologyandMedicine,vol.170,p.107920, withfusionofaspectinformation,§WorldWideWeb,vol.22,pp.221每
2024. 240,2019.
[4] L. Yao, Y. Zhang, B. Wei, W. Zhang, and Z. Jin, ※A topic modeling [25] R. Shimizu, M. Matsutani, and M. Goto, ※An explainable recommen-
approachfortraditionalchinesemedicineprescriptions,§IEEETransac- dation framework based on an improved knowledge graph attention
tions on Knowledge and Data Engineering, vol. 30, no. 6, pp. 1007每 networkwithmassivevolumesofsideinformation,§Knowledge-Based
1021,2018. Systems,vol.239,p.107970,2022.
[5] X. Wang, Y. Zhang, X. Wang, and J. Chen, ※A knowledge graph [26] J. Zheng, Z. Qin, S. Wang, and D. Li, ※Attention-based explainable
enhancedtopicmodelingapproachforherbrecommendation,§pp.709每 friend link prediction with heterogeneous context information,§ Infor-
724,2019. mationSciences,vol.597,pp.211每229,2022.
[6] Y.QinandZ.Ma,※Atraditionalchinesemedicineprescriptionrecom- [27] R.Boughareb,H.Seridi,andS.Beldjoudi,※Explainablerecommenda-
mendationmethodbasedonmutualinformationclustering,§inJournal tionbasedonweightedknowledgegraphsandgraphconvolutionalnet-
ofPhysics:ConferenceSeries,vol.1544,no.1. IOPPublishing,2020, works,§JournalofInformation&KnowledgeManagement,p.2250098,
p.012065. 2023.
[7] C.Pei,C.Ruan,Y.Zhang,andY.Yang,※Bayesclassifierchainbased [28] Y.Du,X.Zhu,L.Chen,Z.Fang,andY.Gao,※Metakg:Meta-learning
onsvmfortraditionalchinesemedicalprescriptiongeneration,§inWeb onknowledgegraphforcold-startrecommendation,§IEEETransactions
andBigData:4thInternationalJointConference,APWeb-WAIM2020, onKnowledgeandDataEngineering,2022.
Tianjin,China,September18-20,2020,Proceedings,PartI4. Springer, [29] Z.YangandS.Dong,※Hagerec:Hierarchicalattentiongraphconvolu-
2020,pp.748每763. tional network incorporating knowledge graph for explainable recom-
[8] Z. Liu, C. Luo, D. Fu, J. Gui, Z. Zheng, L. Qi, and H. Guo, ※A mendation,§Knowledge-BasedSystems,vol.204,p.106194,2020.
novel transfer learning model for traditional herbal medicine prescrip- [30] M. Zhang, G. Wang, L. Ren, J. Li, K. Deng, and B. Zhang, ※Metonr:
tion generation from unstructured resources and knowledge,§ Artificial A meta explanation triplet oriented news recommendation model,§
IntelligenceinMedicine,vol.124,p.102232,2022. Knowledge-BasedSystems,vol.238,p.107922,2022.
[9] Y.Jin,W.Zhang,X.He,X.Wang,andX.Wang,※Syndrome-awareherb [31] Y. Jin, W. Ji, Y. Shi, X. Wang, and X. Yang, ※Meta-path guided
recommendationwithmulti-graphconvolutionnetwork,§in2020IEEE graphattentionnetworkforexplainableherbrecommendation,§Health
36th International Conference on Data Engineering (ICDE). IEEE, InformationScienceandSystems,vol.11,no.1,p.5,2023.
2020,pp.145每156. [32] H. L. Morgan, ※The generation of a unique machine description for
[10] C.Li,D.Liu,K.Yang,X.Huang,andJ.Lv,※Herb-know:knowledge chemicalstructures-atechniquedevelopedatchemicalabstractsservice.§
enhanced prescription generation for traditional chinese medicine,§ in Journalofchemicaldocumentation,vol.5,no.2,pp.107每113,1965.
2020IEEEInternationalConferenceonBioinformaticsandBiomedicine [33] M. Schlichtkrull, T. N. Kipf, P. Bloem, R. Van Den Berg, I. Titov,
(BIBM). IEEE,2020,pp.1560每1567. and M. Welling, ※Modeling relational data with graph convolutional
[11] Y. Dai, Z. Yan, J. Cheng, X. Duan, and G. Wang, ※Analysis of multi- networks,§inThesemanticweb:15thinternationalconference,ESWC
modaldatafusionfromaninformationtheoryperspective,§Information 2018, Heraklion, Crete, Greece, June 3每7, 2018, proceedings 15.
Sciences,vol.623,pp.164每183,2023. Springer,2018,pp.593每607.
[12] C.Zhang,Y.Zhang,andX.Gao,※Multi-headself-attentiongated-dilated [34] W.Zhou,K.Yang,J.Zeng,X.Lai,X.Wang,C.Ji,Y.Li,P.Zhang,and
convolutional neural network for word sense disambiguation,§ IEEE S.Li,※Fordnet:recommendingtraditionalchinesemedicineformulavia
Access,vol.11,pp.14202每14210,2023. deep neural network integrating phenotype and molecule,§ Pharmaco-
[13] C. Yang, Y. Xiao, Y. Zhang, Y. Sun, and J. Han, ※Heterogeneous logicalresearch,vol.173,p.105752,2021.
network representation learning:A unifiedframework with surveyand [35] R. Zhou, S. Chu, H. Li, and C. Yan, ※Traditional chinese medicine
benchmark,§ IEEE Transactions on Knowledge and Data Engineering, prescriptionrecommendationforalzheimer＊sdiseasebasedonnetwork
vol.34,no.10,pp.4854每4873,2020. propagation and reinforcement learning,§ Tsinghua Science and Tech-
[14] Y.Yang,Y.Rao,M.Yu,andY.Kang,※Multi-layerinformationfusion nology,vol.31,no.1,pp.658每673,2026.
based on graph convolutional network for knowledge-driven herb rec- [36] X. Gan, Z. Shu, X. Wang, D. Yan, J. Li, S. Ofaim, R. Albert, X. Li,
ommendation,§NeuralNetworks,vol.146,pp.1每10,2022. B. Liu, X. Zhou et al., ※Network medicine framework reveals generic
[15] X. Yang and C. Ding, ※Smrgat: A traditional chinese herb recommen- herb-symptom effectiveness of traditional chinese medicine,§ Science
dation model based on a multi-graph residual attention network and advances,vol.9,no.43,p.eadh0215,2023.
semantic knowledge fusion,§ Journal of Ethnopharmacology, vol. 315, [37] R.Kleemann,L.Verschuren,M.Morrison,S.Zadelaar,M.J.vanErk,
p.116693,2023. P. Y. Wielinga, and T. Kooistra, ※Anti-inflammatory, anti-proliferative
[16] J.Wang,Y.Shi,H.Yu,Z.Yan,H.Li,andZ.Chen,※Anovelkg-based and anti-atherosclerotic effects of quercetin in human in vitro and in
recommendationmodelviarelation-awareattentionalgcn,§Knowledge- vivomodels,§Atherosclerosis,vol.218,no.1,pp.44每52,2011.
BasedSystems,p.110702,2023. [38] Q.-Y. Lu, L. Guo, Q.-Y. Zhang, F.-M. Yang, S.-T. Zhou, and Q.-Y.
[17] C. Troussas and A. Krouska, ※Path-based recommender system for Sun, ※Luteolin alleviates the tnf-汐-induced inflammatory response of
learningactivitiesusingknowledgegraphs,§Information,vol.14,no.1, humanmicrovascularendothelialcellsviatheakt/mapk/nf-百bpathway,§
p.9,2022. MediatorsofInflammation,vol.2024,no.1,p.6393872,2024.
[18] F. Zhang, N. J. Yuan, D. Lian, X. Xie, and W.-Y. Ma, ※Collaborative [39] J. Shu, X. Cui, X. Liu, W. Yu, W. Zhang, X. Huo, and C. Lu, ※Lic-
knowledgebaseembeddingforrecommendersystems,§inProceedings ochalconeainhibitsige-mediatedallergicreactionthroughplc/erk/stat3
of the 22nd ACM SIGKDD international conference on knowledge pathway,§ International Journal of Immunopathology and Pharmacol-
discoveryanddatamining,2016,pp.353每362. ogy,vol.36,p.03946320221135462,2022.
This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see https://creativecommons.org/licenses/by/4.0/
