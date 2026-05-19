import os
from pathlib import Path
from tqdm import tqdm

# =================================================================
# 1. 路径配置
# =================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 假设脚本放在 MKG/dataset/NEWHERB/ 下，回退两级到 MKG 根目录逻辑（或者直接指定）
# 这里的逻辑是：读取 NEWHERB/kge_data 下的文件
NEWHERB_DIR = SCRIPT_DIR 

INPUT_TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"
OUTPUT_FILE = NEWHERB_DIR / "features/protein2textlong.txt"

# 确保输出目录存在
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

# =================================================================
# 2. 文本生成逻辑
# =================================================================
def generate_protein_desc(entity_name):
    """
    将 STRING ID 转换为中文描述，适配 bert-base-chinese
    """
    # 默认模版
    desc = f"生物靶点蛋白：{entity_name}"
    
    # 尝试解析 STRING 格式
    if "." in entity_name:
        parts = entity_name.split('.', 1)
        tax_id = parts[0]
        prot_id = parts[1]
        
        # 9606 是人类
        if tax_id == "9606":
            organism = "人类(Homo sapiens)"
        else:
            organism = f"物种ID {tax_id}"
            
        # ✅ 中文模版
        if prot_id.startswith("ENSP"):
            desc = f"生物靶点蛋白。Ensembl蛋白编号：{prot_id}。所属物种：{organism}。"
        else:
            desc = f"生物靶点蛋白。标识符：{prot_id}。所属物种：{organism}。"
            
    return desc

# =================================================================
# 3. 主逻辑
# =================================================================
def main():
    print(f">>> 开始生成 Protein 文本特征...")
    print(f"    输入: {INPUT_TYPE_FILE}")
    print(f"    输出: {OUTPUT_FILE}")

    if not INPUT_TYPE_FILE.exists():
        print("Error: 输入文件不存在！请先运行步骤 3 生成 KGE 数据。")
        return

    protein_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        with open(INPUT_TYPE_FILE, 'r', encoding='utf-8') as f_in:
            # 读取每一行，判断类型
            for line in tqdm(f_in, desc="Processing"):
                parts = line.strip().split('\t')
                if len(parts) != 2:
                    continue
                
                entity_name = parts[0]
                entity_type = parts[1]
                
                # 只处理 Protein 类型
                if entity_type == 'Protein':
                    text = generate_protein_desc(entity_name)
                    f_out.write(f"{entity_name}\t{text}\n")
                    protein_count += 1

    print("\n" + "="*30)
    print("处理完成！")
    print(f"✅ 共生成 {protein_count} 条 Protein 描述。")
    print(f"   文件保存至: {OUTPUT_FILE}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()