import os
from pathlib import Path

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()

# 修正：脚本就在 NEWHERB 目录下，所以 NEWHERB_DIR 就是 SCRIPT_DIR
NEWHERB_DIR = SCRIPT_DIR 

# 输入：KGE 标准实体文件
ENTITIES_FILE = NEWHERB_DIR / "kge_data/entities.txt"
TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"

# 输出：用于 fetch_smiles 的列表
FEATURES_DIR = NEWHERB_DIR / "features"
os.makedirs(FEATURES_DIR, exist_ok=True)
OUTPUT_CHEMICAL_LIST = FEATURES_DIR / "chemicals_for_smiles.txt"

def main():
    print(">>> 正在提取 Component 实体列表...")
    
    if not ENTITIES_FILE.exists() or not TYPE_FILE.exists():
        print("错误：未找到 kge_data 文件，请先运行步骤 3。")
        return

    # 1. 加载类型映射
    entity2type = {}
    with open(TYPE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                entity2type[parts[0]] = parts[1]

    # 2. 筛选 Component
    component_list = []
    with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entity = line.strip()
            if not entity: continue
            
            # 检查类型
            etype = entity2type.get(entity, "Unknown")
            if etype == 'Component':
                component_list.append(entity)

    print(f"   在 {len(entity2type)} 个实体中找到了 {len(component_list)} 个 Component。")

    # 3. 保存列表
    with open(OUTPUT_CHEMICAL_LIST, 'w', encoding='utf-8') as f:
        for chem in component_list:
            f.write(f"{chem}\n")

    print(f"✅ 已保存至: {OUTPUT_CHEMICAL_LIST}")
    print("   下一步：请修改 fetch_smiles.py 的输入路径指向此文件，并运行以获取 SMILES。")

if __name__ == "__main__":
    main()