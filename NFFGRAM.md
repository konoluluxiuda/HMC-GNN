3698 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
| NFFGRAM: |             |           |     | Nonlinear |         |                |     | Multi-Feature |     |           |         | Fusion |     | and |     |
| -------- | ----------- | --------- | --- | --------- | ------- | -------------- | --- | ------------- | --- | --------- | ------- | ------ | --- | --- | --- |
| Gated    |             | Recurrent |     |           |         | Self-Attention |     |               |     | Mechanism |         |        |     | for |     |
|          | Traditional |           |     |           | Chinese |                |     | Medicine      |     |           | Formula |        |     |     |     |
Recommendation
|     |     |     | Hailong |     | Hu  | , Yaqian | Li , | and Zhong | Li  | , Member, | IEEE |     |     |     |     |
| --- | --- | --- | ------- | --- | --- | -------- | ---- | --------- | --- | --------- | ---- | --- | --- | --- | --- |
Abstract¡ªTraditional Chinese Medicine (TCM) prescrip- I. INTRODUCTION
tionsarederivedfromthedistinctivethoughtprocessand
TcmprescriptionsareoutcomesoftheTCMdiagnosticand
clinicalexperiencesofChinesemedicaltheory.Withthead-
ventofartificialintelligence(AI),thereisanenhancedabil- treatment process, reflecting the principles of TCM diagnosis
itytoformulatetheseprescriptionsbyanalyzingsymptom andtreatment.Furthermore,TCMprescriptionsholdsignificant
| data. However, |     | the inherent |     | sparseness |     | of herb-symptom |     |     |     |     |     |     |     |     |     |
| -------------- | --- | ------------ | --- | ---------- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
researchpotentialwithintherealmofartificialintelligence[1].
| association | data | still | limits | the efficacy |     | of such | predic- |     |     |     |     |     |     |     |     |
| ----------- | ---- | ----- | ------ | ------------ | --- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
Throughtraditionalformulasandclinicalexpertise,TCMprac-
tivemethods.Thisstudyintroducesanenhancedbipartite
|                 |     |           |         |     |      |         |           | titioners | select | specific | herbs | from a vast | array | and formulate |     |
| --------------- | --- | --------- | ------- | --- | ---- | ------- | --------- | --------- | ------ | -------- | ----- | ----------- | ----- | ------------- | --- |
| graph diffusion |     | algorithm | coupled |     | with | a gated | recurrent |           |        |          |       |             |       |               |     |
self-attention mechanism for predicting herb and symp- prescriptionstailoredtopatients¡¯symptomsandphysicalsigns.
tomassociations.Theinitialphaseinvolvesthereconstruc- These prescriptions encapsulate knowledge and prescriptive
tion of the herb-symptom association matrix, leveraging guidelines, equipping novice TCM practitioners with tools to
| the fractal-weighted |     | K-nearest |     | neighbor | algorithm. |     | Subse- |     |     |     |     |     |     |     |     |
| -------------------- | --- | --------- | --- | -------- | ---------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
quicklyandskillfullyselectherbsanddeviseeffectiveformula-
| quently, | a method | is  | conceived | to  | extract | analogous | fea- |     |     |     |     |     |     |     |     |
| -------- | -------- | --- | --------- | --- | ------- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
tions[2].Nonetheless,thisdiagnosticapproachremainsnotably
| tures between |     | herbs | and symptoms, |     | which | integrates | lin- |     |     |     |     |     |     |     |     |
| ------------- | --- | ----- | ------------- | --- | ----- | ---------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
earneighborhoodsimilaritywithGaussiankernelsimilarity, subjective,largelyrelyingonthephysician¡¯sexpertise,whichof-
bothbasedonfractaldimensions.Thenextstageemploys tenlacksstructuredstandardization.Consequently,therearisesa
a modified bipartite graph diffusion to deduce underlying compellingneedtodelveintoclassicalprescriptionstoelucidate
herb-symptomrelationships.Thisprocessculminateswith
|     |     |     |     |     |     |     |     | formulation |     | principles | and offer | intelligent | herb | recommenda- |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ---------- | --------- | ----------- | ---- | ----------- | --- |
theintegrationofthegatedrecurrentself-attentionmecha-
|          |              |     |         |        |     |        |           | tions | for clinical | practice. | Our | research | contributes | a   | robust, |
| -------- | ------------ | --- | ------- | ------ | --- | ------ | --------- | ----- | ------------ | --------- | --- | -------- | ----------- | --- | ------- |
| nism and | a confidence |     | scoring | system | to  | refine | the herb- |       |              |           |     |          |             |     |         |
symptom association predictive matrix at a granular level. data-driven solution to support more informed and effective
Webenchmarkourresultsagainstleading-edgealgorithms TCMtreatmentdecisions.
toascertaintheprecisionandreliabilityofourmodel.Such Researcheffortsgearedtowardscomputationalreconfiguring
asimprovementsofprecision@20by21.77%,recall@20by
|         |                 |     |     |        |          |     |          | TCM | prescriptions | predominantly |     | align | with | three methods: |     |
| ------- | --------------- | --- | --- | ------ | -------- | --- | -------- | --- | ------------- | ------------- | --- | ----- | ---- | -------------- | --- |
| 12.46%, | and F1-score@20 |     | by  | 19.28% | compared |     | with the |     |               |               |     |       |      |                |     |
topicmodeling,sequencegenerationmodeling,andgraphrep-
| best baseline |     | for the | TCM2 | dataset. | Additionally, |     | compre- |     |     |     |     |     |     |     |     |
| ------------- | --- | ------- | ---- | -------- | ------------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
hensive case studies are undertaken, evaluating recom- resentationlearning[3],asshowninFig.1.
mended prescriptions using insights from contemporary (1) Topic model-based methods: In the context of the topic
medicineandnetworkpharmacology.Theproposedmodel model, a prescription is conceptualized as a text. Herein, both
| provides | a novel | paradigm | for | enhancing |     | herbal | prescrip- |     |     |     |     |     |     |     |     |
| -------- | ------- | -------- | --- | --------- | --- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
symptomsandincludedTCMelementsareviewedastangible
tionmethodologiesandTCMherb-basedtreatments.
|            |                |                 |       |     |             |                |         | words,   | while | underlying    | syndromes | and        | treatment | principles |      |
| ---------- | -------------- | --------------- | ----- | --- | ----------- | -------------- | ------- | -------- | ----- | ------------- | --------- | ---------- | --------- | ---------- | ---- |
| Index      | Terms¡ªFractal, |                 | gated |     | recurrent   | self-attention |         |          |       |               |           |            |           |            |      |
|            |                |                 |       |     |             |                |         | function | as    | latent topics | that      | bridge the | symptoms  | and        | TCM, |
| mechanism, | herb           | recommendation, |       |     | traditional |                | chinese |          |       |               |           |            |           |            |      |
therebyemulatingthe¡®dialecticaltreatment¡¯paradigmintrinsic
medicine.
toTCM[3].Wuetal.[4]delvedintotheprobabilitydistribution
|          |             |     |               |     |             |     |            | linking | symptoms | to  | distinct | ¡®syndromes¡¯ | topics | and TCM | to  |
| -------- | ----------- | --- | ------------- | --- | ----------- | --- | ---------- | ------- | -------- | --- | -------- | ----------- | ------ | ------- | --- |
| Received | 19 December |     | 2023; revised |     | 8 July 2024 | and | 16 October |         |          |     |          |             |        |         |     |
2024;accepted24January2025.Dateofpublication28January2025; varied ¡®treatment methods¡¯ topics. Similarly, Yao et al. [5]
dateofcurrentversion7May2025.Thisworkwassupportedinpartby constructedalatenttopicmodeltoprobethegenesisofTCMpre-
theScienceandTechnologyPlanProjectofHuzhouCity,Chinaunder
scriptions,spotlightingtheinherentregularitiesofprescriptions
| Grant 2022YZ15 |     | and Grant | 2022GZ51, | in  | part by | the National | Natu- |     |     |     |     |     |     |     |     |
| -------------- | --- | --------- | --------- | --- | ------- | ------------ | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
andtheassociationslinkingsyndromesandherbs.Furthermore,
| ral Science | Foundation | of  | China | under Grant | U24A20249 |     | and Grant |     |     |     |     |     |     |     |     |
| ----------- | ---------- | --- | ----- | ----------- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
12171434,andinpartbyHuzhouUniversityExcellentGraduateCourse
Zhouetal.[6]introducedatopicmodelthateffectivelycombines
ProjectunderGrantYJGX24003.(Correspondingauthor:ZhongLi.)
|                  |     |      |              |          |        |                |     | phenotypic | data          | with | molecular | knowledge | graphs.    | However,   |     |
| ---------------- | --- | ---- | ------------ | -------- | ------ | -------------- | --- | ---------- | ------------- | ---- | --------- | --------- | ---------- | ---------- | --- |
| The authors      | are | with | the Zhejiang | Province |        | Key Laboratory |     | of         |               |      |           |           |            |            |     |
|                  |     |      |              |          |        |                |     | these      | methodologies | tend | to        | overlook  | a holistic | simulation | of  |
| Smart Management |     | and  | Application  | of       | Modern | Agricultural   | Re- |            |               |      |           |           |            |            |     |
sources,SchoolofInformationEngineering,HuzhouUniversity,Huzhou symptom-herbinterrelations.Buildingonthissituation,certain
| 313000, | China (e-mail: | 03139@zjhu.edu.cn; |     |     | cornelia_lyq@163.com; |     |     |     |     |     |     |     |     |     |     |
| ------- | -------------- | ------------------ | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
researchershaveleveragedtopicmodelstofusesemanticrepre-
lizhong@zjhu.edu.cn).
DigitalObjectIdentifier10.1109/JBHI.2025.3535752 sentationsconduciveforTCMrecommendations.Forexample,
2168-2194?2025IEEE.Allrightsreserved,includingrightsfortextanddatamining,andtrainingofartificialintelligenceandsimilartechnologies.
Personaluseispermitted,butrepublication/redistributionrequiresIEEEpermission.Seehttps://www.ieee.org/publications/rights/index.html
formoreinformation.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore.  Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3699
recommendation. Liu et al. [15] developed a COVID-19
herb recommendation system that addresses data sparsity
issues by employing local graph aggregation representation in
heterogeneousnetworks.Zhaoetal.[16]introducedtheMGCN
model, which incorporates state elements and syndrome types
to emulate the n-ary relationship between symptoms and
prescriptions.Dong[17]proposedamethodforrecommending
TCM prescriptions through a subnetwork term mapping and a
CNNmodel.Ruanetal.[18]initiallyestablishedacontextfor
symptomandTCMnodesbasedonpredeterminedrulestoform
ametapath,andsubsequentlyutilizedanautoencoderforentity
representation.Despitetheseadvancements,thesemodelsoften
failtofullycapturetheintricaterelationshipsbetweensymptoms
Fig.1. Literaturereviewchart. andherbs,whichresultsininformationloss,especiallyregarding
high-ordercorrelationswithinthegraph.Inresponse,Shietal.
[19] implemented a heterogram-based recommendation tech-
Wangetal.[7]integratedknowledge,harnessingsymptomsand nique to refine the aggregation strategy of diverse information
TCMnameswordvectorstoaugmentlatentsemanticrepresen- inentityassociations.Furthermore,Jinetal.[20]introducedan
tations and discern TCM compatibility principles. In contrast, SMGCN method to represent the latent associations between
Lin et al. [8] unveiled a multi-faceted LDA model, focusing syndromes and herbs. Subsequently, Jin et al. [21] proposed a
onthedistributiondynamicsspanningsyndromestosymptoms meta-path-guided graph attention network to offer explainable
andsyndromestoherbs.Nevertheless,asalientshortcomingof herb recommendation solutions. These methods demonstrated
the topic model-oriented TCM recommendation methodology commendableresultswithTCMdatasets.Yet,duringtheprocess
isitsrudimentaryapplicationandportrayalofcomplexinterre- ofgraphrepresentationlearningandassociationgraphmodeling
lationships during TCM prescription crafting. More pointedly, based on medical records, these models do not adequately
extantresearchinadequatelyharnessestheintricateassociations capture the relational nuances among different nodes. As a
between symptoms and herbs, and an overreliance on mere result, all edge conduction parameters remain uniform, failing
word co-occurrence fails to adequately capture the complex toalignwiththeintricaterequirementsofTCMcompatibility.
relationshipsbetweenmedicalentities. All in all, the diagnostic and treatment process in TCM is
(2)Machinelearningmethodsbasedonsequencegeneration: subjectiveandlacksstructuredstandardizationduetoitsreliance
Initially, researchers employed sequence generation models to on practitioner experience. Moreover, existing computational
deriverelevantherbalselections fromsymptomaticdescriptions methods struggle to model the complex relationships between
and medical documentation. Yao et al. [9] applied a weighted symptomsandherbs,especiallyincapturingnonlinearinterac-
bag-of-words model utilizing an ontology structure for entity tions and handling sparse prescription data. To address these
representationlearningtopredictpotentialprescription-related limitations and facilitate more nuanced herbal recommenda-
drugsideeffects.Ahmedetal.[10]leveragedattentionnetworks tionsbymoreaccuratelyevaluatingnonlinearfeaturesbetween
to refine treatment recommendation processes. Concurrently, symptomsandherbs,improvingrecommendationaccuracy,and
Zhangetal.[11]introducedadiagnosticsystemrootedindeep enhancingconfidenceinherb-symptomassociations,weintro-
reinforcementlearning,aimingtoenhancesyndromeclassifica- duceanovelherbrecommendationmodelnamedNFFGRAM.
tionandprescriptionsuggestionaccuracy.Similarly,Leeetal. Thismodelcomprisessixdistinctmodules:fractal-basedweight
[12] utilized the Missforest method for dataset normalization K-nearestneighboralgorithm(FWKNKN),fractal-basedlinear
andlocalinterpretablemodel-agnosticinterpretationtoidentify neighbor similarity (FLNS), Gauss kernel similarity based on
and extract pivotal predictive features. Additionally, Li et al. fractal dimensions (FGSK), modified bipartite graph diffusion
[13]implementedaseq2seqmodelcomplementedbyacoverage (MBGD), gated recurrent self-attention mechanism (GRAM),
mechanism,whileLiuetal.[14]introducedtheTCMbertmodel, and dual augmentation at the granular level (DAGL). Our
designed to generate TCM prescriptions. These models have method,combiningthesealgorithmsforfeatureformation,ad-
demonstrated broad applicability in tasks requiring the pro- dresses both correlated and non-linear features, alongside a
cessingandgenerationofsemi-structuredsequences.However, mechanism for the information exchange between herb nodes
these models exhibit limitations in capturing multiple nonlin- and symptom nodes. This not only focuses on the herb rec-
ear high-order interactions among TCM entities. Furthermore, ommendationtaskbutalsostrengthenstheconfidencebetween
the inherent sparsity of prescription data may impede optimal predictedherbalmedicinesandsymptoms.Thedetailedcontri-
performance in large-scale prescription analysis and obstruct butionsareasfollows
a comprehensive examination of the complex interrelations 1) Weintegratethefractaldimensionintothelinearneighbor
amongdiverseentities. similarity(LNS)measure,allowingforanuancedassess-
(3) Methods based on graph representation learning: This mentofnonlinearfeaturesbetweenherbsandsymptoms.
approach primarily involves generating a low-dimensional Furthermore, by utilizing the modified Gauss kernel
representation and embedding of TCM entities for herbal similarity grounded in fractal principles and employing
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

3700 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
multi-featureminingandfusion,andinconjunctionwith
Recall@K =
|Recsym (h,K)¡ÉTruesym (h)|
(2)
the MBGD algorithm, our model can comprehensively |Truesym (h)|
discern potential correlations between herbs and symp-
2¡ÁPrecision@K¡ÁRecall@K
toms. F1?score@K = (3)
Precision@K+Recall@K
2) WeleveragethematrixFrobeniusnormandsparsityrate
todesignthelossfunctionanddeterminethegatingco- where Recsym (h,K) is the top K recommended herbs with
efficient.TheintroductionoftheGRAMemphasizesthe theformerKhighestpredictionscoresforspecifiedsymptoms,
herb-symptomrelationship,thusenhancingtheprecision Truesym (h)isthegroundtruthforthegivensymptomswithina
ofherbalrecommendations. prescription.Consequently,Precision@Ksignifiestheaccuracy
3) We present a refined herbs and symptoms confidence of correctly identifying the top-K herbs. Recall@K describes
scorefunction,whichissubsequentlytransformedusing the coverage of true herbs within the top-K recommendations.
theSoftMaxfunction.ByapplyingtheHadamardproduct TheF1-score@Kprovidesacomprehensiveevaluationofboth
ofmatricestwice,weamplifytheherb-symptomassocia- precisionandrecall.
tionatthegranularlevel,ensuringthattheNFFGRAMin-
tensivelyhighlightseachentrywithintheherb-symptom III. METHODS
heterogeneousnetworks.
Additionally, in our case study, we leverage contemporary A. ThePreliminaryofOurMethod
medicalknowledgeandnetworkpharmacologyinsightstoan- 1) Construction of a Multilayer Heterogeneous Graph Net-
alyze the effectiveness of recommended herbal medicines for work: Aheterogeneousnetwork,encompassingChineseherbal
specific symptoms. This involves examining the symptom tar- medicine, prescriptions, and symptoms, is built referencing
getsandpathwaysfacilitatedbyTCMprescriptions. TCMdatabases:SymMap[4],ETCM2.0[25],andHERB[3].
Inthis network, Ah signifies the interaction network of herbal
II. MATERIALSANDEVALUATIONMETRICS
medicine,Asrepresentsthesymptomassociationnetwork,andY
indicatestheinitialassociationnetwork.Thus,theprescription
A. Dataset data is structured into a three-layer heterogeneous graph net-
TCM1Dataset:WeutilizethebenchmarkTCMdataset[7], work:prescription-symptom-herb.Thisnetworkissubsequently
whichcomprises26360prescriptions,containing360symptoms mappedontothreeembeddedsubspaces:herb-herb,symptom-
and 753 herbs. These data are divided into 22917 for training symptom,andsymptom-herbassociationmatrixspaces.
and3443fortesting. 2) The Pipeline of NFFGRAM: Initially, matrices
TCM2 Dataset: We draw upon another benchmark TCM Ah, As,andY are recalculated to derive the herb-symptom
dataset[22],whichencompasses27012prescriptionswith390 association matrix, Ym, via FWKNKN. Next, the nonlinear
symptoms and 805 herbs, divided into 20259 for training and neighborhood similarity matrix AF h and AF s of herbs and
6753fortesting. symptoms are obtained by solving the optimization problem
withFLNS,inwhichAhandAsareinputs.Then,usingFGSK,
Gh and Gs matrices are derived from Ym, AF
h
and AF
s
,the
B. EvaluationMetrics
nonlinear multi-feature similarity information of herbs and
Toassessthepredictiveefficacyofourherb-symptomassoci- symptomsareintegratedtoobtainthecomprehensivesimilarity
ationmodelNFFGRAM,weconductpreliminaryexperiments matrices AI h and AI s , respectively. Subsequently, the MBGD
on the FWKNKN, FLNS, FGSK, and MBGD modules. We algorithmupdatesYmintotheherb-symptomassociationscore
(cid:2) (cid:2)
employ the AUC and AUPR metrics derived from a ten-fold matrix SH. Finally, the final prediction score matrix SHe is
cross-validation technique to evaluate the method¡¯s stability obtainedbyapplyingtheGRAMandDAGLalgorithmstothe
[23].WeadjusttheclassificationthresholdtocomputetheTrue correlation importance matrix of herb (symptom) to enhance
Positive Rate (TPR = TP/(TP + FN)) and False Positive Rate (cid:2) SH. The workflow and detailed process of NFFGRAM are
(FPR = FP/(TN + FP)), plotting an ROC curve to determine illustratedinFigs.2and3,respectively.
the AUC. Additionally, we construct a Precision-Recall (PR)
curve using TPR and the precision of various classification
B. Herb-SymptomAssociationMatrixCompletionUsing
outcomestocalculateAUPR.Here,TP,FP,TN,andFNdenote
FWKNKNAlgorithm
truepositives,falsepositives,truenegatives,andfalsenegatives,
Giventhesparsenatureoftheinitialherb-symptomassocia-
respectively.Furthermore,weusePrecision@K,Recall@K,and
tionmatrix,theenhancedweightedk-nearestneighboralgorithm
F1-score@K to assess the effectiveness of the top-K recom-
isemployedfordatapreprocessing.Itaimstouncoverpotential
mendations during the ultimate prescription recommendation
interactions and reweight the interaction probabilities of each
phase(GRAMandDAGL).ThePrecision@K,Recall@K,and
associationpairbetween0and1.
F1-score@K equations are defined in (1)¨C(3) [24], where K
representsthenumberofrecommendedherbs.
FromtheherbalassociationmatrixAh,foreachherbhi,the
similaritydistancebetweenherbsisdetermined.Thenonlinear
Precision@K =
|Recsym (h,K)¡ÉTruesym (h)|
(1)
s
re
im
la
i
t
l
i
a
o
r
n
ity
di
a
m
m
e
o
n
n
si
g
on
he
(
r
6
b
)
s
.
i
T
s
h
t
e
he
K
nc
h
o
e
m
rb
p
s
u
m
te
o
d
st
us
s
i
i
n
m
g
il
t
a
h
r
e
t
f
o
ra
t
c
h
t
e
a
m
lc
a
o
r
r
e
-
K
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3701
Fig.2. WorkflowoftheNFFGRAMmodel.
Fig.3. Multi-layerheterogeneousgraphnetworkconstructionandtherecommendedresearchpipelineofTCM.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

3702 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
identified, and the probability distribution of their interaction
with hi is inferred from the correlation score between these
herbsandsyndromes.Thecorrespondingcomputationformula
isasfollows:
1 (cid:2)K
Yh (hi,:) = ¦Øk Y (hk ,:), (4)
Qh h h
k =1
h
where¦Øk
h
=¦Çk h ?1 Ah (hi,hk
h
)
(cid:3)
istheweightcoefficient,¦Ç ¡Ü
1isthedecaycoefficient;Qh = K
k h =1
Ah (hi,hk
h
)isthereg-
ularizationterm.FromthesymptomaticassociationmatrixAs,
the likelihood distribution of interaction is calculated for each
Fig.4. Reconstructionofherb-herbassociationmatrixutilizingFLNS
symptomsi:
algorithm.
1 (cid:2)K
Ys (:,si ) = ¦Øk Y (:,sk ), (5) optimizationmodelisframedandsolved
Qs
k =1
s s (cid:4)
(cid:4)
(cid:4)
(cid:4)
(cid:4)
(cid:4)
(cid:4)
(cid:4)2
s (cid:4)(cid:4) (cid:3) (cid:4)(cid:4)
i
w
s
h
t
e
h
r
e
e
d
¦Ø
e
k
c
s
ay
=
c
¦Ç
o
k
e
s
f
?
fi
1
ci
A
en
s
t
(
;
s
Q
i,
s
sk
=
s ) (cid:3) is
K k
th
s =
e
1
w
A
ei
s
g
(
h
s
t
i,
c
s
o
k
e
s
f
)
fic
is
ie
t
n
h
t
e
,¦Ç
re
¡Ü
gu
1
-
m ¦Ø i i n¦Åi
=
=(cid:4) (cid:4) (cid:4) (cid:4) hi ? (cid:3)i j :h ij ¡ÊO(h
¦Ø
i )
i,
¦Ø
i j
i
G
,i j
i i j
h
,
i
i
j
l
(cid:4) (cid:4) (cid:4) (cid:4)
¦Øi,i d =¦Ø i T Gi¦Øi (7)
larizationterm. (cid:3)i j ,i d :h ij ,h id ¡ÊO(z i )
The symptom-herb association matrix Ym: (Ym )
ij
= l¡¤ s.t. ¦Øi,i
j
= 1, ¦Øi,i
j
¡Ý0, j = 1,2,¡¤¡¤¡¤ ,kh
(Y h +
2
Y s ) ij +(1?l)¡¤Yij is derived by employing the average i j :h ij ¡ÊO(h i )
valuesofYh andYs topopulatetherespectiveelementswithin whereO(hi )signifiestheclosestneighborofkh (0<kh <nh )
the herb-symptom association matrix, where l is the Boolean tohi,determinedviathefractalcorrelationdimension.hi isthe
j
coefficient. jthnearestneighborofhi,¦Øi,i isthesimilaritybetweenhiand
j
hi ,indicating thereconstruction contribution weight between
j
C. MiningHerb-SymptomSimilarityInformationUsing them. ¦Øi =(¦Øi,i 1 ,¦Øi,i 2 ,¡¤¡¤¡¤ ,¦Øi,i k )T and Gi = Gi i j ,i l , and
theFLNSAlgorithm ifhi
j
,hi
l
¡ÊO(hi ),Gi
i j ,i l
=(hi ?hi
j
)T (hi ?hi
j
),otherwise
The linear relationships between herbs and correlations be-
Gi
i ,i
= 0.
j l
tweensymptoms,areinsufficienttoreflecttheircomplexrela- To counter potential overfitting, the model incorporates a
tionships[26].Thefractaldescriptionofnonlinearrelationships Tikhonov regularization term to reduce the magnitude of the
offers natural advantages [28]. Accordingly, a linear neigh- standardweight¦Øi
borhood similarity (LNS) algorithm [27] is adapted, utilizing min¦Åi =¦Ø
i
T G i ¦Øi +¦Ë||¦Øi ||2 =¦Ø
i
T(G i+¦ËE)¦Øi, (8)
fractalstoreconfigurethedataforbothherb-herbandsymptom- ¦Ø i
symptomrelations. where ¦Ë is the regularization coefficient, and E represents the
Taking the herb association matrix as a reference, the herb- identity matrix. The weight matrix Wh ¡ÊRn h ¡Án hcan be ob-
symptomassociationnetworkisfirstmappedontotheherbspace tained as the FLNS matrix among herbs, denoted as AF. This
h
H. For any vector h = {hi,i = 1,2, ..., nh }¡ÊH, where processisgraphicallyrepresentedinFig.4.
nh denotes the number of herbs, the ns dimensional column Inparallel,ananalogousprocedureisappliedforsymptoms
vectorhi istransformedintonx ¡Ány ¡Öns,wherenx,ny are toretrievetheweightmatrixWs ¡ÊRn s ¡Án s,representedasthe
as close as possible to being equal. Subsequently, all matrices FLNSmatrixbetweensymptoms,anddenotedasAF.
s
are converted into the tensor structures. Each tensor layer is TodemonstratetheefficacyandsuperiorityoftheFLNSalgo-
characterized by fractal-dimension distances as a distinctive rithm,aten-foldcross-validationisconductedontheTCM1and
feature of herbal medicine to encapsulate the nonlinear asso- TCM2 datasets. Results are juxtaposed with the original LNS
ciations between herbs [28]. The fractal dimension formula is algorithm,whichutilizesEuclideandistanceandthecorrelation
presentedas coefficientmetric.Figs.5and6revealthattheAUCandAUPR
valuesderivedfromtheFLNSusingthefractaldimensionmetric
logN(I,r)
D(x) = ?lim (6) surpassedthoseoftheothertwomethods.
r¡ú0 logr
where r is the radius of the enclosure box, and N(I,r) is the D. TheFGSKAlgorithmandMulti-FeatureFusion
numberofboxescoveringthepointsetI. 1) TheFGSKAlgorithmforSimilarityMining: TheGaussian
Based on the distance matrix, the k-nearest neighbor set of kernelsimilarityoftencharacterizesthelikenessbetweendiverse
herbal medicine for the feature vector hi of the ith herb is datatypes.Thismethodleveragestheradialbasisprojectionof
obtained. To reconfigure hi,i = 1,2, ..., nh, a quadratic data in high-dimensional space to ascertain similarity weights
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3703
integrationofherbandsymptomsimilaritiesareexecuted
?
?AF h (h i ,h j )+
2
G h (h i ,h j ) , if AF
h
(hi,hj )(cid:8)=0
A I h (hi,hj )= ? Gh (hi,hj ), otherwise
(13)
?
?AF s (s i ,s j )+
2
G s (s i ,s j ) , if AF
s
(si,sj )(cid:8)=0
Fig.5. ComparisonoftheLNSalgorithmbythreedifferentmeasures A I s (si,sj )= ? Gs (si,sj ), otherwise
regardingAUCandAUPRforTCM1dataset.
(14)
E. MBGDAlgorithmforDiffusingInformationBetween
HerbsandSymptoms
The bipartite graph is a prevalent tool in recommendation
systems, facilitating resource exchange between herbal and
symptom nodes. The graph-based two-step diffusion process
comprises two core stages: constructing the diffusion weight
Fig.6. ComparisonoftheLNSalgorithmbythreedifferentmeasures matrix and implementing successive two-step diffusion proto-
regardingAUCandAUPRforTCM2dataset. cols. This study refines the bipartite graph diffusion algorithm
[29] to forecast the herb-symptom associations. As delineated
byHuangetal.[30],byusingasymptomnodeasareference,the
for each data point. While formulating the feature representa- initialfeaturediffusionprobabilitymatrixAv forthesymptom
tions, Gaussian kernel similarity becomes instrumental in de- isderivedbymappingthesimilarfeatureAs ofeachsymptom
termining the nonlinear associations of known herb-symptom sj onto the association probability matrix Ym. Similarly, by
relationships. mappingthecomprehensivesimilaritymatrixAhofherbstothe
Within the adjacency matrix Ym, the ith row depicts the association probability matrix Ym, the initial feature diffusion
interaction likelihood between herbal medicine hi and each probability matrix Ad for the herbs is achieved. These two
symptom, and the jth column signifies the interaction proba- initial matrices, which bridge the similarity data with proba-
bilitybetweensymptomsj andeveryherbalmedicine.Vectors bilitycorrelation, serve as thepreliminary diffusionweighting
Q(hi )andQ(sj )denotethefeaturevectorsoftheithrowvector
matrices during the graph diffusion, specifically denoted as
and the jth column vector as the Gaussian similarity kernel, Av =AI
s
¡¤Y
m
T, Ad =Y
m
T ¡¤AI
h
,whereY
m
T isthetransposition
respectively. We express the Gaussian kernel similaritymatrix ofYm.TheMBGDmethodisasfollows:
betweenherbhiandhjasGh,andtheGaussiankernelsimilarity Step 1, every symptom node allocates weights based on the
matrix between syndrome si and sj as Gs. The calculation correlation degree of its affiliated herbs and the newly formed
equationsare matricesAvandAd.Toclarify,herbnodespropagatethecorrela-
(cid:5) (cid:6)
tiondegreecapturedinAvandAdtotheirassociatedsymptoms
Gh (hi,hj ) = exp ?¦Âh ||Q(hi )?Q(hj )||2 , (9) using(15)
Gs (si,sj ) = exp (cid:5) ?¦Âs ||Q(si )?Q(sj )||2 (cid:6) , (10) SS(vi ) =¦Á¡¤ (cid:2) j n = h 1 (cid:3) n t= s 1 2 A A d d ( ( t i , , j j ) ) + ¡¤Y (cid:3)m T n j= ( h ? 1 , A j) d (i,j)
where +(1?¦Á) ¡¤ (cid:2) j n = h 1 (cid:3) n t= s 1 2 A A v v ( ( t i , , j j ) ) + ¡¤Y (cid:3)m T n j= ( h ? 1 , A j) v (i,j) ,
1 (cid:2)n h
¦Âh = ||Q(hi )||2 , (11) i = 1,2,...,ns (15)
nh
i=1 Here,Ad (i,j)andAv (i,j)representtheelementsoftheith
¦Âs = n 1 s (cid:2)n s ||Q(si )||2 , (12) r Y o m T w (? a , n j d ) j r t e h p c re o s l e u n m ts n t o h f e t j h th e c A o v lu a m nd n A ve d ct m or at o ri f ce Y s m T , . re ¦Á sp a e c c t t s iv a e s ly a ;
i=1
dampingfactortoharmonizetheinputfromAvandAd.
Step 2, drawing from the SS matrix obtained in the first
|¡¤|isthenormofthefractalassociationdimension.
step, the correlation degree of symptom nodes is retroactively
2) NonlinearMulti-FeatureFusion: Fromthepreviouslyout- channeledtothecorrelatedherbnodes.Thegoverningequations
linedsteps,twosimilaritymatricesforherbs(AF
h
andGh)and
are
c
a
sy
r
o
e
m m
a
p p
m
t r o e
a
m h
lg
e s n
a
(
m
s A iv
a
F s e
te
a
d
s n im
b
d
a
G i
s
la
e
s r
d
) it a y
o
r
n
e d o
t
a
h
b ta
e
ta
c
f i o n
o
r e
m
d N
p
,
l
F r
e
e F
m
s G p
e
e R
n
c
t
A t
a
iv
r
M
i
e
t
l
y
, y t .
p
h T
r
e
i
o s
n
e o
c
f
i
m f
p
e
l
a r
e
t
.
m r
T
i o c
h
e re
e
s (cid:2) SH(dj ) = ¦Â¡¤
k
(cid:2)n
=
s
1
(cid:3)
n t= h 1 A
2A
d (
d
k
(
,
k
t
,
)
j
+
)¡¤ (cid:3) SS
n k= s
(
1
vk
A
)
d (k,j)
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

3704 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
+(1?¦Â)¡¤ k (cid:2)n = s 1 (cid:3) n t= h 1 A 2A v ( v k ( , k t , ) j + )¡¤ (cid:3) SS n k= s ( 1 vk A ) v (k,j) , onthesy (cid:2) S m H pt e om (h - i h , e s r j b ) a = sso (cid:2) S c H iati ( o h n i, m sj a ) tr ¡¤ ix C (cid:2) S s H (hi b , y sj )¡¤
j = 1,2,¡¤¡¤¡¤ ,nh (16)
¡Ásoftmax
(cid:18) Cs(hi,sj ) (cid:19)
(19)
where¦Âservesasthedampingfactorbalancingthecontribution
|Rx(hi )|
be (cid:2) t S w H ee ( n dj A ) v is an fo d r A m d u . latedasanns ¡Á1dimensionalweightvec- t i o nd m ic s a j ti , ng w t h h e e re pro C b s a ( b h il i i , t s y j t ) hat = he |R rb x al ( m hi e ) d ¡É ic R in x e ( h s i j c ) a |/ n | t R re x a ( t s s j y ) m | p is -
tor, capturing the potential association of herbal medicine dj
theconfidencescoreforsymptom-herbassociations[29].Here,
for each symptom. (cid:2) SH = [(cid:2) SH(d1 ), (cid:2) SH(d2 ),¡¤¡¤¡¤ , (cid:2) SH(dn
h
)] st represents the tth symptom and hi represents the ith herb,
isthepredictionmatrixofsymptom-herbcorrelationinthens ¡Á Rx(hi ) represents the prescription containing hi, Rx(st ) rep-
nh dimension. resents the prescription containing st, |¡¤| is the number of
In cont(cid:3)rast to the ap(cid:3)proach in [3(cid:3)0], (15), (16) in- aset.
c (cid:3) orporate n j= h 1 Ad (i,j), n j= h 1 Av (i,j), n k= s 1 Ad (k,j) and When comparing TCM recommendations based on the
n k= s 1 Av (k,j) in denominators. This inclusion ensures that original, singularly-augmented, and doubly-augmented herb-
thedenominatoroftheinitialmethodcansidestepinstancesof symptom association matrices, the comparison results are dis-
zero,effectivelymitigatingthecoldstartchallengeprevalentin played in Figs. 7 and 8 using precision, recall, and F1-score.
recommendationsystems. Whetherthetop5,10,or20selectionsareconsidered,thedual
augmentationconsistentlydeliversimprovedresultsforboththe
F. GRAMAlgorithmforHerb-SymptomAssociation TCM1andTCM2datasets.
Prediction It is noteworthy that, from a broader perspective, the herbal
prescription recommendation model will significantly impact
The attention mechanism in neural networks serves as a
theTCMpractice.Itenablesresearcherstoanalyzelargedatasets
resource allocation scheme, prioritizing computing resources
ofTCMandsymptominformation,discoveringnewdrugcom-
formore criticaltasks and addressing theissueofinformation
binationsandtherapeuticeffects,whichcaninspiredrugdevel-
overload. We introduce the GRAM algorithm to enhance the
opment. Additionally, by leveraging AI and machine learning,
precisionofherbal-symptomassociationpredictions.
the model can uncover patterns and connections within TCM
Weobservethatherb-symptomassociationscorrelatesignifi-
theory,helpingtoverifyandrefineit.Thisdata-drivenapproach
cantlywiththematrix¡¯ssparsityandnorm.Consequently,aloss
promotesthemodernizationofTCM.
functionisestablishedby
(cid:10) (cid:5) (cid:6) (cid:5) (cid:6)(cid:10) (cid:5)(cid:10) (cid:10) (cid:10) (cid:10) (cid:6)
(cid:10) (cid:10) (cid:10) (cid:10) (cid:10) (cid:10)
L=(cid:10)RS (cid:2) SHt+1 ?RS (cid:2) SHt (cid:10) ¡¤ (cid:10)(cid:2) SHt+1 (cid:10) ?(cid:10)(cid:2) SHt (cid:10) IV. RESULTSANDDISCUSSION
F F
(cid:11) (17) We used MATLAB R2022A for programming,
where (cid:10)(cid:2) SHt (cid:10)
F
= (cid:3) n
i=
s
1
(cid:3) n
j=
h
1
|(cid:2) SHij | 2 refers to the Frobe- s
h
o
tt
u
p
r
s
c
:
e
//gith
c
u
o
b
d
.
e
c
s
om/h
an
h
d
l0313
d
9
at
/
a
NFF
a
G
re
RAM
fr
_
e
T
el
C
y
M.I
a
n
va
th
il
i
a
s
b
s
l
e
e
ction
at
,
nius norm of the association matrix obtained by the tth loop
weevaluatetheproposedNFFGRAMwithbaselinemethods.
(cid:2)
ofthematrix;RS representsthematrix¡¯ssparsityrate,SHt+1
The experiments are designed to demonstrate the effective-
denotestheassociationmatrixderivedfromthematrix¡¯s(t+1)th
nessofourmodel¡¯seffectivenessincapturingthehigher-order
self-attentionmechanismloop
and delicate interactive relationships, as addressed by the fol-
? (cid:5) (cid:6) ?
T lowingresearchquestions:
? (cid:2) SHt ¡¤ (cid:2) SHt ?
(cid:2) SHt+1 = softmax? ¡Ì ?¡¤(cid:2) SHt (18) RQ1. How do different modules of our model influence our
nh
approachperformance?
RQ2.Howdodifferenthyperparametersettingsaffectourmodel
wheresoftmax(¡¤)appliestheSoftMaxtransformationtoeach
performance?
rowvectorofthematrix. RQ3.Howdoesourapproachoutperformthestate-of-the-arton
Weestablishathreshold¦Ä,andtheself-attentionmechanism herbrecommendationtasks?
loop terminates if L is less than ¦Ä, subsequently outputting RQ4.Whatarethetheoreticalcontributionsofourstudy?
(cid:2)
the association prediction matrix SH after the loop of the RQ5.Canourapproachprovidereasonableherbrecommenda-
self-attentionmechanism. tionswithherb-symptommapping?
Itisworthnotingthatperformancevariationsacrossmodels
G. DAGLAlgorithmforHerb-SymptomAssociation
mainly result from dataset discrepancies. While TCM1 and
Enhancement
TCM2 datasets share a common origin [5], the TCM1 dataset
Tosimultaneouslyconsiderthediversityofherbaluseandthe undergoes additional standardization (synonym harmonization
relativeimportanceofsymptoms,afinalcorrelationmatrixcan andduplicateprescriptionremoval),enhancingconsistencyand
moreaccuratelyreflectthetreatmentpatternsandherbalefficacy reliability. This refinement fosters improved accuracy and ro-
intherealworld.weexecuteadualgranularlevelaugmentation bustnessinhandlingcomplexmedicaldata.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3705
Fig.7. Comparisonofherb-symptomassociationpredictedenhancementeffectsintheTCM1dataset.
Fig.8. Comparisonofherb-symptomassociationpredictedenhancementeffectsintheTCM2dataset.
TABLEI
ABLATIONSTUDYONTHETCM1DATASET
A. AblationExperiments(RQ1)
ToassesstherobustnessofNFFGRAM,weconductablation
| experiments.  | Model | 1 excludes  | the            | GRAM | module | from the |     |     |     |     |
| ------------- | ----- | ----------- | -------------- | ---- | ------ | -------- | --- | --- | --- | --- |
| full NFFGRAM, |       | while Model | 2 incorporates |      | only   | the FLNS |     |     |     |     |
andFGSKmatrixfusionwithMBGD,omittingtheFWKNKN
algorithm,andsubsequentlyemploystheGRAMmodule.Mod-
| els 3-4 utilize | a        | single similarity |          | matrix | (FGSK | and FLNS, |     |     |     |     |
| --------------- | -------- | ----------------- | -------- | ------ | ----- | --------- | --- | --- | --- | --- |
| respectively),  | followed | by                | the MBGD | and    | GRAM  | modules.  |     |     |     |     |
Fig.9. TheF1-scoreofeachmodelbytop5-20forTCM2dataset.
| Model 5   | integrates     | all three | similarity | matrices¡ªthe |          | original, |     |     |     |     |
| --------- | -------------- | --------- | ---------- | ------------ | -------- | --------- | --- | --- | --- | --- |
| FLNS, and | FGSK¡ªutilizing |           | Poleksic¡¯s | fusion       | strategy | [31].     |     |     |     |     |
This integrated matrix is fed into the MBGD network and stages, enhancing NFFGRAM¡¯s global predictive capabilities.
subsequentlyprocessedbytheGRAMlayer. Assuch,weconsidertheFWKNKNalgorithmtobeanintegral
1) Performance of Each Model: Table I presents the preci- component of NFFGRAM. When assessed at the top K = 5,
sion, recall, and F1-score for our method and other models at the performances of Models 3 and 4 are comparably matched
top K values of 5, 10, and 20. When compared to Model 1, withthoseofNFFGRAM.However,NFFGRAM¡¯ssuperiority
NFFGRAM exhibits a superior performance. The reason may isevidentatthetopKvaluesof10and20.Theamalgamationof
be that the GRAM module is influenced by both the change FLNSandFGSKmarkedlyaugmentsthemodel¡¯spredictions.In
in sparsity and the Frobenius norm of the matrix, while the contrast,inModel5,thesimilaritycombination¡¯sincorporation
|     |     |     |     |     |     |     | of the original | similarity matrix | amplifies | the informational |
| --- | --- | --- | --- | --- | --- | --- | --------------- | ----------------- | --------- | ----------------- |
attentionmechanismprimarilyconcentratesonpredictingherb-
symptomassociations.AgainstModel2,NFFGRAM¡¯smetrics redundancy, rendering its overall performance inferior to NF-
| are higher, | largely | because | the FWKNKN |     | algorithm | directs | FGRAM. |     |     |     |
| ----------- | ------- | ------- | ---------- | --- | --------- | ------- | ------ | --- | --- | --- |
probability association channels to herb or symptom nodes RegardingtheablationexperimentsfortheTCM2datasetin
lacking associated labels. This approach enables these nodes Fig.9,NFFGRAMoutperformsothermodelsintheF1-scoreat
topKvaluesof5through20.Thesefindingsareconsistentwith
| to access | diffusion | resources | in  | subsequent | graph | diffusion |     |     |     |     |
| --------- | --------- | --------- | --- | ---------- | ----- | --------- | --- | --- | --- | --- |
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore.  Restrictions apply.

3706 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
|     |     |     |     |     | Fig.13. | Thesensitivityanalysisof¦Áand¦ÂforTCM2dataset. |     |     |     |     |
| --- | --- | --- | --- | --- | ------- | -------------------------------------------- | --- | --- | --- | --- |
Fig.10. ThedifferencesinSRforablationstudy.
|                                                         |     |     |     |     | Fig. 14. | The performance | of comparison | methods | on  | the TCM2 |
| ------------------------------------------------------- | --- | --- | --- | --- | -------- | --------------- | ------------- | ------- | --- | -------- |
| Fig.11. SensitivityanalysisforparameterKunder10-foldCV. |     |     |     |     | dataset. |                 |               |         |     |          |
C. ComparisonWithOtherMethods(RQ3)
UsingtheTCM1andTCM2datasetsasbenchmarkdatasets,
|     |     |     |     |     | we juxtapose | NFFGRAM¡¯s | performance |     | with other | cutting- |
| --- | --- | --- | --- | --- | ------------ | --------- | ----------- | --- | ---------- | -------- |
edgetechniquesbyassessingvariousmodelperformancemet-
|     |     |     |     |     | rics to validate | its predictive | efficacy. | For   | the TCM1 | dataset, |
| --- | --- | --- | --- | --- | ---------------- | -------------- | --------- | ----- | -------- | -------- |
|     |     |     |     |     | we benchmark     | NFFGRAM        | against   | SMGCN | [20],    | and KG-  |
ASMGNN[32].FortheTCM2dataset,webenchmarkagainst
Fig.12. Thesensitivityanalysisof¦Áand¦ÂforTCM1dataset.
|     |     |     |     |     | state-of-the-art | methods             | such as | SMGCN       | [20], KDHR | [22], |
| --- | --- | --- | --- | --- | ---------------- | ------------------- | ------- | ----------- | ---------- | ----- |
|     |     |     |     |     | SMRGAT           | [33], and PresRecST |         | [34]. Their | advantages | and   |
thoseobservedintheTCM1dataset,affirmingtheessentiality
disadvantagesareshowninTableII.
ofeachNFFGRAMmodule.
|                |                  |             |                |     | 1) Performance | Comparison: | The       | experimental | results    | for  |
| -------------- | ---------------- | ----------- | -------------- | --- | -------------- | ----------- | --------- | ------------ | ---------- | ---- |
| 2) Sparsity    | Rate (SR) of     | Each Model: | To demonstrate | the |                |             |           |              |            |      |
|                |                  |             |                |     | the TCM1       | dataset are | displayed | in Table     | III, where | P@K, |
| impact of each | module on matrix | completion, | we evaluate    | the |                |             |           |              |            |      |
R@K,andF1@KstandasabbreviatedformsforPrecision@K,
SRofeachmodel,asdetailedinFig.10.TheoriginalSRsare
Recall@K,andF1-score@K.Theprecision,recall,andF1-score
| 0.8709 and | 0.8728, respectively. | We find | that each module | is  |     |     |     |     |     |     |
| ---------- | --------------------- | ------- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
forNFFGRAMconsistentlyoutperformthoseofothermethods.
importanttoreducetheSRsto0.0472and0.0513,respectively,
|            |                         |          |              |        | In contrast | to both SMGCN         | and           | KG-ASMGNN, | NFFGRAM        |     |
| ---------- | ----------------------- | -------- | ------------ | ------ | ----------- | --------------------- | ------------- | ---------- | -------------- | --- |
| indicating | that the final matrices | for both | datasets are | nearly |             |                       |               |            |                |     |
|            |                         |          |              |        | accounts    | for the co-occurrence | relationships |            | and confidence |     |
complete.
scoresbetweenherbsandsymptoms.Moreover,itincorporates
|     |     |     |     |     | the element-level | product, | enhancing | the | model¡¯s expressive- |     |
| --- | --- | --- | --- | --- | ----------------- | -------- | --------- | --- | ------------------- | --- |
B. ParametricSensitivityAnalysis(RQ2)
nessandadaptability.Notably,GRAMeffectivelyvalidatesthe
We also scrutinize the impact of key parameters on NFF- intricateprocessofsymptominduction.
GRAM¡¯s performance. The default values of the parameters FortheTCM2dataset,Fig.14delineatesthecomparativere-
are set as follows: K = 9, ¦Á = 0.1, and ¦Â = 0.6. Moreover, sults.ItisevidentthatNFFGRAMexcelsoverothertechniques,
each parameter is tested in isolation while keeping the other andthesecond-bestmethodisSMRGAT.Thisunderscoresour
parametersconstant.Usingaten-foldcross-validationapproach method¡¯sadeptnessatcapturingsymptomandherbfeaturesand
repeated ten times, we derive an average value to serve as the theirintricateinterrelations.
final evaluation metric. Through this comparative process, the While both SMGCN and KDHR address the interactivity
optimalperformanceparametersareidentified. between symptoms and herbs, SMGCN lags behind KDHR,
We examine the neighborhood parameter K within the potentially due to its limited external herb knowledge. SMR-
FWKNKN algorithm from 1 to 10. As illustrated in Fig. 11, GATemphasizestheinherentcontextualnuancesofsymptoms
themaximumvaluesoftheAUCandAUPRareobtainedatK and the varied impact levels of different herbs on designated
| =4. |     |     |     |     | symptoms.Ourmethodologyshinesasitholisticallyembraces |     |     |     |     |     |
| --- | --- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- | --- |
For the MBGD algorithm, the parameters ¦Á and ¦Â dictate multiple nonlinear attributes of herbs and symptoms, further
theweightscoredistributionduringthediffusionstep.Both¦Á bolstered by the integration of GRAM and DAGL algorithms
and ¦Â vary between 0.1 and 1, increasing with a step of 0.1. forherb-symptomcorrelation.
AsdemonstratedinFigs.12and13,boththeAUCandAUPR 2) ExternalValidationonanIndependentDataset: Toassess
values for TCM1 and TCM2 datasets decrease as ¦Â ascends, thegeneralizabilityofNFFGRAM,weconstructanindependent
withthehighestvaluesobservedat¦Â =0.1. dataset,theTyphoiddataset,whichcomprises258prescriptions
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore.  Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3707
TABLEII
COMPARISONOFOTHERMETHODSANDOURSINTERMSOFADVANTAGES,DISADVANTAGES,TIMECOMPLEXITY,ANDKEYMETRICS
TABLEIII
PERFORMANCEOFCOMPARISONMODELSANDOURMETHODONTHETCM1DATASET
Fig.15. Theperformanceradarchartoftheindependentdataset. Fig.16. Thecorrelationcoefficientsandt-testvaluescomparedforthe
TCM2dataset.
sourcedfromtwomedicaltexts,¡®TreatiseonColdDisease¡¯and
¡®SynopsisofGoldenChamber¡¯.Thisdatasetincludesstandard- function where N represents the number of nodes, D indicates
ized terminology for 185 herbs and 280 symptoms, divided thefeaturedimensionofthenode.
into 220 for training and 38 for testing. The precision, recall, 4) Correlation Coefficients and Significance Test: To sub-
andF1-scoreofNFFGRAMaresuperiorcomparedwithother stantiateourclaimsofsuperiority,wetestthestatisticalsignifi-
methods,asshowninFig.15. canceoftheTCM2dataset.Fig.16(left)depictsthecorrelation
3) TimeComplexityComparison: Weanalyzethetimecom- coefficientsbetweenthepredictedherb-symptomscorematrices
plexity of several algorithms, as presented in Table II. The generatedbyeachmethodandtheoriginalherb-symptomma-
time complexity of NFFGRAM is O(N2¡¤D), expressed as a trix.Withasignificancethresholdof(cid:2)r(cid:2)>0.10(givenn=390),
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

3708 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
D. MotivationforCombiningTheseMethods(RQ4)
Theoverallperformancesofexistingmethodsaresuboptimal,
largely due to two reasons: first, the complexities of the TCM
recommendationtask.Unliketypicalrecommendationsystems,
every prescription may include multiple herbs and numerous
waystocombinethem;second,theassociationsbetweenherbs
andsymptomsarecharacterizedbyhighsparsity.
Insummary,themethodologyentailssophisticatedextraction
and merging of features (FWKNKN), addressing both inter-
dependent and nonlinear characteristics (FLNS and FGKS),
while facilitating a communication process (MBGD) between
herbal and symptom nodes. It focuses not only on suggesting
Fig.17. VenndiagramandPPInetworkdiagram. appropriate herbs (GRAM) but also on enhancing the reliabil-
ity of the connections between predicted herbal remedies and
theircorrespondingsymptoms(DAGL).Therefore,ourmethod
outperformsothermethods.
E. CaseStudy(RQ5)
In this section, a case study is presented to validate the
feasibilityofNFFGRAM.
1) HerbRecommendationResults: TableIVprovidesacon-
creteexamplewithintheherbrecommendationcontext.Given
a set of symptoms, NFFGRAM suggests a corresponding set
of herbs for treatment. In the ¡®Herb set¡¯ column, items in red
font indicate herbs that are common to both the NFFGRAM
recommendation and the reference standard. For the actual
Fig.18. GOenrichmentanalysis.
prescription consisting of eight herbs, as sourced from ¡®The
Dictionary of TCM¡¯, our method¡¯s first eight suggested herbs
matchsixfromthereference,yieldingprecisionandrecallrates
of75%.
2) Target Interaction Analysis: To further assess the in-
hibitoryimpactoftheconstituentsinthesuggestedprescription
onthetargetsymptom,weobtainallthetargetsoffoursymp-
tomsandeightherbsfromtheSymMap[4]database,Fig.17¡¯s
leftVenndiagramillustratestargetoverlapsamongactualpre-
scriptions,recommendationsbyNFFGRAM,andrelevantsyn-
dromes.Theyellow,cyan,andpurpleellipsesrepresenttargets
of the actual prescription, NFFGRAM, and syndrome-linked
targets, respectively; gray, red, and blue areas indicate over-
laps:actualvs.recommended,actualvs.syndrome,andrecom-
Fig.19. KEGGenrichmentanalysis. mendedvs.syndrome.Greenhighlightstargetscommontoall
three.Fig.17¡¯srightfurtherexploresthesezones(dashed-ellipse
our analysis focus on determining linear correlation. Remark- area in Fig. 17¡¯s left), illustrating target connections through
ably, the NFFGRAM method exhibits the highest correlation networkpharmacology.UsingtheSTRINGtool[35],webuilt
value of 0.5116, exceeding those of other methods [20], [22], a PPI network that highlights these inter-target relationships.
[33],[34]. ThePPInetworkdemonstratesthepotentialinterferenceamong
Tovalidatetherobustnessofthesecorrelations,asignificance recommended herb targets, actual herb targets, and disease
analysis t-test is conducted. This test is applied to correlation targets. Node sizes reflect their connectivity, indicating that
coefficients exceeding 0.10 (because our dataset¡¯s size of 390 larger nodes, by interacting with many targets, are potentially
yields 388 degrees of freedom), ensuring they represent sub- integraltodiversebiologicalprocessesandsignalingpathways.
stantialassociationsratherthanrandomoccurrences.At-value Blue and red nodes emphasize therapeutic variations between
exceeding 1.90 indicates a less than 0.05 probability that the distinctTCMprescriptions,highlightingtheirsharedcapability
resultsareduetochance.Fig.16¡¯srightpanelshowsthecorre- toalleviatesymptomatologybytargetingthesekeyproteins.
spondingt-valuesforr-valuesabove0.1,allofwhichsurpassthe Thesetargetsaredemonstratedtobestronglyassociatedwith
1.90threshold,therebyconfirmingthatthedepictedcorrelations thesymptoms,indicatingthattheherbcombinationhasagood
arestatisticallysignificantandnotmerelycoincidental. therapeuticeffectondiseases[2],[36].
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3709
Fig.20. TheKEGGcancerpathway.
TABLEIV
THEHERBRECOMMENDATIONCASE
3) GO Enrichment Analysis: Fig. 18 presents the results of showingthattheherbalformulacanplayatherapeuticroleby
the GO enrichment analysis for targets influenced by the in- affecting the targets in the pathway [38]. Targets associated
gredientsintherecommendedherbalformula.Withinthese15 with these pathways include Lipid and atherosclerosis, Toxo-
biologicalprocesses,suchasresponsetocold,negativeregula- plasmosis, Apoptosis, Salmonella infection, and Hepatitis B,
tionofneuronapicalprocess,andresponsetotoxicsubstance, most of which are implicated in cancer pathways. Notably, 10
there is a notable concentration of targets. This concentration targetsareconcentratedinthelungcancerpathway.Patientswith
suggeststhattheproposedChinesemedicineprescriptionmod- advanced-stagecanceroftenexhibitsymptomslikespontaneous
ulates various biological pathways to exert therapeutic effects sweatingandnightsweatingandmayprogressivelyloseweight
onsyndromes[37].Fig.19depictstheinitial15signalingpath- due to disease complications. Thus, we investigate the cancer
ways enriched and identified by the KEGG pathway analysis, pathwayrelevanttothissymptomset,suggestingthattheTCM
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

3710 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
prescriptioncanexerttherapeuticeffectsbymodulatingtargets FacingthechallengesexistingintheTCMfield,itiscrucial
within this pathway [35], as illustrated in Fig. 20. From the tostrengthencooperationwithotherrelatedspecialties,suchas
perspectiveoftraditionalTCMdiagnosisandtreatment,theun- clinicalmedicineandpharmacology.Throughmultidisciplinary
derlyingcauseofsymptomslikenightsweatingandspontaneous teamwork,knowledgeexchangeandsharingcanbepromotedto
sweating is identified as a combined deficiency of Qi and Yin jointlydriveanevidence-basedpersonalizedmedicinepractice
()inpatients.ThesuggestedTCMtreatmentapproachencom- forward.Inthefuture,ourresearchwillfocusonexpandingthe
passesstrategiessuchassupplementingQiandnourishingYin scope of NFFGRAM by incorporating a more comprehensive
(), clearing heat and resolving phlegm (). Our recommended set of biomedical data, including genetic, epigenetic, and en-
herbssuchasginseng,largeheadatractylodes,poriacocos,and vironmental factors, to enhance the model¡¯s ability to capture
glycyrrhizauralensisarethekeyherbsinthistreatmentprotocol individualpatientdifferences.Thisapproachwillnotonlyim-
[29]. Additionally, Chinese angelica is an important Chinese provetheaccuracyofherb-symptomassociationpredictionsbut
medicineforthetreatmentofscrofula[25],[39].Inconclusion, alsofacilitatethedevelopmentofpersonalizedtreatmentplans
theevidenceunderscorestheefficacyofourrecommendedTCM thatarebettertailoredtoeachpatient¡¯suniquehealthprofile.
prescription.
REFERENCES
V. CONCLUSIONANDFUTUREWORK [1] B.Heetal.,¡°ASGARDisasingle-cellguidedpipelinetoaidrepurposing
ofdrugs,¡±NatureCommun.,vol.14,no.1,pp.993¨C1006,Feb.2023.
A. Conclusion [2] Q.Niuetal.,¡°TCMFP:Anovelherbalformulapredictionmethodbased
onnetworktarget¡¯sscoreintegratedwithsemi-supervisedlearninggenetic
The efficacy of most existing herb recommendation ap- algorithms,¡±Brief.Bioinf.,vol.24,no.3,May2023,Art.no.bbad102.
proachesisunderminedbythesparsenatureofherb-symptom [3] S.S.Fangetal.,¡°HERB:Ahigh-throughputexperiment-andreference-
guided database of traditional Chinese medicine,¡± Nucleic Acids Res.,
associationdata.Toaddressthisissue,themethodology intro-
vol.49,no.D1,pp.D1197¨CD1206,Jan.2021.
ducedinthisstudyinitiallyutilizestheFWKNKNalgorithmto [4] Y.Wuetal.,¡°SymMap:AnintegrativedatabaseoftraditionalChinese
refinetheprimaryadjacencymatrixofherb-symptomassocia- medicineenhancedbysymptommapping,¡±NucleicAcidsRes.,vol.47,
no.D1,pp.D1110¨CD1117,Oct.2019.
tions.Subsequently,alinearneighborhoodsimilarityalgorithm,
[5] L. Yao, Y. Zhang, B. Wei, W. Zhang, and Z. Jin, ¡°A topic modeling
based on the fractal dimension metric, is developed to recon- approach for traditional Chinese medicine prescriptions,¡± IEEE Trans.
structherb-symptomsimilarity.Itisfurtherintegratedwiththe Knowl.DataEng.,vol.30,no.6,pp.1007¨C1021,Jun.2018.
[6] W.Zhouetal.,¡°FordNet:RecommendingtraditionalChinesemedicine
similarity matrix derived from the Gaussian kernel similarity
formulaviadeepneuralnetworkintegratingphenotypeandmolecule,¡±
algorithmtorestructurebothherbandsymptommatrices.Inthe Pharmacol.Res.,vol.173,Nov.2021,Art.no.105752.
thirdphase,potentialherb-symptomassociationsarepredicted [7] X.Wang,Y.Zhang,X.Wang,andJ.Chen,¡°Aknowledgegraphenhanced
topicmodelingapproachforherbrecommendation,¡±inProc.Database
byimplementingamodifiedbipartitegraphdiffusioncombined
Syst.Adv.Appl.,24thInt.Conf.,2019,pp.709¨C724.
with a gated recurrent self-attention mechanism. Finally, dual [8] F.Lin,J.Xiahou,andZ.Xu,¡°TCMclinicrecordsdataminingapproaches
element-levelenhancementsareapplied,leveragingconfidence basedonweighted-LDAandmulti-relationshipLDAmodel,¡±Multimedia
ToolsAppl.,vol.75,pp.14203¨C14232,Apr.2016.
scores associated with herbs and symptoms. Extensive testing
[9] Y.Yaoetal.,¡°Anontology-basedartificialintelligencemodelformedicine
and comparative analyses on two datasets demonstrate the ef- side-effectprediction:TakingtraditionalChinesemedicineasanexample,¡±
fectivenessandsuperiorityoftheNFFGRAMapproach. Comput.Math.MethodsMed.,vol.8617503,pp.1¨C7,Oct.2019.
[10] G.S.U.AhmedandJ.C.L.U.Yun,¡°EANDC:Anexplainableattention
network based deep adaptive clustering model for mental health treat-
B. LimitationandFutureWork ment,¡±FutureGener.Comput.Syst.,vol.130,pp.106¨C113,May2022.
[11] Q. Zhang, C. Bai, L. T. Yang, Z. Chen, P. Li, and H. Yu, ¡°A unified
DespiteNFFGRAMhassomeadvantagesandsuperiority,it smartChinesemedicineframeworkforhealthcareandmedicalservices,¡±
IEEE/ACM Trans. Comput. Biol. Bioinf., vol. 18, no. 3, pp.882¨C890,
alsohassomelimitations.Firstly,ouradoptedmodelsimplifies
May/Jun.2021.
TCM¡¯scomplexity,potentiallyoverlookingsubtlepathophysio- [12] W.Y.Lee,Y.Lee,S.Lee,Y.W.Kim,andJ.H.Kim,¡°Amachinelearning
logicalnuances.Toremedythislimitation,futureworkwillin- approachforrecommendingherbalformulaewithenhancedinterpretabil-
ity and applicability,¡± Biomolecules, vol. 12, no. 11, pp.1604¨C1616,
volveexploringmoreintricatemodelstobetterreplicateTCM¡¯s
Oct.2022.
multidimensionalnature,integratingmoretypesofbiomedical [13] W. Li and Z. Yang, ¡°Exploration on generating traditional Chinese
data,consideringindividualpatientdifferences,andthedifferent medicine prescription from symptoms with an end-to-end method,¡± in
Proc.NaturalLang.Process.Chin.Comput.,2019,pp.486¨C498.
developmentalstagesofdiseases.
[14] Z. Liu et al., ¡°A novel transfer learning model for traditional herbal
Secondly, the process of matrix completion may introduce medicineprescriptiongenerationfromunstructuredresourcesandknowl-
noise,whichcanaffectthequalityandaccuracyofthedataand edge,¡±Artif.Intell.Med.,vol.124,Feb.2022,Art.no.102232.
[15] H.Liuetal.,¡°AnetworkrepresentationapproachforCOVID-19drug
predictions.Todevelopeffectivenoisereductionstrategies,we
recommendation,¡±Methods,vol.198,pp.3¨C10,Feb.2022.
plantoexploreandimplementadvancedsignalprocessingtech- [16] W.Zhaoetal.,¡°TCMherbalprescriptionrecommendationmodelbased
niquesandstatisticallearningmethodstoidentifyandeliminate on multi-graph convolutional network,¡± J. Ethnopharmacol., vol. 297,
Oct.2022,Art.no.115109.
irrelevantorerroneousinformationpoints.
[17] X. Dong et al., ¡°TCMPR: TCM prescription recommendation based
Finally, longitudinal studies are planned to analyze the dy- on subnetwork term mapping and deep learning,¡± in Proc. IEEE
namicsofmatricesandscoresovertime,aimingtoenhancetheir Int. Conf. Bioinf. Biomed., Houston, TX, USA, Dec. 9¨C12, 2021,
pp.3776¨C3783.
predictivepowerfordiseaseprogressionandtherapyoutcomes,
[18] C.Ruan,J.Ma,Y.Wang,Y.Zhang,andY.Yang,¡°Discoveringregularities
thereby bolstering the evidentiary foundation for personalized fromtraditionalChinesemedicineprescriptionsviabipartiteembedding
treatmentstrategies. model,¡±inProc.IJCAI,2019,vol.8,pp.3346¨C3352.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.

HUetal.:NFFGRAM:NONLINEARMULTI-FEATUREFUSIONANDGATEDRECURRENTSELF-ATTENTIONMECHANISM 3711
[19] C.Shi,B.Hu,W.X.Zhao,andP.S.Yu,¡°Heterogeneousinformation [30] Y. A. Huang, Z. H. You, X. Chen, Z. A. Huang, S. Zhang, and G. Y.
networkembeddingforrecommendation,¡±IEEETrans.Knowl.DataEng., Yan,¡°Predictionofmicrobe-diseaseassociationfromtheintegrationof
vol.31,no.2,pp.357¨C370,Feb.2019. neighborandgraphwithcollaborativerecommendationmodel,¡±J.Transl.
[20] Y.Jin,W.Zhang,X.He,X.Wang,andX.Wang,¡°Syndrome-awareherb Med.,vol.15,no.1,pp.1¨C11,Oct.2017.
recommendationwithmulti-graphconvolutionnetwork,¡±inProc.36thInt. [31] A.Poleksic,¡°Overcomingsparsenessofbiomedicalnetworkstoidentify
Conf.DataEng.,2020,pp.145¨C156. drugrepositioningcandidates,¡±IEEE/ACMTrans.Comput.Biol.Bioinf.,
[21] Y.Jin,W.Ji,Y.Shi,X.Wang,andX.Yang,¡°Meta-pathguidedgraph vol.19,no.4,pp.2377¨C2384,Jul./Aug.2022.
attention network for explainable herb recommendation. Health infor- [32] Y. Jin, W. Ji, W. Zhang, X. He, X. Wang, and X. Wang, ¡°A KG-
mationscienceandSystems,¡±HealthInf.Sci.Syst.,vol.11,Jan.2023, enhancedmulti-graphneuralnetworkforattentiveherbrecommendation,¡±
Art.no.5. IEEE/ACMTrans.Comput.Biol.Bioinform.,vol.19,no.5,pp.2560¨C2571,
[22] Y.Yang,Y.Rao,M.Yu,andY.Kang,¡°Multi-layerinformationfusion Sep./Oct.2022.
basedongraphconvolutionalnetworkforknowledge-drivenherbrecom- [33] X. Yang and C. Ding, ¡°SMRGAT: A traditional Chinese herb recom-
mendation,¡±NeuralNetw.,vol.146,pp.1¨C10,Feb.2022. mendationmodelbasedonamulti-graphresidualattentionnetworkand
[23] N.Q.K.Le,D.T.Do,T.T.Nguyen,andQ.A.Le,¡°Asequence-based semantic knowledge fusion,¡± J. Ethnopharmacol., vol. 315, Oct. 2023,
predictionofKruppel-likefactorsproteinsusingXGBoostandoptimized Art.no.116693.
features,¡±Gene,vol.787,Jun.2021,Art.no.145643. [34] X.Dongetal.,¡°PresRecST:Anovelherbalprescriptionrecommendation
[24] Q.H.Kha,V.H.Le,T.N.K.Hung,N.T.K.Nguyen,andN.Q.K.Le, algorithmforreal-worldpatientswithintegrationofsyndromedifferentia-
¡°Developmentandvalidationofanexplainablemachinelearning-based tionandtreatmentplanning,¡±J.Amer.Med.Inform.Assoc.,vol.31,no.6,
prediction model for drug-food interactions from chemical structures,¡± pp.1268¨C1279,Apr.2024.
Sensors,vol.23,pp.3962¨C3978,Apr.2023. [35] D.Szklarczyketal.,¡°TheSTRINGdatabasein2023:Protein-proteinas-
[25] Y.Zhangetal.,¡°ETCMv2.0:Anupdatewithcomprehensiveresourceand sociationnetworksandfunctionalenrichmentanalysesforanysequenced
richannotationsfortraditionalChinesemedicine,¡±ActaPharm.SinicaB, genomeofinterest,¡±NucleicAcidsRes.,vol.51,no.D1,pp.D638¨CD646,
vol.13,no.6,pp.2559¨C2571,Jun.2023. Jan.2023.
[26] F.WangandC.Zhang,¡°Labelpropagationthroughlinearneighborhoods,¡± [36] D.Zhangetal.,¡°Networkpharmacologysuggestsbiochemicalrationale
IEEETrans.Knowl.DataEng.,vol.20,no.1,pp.55¨C67,Jan.2008. fortreatingCOVID-19symptomswithatraditionalChinesemedicine,¡±
[27] G.Xieetal.,¡°DRPADC:Anoveldrugrepositioningalgorithmpredicting Commun.Biol.,vol.3,Aug.2020,Art.no.666.
adaptivedrugsforCOVID-19,¡±Comput.Chem.Eng.,vol.166,pp.1¨C12, [37] S.GuandL.Lai,¡°Associating197Chineseherbalmedicinewithdrug
Aug.2022. targetsanddiseasesusingthesimilarityensembleapproach,¡±ActaPhar-
[28] E.A.AlgehyneandM.Ibrahim,¡°Fractal-fractionalordermathematical macologicaSinica,vol.41,no.3,pp.432¨C438,Sep.2020.
vaccinemodelofCOVID-19undernon-singularkernel,¡±Chaos,Solitons [38] L.Yangetal.,¡°Targetingcancerstemcellpathwaysforcancertherapy,¡±
Fractals,vol.150,Sep.2021,Art.no.111150. SignalTransduct.Target.Ther.,vol.5,Feb.2020,Art.no.8.
[29] D.Buetal.,¡°FangNet:MiningherbhiddenknowledgefromTCMclinical [39] Z.Wangetal.,¡°AstudyontheregularityofancientTCMprescriptions
effective formulas using structure network algorithm,¡± Comput. Struct. ofexternaldrugsfortuberculouslymphadenitis,¡±Chin.ExternalMed.,
Biotechnol.J.,vol.19,pp.62¨C71,Feb.2021. vol.26,no.11,pp.164¨C168,Jul.2020.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 08:03:38 UTC from IEEE Xplore. Restrictions apply.
