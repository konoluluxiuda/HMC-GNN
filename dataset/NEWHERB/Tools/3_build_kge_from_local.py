import pandas as pd
import os
import random
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置 (修正版)
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()

# 因为脚本就在 dataset/NEWHERB/ 下，直接引用同级目录
ENT_DIR = SCRIPT_DIR / "entities"
REL_DIR = SCRIPT_DIR / "relation"
OUT_DIR = SCRIPT_DIR / "kge_data"
os.makedirs(OUT_DIR, exist_ok=True)

# 种子映射 (用于将 Herb ID 映射回原始中文名)
SEED_MAP_FILE = SCRIPT_DIR / "intermediate/seed_herbs_map.csv"

# 关系配置文件：(文件名, 关系名, 头类型, 尾类型)
RELATION_CONFIG = [
    ('herbTOchemical.csv', 'has_component', 'Herb', 'Component'),
    ('herbTOdisease.csv', 'treats_disease', 'Herb', 'Disease'),
    ('herbTOeffect.csv', 'has_effect', 'Herb', 'Effect'),
    ('herbTOchannelTropism.csv', 'belongs_to_meridian', 'Herb', 'Meridian'),
    ('herbTOflavor.csv', 'has_property', 'Herb', 'Property'),
    ('chemicalTOprotein.csv', 'interacts_with', 'Component', 'Protein'),
    ('proteinTOgene.csv', 'associated_with', 'Protein', 'Gene')
]

# =================================================================
# 2. 加载数据
# =================================================================
def load_entity_maps():
    """加载所有实体 CSV 到 {TypeName: {ID: Name}}"""
    maps = {}
    
    # 1. 特殊处理 Herb：我们需要用回你的原始名字
    if SEED_MAP_FILE.exists():
        df_seed = pd.read_csv(SEED_MAP_FILE, dtype=str)
        # {kdhr_id: my_name}
        # 注意：这里可能有多个 KDHR ID 对应同一个 MyName，字典会自动去重保留一个
        # 但因为我们是 ID -> Name，所以没问题，不同的 ID 都会映射回同一个 Name
        maps['Herb'] = dict(zip(df_seed['kdhr_id'], df_seed['my_name']))
    else:
        print("Error: Seed map not found!")
        return {}

    # 2. 加载其他实体
    type_to_file = {
        'Component': 'chemical.csv', 'Disease': 'disease.csv', 'Effect': 'effect.csv',
        'Meridian': 'meridian.csv', 'Property': 'property.csv', 
        'Protein': 'protein.csv', 'Gene': 'gene.csv'
    }
    
    for type_name, fname in type_to_file.items():
        fpath = ENT_DIR / fname
        if fpath.exists():
            try:
                # 读取带表头的 CSV
                df = pd.read_csv(fpath, dtype=str)
                # 假设列名是 id, name
                if 'id' in df.columns and 'name' in df.columns:
                    maps[type_name] = dict(zip(df['id'], df['name']))
                else:
                    # 无表头回退
                    maps[type_name] = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            except Exception as e:
                print(f"Error reading {fname}: {e}")
                maps[type_name] = {}
        else:
            print(f"Warning: {fname} not found.")
            maps[type_name] = {}
            
    return maps

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print("=== 3. 构建最终 KGE 数据 ===")
    print(f"输入目录: {REL_DIR}")
    print(f"输出目录: {OUT_DIR}")
    
    print(">>> 1. 加载实体映射...")
    entity_maps = load_entity_maps()
    
    all_triplets = []
    entity_types = {} # {EntityName: Type}
    relation_types = {} # {RelationName: (HeadType, TailType)}
    
    print(">>> 2. 构建三元组并翻译 ID -> Name ...")
    for fname, rel_name, h_type, t_type in RELATION_CONFIG:
        fpath = REL_DIR / fname
        if not fpath.exists(): continue
        
        try:
            # 读取关系文件 (:START_ID, :END_ID)
            df = pd.read_csv(fpath, dtype=str)
            
            # 确保列名正确 (generate_kdhr_style_relations.py 生成的是 :START_ID, :END_ID)
            start_col = ':START_ID' if ':START_ID' in df.columns else df.columns[0]
            end_col = ':END_ID' if ':END_ID' in df.columns else df.columns[1]

            # 只有当头尾ID都在我们的映射表中时，才生成三元组
            valid_h = df[start_col].isin(entity_maps[h_type])
            valid_t = df[end_col].isin(entity_maps[t_type])
            valid_df = df[valid_h & valid_t]
            
            count = 0
            for _, row in tqdm(valid_df.iterrows(), total=len(valid_df), desc=rel_name):
                h_id = row[start_col]
                t_id = row[end_col]
                
                h_name = entity_maps[h_type][h_id]
                t_name = entity_maps[t_type][t_id]
                
                all_triplets.append((h_name, rel_name, t_name))
                
                # 记录类型 (注意：如果一个实体有多种类型，会被最后一次覆盖，但层级结构通常不冲突)
                entity_types[h_name] = h_type
                entity_types[t_name] = t_type
                count += 1
            
            relation_types[rel_name] = (h_type, t_type)
            # print(f"   {rel_name}: {count} triplets")
            
        except Exception as e:
            print(f"Error processing {fname}: {e}")

    # 去重
    all_triplets = sorted(list(set(all_triplets)))
    print(f"\n>>> 总共生成 {len(all_triplets)} 条唯一三元组。")
    
    # =================================================================
    # 4. 输出 KGE 文件
    # =================================================================
    print(f">>> 3. 保存文件到 {OUT_DIR} ...")
    
    # 1. entities.txt
    # 确保所有出现过的实体都在列表里
    all_entities_set = set(entity_types.keys())
    all_entities = sorted(list(all_entities_set))
    
    with open(OUT_DIR / "entities.txt", 'w', encoding="utf-8") as f:
        f.write('\n'.join(all_entities))
        
    # 2. relations.txt
    all_rels = sorted(list(relation_types.keys()))
    with open(OUT_DIR / "relations.txt", 'w', encoding="utf-8") as f:
        f.write('\n'.join(all_rels))
        
    # 3. entity2type.txt
    with open(OUT_DIR / "entity2type.txt", 'w', encoding="utf-8") as f:
        for e in all_entities:
            f.write(f"{e}\t{entity_types[e]}\n")
            
    # 4. relation2types.txt
    with open(OUT_DIR / "relation2types.txt", 'w', encoding="utf-8") as f:
        for r in all_rels:
            ht, tt = relation_types[r]
            f.write(f"{r}\t{ht}\t{tt}\n")

    # 5. train/dev/test.tsv
    random.seed(42)
    random.shuffle(all_triplets)
    n = len(all_triplets)
    train_end = int(n * 0.9) # 90% 训练
    val_end = int(n * 0.95)  # 5% 验证
    
    def write_tsv(filename, data):
        with open(OUT_DIR / filename, 'w', encoding="utf-8") as f:
            for h, r, t in data:
                f.write(f"{h}\t{r}\t{t}\n")

    write_tsv("train.tsv", all_triplets[:train_end])
    write_tsv("dev.tsv", all_triplets[train_end:val_end])
    write_tsv("test.tsv", all_triplets[val_end:])
    
    print("✅ 数据集构建完成！")

if __name__ == "__main__":
    main()