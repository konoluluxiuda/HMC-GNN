import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()

# 源文件：旧的详细描述文件
SOURCE_TEXT_FILE = SCRIPT_DIR / "../HERB/entity2textlong_updated.txt"

# 新数据集的目标文件
NEWHERB_DIR = SCRIPT_DIR 
ENTITIES_FILE = NEWHERB_DIR / "kge_data/entities.txt"
TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"

# 输出文件
FEATURES_DIR = NEWHERB_DIR / "features"
os.makedirs(FEATURES_DIR, exist_ok=True)
OUTPUT_FILE = FEATURES_DIR / "herb2textlong.txt"

# =================================================================
# 2. 辅助函数
# =================================================================
def load_source_descriptions():
    """加载旧的 entity2textlong_updated.txt"""
    print(f">>> 加载源描述文件: {SOURCE_TEXT_FILE}")
    desc_map = {}
    
    if not SOURCE_TEXT_FILE.exists():
        print(f"Error: 源文件不存在！")
        return desc_map

    with open(SOURCE_TEXT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t', 1)
            if len(parts) == 2:
                name, desc = parts[0], parts[1]
                desc_map[name] = desc
            # 处理可能的别名匹配（如果源文件包含别名，这里简单处理）
            
    print(f"   已加载 {len(desc_map)} 条原始描述。")
    return desc_map

def load_target_entities():
    """加载 NEWHERB 中的所有实体及其类型"""
    print(f">>> 加载新数据集实体...")
    entities = []
    with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
        entities = [l.strip() for l in f if l.strip()]
    
    entity2type = {}
    with open(TYPE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                entity2type[parts[0]] = parts[1]
                
    # 只筛选出 Herb 类型的实体
    herb_list = [e for e in entities if entity2type.get(e) == 'Herb']
    print(f"   在 {len(entities)} 个实体中找到 {len(herb_list)} 个草药实体。")
    return herb_list

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    if not ENTITIES_FILE.exists():
        print("Error: 请先完成步骤 3 (构建 KGE 数据)。")
        return

    # 1. 加载数据
    source_map = load_source_descriptions()
    target_herbs = load_target_entities()
    
    # 2. 匹配与生成
    print(f"\n>>> 生成 Herb 文本特征...")
    found_count = 0
    missing_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for herb in tqdm(target_herbs):
            desc = ""
            
            # 策略 A: 优先使用原始详细描述
            if herb in source_map:
                desc = source_map[herb]
                found_count += 1
            
            # 策略 B: 尝试去除括号匹配 (例如 "海藻（羊栖菜）" -> "海藻")
            elif "(" in herb or "（" in herb:
                import re
                clean_name = re.sub(r'[\(（].*?[\)）]', '', herb).strip()
                if clean_name in source_map:
                    desc = source_map[clean_name]
                    found_count += 1
                else:
                    # 还是没找到，使用 Template
                    desc = f"Traditional Chinese Medicine Herb: {herb}"
                    missing_count += 1
            
            # 策略 C: 完全没找到 (可能是 KDHR 补充的新草药)
            else:
                desc = f"Traditional Chinese Medicine Herb: {herb}"
                missing_count += 1
            
            # 写入文件
            f.write(f"{herb}\t{desc}\n")

    print("\n" + "="*30)
    print("Herb 文本处理完成！")
    print(f"✅ 使用原始详细描述: {found_count}")
    print(f"⚠️ 使用通用模版描述: {missing_count}")
    print(f"结果已保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()