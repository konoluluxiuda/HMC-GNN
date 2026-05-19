import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 输入：实体类型文件 (用于筛选哪些是 Meridian)
INPUT_TYPE_FILE = SCRIPT_DIR / "kge_data/entity2type.txt"
# 输出：经络描述文件
OUTPUT_FILE = SCRIPT_DIR / "features/meridian2textlong.txt"

# 确保输出目录存在
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

# =================================================================
# 2. 中医经络知识库 (Hardcoded Knowledge Base)
# =================================================================
# 这种高质量的手写特征比任何自动生成的都要好
MERIDIAN_KNOWLEDGE = {
    "心经": "中药归经：手少阴心经。五行属火。功能：主血脉，藏神。主治：心痛，心悸，失眠，健忘，神志不清，胸胁痛。",
    "心包经": "中药归经：手厥阴心包经。五行属火（相火）。功能：代心受邪，保护心脏。主治：心痛，胸闷，心悸，癫狂，神志病。",
    
    "肝经": "中药归经：足厥阴肝经。五行属木。功能：主疏泄，藏血。主治：胸胁胀痛，黄疸，头痛，眩晕，月经不调，疝气。",
    "胆经": "中药归经：足少阳胆经。五行属木。功能：主决断，贮藏和排泄胆汁。主治：口苦，目眩，疟疾，头痛，颔痛，目外眦痛。",
    
    "脾经": "中药归经：足太阴脾经。五行属土。功能：主运化，统血。主治：胃脘痛，腹胀，呕吐，泄泻，水肿，便血。",
    "胃经": "中药归经：足阳明胃经。五行属土。功能：主受纳腐熟水谷。主治：胃痛，呕吐，消谷善饥，口渴，腹胀，咽喉肿痛。",
    
    "肺经": "中药归经：手太阴肺经。五行属金。功能：主气，司呼吸，主宣发肃降。主治：咳嗽，气喘，咯血，胸痛，咽喉肿痛，外感风寒。",
    "大肠经": "中药归经：手阳明大肠经。五行属金。功能：主传导之官，变化出焉。主治：腹痛，肠鸣，泄泻，痢疾，咽喉肿痛，齿痛。",
    
    "肾经": "中药归经：足少阴肾经。五行属水。功能：藏精，主生长发育与生殖，主水。主治：腰脊痛，遗精，阳痿，水肿，耳鸣，耳聋，气喘。",
    "膀胱经": "中药归经：足太阳膀胱经。五行属水。功能：主贮存和排泄尿液。主治：小便不利，遗尿，癫狂，头痛，目痛，项背腰尻疼痛。",
    
    "三焦经": "中药归经：手少阳三焦经。五行属火（相火）。功能：主持诸气，通行水道。主治：腹胀，水肿，遗尿，耳聋，耳鸣，咽喉肿痛。",
    "小肠经": "中药归经：手太阳小肠经。五行属火。功能：主受盛化物，泌别清浊。主治：少腹痛，腰脊痛，耳聋，目黄，颊肿，咽喉肿痛。"
}

def get_meridian_desc(entity_name):
    """
    根据实体名查找描述。支持模糊匹配（如 '肝' -> '肝经' 的描述）
    """
    # 1. 精确匹配
    if entity_name in MERIDIAN_KNOWLEDGE:
        return MERIDIAN_KNOWLEDGE[entity_name]
    
    # 2. 后缀匹配 (如果实体名是 '肝'，匹配 '肝经')
    for key, desc in MERIDIAN_KNOWLEDGE.items():
        if entity_name in key: # 例如 "肝" in "肝经"
            return desc
            
    # 3. 默认回退
    return f"中药归经：{entity_name}。"

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print(f">>> 开始生成 Meridian (经络) 文本特征...")
    
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
                
                # 只处理 Meridian 类型
                # 注意：之前的脚本可能将 Channel_tropism 映射为了 Meridian
                if entity_type == 'Meridian' or entity_type == 'Channel_tropism':
                    text = get_meridian_desc(entity_name)
                    f_out.write(f"{entity_name}\t{text}\n")
                    count += 1

    print("\n" + "="*30)
    print(f"✅ 共生成 {count} 条经络描述。")
    print(f"   文件保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()