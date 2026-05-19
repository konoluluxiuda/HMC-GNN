import json
import os
import re
import time
from pathlib import Path

from openai import OpenAI


SCRIPT_DIR = Path(__file__).parent.resolve()
NEWHERB_DIR = SCRIPT_DIR.parent
FEATURES_DIR = NEWHERB_DIR / "features"

FAILED_FILE = FEATURES_DIR / "component2maccs_failed.txt"
SMILES_FILE = FEATURES_DIR / "component2smiles.txt"
MACCS_FILE = FEATURES_DIR / "component2maccs.txt"

RECOVERED_FILE = FEATURES_DIR / "component2maccs_recovered_llm.txt"
UNRESOLVED_FILE = FEATURES_DIR / "component2maccs_unresolved_after_llm.txt"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
MODEL_NAME = "deepseek-chat"
SLEEP_SEC = 0.4


def read_failed_components(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                reason, name = parts[0].strip(), parts[1].strip()
            else:
                reason, name = "UNKNOWN", parts[0].strip()
            if name:
                items.append((reason, name))
    return items


def read_mapping(path):
    mapping = {}
    if not path.exists():
        return mapping
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            k, v = parts[0].strip(), parts[1].strip()
            if k and v:
                mapping[k] = v
    return mapping


def append_mapping(path, kv_pairs):
    if not kv_pairs:
        return
    with open(path, "a", encoding="utf-8") as f:
        for k, v in kv_pairs:
            f.write(f"{k}\t{v}\n")


def maccs_from_smiles(smiles):
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = rdMolDescriptors.GetMACCSKeysFingerprint(mol)
    return fp.ToBitString()


def extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def query_smiles(client, name):
    prompt = (
        "Given a chemical/component name, do fuzzy synonym matching and return canonical SMILES.\n"
        "If uncertain, return null.\n"
        "Output JSON only with keys: matched_name, smiles, confidence.\n"
        f"name: {name}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a medicinal chemistry expert. Output strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        content = resp.choices[0].message.content.strip()
        data = extract_json(content)
        if not data:
            return None, None, 0.0
        matched_name = data.get("matched_name")
        smiles = data.get("smiles")
        conf = data.get("confidence", 0)
        try:
            conf = float(conf)
        except Exception:
            conf = 0.0
        if not smiles or str(smiles).lower() in {"none", "null", ""}:
            return matched_name, None, conf
        return matched_name, str(smiles).strip(), conf
    except Exception:
        return None, None, 0.0


def main():
    print(">>> 使用 LLM 对失败成分进行模糊匹配并补全 MACCS...")

    if not DEEPSEEK_API_KEY:
        print("错误：未设置 DEEPSEEK_API_KEY 环境变量。")
        return

    if not FAILED_FILE.exists():
        print(f"错误：找不到失败文件 {FAILED_FILE}")
        return

    try:
        import rdkit  # noqa: F401
    except Exception:
        print("错误：未安装 rdkit，无法生成 MACCS。")
        return

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

    failed_items = read_failed_components(FAILED_FILE)
    comp2smiles = read_mapping(SMILES_FILE)
    comp2maccs = read_mapping(MACCS_FILE)

    print(f"失败条目: {len(failed_items)}")
    print(f"已有 SMILES: {len(comp2smiles)}")
    print(f"已有 MACCS: {len(comp2maccs)}")

    recovered_maccs = []
    recovered_smiles = []
    unresolved = []

    for reason, comp in failed_items:
        if comp in comp2maccs:
            continue

        smiles = comp2smiles.get(comp)

        # 对现有 smiles 先重试一次解析
        if smiles:
            bits = maccs_from_smiles(smiles)
            if bits is not None:
                recovered_maccs.append((comp, bits))
                comp2maccs[comp] = bits
                continue

        # LLM fuzzy matching
        _, llm_smiles, conf = query_smiles(client, comp)
        if llm_smiles is None:
            unresolved.append((reason, comp, "NO_LLM_SMILES"))
            time.sleep(SLEEP_SEC)
            continue

        bits = maccs_from_smiles(llm_smiles)
        if bits is None:
            unresolved.append((reason, comp, f"INVALID_LLM_SMILES:{llm_smiles}"))
            time.sleep(SLEEP_SEC)
            continue

        recovered_maccs.append((comp, bits))
        comp2maccs[comp] = bits

        # 仅当置信度较高时，回写 smiles 缓存
        if conf >= 0.5:
            recovered_smiles.append((comp, llm_smiles))
            comp2smiles[comp] = llm_smiles

        time.sleep(SLEEP_SEC)

    append_mapping(MACCS_FILE, recovered_maccs)
    append_mapping(SMILES_FILE, recovered_smiles)

    with open(RECOVERED_FILE, "w", encoding="utf-8") as f:
        for comp, bits in recovered_maccs:
            f.write(f"{comp}\t{bits}\n")

    with open(UNRESOLVED_FILE, "w", encoding="utf-8") as f:
        for reason, comp, tag in unresolved:
            f.write(f"{reason}\t{comp}\t{tag}\n")

    print(f"✅ LLM 补全成功: {len(recovered_maccs)}")
    print(f"✅ 回写 component2maccs: {MACCS_FILE}")
    print(f"✅ 新增记录文件: {RECOVERED_FILE}")
    print(f"❌ 仍未解决: {len(unresolved)}")
    print(f"❌ 未解决文件: {UNRESOLVED_FILE}")


if __name__ == "__main__":
    main()
