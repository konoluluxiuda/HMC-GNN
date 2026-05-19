import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# KDHR 原始关系目录 (保持不变)
KDHR_REL_DIR = Path("/home/zry/workspace/KDHR/KDHR/KG/relation")

# 修正：脚本已经在 dataset/NEWHERB/ 下，直接指向同级的 entities 文件夹即可
NEWHERB_ENT_DIR = SCRIPT_DIR / "entities"

# 修正：输出目录同理
OUTPUT_REL_DIR = SCRIPT_DIR / "relation"
os.makedirs(OUTPUT_REL_DIR, exist_ok=True)

# =================================================================
# 2. 配置关系与实体的对应 (文件名 : (头实体文件名, 尾实体文件名))
# =================================================================
# 注意：这里的实体文件名对应 dataset/NEWHERB/entities/ 下的文件
RELATION_CONFIG = {
    'herbTOchemical.csv':       ('herb.csv', 'chemical.csv'),
    'herbTOdisease.csv':        ('herb.csv', 'disease.csv'),
    'herbTOeffect.csv':         ('herb.csv', 'effect.csv'),
    'herbTOchannelTropism.csv': ('herb.csv', 'meridian.csv'), # 注意我们之前把 channel 重命名为了 meridian
    'herbTOflavor.csv':         ('herb.csv', 'property.csv'), # 注意我们之前把 flavor 重命名为了 property
    'chemicalTOprotein.csv':    ('chemical.csv', 'protein.csv'),
    'proteinTOgene.csv':        ('protein.csv', 'gene.csv'),
    'herbTOtaboo.csv':          ('herb.csv', None) # 如果你有taboo的话，没有可忽略
}

# =================================================================
# 3. 辅助函数
# =================================================================
def load_valid_ids(filename):
    """读取实体CSV，获取所有有效的 ID 集合"""
    path = NEWHERB_ENT_DIR / filename
    if not path.exists():
        print(f"  [Warn] Entity file not found: {filename}")
        return set()
    
    try:
        # 假设实体文件格式为: id,name (带表头)
        df = pd.read_csv(path, dtype=str)
        if 'id' in df.columns:
            return set(df['id'].tolist())
        else:
            # 如果没有表头，假设第一列是 ID
            return set(df.iloc[:, 0].tolist())
    except Exception as e:
        print(f"  [Error] Reading {filename}: {e}")
        return set()

def process_relation(rel_filename, head_filename, tail_filename):
    """读取 KDHR 关系，过滤，保存"""
    src_path = KDHR_REL_DIR / rel_filename
    dst_path = OUTPUT_REL_DIR / rel_filename
    
    if not src_path.exists():
        return

    # 1. 加载有效 ID 集合
    valid_heads = load_valid_ids(head_filename)
    valid_tails = load_valid_ids(tail_filename)
    
    if not valid_heads or not valid_tails:
        print(f"Skipping {rel_filename} due to missing entity IDs.")
        return

    print(f"Processing {rel_filename}...")
    
    try:
        # 2. 读取原始关系文件
        # 自动检测分隔符和表头逻辑 (复用之前的经验)
        df = None
        try:
            df = pd.read_csv(src_path, header=0, dtype=str)
        except:
            df = pd.read_csv(src_path, header=None, dtype=str)
            
        # 寻找 ID 列
        start_col, end_col = None, None
        
        # 策略 A: 根据列名查找
        for col in df.columns:
            c_str = str(col).upper().strip()
            if "START_ID" in c_str: start_col = col
            elif "END_ID" in c_str: end_col = col
            
        # 策略 B: 如果找不到列名，且只有2列，假设 0, 1
        if (start_col is None or end_col is None) and len(df.columns) >= 2:
            # 重新读取无表头模式，防止第一行被吞
            df = pd.read_csv(src_path, header=None, dtype=str)
            # KDHR 有些文件第一列是索引，第二列才是 ID，需要小心
            # 通常 KDHR 关系文件是: START_ID, END_ID, TYPE (可选)
            # 或者: Index, START_ID, END_ID ...
            # 这里我们做一个简单的启发式检查
            sample_val = str(df.iloc[0, 0])
            if sample_val.isdigit() and int(sample_val) < 10000 and len(df.columns) > 2:
                # 可能是索引列，尝试 1, 2
                start_col, end_col = 1, 2
            else:
                start_col, end_col = 0, 1
        
        if start_col is None or end_col is None:
            print(f"  [Error] Could not identify ID columns for {rel_filename}")
            return

        # 3. 过滤
        # 清理数据
        df[start_col] = df[start_col].astype(str).str.strip()
        df[end_col] = df[end_col].astype(str).str.strip()
        
        # 核心过滤逻辑：保留 头在有效头集合 且 尾在有效尾集合 的行
        mask = df[start_col].isin(valid_heads) & df[end_col].isin(valid_tails)
        filtered_df = df[mask]
        
        # 4. 保存
        # 我们保存为标准的 CSV: start_id, end_id
        # 不保留原始文件的其他杂乱列，保持纯净
        final_df = filtered_df[[start_col, end_col]]
        # 重命名列以便于阅读
        final_df.columns = [':START_ID', ':END_ID']
        
        final_df.to_csv(dst_path, index=False)
        print(f"  -> Saved {len(final_df)} relations to {dst_path}")
        
    except Exception as e:
        print(f"  [Error] Processing {rel_filename}: {e}")

# =================================================================
# 4. 主逻辑
# =================================================================
def main():
    print("=== 生成 KDHR 风格的关系文件 ===")
    print(f"输入实体目录: {NEWHERB_ENT_DIR}")
    print(f"输出关系目录: {OUTPUT_REL_DIR}")
    print("-" * 30)
    
    for rel_file, (h_file, t_file) in RELATION_CONFIG.items():
        if t_file is None: continue # 跳过配置不全的
        process_relation(rel_file, h_file, t_file)
        
    print("\n✅ 所有关系文件生成完毕。")

if __name__ == "__main__":
    main()