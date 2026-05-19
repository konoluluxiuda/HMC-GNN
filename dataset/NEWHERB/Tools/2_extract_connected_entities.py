import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 修正：既然脚本已经在 NEWHERB 目录下，直接指向同级的 intermediate 即可
SEED_FILE = SCRIPT_DIR / "intermediate/seed_herbs_map.csv"

# KDHR 源数据 (保持绝对路径不变)
KDHR_ROOT = Path("/home/zry/workspace/KDHR/KDHR/KG")

# 修正：输出目录也只需指向同级的 entities
OUTPUT_ENTITIES_DIR = SCRIPT_DIR / "entities"
os.makedirs(OUTPUT_ENTITIES_DIR, exist_ok=True)

# =================================================================
# 2. 工具函数
# =================================================================
def get_target_ids_from_relation(relation_filename, source_ids):
    """
    读取关系文件，查找所有 source_ids 连接的 target_ids。
    增强版：自动识别表头，自动处理列偏移。
    """
    file_path = KDHR_ROOT / "relation" / relation_filename
    if not file_path.exists():
        print(f"Warning: Relation file {relation_filename} not found.")
        return set()

    print(f"   Scanning {relation_filename}...")
    target_ids = set()
    
    try:
        # 1. 读取 CSV，保留表头 (header=0)
        # 这是一个关键修改，因为文件确实有表头
        df = pd.read_csv(file_path, header=0, dtype=str, sep=',')
        
        # 2. 清理列名 (去除空格、冒号等干扰字符)
        # 目的是找到真正的 ID 列，无论前面有没有索引列
        # 例如: columns 可能是 ["Unnamed: 0", ":START_ID", ":END_ID"...] 
        # 或者 [":START_ID", ":END_ID"...]
        
        start_col = None
        end_col = None
        
        for col in df.columns:
            clean_col = col.strip().upper()
            if "START_ID" in clean_col:
                start_col = col
            elif "END_ID" in clean_col:
                end_col = col
        
        if not start_col or not end_col:
            print(f"     Error: Could not find START_ID or END_ID columns. Columns: {df.columns.tolist()}")
            return set()

        # 3. 数据筛选
        # 确保 ID 是字符串并去空格
        df[start_col] = df[start_col].astype(str).str.strip()
        df[end_col] = df[end_col].astype(str).str.strip()
        
        # 筛选出 source 在我们列表中的行
        filtered = df[df[start_col].isin(source_ids)]
        target_ids = set(filtered[end_col].tolist())
        
        print(f"     -> Found {len(target_ids)} related targets (Column: {start_col} -> {end_col})")

    except Exception as e:
        print(f"     Error reading {relation_filename}: {e}")
        
    return target_ids

def save_entity_csv(entity_type, active_ids, output_filename):
    """
    读取 KDHR 的 ID-Name 映射文件，只保留 active_ids 中的实体。
    兼容 Neo4j 风格表头 (:ID, name) 或无表头。
    """
    kdhr_filename = f"{entity_type}ID.csv"
    if entity_type == 'gene': kdhr_filename = "target_geneID.csv"
    if entity_type == 'channel': kdhr_filename = "channel_tropismID.csv"
    
    src_path = KDHR_ROOT / "entity" / kdhr_filename
    dst_path = OUTPUT_ENTITIES_DIR / output_filename
    
    print(f"   Building {output_filename} from {kdhr_filename}...")
    
    if not src_path.exists():
        print(f"Warning: Entity file {kdhr_filename} not found.")
        return

    found_data = []
    encodings = ['utf-8', 'gbk', 'gb18030']
    
    for enc in encodings:
        try:
            # 先尝试读取一行来看看有没有表头关键字
            with open(src_path, 'r', encoding=enc) as f:
                first_line = f.readline()
            
            has_header = ":ID" in first_line or "name" in first_line.lower()
            
            # 读取数据
            if has_header:
                df = pd.read_csv(src_path, header=0, encoding=enc, dtype=str)
                # 寻找 ID 列和 Name 列
                id_col = next((c for c in df.columns if "ID" in c.upper()), df.columns[0])
                name_col = next((c for c in df.columns if "NAME" in c.upper() or "名称" in c), df.columns[1] if len(df.columns)>1 else df.columns[0])
            else:
                df = pd.read_csv(src_path, header=None, encoding=enc, dtype=str)
                id_col = 0
                name_col = 1

            # 筛选
            mask = df[id_col].isin(active_ids)
            filtered_df = df[mask]
            
            for _, row in filtered_df.iterrows():
                found_data.append({'id': row[id_col], 'name': row[name_col]})
            
            break 
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error: {e}")
            return

    if found_data:
        out_df = pd.DataFrame(found_data)
        out_df.drop_duplicates(subset=['id'], inplace=True)
        out_df.to_csv(dst_path, index=False)
        print(f"     -> Saved {len(out_df)} entities to {output_filename}")
    else:
        print(f"     -> No matching entities found for {entity_type}")

# =================================================================
# 3. 主流程
# =================================================================
def main():
    print(">>> 1. 读取种子草药 ID...")
    if not SEED_FILE.exists():
        print("Error: 请先运行 1_match_seeds.py 生成种子映射。")
        return

    df_seed = pd.read_csv(SEED_FILE, dtype=str)
    # 获取所有 KDHR ID 集合
    herb_ids = set(df_seed['kdhr_id'].dropna().tolist())
    print(f"   Active Herb IDs: {len(herb_ids)}")

    # --- 级联提取 ID ---
    print("\n>>> 2. 级联提取关联 ID...")
    
    # Level 1: Herb -> Others
    chemical_ids = get_target_ids_from_relation("herbTOchemical.csv", herb_ids)
    disease_ids = get_target_ids_from_relation("herbTOdisease.csv", herb_ids)
    effect_ids = get_target_ids_from_relation("herbTOeffect.csv", herb_ids)
    channel_ids = get_target_ids_from_relation("herbTOchannelTropism.csv", herb_ids)
    flavor_ids = get_target_ids_from_relation("herbTOflavor.csv", herb_ids)
    
    # Level 2: Chemical -> Protein
    print("   [Deep Search] Chemical -> Protein...")
    protein_ids = get_target_ids_from_relation("chemicalTOprotein.csv", chemical_ids)
    
    # Level 3: Protein -> Gene
    print("   [Deep Search] Protein -> Gene...")
    gene_ids = get_target_ids_from_relation("proteinTOgene.csv", protein_ids)

    # --- 生成实体文件 ---
    print("\n>>> 3. 生成实体定义文件 (CSV)...")
    
    # 保存 Herb (这里比较特殊，我们直接用 seed_herbs_map 的数据，或者从 KDHR 重新拉取)
    # 为了保持 ID 一致性，我们从 KDHR 拉取标准名
    save_entity_csv('herb', herb_ids, 'herb.csv')
    
    save_entity_csv('chemical', chemical_ids, 'chemical.csv')
    save_entity_csv('protein', protein_ids, 'protein.csv')
    save_entity_csv('gene', gene_ids, 'gene.csv')
    save_entity_csv('disease', disease_ids, 'disease.csv')
    save_entity_csv('effect', effect_ids, 'effect.csv')
    save_entity_csv('channel', channel_ids, 'meridian.csv') # 重命名为 meridian
    save_entity_csv('flavor', flavor_ids, 'property.csv')   # 重命名为 property

    print("\n>>> 全部完成！请检查 dataset/NEWHERB/entities/ 目录。")

if __name__ == "__main__":
    main()