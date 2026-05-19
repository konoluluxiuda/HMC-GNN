import os
import time
import random
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

# 输入：已有描述文件 (你的原始积累)
EXISTING_DESC_FILE = SCRIPT_DIR / "../HERB/entity2textlong_updated.txt"

# 输入：新数据集的实体类型定义
ENTITY_TYPE_FILE = NEWHERB_DIR / "kge_data/entity2type.txt"

# 输出：最终的成分描述文件
OUTPUT_FILE = NEWHERB_DIR / "features/component2textlong.txt"

# =================================================================
# 2. 初始化 API
# =================================================================
if "YOUR-KEY" in DEEPSEEK_API_KEY:
    print("⚠️ 请设置 DEEPSEEK_API_KEY 环境变量。")
    exit()

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# =================================================================
# 3. 定义 LLM 生成函数 (Few-shot Prompting)
# =================================================================
def generate_desc_smart(entity_name):
    """
    使用 DeepSeek 生成符合特定风格的化学成分描述
    """
    # 提供示例，让模型模仿这种"科学、客观、包含结构和活性"的风格
    system_prompt = (
        "你是一个专业的药物化学家和中药学专家。请为给定的化学成分生成一段简洁、专业的中文描述。\n"
        "风格要求：\n"
        "1. 格式：'[英文名]是一种[化学分类]...'\n"
        "2. 内容包括：化学分类、分子结构特征（如化学式、取代基）、理化性质（如溶解性）、主要药理活性或生物功能。\n"
        "3. 长度控制在 50-100 字之间，不要分段，不要废话。"
    )
    
    user_prompt = f"""
请模仿以下示例的风格，描述成分："{entity_name}"

示例1：
输入：ethoxychelerythrine
输出：ethoxychelerythrine是一种苯并菲啶类生物碱，具有显著的亲脂性和碱性，其分子结构中含甲氧基和乙氧基取代基，在紫外光下呈现特征性荧光。

示例2：
输入：gamma-aminobutyric acid
输出：γ-氨基丁酸（GABA）是一种非蛋白质氨基酸，作为中枢神经系统的主要抑制性神经递质，具有降低神经元兴奋性、调节焦虑和促进睡眠的生理功能。

示例3：
输入：gondoic acid
输出：Gondoic acid是一种ω-9单不饱和脂肪酸，化学式为C20H38O2，具有顺式构型，熔点约35°C，主要存在于植物油脂中，具有抗氧化和抗炎特性。

现在，请描述："{entity_name}"
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2, # 低温度保证描述的准确性
            max_tokens=200
        )
        ans = response.choices[0].message.content.strip()
        # 简单的后处理：如果模型输出了 "输出：" 前缀，去掉它
        if ans.startswith("输出："):
            ans = ans[3:].strip()
        return ans
    except Exception as e:
        print(f"\nAPI Error for {entity_name}: {e}")
        return None

# =================================================================
# 4. 主逻辑
# =================================================================
def main():
    print(">>> 1. 加载已有描述库...")
    existing_map = {}
    if EXISTING_DESC_FILE.exists():
        with open(EXISTING_DESC_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    existing_map[parts[0]] = parts[1]
    print(f"   已加载 {len(existing_map)} 条现有描述。")

    print(">>> 2. 确定目标成分列表...")
    target_components = []
    if not ENTITY_TYPE_FILE.exists():
        print("Error: entity2type.txt 不存在")
        return

    with open(ENTITY_TYPE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                name, etype = parts[0], parts[1]
                if etype == 'Component':
                    target_components.append(name)
    
    print(f"   NEWHERB 中共有 {len(target_components)} 个成分实体。")

    # 筛选出真正需要生成的（不在已有库中，且还没生成过的）
    # 支持断点续传：先读取 OUTPUT_FILE
    processed_map = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    processed_map[parts[0]] = parts[1]
    
    todo_list = []
    direct_hit_count = 0
    
    # 准备最终写入的数据结构
    # 我们优先使用已有的，其次使用之前生成的，最后才去 API 生成
    
    print("\n>>> 3. 开始处理...")
    # 打开文件准备追加 (a) 或者 写入 (w)
    # 为了保证完整性，建议每次运行如果是补充模式，以追加方式写入
    # 但为了逻辑简单，我们先把已有的写入内存，最后一起更新
    
    final_buffer = {}
    
    # 1. 先把已生成的加载进去
    final_buffer.update(processed_map) 
    
    for comp in target_components:
        if comp in final_buffer:
            continue # 已经搞定
        
        if comp in existing_map:
            final_buffer[comp] = existing_map[comp] # 直接命中旧库
            direct_hit_count += 1
        else:
            todo_list.append(comp) # 需要 API 生成
            
    print(f"   ✅ 直接命中旧库: {direct_hit_count}")
    print(f"   ✅ 已有生成记录: {len(processed_map)}")
    print(f"   🔍 需要 LLM 生成: {len(todo_list)}")

    # 保存当前进度 (命中旧库的部分)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for k, v in final_buffer.items():
            f.write(f"{k}\t{v}\n")

    # 开始 API 生成
    SAVE_INTERVAL = 20
    new_generated = {}
    
    try:
        for i, name in enumerate(tqdm(todo_list, desc="LLM Generating")):
            desc = generate_desc_smart(name)
            
            if desc:
                new_generated[name] = desc
                # 实时追加到文件
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{name}\t{desc}\n")
            else:
                # 失败回退：使用简单模版，避免下次还查
                fallback = f"中药化学成分：{name}。"
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{name}\t{fallback}\n")
            
            time.sleep(0.2) # 限流

    except KeyboardInterrupt:
        print("\n   用户中断！")

    print(f"\n>>> 完成！")
    print(f"   文件已保存至: {OUTPUT_FILE}")
    print("   请记得在 fuse_features.py 中更新对 component2textlong.txt 的读取。")

if __name__ == "__main__":
    main()