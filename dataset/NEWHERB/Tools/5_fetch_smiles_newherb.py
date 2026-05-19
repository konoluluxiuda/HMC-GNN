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

# [输入1] 本次任务的目标成分列表 (由 4_prepare_components.py 生成)
TARGET_LIST_FILE = SCRIPT_DIR / "features/chemicals_for_smiles.txt"

# [输入2] 之前已经跑出来的 SMILES 结果 (作为缓存数据库)
OLD_SMILES_FILE = SCRIPT_DIR / "../HERB/component2smiles_llm.txt"

# [输出] 最终的 SMILES 映射文件
OUTPUT_FILE = SCRIPT_DIR / "features/component2smiles.txt"

# [输出] 失败记录
FAILED_FILE = SCRIPT_DIR / "features/fetch_failed.txt"

# =================================================================
# 2. LLM 查询函数 (保持不变)
# =================================================================
if "YOUR-KEY" in DEEPSEEK_API_KEY and not os.getenv("DEEPSEEK_API_KEY"):
    print("⚠️ 请设置 DEEPSEEK_API_KEY 环境变量。")
    # 仅用于演示逻辑，如果没有 key，后续查询会跳过或报错
    client = None
else:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

def get_smiles_smart(entity_name):
    if not client: return None
    prompt = (
        f"I have a chemical compound name: '{entity_name}'.\n"
        f"Please identify this compound (it might be a TCM component or chemical drug) and provide its canonical SMILES string.\n"
        f"Instructions:\n"
        f"1. If it's a standard name, find the SMILES.\n"
        f"2. If it's a synonym or slightly misspelled, correct it and find the SMILES.\n"
        f"3. Reply with ONLY the SMILES string.\n"
        f"4. If absolutely not found, reply with 'None'."
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert chemist."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200
        )
        ans = response.choices[0].message.content.strip()
        if "None" in ans or len(ans) < 2 or " " in ans: return None
        return ans
    except Exception as e:
        print(f"API Error: {e}")
        return None

# =================================================================
# 3. 主逻辑：匹配与增量查询
# =================================================================
def main():
    print(">>> 1. 加载数据...")
    
    # A. 读取目标列表
    if not TARGET_LIST_FILE.exists():
        print(f"Error: 目标文件 {TARGET_LIST_FILE} 不存在。请先运行 4_prepare_components.py")
        return
    with open(TARGET_LIST_FILE, 'r', encoding='utf-8') as f:
        target_chemicals = [l.strip() for l in f if l.strip()]
    print(f"   目标成分总数: {len(target_chemicals)}")

    # B. 读取旧的 SMILES 数据库 (缓存)
    known_smiles = {}
    if OLD_SMILES_FILE.exists():
        print(f"   正在从旧数据集加载已有的 SMILES...")
        with open(OLD_SMILES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    known_smiles[parts[0]] = parts[1]
        print(f"   已加载旧数据: {len(known_smiles)} 条")
    else:
        print(f"   [Warning] 旧数据文件 {OLD_SMILES_FILE} 未找到，将全部重新查询。")

    # C. 读取当前输出文件 (支持断点续传)
    if OUTPUT_FILE.exists():
        print(f"   正在加载当前已保存的进度...")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    # 如果输出文件里有了，优先用输出文件的（覆盖旧数据）
                    known_smiles[parts[0]] = parts[1]

    # =================================================================
    # 4. 筛选出真正需要查询的列表
    # =================================================================
    print("\n>>> 2. 对比与筛选...")
    todo_list = []
    matched_count = 0
    
    # 准备写入文件 (追加模式 'a' 或者 覆盖模式 'w')
    # 为了保证文件整洁，我们先读取所有已知并需要的，一次性写入，然后再追加新的
    
    final_buffer = {} # 暂存所有确定的结果
    
    for chem in target_chemicals:
        if chem in known_smiles:
            final_buffer[chem] = known_smiles[chem]
            matched_count += 1
        else:
            todo_list.append(chem)
            
    print(f"   ✅ 直接匹配成功: {matched_count} (无需查询)")
    print(f"   🔍 需要 LLM 查询: {len(todo_list)}")

    # 先把已匹配的写入文件（覆盖），确保文件内容是最新的且包含旧数据
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for k, v in final_buffer.items():
            f.write(f"{k}\t{v}\n")
            
    if len(todo_list) == 0:
        print("\n🎉 所有成分都已匹配！无需查询。")
        return

    # =================================================================
    # 5. 执行增量查询
    # =================================================================
    print(f"\n>>> 3. 开始查询剩余的 {len(todo_list)} 个成分...")
    
    new_results = {}
    failed_list = []
    SAVE_INTERVAL = 20
    
    try:
        for i, name in enumerate(tqdm(todo_list)):
            smiles = get_smiles_smart(name)
            
            if smiles:
                new_results[name] = smiles
            else:
                failed_list.append(name)
            
            # 增量保存到文件
            if (i + 1) % SAVE_INTERVAL == 0:
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    for k, v in new_results.items():
                        f.write(f"{k}\t{v}\n")
                new_results = {} # 清空缓冲区
            
            time.sleep(0.5) # 避免 API 速率限制

    except KeyboardInterrupt:
        print("\n   用户中断！保存进度...")

    # 保存剩余的
    if new_results:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            for k, v in new_results.items():
                f.write(f"{k}\t{v}\n")

    # 保存失败列表
    if failed_list:
        with open(FAILED_FILE, 'w', encoding='utf-8') as f:
            for name in failed_list:
                f.write(f"{name}\n")

    print(f"\n>>> 完成！")
    print(f"   最终结果文件: {OUTPUT_FILE}")
    print(f"   本次新增失败: {len(failed_list)} (见 {FAILED_FILE})")

if __name__ == "__main__":
    main()