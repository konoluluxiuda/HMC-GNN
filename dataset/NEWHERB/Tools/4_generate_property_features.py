import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 输入：实体类型文件
INPUT_TYPE_FILE = SCRIPT_DIR / "kge_data/entity2type.txt"
# 输出：药性描述文件
OUTPUT_FILE = SCRIPT_DIR / "features/property2textlong.txt"

# 确保输出目录存在
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

# =================================================================
# 2. 中医四气五味知识库 (Hardcoded Knowledge Base)
# =================================================================
PROPERTY_KNOWLEDGE = {
    # --- 四气 (Four Natures) ---
    "寒": "中药四气之寒。药性寒凉。功能：清热、泻火、凉血、解毒。主治：热证、阳证。",
    "热": "中药四气之热。药性温热。功能：温里、散寒、补火、助阳。主治：寒证、阴证。",
    "温": "中药四气之温。药性温和，程度次于热。功能：温经、散寒、通络。主治：寒证。",
    "凉": "中药四气之凉。药性凉爽，程度次于寒。功能：清热、生津、滋阴。主治：热证。",
    "平": "中药四气之平。药性平和。功能：作用和缓，无明显寒热偏性。主治：寒热虚实各证，或用于调和药性。",

    # --- 五味 (Five Flavors) + 附味 ---
    "辛": "中药五味之辛。能散、能行。功能：发散表邪、行气行血。主治：表证、气滞、血瘀。",
    "甘": "中药五味之甘。能补、能和、能缓。功能：补益、和中、调和药性、缓急止痛。主治：虚证、痛证。",
    "酸": "中药五味之酸。能收、能涩。功能：收敛、固涩、生津。主治：体虚多汗、久咳、久泻、遗精、尿频。",
    "苦": "中药五味之苦。能泄、能燥、能坚。功能：通泄（通便）、降泄（降气）、清泄（清火）、燥湿、坚阴。主治：热证、湿证、气逆喘咳。",
    "咸": "中药五味之咸。能下、能软。功能：泻下通便、软坚散结。主治：大便燥结、痰核、瘰疬、癥伽痞块。",
    
    # --- 附味 ---
    "淡": "中药药味之淡。附于甘。能渗、能利。功能：渗湿、利小便。主治：水肿、小便不利。",
    "涩": "中药药味之涩。附于酸。与酸味作用相似。功能：收敛固涩。主治：滑脱诸证（如自汗、盗汗、久泻、滑精）。"
}

def get_property_desc(entity_name):
    """
    根据实体名查找描述。支持模糊匹配。
    """
    name = entity_name.strip()
    
    # 1. 精确匹配
    if name in PROPERTY_KNOWLEDGE:
        return PROPERTY_KNOWLEDGE[name]
    
    # 2. 包含匹配 (防止实体名带有空格或其他字符)
    for key, desc in PROPERTY_KNOWLEDGE.items():
        if key == name:
            return desc
            
    # 3. 默认回退
    return f"中药药性或气味：{name}。"

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print(f">>> 开始生成 Property (药性/气味) 文本特征...")
    
    if not INPUT_TYPE_FILE.exists():
        print("Error: entity2type.txt 不存在！")
        return

    count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        with open(INPUT_TYPE_FILE, 'r', encoding='utf-8') as f_in:
            for line in tqdm(f_in, desc="Processing"):
                parts = line.strip().split('\t')
                if len(parts) != 2: continue
                
                entity_name = parts[0]
                entity_type = parts[1]
                
                # 只处理 Property 类型 (KDHR 中可能叫 Flavor 或 Property)
                if entity_type == 'Property' or entity_type == 'Flavor':
                    text = get_property_desc(entity_name)
                    f_out.write(f"{entity_name}\t{text}\n")
                    count += 1

    print("\n" + "="*30)
    print(f"✅ 共生成 {count} 条药性描述。")
    print(f"   文件保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()