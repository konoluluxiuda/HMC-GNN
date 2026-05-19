import pandas as pd
import os
import re
from pathlib import Path

# === 配置路径 ===
# 你的原始草药文件
MY_HERB_CSV = Path("dataset/HERB/herb.csv")
# KDHR 实体定义目录
KDHR_ENTITY_DIR = Path("/home/zry/workspace/KDHR/KDHR/KG/entity")
# 输出目录
OUTPUT_DIR = Path("dataset/NEWHERB/intermediate")

def clean_name(name):
    """清洗名字：去除括号及内容"""
    name = re.sub(r'[\(（].*?[\)）]', '', str(name))
    return name.strip()

def load_kdhr_herb_map():
    """加载 KDHR herbID.csv，返回 Name -> [IDs] 字典"""
    path = KDHR_ENTITY_DIR / "herbID.csv"
    name_to_ids = {}
    # KDHR 可能有不同的编码
    for enc in ['utf-8', 'gbk', 'gb18030']:
        try:
            df = pd.read_csv(path, header=None, encoding=enc)
            for _, row in df.iterrows():
                kid = str(row[0]).strip()
                kname = str(row[1]).strip()
                if kname not in name_to_ids:
                    name_to_ids[kname] = []
                name_to_ids[kname].append(kid)
            print(f"成功加载 KDHR 草药索引 ({enc})")
            return name_to_ids
        except: continue
    return {}

def main():
    print(">>> 1. 加载 KDHR 草药列表...")
    kdhr_name_map = load_kdhr_herb_map()
    
    print(">>> 2. 匹配 402 个种子草药...")
    df_my = pd.read_csv(MY_HERB_CSV)
    # 清理列名中的 BOM
    df_my.columns = [c.strip().lstrip('\ufeff') for c in df_my.columns]
    
    matched_data = []
    unmatched = []
    
    for _, row in df_my.iterrows():
        raw_name = row['Herb Name in Chinese'].strip()
        clean = clean_name(raw_name)
        
        # 尝试匹配
        if clean in kdhr_name_map:
            # 可能一个名字对应多个 ID，全部提取
            for kid in kdhr_name_map[clean]:
                matched_data.append({
                    'my_name': raw_name,   # 保留你的原始名字
                    'match_name': clean,   # KDHR中的名字
                    'kdhr_id': kid         # KDHR ID
                })
        else:
            unmatched.append(raw_name)
            
    # 保存种子列表
    df_out = pd.DataFrame(matched_data)
    df_out.to_csv(OUTPUT_DIR / "seed_herbs_map.csv", index=False)
    
    print(f"完成！")
    print(f"原有草药数: {len(df_my)}")
    print(f"成功匹配并获取 ID: {len(df_out)} (包含多ID情况)")
    print(f"未匹配: {len(unmatched)}")
    if unmatched:
        print(f"未匹配示例: {unmatched}")

if __name__ == "__main__":
    main()