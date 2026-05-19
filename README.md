# HMC-GNN

**Heterogeneous Multi-view Contrastive Graph Neural Network** for Traditional Chinese Medicine (TCM) Herb Recommendation.

A multi-modal, self-supervised graph learning framework that recommends herbs for diseases by jointly modeling heterogeneous knowledge graph structure, herbal properties (性味归经), chemical components, and disease text semantics.

---

## Overview

HMC-GNN constructs a heterogeneous graph from TCM knowledge and learns disease-aware herb representations via:

- **RGCN** — Relational Graph Convolution for heterogeneous message passing
- **Multi-modal Fusion** — Gated/element-wise fusion of structural, attribute (property/meridian), chemical (SMILES/BERT), and disease text features
- **Self-supervised Learning** — Three complementary SSL objectives:
  - *Graph Contrastive* (InfoNCE between perturbed graph views)
  - *Cross-Modal Contrastive* (align GNN embeddings with chemical features)
  - *Property-Chemical Alignment* (align 性味归经 with chemical modality)

---

## Project Structure

```
HMC-GNN/
├── config.py                  # Hyperparameters & path configuration
├── dataset.py                 # GraphDataManager & HerbRecDataset
├── model.py                   # HMC_GNN_SSL model architecture
├── train.py                   # Training loop with experiment switches
├── utils.py                   # Evaluator, set_seed, helpers
├── preprocess_kge.py          # Build heterogeneous graph from KGE data
├── preprocess_paper_graph.py  # Build paper-style graph (Jaccard + Top-K)
├── preprocess_semantic_graph.py # Build semantic graph (TF-IDF similarity)
├── .gitignore
├── checkpoints/               # Saved model weights (gitignored)
├── dataset/
│   └── NEWHERB/
│       ├── entities/          # Entity CSV files (herb, disease, chemical, etc.)
│       ├── features/          # Text & chemical features
│       ├── relation/          # Relation CSV files
│       ├── kge_data/          # KGE training data
│       ├── recommendation_data/  # Main graph data (edge_index, rec_data, etc.)
│       ├── paper_graph_data/     # Jaccard + Top-K graph variant
│       ├── full_graph_data/      # Full graph without pruning (gitignored)
│       ├── tfidf_graph_data/     # TF-IDF anti-hub graph variant
│       ├── semantic_data/        # TF-IDF semantic graph variant
│       ├── kdhr_newherb/         # KDHR-style intermediate data
│       └── Tools/                # Dataset construction scripts
└── fig/                       # Visualization scripts & figures
```

---

## Dataset: NEWHERB

The dataset is built from TCM knowledge bases and includes the following entity types:

| Entity | Description |
|--------|-------------|
| Herb (中药) | TCM herbs |
| Disease (疾病) | Diseases / symptoms |
| Chemical (化学成分) | Chemical components of herbs |
| Effect (功效) | Therapeutic effects |
| Property (性味) | Herbal flavor / nature (寒热温凉) |
| Meridian (归经) | Channel tropism |
| Gene (基因) | Genetic targets |
| Protein (蛋白质) | Protein targets |

**Relations** include: `treats_disease`, `has_component`, `has_effect`, `has_property`, `belongs_to_meridian`, etc.

### Multi-modal Features

| Feature | Source | Dimension |
|---------|--------|-----------|
| Structure Embedding | Random ID → Xavier init | 256 |
| Base Attributes (性味归经) | Multi-hot encoding | ~100+ |
| Chemical Dense | BERT / SMILES embeddings | 768 |
| Chemical Fingerprint | MACCS / Morgan fingerprints | ~1024 |
| Disease Text | Chinese BERT embeddings | 768 |

---

## Usage

### 1. Install Dependencies

```bash
pip install torch torch-geometric numpy pandas scikit-learn tqdm
```

### 2. Preprocess Graph Data

Choose your graph construction strategy:

```bash
# Standard heterogeneous graph (from KGE relations)
python preprocess_kge.py

# Paper-style graph (Jaccard similarity + Top-K pruning)
python preprocess_paper_graph.py

# Semantic similarity graph (TF-IDF on entity descriptions)
python preprocess_semantic_graph.py
```

### 3. Train

Edit `train.py` to configure experiment switches, then run:

```bash
python train.py
```

### Experiment Switches (in `train.py`)

```python
# Graph selection (choose one)
USE_TFIDF_GRAPH = False      # TF-IDF anti-hub graph
USE_FULL_GRAPH = False       # Full graph (no pruning)
USE_PAPER_GRAPH = True       # Jaccard + Top-K (paper default)
USE_SEMANTIC_GRAPH = False   # TF-IDF semantic graph

# Feature injection
USE_BASE_ATTR = True         # 性味归经 multi-hot attributes
USE_CHEM_DENSE = True        # BERT/SMILES chemical features
USE_CHEM_FINGERPRINT = True  # MACCS fingerprint features
USE_DISEASE_TEXT = True      # Disease BERT text features

# Fusion strategy
FUSION_MODE = 'gated'        # 'add' | 'gated'

# SSL objectives
USE_CROSS_MODAL = True       # Cross-modal contrastive learning
CROSS_MODAL_WEIGHT = 0.2     # Loss weight

USE_PROP_CHEM_ALIGN = True   # Property-Chemical alignment
PROP_CHEM_WEIGHT = 0.5       # Loss weight
```

---

## Model Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Input Features                      │
├───────────┬───────────┬───────────┬─────────────────┤
│ Structure │ Attribute │ Chemical  │ Disease Text    │
│ (ID Emb)  │ (Multi-   │ (BERT /   │ (BERT)          │
│           │  hot)     │  SMILES)  │                 │
└─────┬─────┴─────┬─────┴─────┬─────┴────────┬────────┘
      │           │           │              │
      ▼           ▼           ▼              ▼
┌─────────────────────────────────────────────────────┐
│           Multi-modal Alignment (Linear)             │
│         (project all modalities to emb_dim)          │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│            Feature Fusion (Add / Gated)              │
│         x_fused = x_st ⊕ x_attr ⊕ x_chem ⊕ x_dis    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              PresRecRF Fusion MLP                    │
│            x = ReLU(W · x_fused + b)                 │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              RGCN Propagation × 2 Layers             │
│         (with BatchNorm + ELU + Dropout)             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│           Layer Aggregation (Concat + Linear)        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │  Node Embeddings │
              └─────────────────┘

Self-Supervised Learning Objectives:
├── Graph Contrastive: InfoNCE between 2 perturbed views
├── Cross-Modal Contrastive: GNN ↔ Chemical features
└── Property-Chemical Alignment: 性味归经 ↔ Chemical
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Embedding dim | 256 |
| Hidden dim | 256 |
| RGCN layers | 2 |
| Optimizer | Adam |
| Learning rate | 1e-3 |
| Weight decay | 1e-5 |
| Batch size | 1024 |
| Max epochs | 800 |
| Early stopping patience | 50 |
| SSL temperature | 0.2 |
| SSL regularization | 0.01 |
| Edge dropout rate | 0.1 |
| Evaluation metrics | Precision@K, Recall@K, F1@K (K=5,10,20,50) |

---

## Citation

If you use this code or dataset in your research, please consider citing the relevant paper (TBA).

---

## License

TBD
