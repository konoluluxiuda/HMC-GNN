import os
import time
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI

# =================================================================
# 1. 配置
# =================================================================
# API 设置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-YOUR-KEY-HERE")

# 路径配置
SCRIPT_DIR = Path(__file__).parent.resolve()
NEWHERB_DIR = SCRIPT_DIR 

# 输入：实体类型定义
ENTITY_TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"

# 输出：疾病描述文件
OUTPUT_FILE = NEWHERB_DIR / "features/disease2textlong.txt"

# =================================================================
# 2. 初始化 API
# =================================================================
if "YOUR-KEY" in DEEPSEEK_API_KEY and not os.getenv("DEEPSEEK_API_KEY"):
    print("⚠️ 请设置 DEEPSEEK_API_KEY 环境变量。")
    exit()

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# =================================================================
# 3. 定义 LLM 生成函数
# =================================================================
def generate_disease_desc(entity_name):
    """
    将英文疾病名称翻译并解释为中文
    """
    system_prompt = (
        "你是一个医学翻译和病理学专家。请将给定的英文疾病名称翻译成中文，并提供一句简短的医学定义。\n"
        "要求：\n"
        "1. 格式：'[中文名]。[定义]。'\n"
        "2. 定义要专业且简洁，包含病因或主要症状。\n"
        "3. 总长度控制在 50 字以内。"
    )
    
    user_prompt = f"""
请处理疾病："{entity_name}"

示例1：
输入：Insulin-Dependent Diabetes Mellitus
输出：胰岛素依赖型糖尿病。一种因胰岛β细胞破坏导致胰岛素绝对缺乏的自身免疫性疾病。

示例2：
输入：Hypertension
输出：高血压。一种以体循环动脉血压持续升高为主要特征的临床综合征。

示例3：
输入：Intellectual Disability, Borderline
输出：边缘智力障碍。智商在70到85之间，介于正常智力和轻度智力障碍之间的一种状态。

现在，请处理："{entity_name}"
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1, # 翻译需要准确
            max_tokens=100
        )
        ans = response.choices[0].message.content.strip()
        if ans.startswith("输出："): ans = ans[3:].strip()
        return ans
    except Exception as e:
        print(f"\nAPI Error for {entity_name}: {e}")
        return None

# =================================================================
# 4. 主逻辑
# =================================================================
def main():
    print(">>> 1. 确定目标疾病列表...")
    if not ENTITY_TYPE_FILE.exists():
        print("Error: entity2type.txt 不存在")
        return

    target_diseases = []
    with open(ENTITY_TYPE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                name, etype = parts[0], parts[1]
                if etype == 'Disease':
                    target_diseases.append(name)
    
    print(f"   NEWHERB 中共有 {len(target_diseases)} 个疾病实体。")

    # 断点续传
    processed_map = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    processed_map[parts[0]] = parts[1]
    
    todo_list = [d for d in target_diseases if d not in processed_map]
    print(f"   ✅ 已生成: {len(processed_map)}")
    print(f"   🔍 待生成: {len(todo_list)}")

    # 写入已有
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for k, v in processed_map.items():
            f.write(f"{k}\t{v}\n")

    if not todo_list:
        print("所有疾病描述已就绪！")
        return

    print("\n>>> 2. 开始 LLM 生成...")
    
    try:
        for i, name in enumerate(tqdm(todo_list, desc="Translating")):
            desc = generate_disease_desc(name)
            
            if desc:
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{name}\t{desc}\n")
            else:
                # 失败回退：保留英文，但加上中文前缀
                fallback = f"中医疾病或症状：{name} (Disease)"
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{name}\t{fallback}\n")
            
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n   用户中断！")

    print(f"\n>>> 完成！文件已保存至: {OUTPUT_FILE}")
    print("   请记得在 fuse_features.py 中更新对 disease2textlong.txt 的读取。")

if __name__ == "__main__":
    main()