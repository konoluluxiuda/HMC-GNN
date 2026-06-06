# dataset.py
import os
import csv
import torch
import numpy as np
from torch.utils.data import Dataset
from config import Config

class GraphDataManager:
    def __init__(self):
        self.num_nodes = 0
        self.num_relations = 0
        self.herb_indices = []
        self.herb_node_indices = []
        self.disease_indices = []
        self.train_dict = {}
        self.val_dict = None
        self.test_dict = {}

    def _load_node_type_indices(self):
        node_map_path = os.path.join(Config.REC_DATA_DIR, 'node_map.csv')
        if not os.path.exists(node_map_path):
            self.herb_node_indices = sorted(self.herb_indices)
            disease_from_labels = set(self.train_dict.keys()) | set(self.test_dict.keys())
            if self.val_dict is not None:
                disease_from_labels.update(self.val_dict.keys())
            self.disease_indices = sorted(disease_from_labels)
            return

        herb_node_indices = []
        disease_indices = []
        with open(node_map_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_type = str(row.get('node_type', '')).strip()
                try:
                    node_index = int(row.get('node_index', -1))
                except (TypeError, ValueError):
                    continue
                if node_type == 'herb':
                    herb_node_indices.append(node_index)
                elif node_type == 'disease':
                    disease_indices.append(node_index)

        if herb_node_indices:
            self.herb_node_indices = sorted(set(herb_node_indices))
        if disease_indices:
            self.disease_indices = sorted(set(disease_indices))
        
    def load_data(self):
        """直接加载 preprocess_kge.py 生成的 .pt 文件"""
        print(f"正在加载推荐数据: {Config.REC_DATA_DIR} ...")
        
        rec_data_path = os.path.join(Config.REC_DATA_DIR, 'rec_data.pt')
        edge_index_path = os.path.join(Config.REC_DATA_DIR, 'edge_index.pt')
        edge_type_path = os.path.join(Config.REC_DATA_DIR, 'edge_type.pt')
        
        if not os.path.exists(rec_data_path):
            raise FileNotFoundError("未找到处理好的数据，请先运行 preprocess_kge.py")
            
        # 加载字典数据
        data_dict = torch.load(rec_data_path)
        self.num_nodes = data_dict['num_nodes']
        self.num_relations = data_dict['num_relations']
        self.herb_indices = data_dict['herb_indices']
        self.herb_node_indices = sorted(self.herb_indices)
        self.train_dict = data_dict['train_dict']
        self.val_dict = data_dict.get('val_dict')
        self.test_dict = data_dict['test_dict']
        self._load_node_type_indices()
        
        # 加载图结构
        edge_index = torch.load(edge_index_path)
        edge_type = torch.load(edge_type_path)
        
        print(f"数据加载完毕:")
        print(f"  - 节点数: {self.num_nodes}")
        print(f"  - 边数: {edge_index.shape[1]}")
        print(f"  - 训练集 Disease 数量: {len(self.train_dict)}")
        if self.val_dict is not None:
            print(f"  - 验证集 Disease 数量: {len(self.val_dict)}")
        print(f"  - 候选 Herb 数量: {len(self.herb_indices)}")
        print(f"  - Herb 节点数量: {len(self.herb_node_indices)}")
        print(f"  - Disease 节点数量: {len(self.disease_indices)}")
        
        return edge_index, edge_type, self.train_dict, self.test_dict
    
    
    def load_pretrained_features(self):
        """加载 fuse_features.py 生成的 .npy 矩阵"""
        print(f"正在加载预训练特征: {Config.FEATURE_PATH} ...")
        
        if not os.path.exists(Config.FEATURE_PATH):
            print("警告: 未找到特征文件，将使用随机初始化！")
            return None
        
        try:
            # 加载 npy
            emb_matrix = np.load(Config.FEATURE_PATH)
            
            # 检查维度匹配
            # self.num_nodes 是从 rec_data.pt 加载的
            # 务必保证 fuse_features.py 使用的 entities.txt 和 preprocess_kge.py 使用的一致
            if emb_matrix.shape[0] != self.num_nodes:
                print(f"警告: 特征数量 ({emb_matrix.shape[0]}) 与 图节点数量 ({self.num_nodes}) 不匹配！")
                print("这可能是因为 entities.txt 版本不一致。将回退到随机初始化。")
                return None
            
            print(f"成功加载特征矩阵: {emb_matrix.shape}")
            return torch.FloatTensor(emb_matrix)
            
        except Exception as e:
            print(f"加载特征失败: {e}")
            return None
        
    def load_attributes(self):
        """加载属性 Multi-hot 矩阵"""
        if not os.path.exists(Config.ATTR_PATH):
            print("Warning: Attribute matrix not found.")
            return None
        
        print(f"Loading node attributes from {Config.ATTR_PATH}...")
        attr_matrix = torch.load(Config.ATTR_PATH)
        return attr_matrix

class HerbRecDataset(Dataset):
    """
    推荐任务 Dataset
    输入: Disease ID
    输出: (Disease, Pos_Herb, Neg_Herb)
    """
    def __init__(self, train_dict, all_herb_indices):
        self.train_dict = train_dict
        self.disease_list = list(train_dict.keys())
        self.all_herbs = list(all_herb_indices)
        self.num_herbs = len(self.all_herbs)
        
    def __len__(self):
        return len(self.disease_list)
    
    def __getitem__(self, idx):
        # 获取用户(Disease)
        u = self.disease_list[idx]
        pos_list = self.train_dict[u]
        
        # 1. 采样正样本
        if len(pos_list) == 0:
            # 容错处理
            rand_h = self.all_herbs[0]
            return torch.tensor(u), torch.tensor(rand_h), torch.tensor(rand_h)
            
        pos_item = np.random.choice(pos_list)
        
        # 2. 采样负样本
        # 简单优化：假设 all_herbs 足够大，随机采样的概率命中 pos 的几率很低
        # 如果追求严格，可以使用循环检查
        while True:
            # 随机选择一个索引，然后取对应的 herb_id
            rand_idx = np.random.randint(0, self.num_herbs)
            neg_item = self.all_herbs[rand_idx]
            
            if neg_item not in pos_list:
                break
                
        return torch.tensor(u), torch.tensor(pos_item), torch.tensor(neg_item)
