import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
NEWHERB_DIR = SCRIPT_DIR 
FEATURES_DIR = NEWHERB_DIR / "features"

# 输入：KGE 标准文件
ENTITIES_FILE = NEWHERB_DIR / "kge_data/entities.txt"
TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"

# 输入：需要合并的各分项描述文件
FILES_TO_MERGE = [
    "herb2textlong.txt",
    "component2textlong.txt",
    "disease2textlong.txt",
    "effect2textlong.txt",
    "meridian2textlong.txt",
    "property2textlong.txt",
    "protein2textlong.txt",
    "gene2textlong.txt"
]

# 输出：最终的汇总文件
OUTPUT_FILE = NEWHERB_DIR / "entity2textlong.txt" # 放在 NEWHERB 根目录或 features 下均可，这里放在 features 下
OUTPUT_FILE = FEATURES_DIR / "entity2textlong.txt"

# =================================================================
# 2. 主逻辑
# =================================================================
def main():
    print(">>> 1. 读取基础实体列表...")
    if not ENTITIES_FILE.exists() or not TYPE_FILE.exists():
        print("Error: kge_data 文件缺失。")
        return

    # 读取所有实体
    all_entities = []
    with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
        all_entities = [l.strip() for l in f if l.strip()]
    
    # 读取实体类型 (用于 Fallback)
    entity2type = {}
    with open(TYPE_FILE, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('\t')
            if len(p) == 2: entity2type[p[0]] = p[1]
            
    print(f"   共需处理 {len(all_entities)} 个实体。")

    # -------------------------------------------------------
    # 2. 合并描述文件
    # -------------------------------------------------------
    print("\n>>> 2. 合并各类型的详细描述...")
    merged_text_map = {}
    
    for filename in FILES_TO_MERGE:
        fpath = FEATURES_DIR / filename
        if not fpath.exists():
            print(f"   [Skip] {filename} 不存在 (可能该类型未生成描述)")
            continue
        
        count = 0
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    name, desc = parts[0], parts[1]
                    merged_text_map[name] = desc
                    count += 1
        print(f"   [Load] {filename}: 加载了 {count} 条描述")

    print(f"   当前已有描述覆盖数: {len(merged_text_map)}")

    # -------------------------------------------------------
    # 3. 生成最终文件 (包含 Fallback)
    # -------------------------------------------------------
    print("\n>>> 3. 生成最终 entity2textlong.txt ...")
    
    missing_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entity in tqdm(all_entities):
            # 优先使用合并字典中的描述
            if entity in merged_text_map:
                desc = merged_text_map[entity]
            else:
                # Fallback: 如果没有详细描述，使用 "类型: 名称" 模版
                # 这通常发生在一些 KDHR 引入的边缘实体，或者生成脚本漏掉的实体
                etype = entity2type.get(entity, "Entity")
                desc = f"{etype}: {entity}"
                missing_count += 1
            
            f.write(f"{entity}\t{desc}\n")

    print("\n" + "="*30)
    print("合并完成！")
    print(f"✅ 总实体数: {len(all_entities)}")
    print(f"✅ 详细描述覆盖: {len(all_entities) - missing_count}")
    print(f"⚠️ 使用默认模版: {missing_count}")
    print(f"最终文件已保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()