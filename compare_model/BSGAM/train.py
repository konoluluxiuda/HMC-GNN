import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data
from utils import presDataset
from BSGAM import BSGAM
import argparse
import random

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

parser = argparse.ArgumentParser()
parser.add_argument('--batchSize', type=int, default=256)
parser.add_argument('--lr', type=float, default=1e-3)
parser.add_argument('--epoch', type=int, default=200)
parser.add_argument('--att_head_num', type=int, default=4)
parser.add_argument('--att_drop', type=float, default=0.0)
args = parser.parse_args()

# ---------------- seed ----------------
def set_seed(seed=2023):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed()

# ---------------- load graphs ----------------
sh_edge = torch.tensor(np.load('./data/sh_graph_train_1.npy'), dtype=torch.long)
ss_edge = torch.tensor(np.load('./data/ss_graph_train_3.npy'), dtype=torch.long)
hh_edge = torch.tensor(np.load('./data/hh_graph_train_20.npy'), dtype=torch.long) - 390

sh_data = Data(edge_index=sh_edge.t()).to(device)
ss_data = Data(edge_index=ss_edge.t()).to(device)
hh_data = Data(edge_index=hh_edge.t()).to(device)

# ---------------- tensors ----------------
sh_tensor = torch.load('./data/sh_tensor.pt').to(device)
s_tensor = torch.load('./data/s_tensor.pt').to(device)
h_tensor = torch.load('./data/h_tensor.pt').to(device)
kg_oneHot = torch.from_numpy(np.load('./data/herb_oneHot.npy')).float().to(device)

# ---------------- prescription ----------------
prescript = pd.read_csv('./data/prescript.csv')
N = len(prescript)
pS = np.zeros((N, 390))
pH = np.zeros((N, 811))

for i in range(N):
    s = eval(prescript.iloc[i,0])
    h = eval(prescript.iloc[i,1])
    h = [x-390 for x in h]
    pS[i,s] = 1
    pH[i,h] = 1

pS = torch.FloatTensor(pS).to(device)
pH = torch.FloatTensor(pH).to(device)

# ---------------- split ----------------
idx = pd.read_csv('./data/dataset_indices.csv')
test_idx = idx['Test_Indices'].dropna().astype(int).tolist()

N = len(prescript)
all_idx = set(range(N))
train_idx = list(all_idx - set(test_idx))

train_set = presDataset(pS[train_idx], pH[train_idx])
test_set = presDataset(pS[test_idx], pH[test_idx])

train_loader = torch.utils.data.DataLoader(train_set, batch_size=args.batchSize, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=args.batchSize)

# ---------------- model ----------------
model = BSGAM(64, args.att_head_num, args.att_drop).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
criterion = torch.nn.BCEWithLogitsLoss()

# ---------------- train ----------------
best_f1 = 0

for epoch in range(args.epoch):
    model.train()
    total_loss = 0

    for tsid, thid in train_loader:
        optimizer.zero_grad()

        # ---- Step A: graph embedding update ----
        es, eh, rs, rh = model(sh_tensor, s_tensor, h_tensor,
                              sh_data.edge_index, ss_data.edge_index, hh_data.edge_index,
                              None, kg_oneHot, False)

        # ---- Step B: prescription prediction ----
        out = model(sh_tensor, s_tensor, h_tensor,
                    sh_data.edge_index, ss_data.edge_index, hh_data.edge_index,
                    tsid, kg_oneHot, True)

        loss = criterion(out, thid)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # ---------- evaluate ----------
    model.eval()
    p5, r5 = 0, 0

    with torch.no_grad():
        for tsid, thid in test_loader:
            out = model(sh_tensor, s_tensor, h_tensor,
                        sh_data.edge_index, ss_data.edge_index, hh_data.edge_index,
                        tsid, kg_oneHot, True)

            for i in range(len(thid)):
                true = (thid[i]==1).nonzero().flatten()
                top5 = torch.topk(out[i],5)[1]
                hit = sum([1 for x in top5 if x in true])
                p5 += hit/5
                r5 += hit/len(true)

    p5 /= len(test_idx)
    r5 /= len(test_idx)
    f1 = 2*p5*r5/(p5+r5+1e-9)

    print(f"Epoch {epoch:03d} | Loss {total_loss:.3f} | P5 {p5:.4f} R5 {r5:.4f} F1 {f1:.4f}")

    if f1 > best_f1:
        best_f1 = f1
        torch.save(model.state_dict(),'./model/best.pt')
        print("🔥 Best model saved")
