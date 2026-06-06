3736 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
SDPR: Prescription Recommendation With
Syndrome Differentiation in Traditional
Chinese Medicine
Wenjing Yue , Wendi Ji , Xinyu Wang , Xin Ma , Pengfei Wang , and Xiaoling Wang
Abstract〞Prescription recommendation is critical for prescription retrieval, confirming the strength of the four-
clinical decision support in Traditional Chinese Medicine partitegraphparadigm.Ourbroadergoalistoadvancethe
(TCM),aimingtorecommendaherbsetbasedonapatient＊s intelligentdevelopmentofTCMinhealthcare.
symptoms. The core principle of TCM clinical practice,
treatment based on syndrome differentiation (SD), follows Index Terms〞Prescription recommendation, traditional
afour-stepprogressiveprocess:symptomstosyndromes, Chinesemedicine,healthcare,contrastivelearning,graph
therapeuticmethods,andherbs.However,existingmodels convolutionnetwork,multi-tasklearning.
oversimplifythisprocessbyoverlookingtherapeuticmeth-
ods, directly mapping symptoms to herbs or syndromes
to herbs, resulting in information loss and reducing the I. INTRODUCTION
effectivenessofrecommendedprescriptions.Furthermore,
the implicit, sparse, and many-to-many relationships be- TRADITIONAL Chinese Medicine (TCM) is an ancient
tween syndromes and therapeutic methods, coupled with medical system renowned globally for its healthcare and
the nonlinear interactions between therapeutic methods rehabilitation benefits [1]. It is also the foundation of many
and herbs, further hinder the modeling of the complete traditional medicine systems across many countries like Japan
SD process. To address these challenges, we propose a andKorea[2].Thetheoryof※treatmentbasedonsyndromedif-
novel four-partite graph paradigm that explicitly models ferentiation§(SD)iscentraltoTCMclinicaldiagnosis,provid-
thefourkeycomponentsofSDandtheirinteractions,pre-
ingfundamentalguidelinesforprescribingherbs[3].TCMhas
servingcriticalinformationateachstepandaligningmore
amassedsubstantialmedicalrecordsfromrenownedphysicians,
closely with clinicians＊ decision-making logic. Building on
containing a wealth of herb prescribing experience grounded
this, we develop SDPR, an SD-based prescription recom-
in SD [4]. However, the lack of standardization in medical
mendationmodelcomprisingfourmodulesalignedwithall
SDsteps.Then,weintegratedthemintoamulti-tasklearn- records and the inherent ambiguity of physicians＊ clinical ex-
ingframeworktofullycapturetheprogressiveprescription periences have resulted in a limited number of record data
process. To handle the implicit and complex relationships thatthoroughlydocumentherbprescribingexperiencesaligned
among syndromes, therapeutic methods, and herbs, we with SD logic [5]. Generally, a TCM medical record contains
introduce a syndrome-induced pre-training strategy and a apatient＊ssymptomsetandacorrespondingherbset[6].This
therapeuticmethod-awarecontrastivelearningframework. situationchallengesTCMphysicianswhoaimtoanalyzethese
Extensive experiments on public and real-world datasets
experiencesandintegratethemintotheirprescribingdecisions.
validateSDPR＊seffectivenessinherbrecommendationand
To address this problem, researchers propose prescription rec-
ommendation models that analyze patterns between symptom
Received 7 August 2024; revised 29 November 2024; accepted setsandherbsetsinTCMmedicalrecordsratherthanfocusing
27December2024.Dateofpublication14January2025;dateofcurrent ona singleuser＊spreferences liketraditionalrecommendation
version 7 May 2025. This work was supported in part by the NSFC models.Whenasymptomsetisinput,themodelcanautomati-
underGrant62136002,inpartbytheMinistryofEducationResearch
callyrecommendappropriateherbsorretrievesimilarprescrip-
JointFundunderGrant8091B042239,inpartbyShanghaiKnowledge
Service Platform Project under Grant ZF1213, and in part by Shang- tions from the historical medical record database. It provides
haiTrustedIndustryInternetSoftwareCollaborativeInnovationCenter. TCMphysicianswithreferencestoassistinmakingprescribing
(Correspondingauthor:XiaolingWang.) decisions.
WenjingYueiswiththeSchoolofComputerScienceandTechnology,
WeusetheclassicandartificiallystandardizedTCMmedical
EastChinaNormalUniversity,Shanghai 200061, China,alsowiththe
record,※MajorBupleurumDecoction§,asanexampleinFig.1to
Shanghai Institute of AI for Education, East China Normal University,
Shanghai 200061, China, and also with the Shanghai Institute of In- demonstratethefour-stepofSDandtheirimportanceinthepro-
telligentScienceandTechnology,TongjiUniversity,Shanghai 201210, gressiveTCMherbprescribingprocess.1)SymptomCollection.
China. First,theTCMphysiciangathersthepatient＊ssymptoms.Inthis
Wendi Ji is with the Data Intelligence and Computational Law Lab-
case,thesymptomsetincludesfivesymptomslike※wiryforceful
oratory, East China University of Political Science and Law, Shanghai
201620,China. pulse§ and ※constipation.§ 2) Syndrome Induction (SI). After
XinyuWang,PengfeiWang,andXiaolingWangarewiththeSchool analyzingthesymptoms,thephysicianinductsasyndromebased
of Computer Science and Technology, East China Normal University, on all symptoms. Thus, the TCM term ※syndrome§ represents
Shanghai200061,China(e-mail:xlwang@cs.ecnu.edu.cn).
acomprehensiveassessmentofasymptomset.Inthiscase,the
XinMaiswiththeShanghaiSkinDiseaseHospital,InstituteofDerma-
physicianidentifiesthesyndromewithfivesymptomsas※Lesser
tology,SchoolofMedicine,TongjiUniversity,Shanghai200443,China.
DigitalObjectIdentifier10.1109/JBHI.2025.3525507 Yang and Yang Brightness Combination Disease§. However,
2168-2194?2025IEEE.Allrightsreserved,includingrightsfortextanddatamining,andtrainingofartificialintelligenceandsimilartechnologies.
Personaluseispermitted,butrepublication/redistributionrequiresIEEEpermission.Seehttps://www.ieee.org/publications/rights/index.html
formoreinformation.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3737
Fig.2. TheTCMherbprescribingprocessismodeledasabipartite,
Fig.1. FourSDstepsintheTCMherbprescribingprocessbyphysi- tripartite and four-paritite graph paradigm, with their core differences
cians.Thedashedboxindicatestheabsenceofstandardgroundtruth highlightedinred.
forthisinformationinTCMmedicalrecords.
Similarly, in TCM prescription recommendation, studies [6],
different physicians may infer different syndromes from the [13] utilize graph-based models to capture higher-order re-
same patient symptom set. Consequently, no standard ground lationships between symptoms and herbs, treating syndrome
truthforsyndromeinformationexists,makingitchallengingto information as a holistic representation of symptom sets in
model [6].3) Therapeutic Method Determination (TD).Based alignmentwithTCM＊sholismtheory.However,existingmodels
on the syndrome, the physician determines a corresponding stillcannotincorporateinformationonthetherapeuticmethod
therapeutic method to formulate a prescription with multiple andtheTDstep.ConsideringtherunningexampleintheFig.2,
herbs. In this case, the therapeutic method ※Harmonize the sc1 is the target symptom set that interacted with prescription
Lesser Yang and Internally Purge Heat Congestion§ is chosen p1 ={h1,h2,h3 } and p2 ={h4,h5 }. By modeling PG, the
by physicians to treat the syndrome. It is important to note herbh1,h2,h3,h4,h5areequalrelatedtotheimplicitsyndrome
that a therapeutic method corresponds to multiple effects, and syn1,whichmayrecommendtheherbh3 andh4 togeneratea
a single effect requires various herbs to manifest. Thus, the prescriptionp3.However,h3andh4arerelatedtothetherapeutic
※therapeutic method§ reflects the overall characteristics of an method the3, which is not related to syn1. Therefore, recom-
herb set through its effects. Similar to syndrome information, mending p3 can not effectively treat sc1. Thus, incorporating
therapeutic method information lacks a standard ground truth therapeuticmethodsasconstraintsinherbformulationiscrucial
in records and is challenging to model [7]. 4) Prescription for the prescription recommendation task. Unlike the linear
Generation (PG). Finally, the prescription ※Major Bupleurum relationshipbetweensyndromesandsymptoms,therelationship
Decoction§isformulated,includingsixherbssuchas※rhubarb§ betweentherapeuticmethodsandherbsisnonlinear.Asshown
and※radixbupleuri.§ThefourstepsofSDarecrucialforpre- inFig.1,therapeuticmethodsconnecttomultipleeffects,each
ciselyprescribingherbsinTCM.Theessenceliesinaccurately linked to various herb combinations. The lack of ground truth
identifying the four diagnostic factors, including symptoms, for effect information in clinical records further complicates
syndromes,therapeuticmethods,andherbs,andreasoningtheir modeling this relationship. In TCM, a single syndrome may
multivariaterelationships. correspondtomultipletherapeuticmethods,andviceversa[4],
Recently, researchers have used data analysis techniques to asillustratedinFig.2.Therefore,modelingthemany-to-many
analyze the herb prescribing experience from TCM medical relationships between therapeutic methods and syndromes is
records, aiding physicians in precise prescriptions [5]. Based morechallengingthanmodelingtheone-to-manyrelationships
onthediagnostic factors included inthemodel,wecategorize betweensyndromesandherbsinTG.Additionally,thelackof
thesetechniquesintodistinctmodelingparadigmsfortheherb ground truth for these two information types and their sparse
prescribing process. Some researchers use data mining tech- relationshipsfurthercomplicatedirectmodeling.
niques,suchasassociationrules[8],Bayesiannetworks[9]and Toaddressthesechallenges,weproposeafour-partitegraph
clustering[10]toanalyzeherboccurrencesforspecificdisease paradigmFGthatalignswiththefourstepsofSD,representing
types. We refer to them as the bipartite graph paradigm BG thefourdiagnosticfactorsofTCM,includingsymptoms,syn-
because they mainly establish connections between symptoms dromes, therapeutic methods, and herbs, with modeling their
andherbs,asshowninthesecondcolumnofFig.2.However, relationships,asshowninthefourthcolumnofFig.2.Basedon
asillustratedinFig.1,symptomsandherbsmustundergofour thisparadigm,weintroduceaSD-basedprescriptionrecommen-
steps to establish accurate connections, not just co-occurrence dationmodel,SDPR.Wedesignfourmodulescorrespondingto
frequency.Consequently,thesemodelsarechallengedinanalyz- thesymptomcollection,SI,TD,andPGstepsinSDandemploya
ingmultiplediseasetypeswithcomplexsyndromes,leadingto multi-tasklearningframeworktointegratethem.Specifically,to
lower accuracy and generalizability. Some researchers further enhancetherepresentationofsymptomsandherbs,weproposea
consider syndrome information and propose prescription rec- representationlearningmoduleofTCMentitiesbasedonGraph
ommendationmodelsbasedonatripartitegraphparadigmTG, NeuralNetworks(GNNs),whichmodelsandintegratesinforma-
which models the relationships among symptoms, syndromes, tionfromdifferentgraphstructures.Toaddressthechallengeof
andherbs,asshowninthethirdcolumnofFig.2.Thesemodels modelingsyndromesandtherapeuticmethodsinactualmedical
includetopicmodel-based[11],[12]andgraphmodel-based[6], records, we introduce a symptom set aggregator in syndrome-
[13] approaches. Graph models, such as graph convolutional inducedpre-trainingstrategythattreatssyndromesaslatentvari-
networks (GCNs), are increasingly applied in biomedicine ablesrepresentingoverallsymptomsets.Similarly,wepropose
to model complex entity relationships effectively [14], [15]. a herb set aggregator to model therapeutic methods as latent
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

3738 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
variablesrepresentingoverallherbsets,capturingthenonlinear patterns.However,incomplexdiseases,thisapproachisinsuf-
relationshipbetweentherapeuticmethodsandherbs.Toaddress ficient.Accurateprescribingrequiresmatchingsymptomsetsto
the implicit, sparse, and many-to-many relationships between herbsetsthroughallSDsteps.However,bipartitegraph-based
syndromes and therapeutic methods, we propose a therapeutic methodsfailtomodelthecriticalSIandTDsteps,overlooking
method-awarecontrastivelearningframeworktoenhancetheir keyfactorslikesyndromesandtherapeuticmethods.Thislim-
association. Finally, we utilize a joint training strategy within itationrestrictsthemodel＊scapacitytoaddressthecomplexity
amulti-tasklearningframeworktocomprehensivelymodelthe and diversity of clinical prescriptions, reducing accuracy and
fourstepsofSD.Insummary,ourmodelcouldfullycapturethe generalizability.
progressiveprescriptionprocess,achievingpreciseprescription 2) Tripartite Graph-Based Herb Recommendation Model:
recommendations. The primary contributions of this study are Herbrecommendationstudiescanbeclassifiedintotwotypes:
summarizedasfollows. (a) Based on topic model: To further model the syndrome
(cid:2)
Weemphasizetheimportanceoffullymodelingthefour- information, one research line like research [11] that models
step progressive process in SD for the prescription rec- syndromesasthelatenttopictocapturethedependencebetween
ommendation. To this end, we propose a novel four- thesinglesymptomandherb.Thesemodelsconsidersymptoms
and herbs in the prescription as words in the document. To
partite graph paradigm that explicitly captures the four
enhancetheassociationbetweentheTCMentities,somestudies
SD components and their interactions, preserving criti-
like[12]incorporatetheTCMdomainknowledgeintothetopic
cal information. Building on this, we develop the SDPR
model.Nevertheless,theyoverlookthevaluablesetinformation
model, employing a multi-task learning framework with
ofsymptomsandthehigher-orderrelationshipsbetweensymp-
fourmodulestomodelallSDstepsthatbetteralignwith tomsandherbs.
(cid:2) theactualprescribingprocess. (b) Based on the graph model: The growing application
We employ GNNs, attention, and contrastive learning of GCNs in biomedicine underscores their effectiveness. For
technologiestomitigatethechallengesofsparseandcom- instance, Ma et al. [14] and Liu et al. [15] employ GCNs to
plexdatarelationshipsinTCMmedicalrecords.Addition- predictassociationsbetweennon-codingRNAs(e,g.,circRNAs
ally,weproposethesymptomsetandherbsetaggregator and miRNAs) and diseases. Further, research [17] uses graph
tomodelsyndromeandtherapeuticmethodinformation, attentionnetworkstofurtherexploreinteractionmechanismsbe-
tweencircRNAsandmiRNAs.Similarly,recentstudiesonherb
enhancingthemodel＊sgeneralizability.
(cid:2) recommendation leverage GCNs to overcome the limitations
Experimentalresultsontwoprescriptionrecommendation
of topic model-based approaches by encoding TCM entities
tasksdemonstratethatourmodelgeneratesandretrieves
intoalow-dimensionalspace.Chenetal.[18]employagraph
prescriptionscloserclinicalrecords,outperformingstate-
and auto-encoder framework to learn low-dimensional node
of-the-art(SOTA)techniquesingeneralandprescription embeddings, followed by clustering to capture symptom-herb
recommendationdomains. interactionsforherbrecommendation.Jinetal.[6]utilizeGCNs
Thepaperisorganizedasfollows:SectionIIreviewsrelated tomodelsymptom-herbinteractionsacrossthreeTCMgraphs
work. Section III outlines the problem formulation and nota- and introduce a syndrome induction mechanism to aggregate
tions.SectionIVpresentstheproposedmethodology.SectionV symptomsetinformation.However,thesemodelsadheretothe
reports comparative experimental results and analysis of our TGparadigm,neglectingtheimportanceoftherapeuticmethod
model and baselines on two datasets. Finally, Section VI con- information and the TD step in SD, which are essential for
cludesthisworkanddiscussesfutureresearchdirections. precise herb formulation. Yang et al. [19] and Jin et al. [13]
integratetherapeuticmethodinformationofaknowledgegraph
(KG) via customized meta-paths to enhance herb representa-
II. RELATEDWORK tionbutfocusonsingleherb-therapeuticmethodrelationships.
This limits their ability to model holistic herb coordination in
A. DataAnalysisModelsinTCM
prescriptionsaccordingtoSDtheory,deviatingfromtheactual
WeclassifyTCMdataanalysismodelsintotwotypesbased TCMprescribingprocess.
on the granularity of modeling the herb prescribing process:
bipartitegraph-based dataminingmodelsandtripartitegraph-
basedherbrecommendationmodels.
B. Graph-BasedRecommenderSystems
1) Bipartite Graph-Based Data Mining Model: Traditional
dataminingtechniquesareemployedbyresearcherstoextract Thetwoprescriptionrecommendationtasksexploredinthis
core symptoms, essential herbs, and other critical information paperresembleitemandsetrecommendationtasksincollabora-
fromTCMmedicalrecords.Thesemethodsaimtosummarize tivefiltering-basedrecommender systems.Wheregraph-based
renowned TCM experts＊ experiences by data co-occurrence models have recently achieved SOTA performance, here, we
frequency. For example, Guo et al. [8] use association rule focusonleveraginggraph-basedmethodsforthesetasks.
analysisonTCMprescriptionstoidentifycompatibilitypatterns 1) Item Recommendation: Item recommendation tasks in-
and therapeutic effects. Similarly, Zheng et al. [16] apply the volverecommendingindividualitemsthatalignwithuserpref-
ApriorialgorithmtoanalyzeherbcombinationsforCOVID-19 erences.Bergetal.[20]proposeauser-itemmatrixcompletion
treatment.Wuetal.[9]leverageBayesiannetworkstogenerate modelbasedonauto-encoder,whichusestheGCNasencoder.
herbcombinationsfromlungcancerclinicalrecords,whileJun Wangetal.[21]andHeetal.[22]usemulti-layerGCNonthe
et al. [10] use hierarchical clustering to study disease char- user-iteminteractiongraphtomodelhigher-orderrelationships
acteristics in Parkinson＊s cases. For single-disease scenarios, betweenuserpreferencesanditems.Toimprovetheefficiencyof
symptom-herb co-occurrence frequency effectively identifies graphprocessingalgorithms,Yingetal.[23]usetheGCNwith
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3739
therandomwalkstrategytosampleafixednumberofneighbors input:S,H,P,SS M℅M ,HH N℅N andSH M℅N .
andgeneratenodeembeddings. output:F 1(sc,H)andF 2(sc,P).
2) SetRecommendation: Setrecommendationaimstorec-
ommendaitemsetthatrelatedwithacertaintheme.DAM[24] IV. METHODS
leverages the attention to merge items embedding as the bun-
Weaimtodevelopaprescriptionrecommendationmodelthat
dle (the set of items) embedding, which model the set-item
adheres to the four SD steps to accurately represent the TCM
affiliationrelations.BundleNet[25]considersthreeofrelations
prescribingprocess,aidingphysicianstounderstandclassicpre-
typesamongusers,sets,anditemsbasedonGCNs.BGCN[26]
scribingpatternsandenhancetheirdiagnosticskills.Toachieve
furtherdecomposethepreferenceofusersintoitemandbundle
this, we propose a four-partite graph paradigm that explicitly
view, and CrossCPR [27] leverage the contrastive learning to
representsfourdiagnosticfactors:symptoms,syndromes,ther-
capturethecooperationoftwoviews.However,thesemethods
apeuticmethods,andherbs,andmodeltheirinteractionsinturn,
are unfriendly towards sparse information among users, items
ensuringcomprehensivemodelingofallSDsteps,asshownin
andsets.
Fig.2.Basedonthisparadigm,weproposeSDPR,anSD-based
prescriptionrecommendationmodelcomprisingfourmodules:
C. ContrastiveLearninginRecommenderSystems the representation learning module for TCM entities, the
inducting syndrome module, the determining therapeutic
Contrastive Learning, a self-supervised paradigm, is widely
method module, and the generating prescriptions module,
applied in domains like computer vision [28] to capture im-
each aligned with an SD step, as shown in Fig. 3. Further-
plicit relationships in unlabeled sparse data. Recent studies
more, it could display the importance of recommended herbs
haveleveragedcontrastivelearningasapretexttasktoimprove
in prescriptions. This modular design ensures comprehensive
recommendation tasks and mitigate data sparsity [29]. Wei
alignment with the TCM prescribing process, enabling more
et al. [30] highlight its potential to model complex user-item
accuraterecommendations.
relationships in real-world scenarios. CLCRec [31] employs
contrastivelearningtomaximizemutualdependenciesbetween
user-item collaborative signals and item content for cold-start A. RepresentationLearningModuleofTCMEntities
recommendation.Wangetal.[32]useittoenhancesequential
Weproposethismoduletosimulatethesymptomcollection
recommendation by refining user interaction sequence repre-
step, which is the first step in SD, aiming to represent herbs
sentations.Inspiredbytheseadvances,weleveragecontrastive
and symptoms. Inspired by SMGCN [6], we employ GCNs to
learningtoaddressthechallengeofmodelinglatentandsparse
modelhigher-orderrelationshipsbetweensymptomsandherbs
relationshipsbetweensyndromesandtreatmentmethods,which
toobtainmoreplentifulinformation.Additionally,weconstruct
lack explicit labels. By employing contrastive learning as a a symptom-symptom association graph G and a symptom-
SS
pretexttaskandaugmentingsymptom-herbrelationshipsfrom herb relationship graph G . By fusing these two graphs, the
SH
asetperspective(i.e.,symptomset-herbset),wecouldenhance
information on symptoms and herb is enhanced. Specifically,
theaccuracyofherbprescribing.
the representation of a symptom node s comes not only from
its neighboring nodes h﹋NSH in the G but also from its
s SH
III. PROBLEMFORMULATIONANDNOTATIONSDESCRIPTION neighboring nodes s k ﹋N s SS in the G SS . Thus, the symptom
embeddinge isasfollows:
s
Theprescriptionrecommendationtaskaimstogenerateaherb
set or retrieval a reasonable prescription for a given symptom e =eL1(G )+eL2(G ), (1)
s s SH s SS
s P et = . L { e p t 1, S p2 = ,.. { . s , 1 p , U s2 } , r . e . p . r , e s s M en } t , M H sy = m { p h to 1 m ,h s 2 , , N .. h . e , r h b N s, } a , nd an U d ( w L h ) er p e ro e p L s a 1 g ( a G te S d H t ) o ﹋ sy R m d pt i o s m th n e od i e n s fo s rm in at G ion o , f d t i h s e th l e as d t im lay en er -
prescriptionsinTCMmedicalrecords,respectively.Eachrecord SH
r a d pr = es (cid:2) c s ri c p , t p io (cid:3) n co p n = sis { ts h o 1 f , a h s 2 y , m .. p . t , o h m n } se . t F s o c ll = ow { e s d 1 b ,s y 2 S , M ..., G s C m N }a [6 n ] d , s (l io ﹋ n 1 o , f 2 e , m .. b . e , d L d 1 in ) g is s. d T e h n e ot i e n d fo a r s m : ationpropagationinl-thlayer
we construct the symptom-symptom association graph, i.e., el(G )=tanh(Wl ﹞(el?1 (G )||el?1 )),
S-HgraphG SH ,thesymptom-herbrelationshipgraph,i.e.,S-S s SH (cid:2) 1s s SH N s SH (cid:4)
graph G , and the herb-herb compatibility graph, i.e., H-H (cid:3)
graphG H SS H ,basedonthefrequencyofsymptomsandherbsin el N ? s S 1 H =tanh |N 1 SH| el h ?1﹞W 2 l s , (2)
TCMmedicalrecords.Theiradjacencymatricesaredefinedas s h﹋N
s
SH M℅N ={x sh |s﹋S,h﹋H}, SS M℅M ={y si,sj |s i ,s j ﹋ where,N aretheneighborsofsintheG .Wl denotesthe
S} and HH N℅N ={z hi,hj |h i ,h j ﹋H}, respectively. x sh , aggregatio s nweightmatrixforthegraphn S o H de,W 1 l s indicesthe
y ,andz ﹋{0,1},where1indicestheherbhasefficacy 2s
si,sj hi,hj transitionweightmatrixfortheneighbor node.When l equals
on the symptom, or two symptom belong to a disease, or the 0,theembeddingse0ande0 areinitializedrandomly.
herbpairappeartoarecordfrequently. s h
Inaddition,eL2(G )﹋Rdistheinformationaggregatedone
Given a symptom set sc, the core aim of our model is to s SS
hopbasedonG tonodes,theprocessisdenotedas:
recommend K1 herbs to generate a prescription based on the SS ? ?
probabilityvectorF 1(sc,H),definingtheherbrecommendation (cid:3)
p
t
ti
a
r o
s
e n
k
s s
.
cr f
A
i r p o
d
t m
d
io
it
m n
io
s e
n
f d r
a
i o
l
c
l
m a
y
l
,
t r
l
h e
e
e c
v
c o
e
a r
r
d
a
n
g
s d ,
i
i
n
w d
g
a e t
o
e c s
u
a
r
b n a
m
a s l e
o
s d o
de
o re
l
n c
t
t
o
o h m e
re
p m
p
r e
r
o
e
n b
s
d a
e
b K
n
i
t
l 2 i
p
ty e
r
x
e
v
s
i e s
c
c t
r
i t
i
n o
p
g r
- eL
s
2 (G
SS
)=tanh ?
sk ﹋N s SS
e 0
sk
﹞W3s ? . (3)
F 2(sc,P),defininganewtaskcalledprescriptionretrieval.The where N
s
SS is the neighbor symptom nodes of s in G
SS
. W3s
inputandoutputaredefinedasfollows: istheweightparametermatrixusedtodistillusefulinformation
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

3740 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
Fig. 3. The overall framework of SDPR consists of four module: (1) Representation Learning of TCM Entities, (2) Inducting Syndrome,
(3)DeterminingTherapeuticMethod,and(4)GeneratingPrescriptions.Dashedboxesrepresentthelearningmodules.
(cid:2) (cid:4)
TABLEI (cid:3)
1
THESTATISTICSOFG SS,G SH,AN D D AT G A H SE H T ONTHETCMANDLUNGCANCER el N ? h S 1 H =tanh |NSH| el s ?1﹞W 2 l h , (6)
h s﹋N
h
? ?
(cid:3)
eL
h
2(G
HH
)=tanh ? e 0
hk
﹞W3h ? , (7)
hk ﹋N h HH
whereWl denotestheaggregationweightmatrixfortheherb
1h
nodeinG ,Wl indicesthetransitionweightmatrixinG ,
SH 2h SH
andW3h istheweightparametermatrixinG
HH
.
fromtheinitialembeddingse0 oftheneighboringnodess .We Throughthemulti-layerinformationpropagationandinfusion
setL2 =1,withnoneedfor s p k ropagatingmulti-layerneig k hbor mechanism of GCNs, we can provide a richer representation
information as in (2). This setting is based on graph statistics, of symptom and herb entities and establish the higher-order
including the mean (#Avg. ND) and standard deviation (#SD. interactionbetweenthem.
ND) of node degrees and the average connective path length
(#Avg.PCL)acrosstheTCMandLungCancerdataset(details B. InductingSyndromeMoudule
providedinSectionV-A1),asshowninTableI.Homogeneous
We propose this module to simulate the SI step, which is
graphsG exhibitsparserstructuresandsmootherdegreedistri-
SS the second step in SD, aiming to represent the syndrome and
butions compared to the heterogeneous graph G , with most
SH modelitslinearrelationshipwiththesymptoms.Weintroduce
nodes connected via one-hop paths. Consequently, increasing
asymptomsetaggregatorthatfollowsTCM＊sholisticprinciple
L2 wouldriskover-smoothingwithoutsignificantperformance
to learn syndrome representation. Without a standard ground
gains while incurring additional computational overhead. Ad-
truthforsyndromeinformationinTCMrecords,weusealatent
ditionally, the effectiveness of L2 =1 can be confirmed by
variable as the syndrome representation, reflecting the holistic
experimentsinSectionV-E.SimilarconclusionsapplytoG .
HH inputsymptomset.Welinearlyaggregatethesymptomsetrepre-
For G , which has a non-uniform degree distribution and
SH sentationbyemployingamulti-layerperceptron(MLP)similar
morediverseconnectivitypaths.ThusL1istreatedasatunable
to SMGCN, effectively addressing the challenge of modeling
hyperparameter,asdetailedinSectionV-E.
syndromeinformationinmedicalrecords.Thus,thesyndrome
Similarly, the representation of herb node comes from two
embeddinge (sc)canbedenotedas:
sources,includingitsneighboringnodess﹋NSH intheG syn
h SH
and its neighboring nodes h ﹋NHH in the G . Thus, the e (sc)=ReLU(W ﹞E +b ), (8)
k h HH syn mlp esc mlp
herbembeddinge isasfollows:
h
where e ﹋R|sc|℅d is the matrix stacked by the symptom
sc
embedding vector e in sc, E ﹋R1℅d is the average repre-
s esc
e =eL1(G )+eL2(G ), (4) sentation of it. And e (sc)﹋R1℅d is the latent variable to
h h SH h HH syn
represent the syndrome information. W and b are the
el h (G SH )=tanh(W 1 l h ﹞(el h ?1 (G SH )||el N ? S 1 H )), (5) trainableweightmatricesinMLP. mlp mlp
h
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3741
We further employ the pre-training strategy to enrich the Algorithm 1: The Calculation Process of Hard-Negative
| syndrome |     | information |     | from | its related | herbs. | We  | propose | an  |     |     |     |     |     |
| -------- | --- | ----------- | --- | ---- | ----------- | ------ | --- | ------- | --- | --- | --- | --- | --- | --- |
TherapeuticMethodSampler.
| improved |              | multi-label | loss,         | whose     |             | core idea  | is           | that if       | a herb  |     |     |     |     |     |
| -------- | ------------ | ----------- | ------------- | --------- | ----------- | ---------- | ------------ | ------------- | ------- | --- | --- | --- | --- | --- |
| is       | associated   | with        | an symptom    |           | set,        | regardless | of           | the prescrip- |         |     |     |     |     |     |
| tion     | in which     | it          | is used,      | it is     | considered  |            | a herb       | label         | related |     |     |     |     |     |
| to       | the syndrome |             | corresponding |           | to          | that set   | of symptoms. |               | This    |     |     |     |     |     |
| strategy |              | effectively | constructs    |           | an implicit |            | global       | relationship  |         |     |     |     |     |     |
| graph    | G            |             | between       | syndromes |             | and        | herbs,       | revealing     | the     |     |     |     |     |     |
Syn?H
| connection |     | between | single | herbs | and | syndromes. |     | We stack | all |     |     |     |     |     |
| ---------- | --- | ------- | ------ | ----- | --- | ---------- | --- | -------- | --- | --- | --- | --- | --- | --- |
﹋RN℅d.
| herbs | embedding |     | to build | a learning |     | matrix | e H |     | The |     |     |     |     |     |
| ----- | --------- | --- | -------- | ---------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
improvedmulti-labellossisasfollows.
|     |     |         |     | (cid:3) (cid:3)N |       |            |         |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | ---------------- | ----- | ---------- | ------- | --- | --- | --- | --- | --- | --- | --- |
|     | L   |         |     |                  |       | (cid:5) ?F |         | 2   |     |     |     |     |     |     |
|     |     | =argmin |     |                  | w (hs |            | 1(sc,H) | )   | ,   |     |     |     |     |     |
|     | W1  |         |     |                  | i     | i          |         | i   |     |     |     |     |     |     |
牟 hs(cid:5)﹋P(cid:5)i=1
|     | F         |     |     | (sc)﹞(e | )T, |     |     |     |     |     |     |     |     |     |
| --- | --------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | 1(sc,H)=e |     | syn |         | H   |     |     |     | (9) |     |     |     |     |     |
hs(cid:5) ﹋RN℅d
| where | the        |     |         | is a multi-hot |       | vector, | which | indices | all      |     |     |     |     |     |
| ----- | ---------- | --- | ------- | -------------- | ----- | ------- | ----- | ------- | -------- | --- | --- | --- | --- | --- |
| herbs | associated |     | with sc | in a           | batch | with G  |       | , i is  | the i-th |     |     |     |     |     |
Syn?H
| herbinHandhs(cid:5)(i)equals1.w |     |     |     |     | isthepenaltytermoftheherb |     |     |     |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | --- | ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
i
| frequency |     | same | as SMGCN. |     | F indices |     | the predict | function |     |     |     |     |     |     |
| --------- | --- | ---- | --------- | --- | --------- | --- | ----------- | -------- | --- | --- | --- | --- | --- | --- |
1
betweenthesyndromeandallcandidateherbsinH.Inaddition, embeddinge thm (p)isdenotedas:
(cid:2) (cid:4)
| we  | can get | several | top-scoring |     | herbs | based | on  | the syndrome |     |     |     |     |     |     |
| --- | ------- | ------- | ----------- | --- | ----- | ----- | --- | ------------ | --- | --- | --- | --- | --- | --- |
(cid:3)n
| e   | (sc)byusingF |     | 1.  |     |     |     |     |     |     |     |     |          |     |     |
| --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- |
| syn |              |     |     |     |     |     |     |     |     |     | e   | (p)=Mean | e , |     |
By optimizing this loss function, we can update the GCN thm f
| parametersfromthepreviousmodule,allowingforthedistilling |     |     |     |     |     |     |     |     |     |     |     |     | i   |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:3)n
ofherbinformationtoenhancetherepresentationofsyndromes.
|     |     |     |     |     |     |     |     |     |     |     | e   | = 汐 (W | e ), |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | ---- | --- |
Additionally, through the pre-training of the GCN, we obtain f ij V hj
well-initialized embeddings for symptoms and herbs. We use i,j,i(cid:6)=j
|     |          |     |          |     |           |       |             |     |       |     |     | (cid:2) | (cid:4) |     |
| --- | -------- | --- | -------- | --- | --------- | ----- | ----------- | --- | ----- | --- | --- | ------- | ------- | --- |
| the | syndrome | as  | a bridge | to  | establish | their | association |     | rules |     |     |         |         |     |
)T
indirectly,providingasolidfoundationforthesubsequentpre- W Q e hi﹟ (W K e hj
|     |     |     |     |     |     |     |     |     |     |     | 汐   | =softmax |     | , (10) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------ |
ij
| scriptionrecommendationmodel.However,inthismodule,we |     |             |     |          |             |     |        |             |     |     |     |     | d   |     |
| ---------------------------------------------------- | --- | ----------- | --- | -------- | ----------- | --- | ------ | ----------- | --- | --- | --- | --- | --- | --- |
| have                                                 | yet | to consider | the | critical | information |     | of the | therapeutic |     |     |     |     |     |     |
method, so the herbs generated directly from this pre-trained where 汐 ij represents the attention weight used to model the
;Mean(﹞)indicatestheoverall
modellackformulationinformation.Therefore,weproposethe effecte ofherbh andherbh
|     |     |     |     |     |     |     |     |     |     |     | f   | i   | j   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
nextmoduletoaddressthis. prescription information through average pooling the multiple
|     |     |     |     |     |     |     |     |     |     | effect.W | ,W  | ,andW arethetrainableweightmatricesof |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------------------------------------- | --- | --- |
|     |     |     |     |     |     |     |     |     |     |          | Q   | K V                                   |     |     |
query,key,andvalueinself-attention,respectively.
C. DeterminingTherapeuticMethodMoudle
|     |     |     |     |     |     |     |     |     |     | 2)  | Therapeutic | Method-Aware | Contrastive Learning | Frame- |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ------------ | -------------------- | ------ |
We propose this module to simulate the TD step, which is work: To address the challenge of modeling the sparse, im-
thethirdstepinSD.Importantly,ithasoftenbeenoverlookedin plicit, and many-to-many interaction between syndromes and
previousprescriptionrecommendationmethods.Inthismodule, therapeutic methods, we propose a therapeutic method-aware
we aim to obtain the representation of therapeutic methods, contrastive learning framework. To address the challenge of
as well as model their nonlinear relationship with herbs and implicit relationships, we treat the therapeutic method in herb
theimplicitmany-to-manyrelationshipwithsyndromes.Since set p as a positive example Poi sc (p) for the syndrome with
therapeutic methods often lack ground truth in TCM records, symptomsetsc,providedscandpco-occurinthesamerecord.
wemodeltheirrepresentationusingalatentvariablee (p).In For negative examples Neg (p), we use therapeutic method
|     |     |     |     |     |     |     |     | thm |     |     |     | sc  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
SD,thetherapeuticmethodservesastheformulatingprincipleof embeddingsfromotherrecordsinthetrainingbatch.Poi (p)
sc
theprescription,anditsrepresentationshouldreflecttheoverall andNeg (p)arecalculatedusing(10).
sc
characteristicsoftheprescription. However,randomlysampledtherapeuticmethod-basedneg-
1) Herb Set Aggregator: A prescription represents a set of ativeexamplesmayliefarfromthetargetsyndromeinfeature
herbs, with different combinations producing various effects space, limiting the ability of contrastive learning to extract
guided by a therapeutic method. This nonlinear relationship effectiveinformation.Toaddressthis,wedesignahard-negative
betweentherapeuticmethodsandherbsmakesrepresentingthe example therapeutic method sampler to generate more chal-
herbsetmorecomplexthanthesymptomset.Weproposeaherb lenging negative examples, enhancing feature discrimination
set aggregator that employs the self-attention mechanism [33] and model robustness. We also adopt a supervised contrastive
to represent the therapeutic method. It first models the effects loss[28]tomodelthemany-to-manyrelationships.Weaimto
of different herb combinations within a prescription and then deeplycapturetheintrinsicconnectionsbetweensyndromesand
aggregatestheseeffectstogeneratetherapeuticmethodembed- therapeutic methods from the perspective of the overall herb
| dings.Wesettheinitialtherapeuticmethodrepresentationofa |     |     |     |     |     |     |     |        |     | set. |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | ---- | --- | --- | --- | --- |
|                                                         |     |     | ={e |     |     | },  |     | ﹋Rn℅d, |     |      |     |     |     |     |
prescription as e p h1 ,e h2 ,...,e hn where e p n (a)Hard-negativeTherapeuticMethodSampler:Sincethein-
isthenumberofherbsinaprescription.Thetherapeuticmethod ductingsyndromemodule(refertoSectionIV-B)ispre-trained,
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

3742 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
ithasthepotentialtogenerateprescriptions.However,because D. GeneratingPrescriptionsModule
this module does not consider the formulating principle, the
WeutilizethismoduletosimulatethePDstep,whichisthe
therapeuticmethodsimpliedintheprescriptionsgeneratedare
finalstepinSD.Theultimategoalofourmodelistorecommend
very similar yet distinctly different from the target therapeutic
herbs that are closest to the actual prescription for a given
method. Thus, the therapeutic methods in these prescriptions
symptomset.WeutilizetheMSElossfunctiontooptimizeour
can serve as excellent hard negative examples, enhancing the
model＊sparameters.Theformulaisasfollows.
featureextractioncapabilityofcontrastivelearning.Byinputting
thesehardnegativeexamplesintothecontrastivelearningframe- (cid:3) (cid:3)N
work, we strengthen our model＊s ability to explore the rela- L
W2
=argmin w
i
(p
i
?F 1(sc,H)
i
) 2 , (12)
tionship between the syndrome and the therapeutic method. 牟 (cid:2)sc,p(cid:3)﹋Ri=1
Theconstructionalgorithmofhard-negativetherapeuticmethod
sampler is in Algorithm 1. Specifically, we sort the candidate wherethep i ﹋RN℅d,whichindicestheherbsinaprescriptions
herbs based on the F 1 from (9) as H sort . Then, we select passociatedwiththesymptomsetsc.
sequentialqherbstoformaprescriptionP c ={h c ,...,h c+q }, We adopt a multi-task learning approach to achieve mod-
wherec=1,2,...,C(cid:5)?q,C(cid:5)isthemaxhard-negativesample eling and optimization of the four modules within the same
search length. Next, we can calculate the hard-negative ther- framework.Bysimultaneouslytrainingthesemodules,wecan
apeutic method e (P ) by (10). Finally, we can obtain a recommendmorereasonablecombinationsofherbsforagiven
thm c
set of hard-negative therapeutic method samples, denoted as set of symptoms, guided by SD logic and leveraging classi-
Q thm (sc)={e thm (P 1),e thm (P 2),...,e thm (P C(cid:5)?q )}, where calprescriptionresources.Furthermore,weintroduceanauto-
|Q
thm
(sc)|=C(cid:5)?q. correlationconstraintA
cor
tomitigatepotentialover-smoothing
(b) Therapeutic Method-aware Contrastive Loss: To inherbrepresentationscausedbytheattentionmechanism.The
effectively capture the many-to-many and sparse relationship equationofA cor areasfollows:
(cid:3)
between syndromes and therapeutic methods, we propose a
therapeutic method-aware contrastive learning loss function. A cor = e hi ﹞e hj . (13)
This function optimizes the model＊s ability by considering hi,hj,i(cid:6)=j
multiple positive and negative examples simultaneously. The
Thisconstraintpreventsherbsfrombecomingexcessivelysim-
lossfunctionisasfollows.
ilar due to frequent connections to the same symptom sets. It
L alsohelpsavoidrecommendingherbswithantagonisticortoxic
C
properties in the same prescription when linked to the same
(cid:3) ?1 (cid:3)
symptomset.
=
|Poi (p)| Finally,wecombinethemulti-labellossL ,thecontrastive
i﹋B sci j﹋Poisci (p) lossL ,auto-correlationconstraintA and W th 2 eL2regulariza-
C cor
log (cid:9)
b﹋Negsci (p
F
)+
2
Q
(s
th
c
m
i ,
(
p
sc
j
i
)
)
F 2(sc
i
,p
b
) , o
T
ti u o
h
s n
e
ly t
fi
e ,
n
r w m
al
h |
l
i |
o
c 牟 h
s
|
s
| s 2 2
i
h
s
a a s
a
r
s
e th
f
t e
o
h
l
e fi
lo
n r
w
a e l p
s
l r
:
o e s s s en to ta o ti p o t n im o i f ze sy t n w d o ro ta m sk es ss a i n m d u h lt e a r n b e s - .
L=L +L +竹 A +竹 ||牟||2 , (14)
W2 C A cor 牟 2
F 2(sc i ,p i )=exp(e syn (sc i )﹞eT thm (p i )/而), (11) where 竹 A is the weight of A cor , 牟 represents all of model
parameters,and竹 istheweightofregularization.
whereP(sc )indicesthesetofindicesofallpositivetherapeutic 牟
i
methodsthatcantreatthesymptomsetsc inatrainingbatchB,
i
and|P(sc )|isitscardinality.e (p )denotestherepresenta- E. TwoPrescriptionRecommendationTaskPrediction
i thm i
tionoftherapeuticmethodsamples而isahyper-parametermeans
WeselecttopK1 herbswiththehighestprobabilitiesinthe
thetemperatureparameter.Thecoreideaofourproposedloss F 1 in (12) for the herb recommendation task. Simultaneously,
functionistoguidethemodeltolearnrepresentationsthataccu-
asourmodelobtainstheoverallrepresentationofprescriptions
ratelydistinguishdifferenttherapeuticmethodsbyminimizing
while modeling the therapeutic methods within the therapeu-
the distance between positive examples and maximizing the
tic method-aware contrastive learning framework, it can also
distance between negative examples. By pulling the distances
directlyretrievethetopK2prescriptionswiththehighestprob-
between different therapeutic method representations under abilities among all candidates P based on F 2(sc,P) in (11),
the same syndrome closer, the model learns a more compact
correspondingtotheprescriptionretrievaltask.Furthermore,in
feature space to relieve the challenge of sparsity. Optimizing
the herb set aggregator, we use the attention score 汐 in (10)
ij
this loss function allows our model can capture the implicit,
to represent the effect of different herbs and aggregate them
sparse, and many-to-many relationship between the syndrome
torepresentthetherapeuticmethod.ItallowsSDPRtoexplain
and therapeutic method, thereby improving the accuracy and
eachherb＊simportanceintherecommendedprescriptionandits
generalization ability of the prescription recommendation
relationshipwithotherherbs.
model.
WeproposeanovellossfunctionforTCMprescriptionrec-
V. EXPERIMENTS
ommendationmodels.Itcouldofferaneffectivedatamodeling
schemeforhandlingsituationswherethesamediseasewithdif- Inthisstudy,weemploytwotaskstoevaluatetheeffectiveness
ferenttreatmentsanddifferentdiseaseswiththesametreatment ofourmodelSDPRinprescriptionrecommendation.First,we
in clinical records. It further enhances the model＊s ability to evaluate the herb recommendation task, which takes a set of
simulatecomplexclinicaldiagnosticscenarios. symptoms as input and generating the prescription with K1
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3743
TABLEII 2) Evaluation Metric: We utilize four key metrics for the
THEDATASETSTATISTICS herb recommendation task, extending traditional recommen-
|     |     |     |     |     |     |     | dation | metrics | with | guidance | from | TCM | experts | and | theory. |
| --- | --- | --- | --- | --- | --- | --- | ------ | ------- | ---- | -------- | ---- | --- | ------- | --- | ------- |
ConsideringthecomplexityoftheTCMclinicalprocess,where
multipleprescriptionscouldaddressthesamesymptomsetsc,
p?
|     |     |     |     |     |     |     | we     | select         | the most | relevant | prescription |          | from  | the    | multiple |
| --- | --- | --- | --- | --- | --- | --- | ------ | -------------- | -------- | -------- | ------------ | -------- | ----- | ------ | -------- |
|     |     |     |     |     |     |     | actual | prescriptions. |          | Inspired | by           | research | [26], | we use | (15) to  |
identifytheprescriptionwiththemostsignificantoverlapwith
p?
|     |     |     |     |     |     |     | the    | top   | K1 recommended |           | herbs.         | is  | then considered |     | as the |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----- | -------------- | --------- | -------------- | --- | --------------- | --- | ------ |
|     |     |     |     |     |     |     | ground | truth | to             | calculate | Precision1@K1, |     | Recall1@K1      |     | and    |
NDCG@K1.Thenewmetricsareasfollows:
(cid:10)
|     |     |     |     |     |     |     |     |     | ? =max|Top1(sc,K1) |     |     |     | p|, |     |      |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | ---- |
|     |     |     |     |     |     |     |     |     | p                  |     |     |     |     |     | (15) |
p﹋D
(cid:11)
|                                    |             |              |              |               |              |             |             |     |               |     | |Top1(sc,K1) |      |          | p?| |      |
| ---------------------------------- | ----------- | ------------ | ------------ | ------------- | ------------ | ----------- | ----------- | --- | ------------- | --- | ------------ | ---- | -------- | --- | ---- |
|                                    |             |              |              |               |              |             |             |     | Precision1@K1 |     | =            |      |          | ,   | (16) |
| herbs, where                       | K1          | ﹋{5,20},     | representing |               | concise      | and compre- |             |     |               |     |              |      | K1       |     |      |
| hensiveprescriptions,respectively. |             |              |              |               |              |             |             |     |               |     |              |      | (cid:11) |     |      |
|                                    |             |              |              |               |              |             |             |     |               |     | |Top1(sc     | , K  | 1) p?|   |     |      |
| S ec o nd                          | ly , w e in | t r o d u    | ce a p re sc | ri p ti o n   | r e tr i e v | a l ta s k  | to ev a l - |     |               |     |              |      |          |     |      |
|                                    |             |              |              |               |              |             |             |     | Recall1@K1    |     | =            |      |          | ,   | (17) |
|                                    |             |              |              |               |              |             |             |     |               |     |              | |p ? | |        |     |      |
| uat e th e                         | m o d el ＊s | a b i l it y | to re p re   | se n t t h er | a p e u t i  | c m e t ho  | ds a n d    |     |               |     |              |      |          |     |      |
completeprescriptions.ThistaskrecommendsK2existingpre- DCG@K1(p?)
s c ri p ti o n s b a s e d o n th e i n p u t s ym p t o m s e t. G i ve n th e c h a l - NDCG@K1 = . (18)
IDCG@K1(p?)
| le n g e o f | d ir e c t ly a | p ply in | g e x i s tin g | pr e s c rip | t io ns        | t o p ers o | na li z e d |     |     |     |     |     |     |     |     |
| ------------ | --------------- | -------- | --------------- | ------------ | -------------- | ----------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
| patients,    | the model       | should   | provide         | diverse      | recommendation |             |             |     |     |     |     |     |     |     |     |
Then,toevaluatetheorderinformationofherbinaprescription
| options as | references. | Therefore, |     | we set | larger | values | for K2,                                   |     |     |     |     |     |     |     |       |
| ---------- | ----------- | ---------- | --- | ------ | ------ | ------ | ----------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- |
|            |             |            |     |        |        |        | better,weproposeanewrankmetricRank_MRR@K1 |     |     |     |     |     |     |     | based |
﹋{10,15,20},tofullyassessthemodel＊scapability
| whereK2                               |             |     |            |     |             |     | ontherelativeposition|ai |     |     |     | ?ai         |       | |.  |     |     |
| ------------------------------------- | ----------- | --- | ---------- | --- | ----------- | --- | ------------------------ | --- | --- | --- | ----------- | ----- | --- | --- | --- |
|                                       |             |     |            |     |             |     |                          |     |     |     | rank        | refer |     |     |     |
| to offer diverse                      | prescribing |     | solutions. | In  | particular, | we  | aim to                   |     |     |     |             |       |     |     |     |
| answerthefollowingimportantquestions: |             |     |            |     |             |     |                          |     |     |     | (cid:3)|p?| |       |     |     |     |
| (cid:2)                               |             |     |            |     |             |     |                          |     |     |     | 1           |       | 1   |     |     |
RQ1:CanourproposedmodeloutperformtheSOTAherb Rank_MRR@K1 = , (19)
|     |     |     |     |     |     |     |     |     |     |     | |p?| | |ai | ?ai | |+1 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
and graph neural network-based item recommendation i=1 rank refer
methodsinherbrecommendationtask?
(cid:2) For the prescription retrieve task, we adopt Recall2@K2 and
RQ2:CanourproposedmodeloutperformtheSOTAset Precision2@K2,whicharecommonlyusedinsetrecommen-
recommendationmodelsinprescriptionretrievaltask? dationtasks[27].Sincetheorderoftheretrievedprescriptions
(cid:2)
RQ3:Howeffectiveareourproposedkeycomponents? isnot practically significant, we do not userelated metrics for
(cid:2)
| RQ4:Howdoesourmodelperformancereacttodifferent |     |     |     |     |     |     | thistask. |     |     |     |     |     |     |     |     |
| ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
hyper-parametersettings? 3) Baselines: Forherbrecommendationtask,weselectboth
(cid:2)
herbrecommendationmodelandgeneralgraph-baseditemrec-
RQ5:CanourproposedSDPRprovidereasonableherb
ommendationmodels.Asfarasweknow,noworkisexplicitly
recommendationtogenerateaprescription?
|     |     |     |     |     |     |     | dedicated |     | to the | prescription | retrieval |     | task now. | Therefore, | we  |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------ | ------------ | --------- | --- | --------- | ---------- | --- |
selectgraph-basedsetrecommendationmodelstocomparewith
A. ExperimentalSettings ourmethod.Inparticular,wetreatusersassymptoms,itemsas
herbs,andbundlesasprescriptions.
| 1) Dataset: | Weconductexperimentsontwodatasets:(1)a |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
| ----------- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Herbrecommendationmodels:
| publiclyavailablebenchmarkdatasetnamedTCM,comprising |     |     |     |     |     |     |     | (cid:2)   |       |           |     |              |           |     |       |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --------- | ----- | --------- | --- | ------------ | --------- | --- | ----- |
|                                                      |     |     |     |     |     |     |     | Bipartite | Graph | Paradigm: |     | (i) Apriori. | Following |     | [16], |
26360samplesderivedfromclassicalmedicalrecords[6],[12],
|     |     |     |     |     |     |     |     | we  | use the | Apriori | algorithm | for | herb recommendation. |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | --------- | --- | -------------------- | --- | --- |
and(2)amodernTCMdatasetnamedLungCancer,basedonac-
|     |     |     |     |     |     |     |     | Herbs | are | ranked | by confidence |     | score, | and the | top K1 |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | ------ | ------------- | --- | ------ | ------- | ------ |
tuallungcancermedicalrecordsfromarenownedTCMclinician
atourcollaboratinghospital.Afterfilteringredundantdata,we herbsareselectedbasedonthebipartitegraphparadigm.
retained947high-qualitymedicalrecords.Notably,theoriginal (ii) MP. This is the easiest method that recommends the
dataforbothdatasetslackexplicitinformationaboutsyndromes mostfrequentherbsforallsymptomset.
(cid:2)
andtherapeuticmethods.Eachsampleconsistsofasymptomset TripartiteGraphParadigm:(i)SMGCN[6].Itconstructs
andaprescriptioncomprisingmultipleherbs.TableIIprovides multiplegraphswithMLPtoinduceanimplicitsyndrome
thestatisticaldetailsofthesedatasets.Additionally,weusethe
representation.(ii)MGAT[13].Itenhancestherepresen-
| commonly | employed        | sparsity | metric, | Density,       |     | to measure | the   |        |             |     |           |     |         |     |         |
| -------- | --------------- | -------- | ------- | -------------- | --- | ---------- | ----- | ------ | ----------- | --- | --------- | --- | ------- | --- | ------- |
|          |                 |          |         |                |     |            |       | tation | of symptoms |     | and herbs | by  | the TCM | and | Western |
| sparsity | of interactions |          | between | entities [21]. | A   | Density    | value |        |             |     |           |     |         |     |         |
medicineKGandcustomizedSD-basedmeta-paths.(iii)
closerto0indicatesgreatersparsityinthematrix.Ourobserva-
SDPR(SI).Itisourproposedbaseline,thatpre-trainedin
tionsrevealthatallfourmatricesarehighlysparse,withsparsity
inducingsyndromemoduleoftheSDPR.
levelsrankedasS-H>SC-H＞P-H>SC-P.Notably,interac-
Graph-baseditemrecommendationmodels:
| tionmatricesinvolvingprescriptions(therapeuticmethod)and |     |     |     |     |     |     |     | (cid:2) |     |     |     |     |     |     |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
symptom sets (syndrome) are even sparser. Additionally, the Tripartite Graph Paradigm for herb recommendation: (i)
GC-MC[20].ItutilizesGCNtomodeltherepresentation
| SC-P matrix | shows | significantly |     | higher | sparsity | than | SC-H, |     |     |     |     |     |     |     |     |
| ----------- | ----- | ------------- | --- | ------ | -------- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
highlighting that modeling the sparse relationships between of users and items. (ii) PinSage [23]. It combines the
syndromesandtherapeuticmethodsisincrediblychallenging. random walk and GCN for web-scale recommendation
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

3744 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
TABLEIII
THEOVERALLPERFORMANCECOMPARISONFORHERBRECOMMENDATIONTASKONTHETCMDATASET,WHEREr 1,p
1ANDR_MRRISSHORTOF
|     |     |     | @K                   |     | @K 1ANDRANK_MRR@K |     |               |     |     |     |
| --- | --- | --- | -------------------- | --- | ----------------- | --- | ------------- | --- | --- | --- |
|     |     |     | RECALL1 1,PRECISION1 |     |                   |     | 1RESPECTIVELY |     |     |     |
TABLEIV
THEOVERALLPERFORMANCECOMPARISONFORHERBRECOMMENDATIONTASKONTHELUNGCANCERDATASET,WHEREr 1,p
1ANDR_MRRISSHORTOF
|     |     |     | @K                   |     | @K 1ANDRANK_MRR@K |     |               |     |     |     |
| --- | --- | --- | -------------------- | --- | ----------------- | --- | ------------- | --- | --- | --- |
|     |     |     | RECALL1 1,PRECISION1 |     |                   |     | 1RESPECTIVELY |     |     |     |
G
task on item-item graphs. We adopt it on the symptom- layer number(L1) of SH is set to 3, the layer number(L2) of
|     |     |     |     |     |     | G andG |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- |
herb graph. (iii) NGCF [21]. It uses a recommendation SS HH issetto1.Forafaircomparison,weincorporate
modelthatcombinesGCNandCollaborativeFilteringto theinducingsyndromemoduleintoGC-MC,PinSage,NGCF,
DAM,BGCN,andCrossCBR,andapplythemulti-labellossto
representusersanditems.
GC-MC,PinSage,andNGCF.
Graph-basedsetrecommendationmodels:(i)DAM[24].It
modelsrelationshipsbetweenusers,singleitems,anditemsets
| (bundles) | for bundle | recommendation. | It uses | an MLP-based |     |     |     |     |     |     |
| --------- | ---------- | --------------- | ------- | ------------ | --- | --- | --- | --- | --- | --- |
attentionmechanismtoderivebundlerepresentationsfromitems B. HerbRecommendationPerformanceComparison
(RQ1)
andemploysmulti-tasklearningtooptimizeuser-bundleinter-
actions.(ii)BGCN[26].Itconstructstwoheterogeneousgraphs BasedontheTCMandLungCancerdataset,wefirstcompare
usingGCN,basedoninteractionandaffiliationrelationships.It theoverallperformanceforallmethodsforherbrecommenda-
| captures | user-bundle | relationships | from both item | and | bundle |                                                  |     |     |     |     |
| -------- | ----------- | ------------- | -------------- | --- | ------ | ------------------------------------------------ | --- | --- | --- | --- |
|          |             |               |                |     |        | tiontask,asshowninTableIIIandTableIV.%Improv.byX |     |     |     | =   |
views.(iii)CrossCBR[27].ItachievesSOTAperformancein (SDPR?X)/X,
|     |     |     |     |     |     |     | which | measures the | relative improvements |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | ------------ | --------------------- | --- |
bundle recommendation by introducing cross-view contrastive of SDPR over the baseline X on metrics. We categorize the
learning to model interaction associations between item and comparable methods based on different modeling paradigms,
bundleviews.Weadoptitscross-viewcontrastivelearningfor includingbipartitegraph-based,tripartitegraph-based,andfour-
syndromesandprescriptions.
|     |     |          |            |        |          | partite graph-based | methods. | From Tables | III and IV, | we can |
| --- | --- | -------- | ---------- | ------ | -------- | ------------------- | -------- | ----------- | ----------- | ------ |
|     |     | We adopt | the Xavier | normal | initial- |                     |          |             |             |        |
4) Parameter Setting: observe that the model using the tripartite graph paradigm
ization [34] for all methods, the models are optimized using outperformsthosewithabipartitegraph,whileourfour-partite
Adamoptimizer[35],theembeddingsizeisfixedto32forthe graph paradigm surpasses the tripartite graph. The tripartite
TCMdataset,while64fortheLungCancerdataset,andthebatch graphparadigmincorporatessyndromes,offeringamoreholis-
sizeissetto512.ForourproposedSDPRontheTCMdataset,
ticviewofTCMprescribing,whilethefour-partitegraphfurther
| the learning | rate(lr) | is set to | 2e?5, 竹 is set | to 7e?3, | the |                                                         |     |     |     |     |
| ------------ | -------- | --------- | -------------- | -------- | --- | ------------------------------------------------------- | --- | --- | --- | --- |
|              |          |           | 牟              |          |     | integratestherapeuticmethods,fullyaligningwiththefourSD |     |     |     |     |
hard-negativesamplesqissetto6,themaxhard-negativesample steps,enablingthemodeltosimulatetheTCMherbprescribing
|     | C(cid:5) |     |     | 竹   |     |     |     |     |     |     |
| --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
search length is set to 26, the 而 is set to 0.3, and A is set process more accurately. This demonstrates that the closer the
1e?6.
to For SDPR on the LungCancer dataset, lr is set to recommendationmodel＊sparadigmistothecompleteSDsteps,
| 1e?3,竹                | issetto1e?2,thehard-negativesamplesqissetto |                                |               |                 |        |                                                          |        |                  |             |      |
| --------------------- | ------------------------------------------- | ------------------------------ | ------------- | --------------- | ------ | -------------------------------------------------------- | ------ | ---------------- | ----------- | ---- |
|                       | 牟                                           |                                |               |                 |        | theclosertherecommendedherbsaretotheactualprescriptions. |        |                  |             |      |
| 7, the max            | hard-negative                               | sample                         | search length | C(cid:5) is set | to 17, |                                                          |        |                  |             |      |
|                       |                                             |                                |               |                 |        | Graph-based                                              | models | like NGCF, GCMC, | and PinSage | out- |
| the而 issetto0.25,and竹 |                                             | issetto1e?7.Forbothdataset,the |               |                 |        |                                                          |        |                  |             |      |
A perform structural models (e.g., Apriori) on the TCM dataset,
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3745
demonstratingtheirsuperiorabilitytorepresentTCMdiagnos- TableVandTableVI.WecanfindthatBGCNandCrossCBR
tic entities and capture their higher-order relationships. This consistently outperform DAM, indicating that multiple graphs
trend is particularly evident in the LungCancer dataset. When can more accurately learn the relationships among symptoms,
K1 =5,thesemethodsshowlimitedadvantage,likelybecause herbs,andherbsets,presentingmorepreciseinformation.
commonly used herbs forasingle diseaseareeasilyidentified CrossCBRrankssecondbest,benefitingfromcross-viewcon-
without complex interactions. However, their strength in cap- trastivelearningthatenhancessyndromeandtherapeuticmethod
turing intricate data relationships, such as personalized herb representations.However,itsneglectoftheirrelationshipsleads
combinations,becomesapparentatK1 =20. topoorperformanceongraphswithsparseinteractionsbetween
SDPR(SI)andSMGCNachievecomparableperformancebut prescriptionsandsymptomsets.
belowthebest,suggestingthatwhilesyndromesareassociated Our SDPR achieves the best performance compared to all
withindividualherbs,forminganeffectiveprescriptionrequires baselines,anditsadvantagescanbesummarizedasfollows.
(cid:2)
moreinformation,suchastherapeuticmethods.SMGCNlever- Weintegratetherapeuticmethods,akeyelementinguid-
agestraininglosstomodelsyndrome-prescriptionconnections
|     |     |     |     |     |     |     |     | ing | prescription | formulation, |     | into | our model. | By con- |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ------------ | --- | ---- | ---------- | ------- |
but struggles with the sparse, many-to-many relationships be- strainingherbcombinationswiththerapeuticmethodsand
| tween syndromes |     | and therapeutic |     | methods. | This | underscores |     |     |     |     |     |     |     |     |
| --------------- | --- | --------------- | --- | -------- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
capturingtheircomplexrelationshipswithsyndromes,the
| the importance |      | of effectively   | modeling |           | the | TD step | in SD    |          |           |            |              |                |      |             |
| -------------- | ---- | ---------------- | -------- | --------- | --- | ------- | -------- | -------- | --------- | ---------- | ------------ | -------------- | ---- | ----------- |
|                |      |                  |          |           |     |         |          | model    | precisely | associates |              | syndromes      | with | therapeutic |
| for accurate   | herb | recommendations. |          | Moreover, |     | the     | improved |          |           |            |              |                |      |             |
|                |      |                  |          |           |     |         |          | methods, | improving |            | prescription | representation |      | and the     |
multi-labellossmakesSDPR(SI)surpassesSMGCNandMGAT
inthreemetricsontheTCMdatasetandfourontheLungCancer performanceofretrievingactualprescriptions.
(cid:2)
|          |            |                   |     |               |          | G           |     | We  | observe  | a distribution |          | bias in | prescription | between   |
| -------- | ---------- | ----------------- | --- | ------------- | -------- | ----------- | --- | --- | -------- | -------------- | -------- | ------- | ------------ | --------- |
| dataset, | validating | the effectiveness |     | of            | modeling | Syn?H       |     | to  |          |                |          |         |              |           |
|          |            |                   |     |               |          |             |     | the | training | and testing    | datasets |         | (Table II),  | with most |
| enhance  | syndrome   | representation.   |     | Additionally, |          | as SDPR(SI) |     |     |          |                |          |         |              |           |
recommends herb sets similar yet distinct from actual pre- testprescriptionIDsabsentinthetrainingset,creatinga
scriptions, it could provide effective hard-negative therapeutic coldstartchallenge.BaselinesrelyingonIDembeddings
methodsamples.
|     |     |     |     |     |     |     |     | struggle | to represent |     | therapeutic | methods | effectively, | re- |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | --- | ----------- | ------- | ------------ | --- |
MGAT outperforms SMGCN, validating the importance of sultinginpoorprescriptionrecall.Totacklethis,weuse
considering the SD process. However, it lags behind SDPR self-attention to aggregate herb representations. It can
| due to its | reliance | on a tripartite |     | graph | that models |     | SD paths |     |     |     |     |     |     |     |
| ---------- | -------- | --------------- | --- | ----- | ----------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
alsocapturenon-linearinteractionsbetweenprescriptions
betweensinglesymptomsandherbs,divergingfromtheactual
|     |     |     |     |     |     |     |     | and | herbs. Additionally, |     | we  | introduce | a self-correlation |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | --------- | ------------------ | --- |
SDprocess.OntheLungCancerdataset,MGAT＊srelianceonthe
|     |     |     |     |     |     |     |     | constraint | to  | prevent | over-smooth |     | herb representations, |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | ------- | ----------- | --- | --------------------- | --- |
KGfurtherlimitsitsperformance,asfeweroverlappingentities
avoidingtheirexcessivesimilarityfromsharedsymptom
| reduce its | information | gain, | narrowing |     | the gap | with | SMGCN |      |                |     |               |     |              |         |
| ---------- | ----------- | ----- | --------- | --- | ------- | ---- | ----- | ---- | -------------- | --- | ------------- | --- | ------------ | ------- |
|            |             |       |           |     |         |      |       | sets | and mitigating |     | inappropriate |     | associations | between |
andevencausingaslightdecline.
OurproposedSDPRoutperformsallmethods.Especially,it antagonisticortoxicherbs.
(cid:2)
exceeds MGAT on the TCM dataset by 9.75% in r1@5 and Giventhemany-to-manyrelationshipbetweentherapeutic
20.88% in rmrr@5, and on LungCancer by 3.28% in r1@5 methods and syndromes,baselines utilizeBPRlosscap-
and22.22%inrmrr@5.Thisconfirmsthatmodelingtherapeu- ture only partial dependencies. Our therapeutic method-
tic methods and their relationships improves recommendation aware contrastive loss function effectively handles the
accuracyandalignsherbrankingswithactualprescriptions.We
fulldependencies,enhancingthemodel＊sperformancein
summarizeitsadvantagesinthreeaspects.
| (cid:2) |     |     |     |     |     |     |     | complexTCMdiagnosticscenarios. |     |     |     |     |     |     |
| ------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- |
Our model comprehensively follows the complete SD Finally,wepresentthemodelparameternumbersontheTCM
stepstobettersimulatetheTCMherbprescribingprocess, datasetinTableVII.Forherbrecommendation,SDPRachieves
| effectively |     | representing | the | four TCM | diagnostic |     | factors |     |     |     |     |     |     |     |
| ----------- | --- | ------------ | --- | -------- | ---------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
superiorperformancewithparameternumberscomparabletoor
andtheirinteractions,therebyimprovingtheaccuracyof lowerthanmodelssuchasMGAT.Itsslightlyhigherparameter
theherbrecommendationtask. number than some models (e.g., SMGCN) is attributed to the
(cid:2)
attentionmechanismintheherbsetaggregator(SectionIV-C1),
WeuseGCNstomodelhigher-orderinteractionsbetween
|     |     |     |     |     |     |     |     | which represents |     | therapeutic | methods | and | explains | their re- |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ----------- | ------- | --- | -------- | --------- |
symptomsandherbs,improvingtheirrepresentation.
(cid:2)
We propose the symptom set aggregator and herb set lationships with herbs. This added explainability justifies the
|            |     |            |               |     |                 |     |      | modest overhead | essential |     | for practical |     | applications | (see Sec- |
| ---------- | --- | ---------- | ------------- | --- | --------------- | --- | ---- | --------------- | --------- | --- | ------------- | --- | ------------ | --------- |
| aggregator |     | to address | the challenge |     | of representing |     | syn- |                 |           |     |               |     |              |           |
tionV-F).Fortheprescriptionretrievaltask,SDPRsignificantly
dromesandtherapeuticmethodssincenostandardground
reducesparameterrequirementsbyavoidinggraphswiththeex-
(cid:2) truthexistsinclinicalrecords. tensiveprescriptionnodes(23732,showninTableII)employed
Ourtherapeuticmethod-awarecontrastivelearningframe-
|      |             |        |             |     |         |     |           | by baselines | for prescription |     | representation. |     | Instead, | it lever- |
| ---- | ----------- | ------ | ----------- | --- | ------- | --- | --------- | ------------ | ---------------- | --- | --------------- | --- | -------- | --------- |
| work | effectively | models | therapeutic |     | methods |     | and their |              |                  |     |                 |     |          |           |
agestheefficientdeterminingtherapeuticmethodmodule(see
nonlinear relationships with herbs while capturing im- Section IV-C). Consequently, SDPR supports both tasks with
plicit, sparse, many-to-many interactions with the syn- fewer parameters while maintaining explainability, underscor-
ingitspracticaladvantagesandpotentialforreal-worlddeploy-
drome,improvingherbrecommendationperformance.
ment.
C. PrescriptionRetrievalPerformanceComparison
| (RQ2) |     |     |     |     |     |     |     | D. AblationAnalysis(RQ3) |     |     |     |     |     |     |
| ----- | --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | --- | --- | --- | --- | --- |
Then, we compare the overall performance with baselines WeconducttheablationstudyontheTCMdatasettoillustrate
for prescription retrieval task on two datasets, as shown in the effectiveness of several critical components of the SDPR,
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

3746 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
TABLEV
THEOVERALLPERFORMANCECOMPARISONFORPRESCRIPTIONRETRIEVALTASKONTHETCMDATASET,WHEREr 2ANDp 2ISSHORTOFRECALL2 @K 2
ANDPRECISION2 @K 2RESPECTIVELY
TABLEVI
THEOVERALLPERFORMANCECOMPARISONFORPRESCRIPTIONRETRIEVALTASKONTHELUNGCANCERDATASET,WHEREr 2ANDp 2ISSHORTOF
RECALL2 @K 2ANDPRECISION2 @K 2RESPECTIVELY
TABLEVII
COMPARISONOFMODELPARAMETERNUMBERS
TABLEVIII
ABLATIONSTUDYOFTHEKEYCOMPONENTSOFSDPR
including the self-attention mechanism, syndrome representa- of syndromes. Utilizing a pre-training strategy provides the
tion,contrastivelearning,thehard-negativetherapeuticmethod model with rich prior knowledge, enabling it to better model
sampler,andtheauto-correlationconstraintinbothprescription syndrome information. Additionally, gradually introducing in-
recommendationtasksathigherKvalues(K1 =20,K2 =15 formation and constraints guides the model to progressively
&20).TheresultsareshowninTableVIII. andprofoundlymasterthelogicofSD,therebyimprovingthe
1) Effect of Self-Attention Mechanism: We implement accuracyofherbrecommendations.
SDPR-Att,whichusesaveragepoolingofherbembeddingsto 3) Effect of the Contrastive Learning in the Determining
represent therapeutic methods. Compared to SDPR, it shows TherapeuticMethodModule: WeusePCAtovisualizethevec-
a notable performance decline across two tasks, emphasizing tor distributions of SMGCN, SDPR(SI), and SDPR in Fig. 4,
theimportanceofself-attentionusedintheherbsetaggregator highlighting the role of contrastive learning in the determin-
for modeling therapeutic methods. This decline likely arises ing therapeutic method module. Blue dots represent symptom
from the inability of SDPR-Att to capture the intricate syner- embeddings,whilereddotsrepresentherbembeddings.Green
gistic effects among herbs, which also might be in methods dashedlinesmarktheboundarybetweentheirrepresentations.
that rely on single prescription ID modeling like CrossCBR. Aclearboundary,characterizedbytheminimaloverlapbetween
Incontrast,self-attentionnaturallyadaptstotheseinteractions thetwotypesofembeddings,signifieseffectivediscrimination
and effectively addresses the challenge of modeling nonlinear between symptoms and herbs and has better recommendation
relationshipsbetweentherapeuticmethodsandherbs. performance.Additionally,thedistancebetweentheseembed-
2) EffectofSyndrome-InducedPre-TrainingStrategy: Inour dingsreflectstheirdegreeofassociation,withshorterdistances
method,whentheinitialsymptomandherbembeddingsarenot signifying better capture of interactions between symptoms
pre-trainedbutrandomlyinitialized,wedenoteitasSDPR-SI. and herbs in TCM diagnosis. For SMGCN and SDPR(SI), the
From Table VIII, we observe a significant performance drop pre-training strategy in the inducing syndrome module effec-
compared to SDPR, which employs a pre-training strategy in tivelydistinguishestheboundariesbetweensymptomandherb
theinducingsyndromemodule.Thisfindingconfirmstheimpor- representations.Theconsistentdatadistributiontrendsbetween
tanceofthepre-trainingstrategyinenhancingtherepresentation SDPR(SI) and SDPR highlight the role of the pre-training
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3747
Fig.4. ThePCAplotthevectordistributionofsymptomsandherbs.
strategyinproducinghigh-qualityTCMentityrepresentations.
Additionally,thetherapeuticmethod-awarecontrastivelearning
| in SDPR | further | reduces | the distance |     | between | symptoms | and |     |     |     |     |     |
| ------- | ------- | ------- | ------------ | --- | ------- | -------- | --- | --- | --- | --- | --- | --- |
herbscomparedtoSDPR(SI).TableIIIandTableIVunderscore
thecriticalroleofcontrastivelearninginimprovingherbrecom-
mendationperformancebycomparingSDPRwithSDPR(SI).
4) EffectoftheHard-NegativeTherapeuticMethodSampler:
|     |     |     |     |     |     |     |     | Fig. 5. | The performance(Recall1@20 |     | and Recall2@10) | for different |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | -------------------------- | --- | --------------- | ------------- |
We remove the hard-negative therapeutic method sampler in parameter而,C(cid:5)andqonSDPR.
| SDPR, named         |            | SDPR-HNS.        | By              | comparing     | SDPR      |           | and SDPR-  |     |     |     |     |     |
| ------------------- | ---------- | ---------------- | --------------- | ------------- | --------- | --------- | ---------- | --- | --- | --- | --- | --- |
| HNS, we             | find       | that introducing |                 | hard-negative |           | examples  | in the     |     |     |     |     |     |
| herb recommendation |            | task             | helps           | the           | model     | recommend | pre-       |     |     |     |     |     |
| viously             | overlooked | correct          | herbs.          | This          | increases | the       | diversity  |     |     |     |     |     |
| of the recommended  |            | herb             | list, improving |               | recall    | and       | precision, |     |     |     |     |     |
thoughitmaylowertherankingofherbsintoppositions.Higher
recallindicatesthatthemodelretrievesmoreaccurateprescrip-
tionswithhard-negativeexamplesfortheprescriptionretrieval
| task. The | improvement |     | in P2@15 | shows | that | the | proportion |     |     |     |     |     |
| --------- | ----------- | --- | -------- | ----- | ---- | --- | ---------- | --- | --- | --- | --- | --- |
of relevant prescriptions among the top 15 recommendations Fig. 6. The performance(Recall1@5, Rank_MRR@5, and Recall2
|     |     |     |     |     |     |     |     | @20)fordifferentLayerL |     | 1ofgraphG | SH. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --------- | --- | --- |
increases,suggestingbetterlearningoftherelationshipbetween
| syndromes | and       | therapeutic | methods. |         | The slight | decrease      |     | in  |     |     |     |     |
| --------- | --------- | ----------- | -------- | ------- | ---------- | ------------- | --- | --- | --- | --- | --- | --- |
| P2@20     | indicates | that our    | model    | focuses | on         | the diversity | and |     |     |     |     |     |
accuracyofthetopfewrecommendations,whichisacceptable
| in practical | scenarios | to  | avoid | overwhelming |     | physicians | with |     |     |     |     |     |
| ------------ | --------- | --- | ----- | ------------ | --- | ---------- | ---- | --- | --- | --- | --- | --- |
toomuchinformation.
| 5) Effect | of  | the Auto-Correlation |     | Constraint: |     | We  | further re- |     |     |     |     |     |
| --------- | --- | -------------------- | --- | ----------- | --- | --- | ----------- | --- | --- | --- | --- | --- |
movetheauto-correlationconstraintinSDPR-HNSthatnamed
SDPR-(HNS&A).Weintroduceanauto-constraintmechanism
| to enhance | the | model＊s | understanding |     | of the | relationships | be- |                        |                            |           |             |             |
| ---------- | --- | ------- | ------------- | --- | ------ | ------------- | --- | ---------------------- | -------------------------- | --------- | ----------- | ----------- |
|            |     |         |               |     |        |               |     | Fig. 7.                | The performance(Recall1@5, |           | Rank_MRR@5, | and Recall2 |
|            |     |         |               |     |        |               |     | @20)fordifferentLayerL |                            | 2ofgraphG | andG        |             |
tweenherbsandpreventexcessivesimilarityintheirrepresen- SS HH.
| tations.   | Comparing | the      | performance   | of      | SDPR-(HNS&A)    |     | and      |                                         |           |            |                  |               |
| ---------- | --------- | -------- | ------------- | ------- | --------------- | --- | -------- | --------------------------------------- | --------- | ---------- | ---------------- | ------------- |
| SDPR-HNS   | shows     | that     | incorporating |         | auto-constraint |     | into the |                                         |           |            |                  |               |
|            |           |          |               |         |                 |     |          | varying                                 | L1 values | on the TCM | dataset, showing | that the best |
| final loss | function  | improves | the           | model＊s | performance     |     | in two   |                                         |           |            |                  |               |
|            |           |          |               |         |                 |     |          | performanceforbothtasksisachievedwhenL1 |           |            |                  | =3.Similarly, |
prescriptionrecommendationtasks.Althoughtheperformance
|     |     |     |     |     |     |     |     | Fig.7validatesthechoiceofL2 |     |     | =1,withexperimentalresults |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | -------------------------- | --- |
G
difference is insignificant, this may be because HH already indicating that the SDPR performs optimally for two tasks in
capturessomeinteractionsbetweenherbs,limitingthepotential
thissetting.Increasingthenumberoflayerscouldreducemodel
improvementfromauto-constraint.
performanceforbothtasks.
| E. HyperparameterAnalysis(RQ4) |     |     |     |     |     |     |     | F. CaseStudy(RQ5) |     |     |     |     |
| ------------------------------ | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- |
Taking the TCM dataset as an example, we evaluate We analyze two prescriptions from the TCM dataset that
the effect of five critical hyper-parameters: the temperature usesimilarherbstotreatdifferentsymptomsets,asillustrated
parameter 而 with range of {0.05,0.1,0.2,0.3,0.5,0.7,1.0}, in Fig. 8. The three columns show the input symptom set,
C(cid:5)
the max hard-negative sample search length with range theherbsthemodelrecommended,andtheactualprescription
of {16,24,25,26,27,28,29}, the number of herbs in hard- from the Chinese Medical Formula Dictionary. In the model＊s
negative samples q with range of {2,4,5,6,8,10,16,20}, the recommendations,herbsthatappearinactualprescriptionsare
layerL1withrangeof{1,2,3,5},andthelayerL2withrangeof highlightedinred,andrepeatedherbsinthetwoprescriptions
{1,2,3,5}.AsshowninFig.5,theperformanceofherbrecom- are underlined, indicating common combinations. Our model
mendationtaskissensitivetothe而,C(cid:5)andqwhileprescription
effectivelyidentifiesthesameherbsusedinbothprescriptions
C(cid:5)
retrieval not. Thus, we set 而 =0.3, =26 and q =6 based andrecommendsherbswithsimilareffects,suchas※costusroot,§
on herb recommendation task. Fig. 6 illustrates the effect of ※medicated leaven,§ and ※villous amomum fruit,§ which have
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

3748 IEEEJOURNALOFBIOMEDICALANDHEALTHINFORMATICS,VOL.29,NO.5,MAY2025
|     |     |     |     |     | enhances | comprehension |     | of herb | interactions, |     | and makes | itan |
| --- | --- | --- | --- | --- | -------- | ------------- | --- | ------- | ------------- | --- | --------- | ---- |
intelligentaidforanalyzingTCMclinicalrecords.
VI. CONCLUSIONANDFUTUREWORK
|     |     |     |     |     | In this         | paper, | we propose | a                 | novel | prescription | recommen-  |     |
| --- | --- | --- | --- | --- | --------------- | ------ | ---------- | ----------------- | ----- | ------------ | ---------- | --- |
|     |     |     |     |     | dation paradigm |        | based      | on a four-partite |       | graph,       | addressing | the |
challengeofcapturingrelationshipsamongthefourdiagnostic
|     |     |     |     |     | factors in | TCM. | Our | SD-based | prescription |     | recommendation |     |
| --- | --- | --- | --- | --- | ---------- | ---- | --- | -------- | ------------ | --- | -------------- | --- |
model,SDPR,introducesfourspecializedmodulesalignedwith
|     |     |     |     |     | SD steps. | Specifically, |     | we propose | a   | GNN-based | entity | repre- |
| --- | --- | --- | --- | --- | --------- | ------------- | --- | ---------- | --- | --------- | ------ | ------ |
sentationmoduletoenhancesymptomandherbrepresentations,
apre-trainingstrategystrategytomodelsyndromeinformation,
|     |     |     |     |     | a therapeutic | method-aware |     | contrastive |               | learning | framework | to   |
| --- | --- | --- | --- | --- | ------------- | ------------ | --- | ----------- | ------------- | -------- | --------- | ---- |
|     |     |     |     |     | capture       | the implicit | and | complex     | relationships |          | among     | syn- |
dromes,therapeuticmethods,andherbs,andamulti-tasklearn-
| Fig. 8. | The herb recommendation |     | cases: the | same herbs in two |               |     |              |     |       |             |     |           |
| ------- | ----------------------- | --- | ---------- | ----------------- | ------------- | --- | ------------ | --- | ----- | ----------- | --- | --------- |
|         |                         |     |            |                   | ing framework |     | to aggregate | the | whole | SD process. |     | Extensive |
groundtruthsareunderlined.
|     |     |     |     |     | experiments | on          | public | and actual          | TCM | datasets | demonstrate      |     |
| --- | --- | --- | --- | --- | ----------- | ----------- | ------ | ------------------- | --- | -------- | ---------------- | --- |
|     |     |     |     |     | SDPR＊s      | superiority | in     | herb recommendation |     |          | and prescription |     |
retrievaltasks,highlightingitspotentialforpreciseandeffective
TCMherbprescribing.
Despiteitsstrengths,SDPRhaslimitations.Whileitemploys
|     |     |     |     |     | attention | mechanisms |     | to explain | herb | recommendations, |     | these |
| --- | --- | --- | --- | --- | --------- | ---------- | --- | ---------- | ---- | ---------------- | --- | ----- |
digital-drivenexplanationsmaylacktheintuitiveanalysis(e.g.,
text-driven)andflexibleuserinteractionthatalignswithhuman
preferences.Moreover,SDPRcannotpredictherbdosagesand
reliesonsymptomwordinputs,whereasactualTCMscenarios
|     |     |     |     |     | often involve | text-based |                | electronic | medical |             | records | (EHR). In  |
| --- | --- | --- | --- | --- | ------------- | ---------- | -------------- | ---------- | ------- | ----------- | ------- | ---------- |
|     |     |     |     |     | the future,   | we         | will integrate | advanced   |         | techniques, |         | like large |
languagemodels(LLMs),toenhancedataprocessing,explain-
|     |     |     |     |     | ability, and | interactivity. |     | Efforts | will | also focus | on  | mitigating |
| --- | --- | --- | --- | --- | ------------ | -------------- | --- | ------- | ---- | ---------- | --- | ---------- |
hallucinationsinherentinLLMs.Additionally,weplantocol-
Fig.9. TheattentionscoreoffiveherbsrecommendedbySTTPRfor laborate with TCM experts to develop an interactive interface
foursymptoms,includingheavybody,abdominalfullness,borborygmus, alignedwithclinicalworkflows,enablingseamlessintegration
andvomit. withEHRstoenhanceuseradoptionandpracticalapplicability.
theeffectof※whetting theappetiteand dispersingfood.§ This REFERENCES
| indicates                    | our model＊s ability | togenerate | diverse | and clinically |                  |       |      |     |         |         |           |           |
| ---------------------------- | ------------------- | ---------- | ------- | -------------- | ---------------- | ----- | ---- | --- | ------- | ------- | --------- | --------- |
|                              |                     |            |         |                | [1] F. Cheung,   | ※TCM: | Made | in  | China,§ | Nature, | vol. 480, | no. 7378, |
| relevantherbrecommendations. |                     |            |         |                | pp.S82每S83,2011. |       |      |     |         |         |           |           |
Using attention scores, our model could analyze the rela- [2] W.Yuetal.,※Traditionalchinesemedicineandconstitutionalmedicine
tionships between herbs and prescriptions. Fig. 9 presents a inChina,JapanandKorea:Acomparativestudy,§Amer.J.Chin.Med.,
heatmap showing the interrelationships among five herbs in vol.45,no.1,pp.1每12,2017.
the generated second prescription. We observe that ※ginseng,§ [3] X. Liu et al., ※Serum metabolomics reveals compatibility rules of the
antidepressanteffectsofXiaoyaosananditsefficacygroups,§Psychiatry
※costusroot,§and※largeheadatractylodes§playcentralroles,as
Res.,vol.299,2021,Art.no.113827.
indicatedbytheirhighattentionscoreswithotherherbs.Notably, [4] X.Ren,Y.Guo,H.Wang,X.Gao,W.Chen,andT.Wang,※Theintelli-
※costusroot§hasthehighestscorewithotherherbs,whichisalso gentexperienceinheritancesystemfortraditionalChinesemedicine,§J.
oneofthereasonsthemodelrecommendsit. Evidence-BasedMed.,vol.16,no.1,pp.91每100,2023.
|     |     |     |     |     | [5] Y. Song | et al., | ※A review | on different |     | kinds of | artificial | intelligence |
| --- | --- | --- | --- | --- | ----------- | ------- | --------- | ------------ | --- | -------- | ---------- | ------------ |
WeinviteprofessionalTCMphysicianstovalidatetheabove
solutionsintcmsyndromedifferentiationapplication,§Evidence-Based
| findings. | The physicians | point out | that ※costusroot§ | primarily |     |     |     |     |     |     |     |     |
| --------- | -------------- | --------- | ----------------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
Complement.Altern.Med.,vol.2021,no.1,2021,Art.no.6654545.
promotesQicirculationintheprescription,aidinginalleviating [6] Y.Jin,W.Zhang,X.He,X.Wang,andX.Wang,※Syndrome-awareherb
symptomslikeabdominalbloatingandpaincausedbyQistag- recommendationwithmulti-graphconvolutionnetwork,§inProc.IEEE
36thInt.Conf.DataEng.,2020,pp.145每156.
nation.TheQicirculationfunctionof※costusroot§allowsitto
[7] Y.-H.Zhangetal.,※Practitioners＊perspectivesonevaluatingtreatment
synergizeeffectivelywithotherherbs,particularlyinaddressing
|          |               |             |               |            | outcomes | in traditional |     | chinese | medicine,§ | BMC | Complement. | Altern. |
| -------- | ------------- | ----------- | ------------- | ---------- | -------- | -------------- | --- | ------- | ---------- | --- | ----------- | ------- |
| symptoms | related to Qi | obstruction | and dampness. | Hence, its |          |                |     |         |            |     |             |         |
Med.,vol.17,pp.1每10,2017.
[8] E.Guo,P.Li,B.Shang,andG.Zhang,※Exploringcompatibilitylawsin
higherassociationwithotherherbsisimportantinthisprescrip-
traditionalChinesemedicineprescriptionsthroughdatamining,§inProc.
tion.Incontrast,※glycyrrhizauralensis§playsasupportiveand
4thInt.Conf.Bioinf.Intell.Comput.,2024,pp.258每269.
harmonizingroleinthisprescription,soitsoverallimpactwithin
|     |     |     |     |     | [9] Y. Wu, | C. Pei, | C. Ruan, | R. Wang, | Y. Yang, | and | Y. Zhang, | ※Bayesian |
| --- | --- | --- | --- | --- | ---------- | ------- | -------- | -------- | -------- | --- | --------- | --------- |
theformulaisrelativelylower,asreflectedintheattentionscores
networksandchainedclassifiersbasedonSVMfortraditionalChinese
provided by our model. By generating a heatmap illustrating medicalprescriptiongeneration,§inProc.WorldWideWeb,2022,pp.1每22.
[10] P.Jun,H.Zhao,I.C.Jung,E.Jang,O.Kwon,andJ.-H.Jang,※Traditional
herbassociations,ourmodelnotonlyidentifiescoreherbsinthe
|     |     |     |     |     | medicine | classification |     | based on | the nature | and | location of | disease in |
| --- | --- | --- | --- | --- | -------- | -------------- | --- | -------- | ---------- | --- | ----------- | ---------- |
prescriptionbutalsoelucidatestheinteractionsanddegreesof
Parkinson＊sdisease:Aclusteringstudyusingpatternidentificationdisas-
associationamongdifferentherbs.Thisintuitiveanalyticaltool
semblepresentedinclinicalstudies,§J.Integr.Complement.Med.,vol.30,
facilitates a deeper understanding of prescription complexity, no.2,pp.99每106,2024.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore.  Restrictions apply.

YUEetal.:SDPR:PRESCRIPTIONRECOMMENDATIONWITHSYNDROMEDIFFERENTIATIONINTRADITIONALCHINESEMEDICINE 3749
[11] W.Ji,Y.Zhang,X.Wang,andY.Zhou,※Latentsemanticdiagnosisin [23] R. Ying, R. He, K. Chen, P. Eksombatchai, W. L. Hamilton, and
traditionalChinesemedicine,§WorldWideWeb,vol.20,pp.1071每1087, J.Leskovec,※Graphconvolutionalneuralnetworksforweb-scalerecom-
2017. mendersystems,§inProc.24thACMSIGKDDInt.Conf.Knowl.Discov.
[12] X.Wang,Y.Zhang,X.Wang,andJ.Chen,※Aknowledgegraphenhanced DataMining,2018,pp.974每983.
topicmodelingapproachforherbrecommendation,§inProc.Int.Conf. [24] L.Chen,Y.Liu,X.He,L.Gao,andZ.Zheng,※Matchinguserwithitem
DatabaseSyst.Adv.Appl.,Springer,2019,pp.709每724. set:Collaborativebundlerecommendationwithdeepattentionnetwork,§
[13] Y.Jin,W.Ji,Y.Shi,X.Wang,andX.Yang,※Meta-pathguidedgraph inProc.Int.JointConf.Artif.Intell.,2019,pp.2095每2101.
attentionnetworkforexplainableherbrecommendation,§HealthInf.Sci. [25] Q.Dengetal.,※Personalizedbundlerecommendationinonlinegames,§
Syst.,vol.11,no.1,2023,Art.no.5. inProc.29thACMInt.Conf.Inf.Knowl.Manage.,2020,pp.2381每2388.
[14] Z.Ma,Z.Kuang,andL.Deng,※CRPGCN:PredictingcircRNA-disease [26] J.Chang,C.Gao,X.He,D.Jin,andY.Li,※Bundlerecommendationand
associationsusinggraphconvolutionalnetworkbasedonheterogeneous generationwithgraphneuralnetworks,§IEEETrans.Knowl.DataEng.,
network,§BMCBioinf.,vol.22,pp.1每23,2021. vol.35,no.3,pp.2326每2340,Mar.2023.
[15] J.Liu,Z.Kuang,andL.Deng,※GCNPCA:miRNA-diseaseassociations [27] Y.Ma,Y.He,A.Zhang,X.Wang,andT.-S.Chua,※CrossCBR:Cross-
prediction algorithm based on graph convolutional neural networks,§ viewcontrastivelearningforbundlerecommendation,§inProc.28thACM
IEEE/ACMTrans.Comput.Biol.Bioinf.,vol.20,no.2,pp.1041每1052, SIGKDDConf.Knowl.Discov.DataMining,2022,pp.1233每1241.
Mar./Apr.2023. [28] P.Khoslaetal.,※Supervisedcontrastivelearning,§inProc.Adv.Neural
[16] Y.ZhengandY.Chen,※TheidentificationofChineseherbalmedicine Inf.Process.Syst.,2020,pp.18661每18673.
combinationassociationruleanalysisbasedonanimprovedApriorial- [29] Z.Chen,W.Gan,J.Wu,K.Hu,andH.Lin,※Datascarcityinrecom-
gorithmintreatingpatientswithCOVID-19disease,§J.HealthcareEng., mendationsystems:Asurvey,§ACMTrans.RecommenderSyst.,2024,
vol.2022,no.1,2022,Art.no.6337082. doi:10.1145/3639063.
[17] Z.Ma,Z.Kuang,andL.Deng,※NGCICM:Anoveldeeplearning-based [30] W.Wei,L.Xia,andC.Huang,※Multi-relationalcontrastivelearningfor
methodforpredictingcircRNA-miRNAinteractions,§IEEE/ACMTrans. recommendation,§inProc.17thACMConf.RecommenderSyst.,2023,
Comput.Biol.Bioinf.,vol.20,no.5,pp.3080每3092,Sep./Oct.2023. pp.338每349.
[18] X. Chen, C. Ruan, Y. Zhang, and H. Chen, ※Heterogeneous informa- [31] Y. Wei et al., ※Contrastive learning for cold-start recommendation,§ in
tionnetworkbasedclusteringforcategorizationsoftraditionalChinese Proc.29thACMInt.Conf.Multimedia,2021,pp.5382每5390.
medicine formula,§ in Proc. IEEE Int. Conf. Bioinf. Biomed., 2018, [32] C.Wang,W.Ma,C.Chen,M.Zhang,Y.Liu,andS.Ma,※Sequential
pp.839每846. recommendationwithmultiplecontrastsignals,§ACMTrans.Inf.Syst.,
[19] Y.Yang,Y.Rao,M.Yu,andY.Kang,※Multi-layerinformationfusion vol.41,no.1,pp.1每27,2023.
basedongraphconvolutionalnetworkforknowledge-drivenherbrecom- [33] A.Vaswanietal.,※Attentionisallyouneed,§inProc.Adv.NeuralInf.
mendation,§NeuralNetw.,vol.146,pp.1每10,2022. Process.Syst.,2017,pp.5998每6008.
[20] R.v.d.Berg,T.N.Kipf,andM.Welling,※Graphconvolutionalmatrix [34] X.GlorotandY.Bengio,※Understandingthedifficultyoftrainingdeep
completion,§ in Proc. KDD Workshop Deep Learn. Day, 2018. [On- feedforwardneuralnetworks,§inProc.13thInt.Conf.Artif.Intell.Statist.,
line]. Available: https://www.kdd.org/kdd2018/files/deep-learning-day/ 2010,pp.249每256.
DLDay18_paper_32.pdf [35] D.P.KingmaandJ.Ba,※Adam:Amethodforstochasticoptimization,§
[21] X. Wang, X. He, M. F. Wang Feng, and T.-S. Chua, ※Neural graph inProc.3rdInt.Conf.Learn.Representations,2015.[Online].Available:
collaborativefiltering,§inProc.42ndInt.ACMSIGIRConf.Res.Develop. http://arxiv.org/abs/1412.6980
InInf.Retrieval,Paris,France,2019,pp.165每174.
[22] X.He,K.Deng,X.Wang,Y.Li,Y.Zhang,andM.Wang,※LightGCN:
Simplifyingandpoweringgraphconvolutionnetworkforrecommenda-
tion,§inProc.the43rdInt.ACMSIGIRConf.Res.DevelopInf.Retrieval,
2020,pp.639每648.
Authorized licensed use limited to: China Jiliang University. Downloaded on June 02,2026 at 07:30:32 UTC from IEEE Xplore. Restrictions apply.
