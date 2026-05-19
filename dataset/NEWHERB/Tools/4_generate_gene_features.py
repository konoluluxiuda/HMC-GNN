import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 此时 SCRIPT_DIR 是 .../dataset/NEWHERB/

INPUT_TYPE_FILE = SCRIPT_DIR / "kge_data/entity2type.txt"
OUTPUT_FILE = SCRIPT_DIR / "features/gene2textlong.txt"

# 确保输出目录存在
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

# =================================================================
# 2. 文本生成逻辑 (适配 bert-base-chinese)
# =================================================================
def generate_gene_desc(entity_name):
    """
    将 Gene Symbol (如 ABCA1) 转换为中文描述
    """
    # 清理可能存在的空白字符
    name = entity_name.strip()
    
    # 构造中文 Prompt
    # 强调它是“基因”，并且属于“人类”（KDHR大部分是人类靶点）
    desc = f"生物靶点基因。基因符号：{name}。所属物种：人类(Homo sapiens)。"
            
    return desc

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print(f">>> 开始生成 Gene 文本特征...")
    print(f"    输入: {INPUT_TYPE_FILE}")
    
    if not INPUT_TYPE_FILE.exists():
        print("Error: 输入文件不存在！请先运行步骤 3 生成 KGE 数据。")
        return

    gene_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        with open(INPUT_TYPE_FILE, 'r', encoding='utf-8') as f_in:
            # 读取每一行，判断类型
            for line in tqdm(f_in, desc="Processing"):
                parts = line.strip().split('\t')
                if len(parts) != 2:
                    continue
                
                entity_name = parts[0]
                entity_type = parts[1]
                
                # 只处理 Gene 类型
                # 注意：在之前的脚本中，我们将 'Target_gene' 统一为了 'Gene'
                if entity_type == 'Gene' or entity_type == 'Target_gene':
                    text = generate_gene_desc(entity_name)
                    f_out.write(f"{entity_name}\t{text}\n")
                    gene_count += 1

    print("\n" + "="*30)
    print("处理完成！")
    print(f"✅ 共生成 {gene_count} 条 Gene 描述。")
    print(f"   文件保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()