import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 输入：实体类型文件
INPUT_TYPE_FILE = SCRIPT_DIR / "kge_data/entity2type.txt"
# 输出：功效描述文件
OUTPUT_FILE = SCRIPT_DIR / "features/effect2textlong.txt"

# 确保输出目录存在
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

# =================================================================
# 2. 文本生成逻辑
# =================================================================
def generate_effect_desc(entity_name):
    """
    为功效实体生成语义增强描述。
    """
    name = entity_name.strip()
    
    # 策略：统一加上"中药功效与主治"的前缀
    # 这样可以将"产后出血"（症状）和"交通心肾"（功能）统一到同一个语义场中
    desc = f"中药功效与主治：{name}。"
            
    return desc

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print(f">>> 开始生成 Effect (功效) 文本特征...")
    print(f"    输入: {INPUT_TYPE_FILE}")
    
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
                
                # 只处理 Effect 类型
                if entity_type == 'Effect':
                    text = generate_effect_desc(entity_name)
                    f_out.write(f"{entity_name}\t{text}\n")
                    count += 1

    print("\n" + "="*30)
    print(f"✅ 共生成 {count} 条功效描述。")
    print(f"   文件保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()