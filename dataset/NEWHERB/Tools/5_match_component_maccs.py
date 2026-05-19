import os
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
NEWHERB_DIR = SCRIPT_DIR.parent
FEATURES_DIR = NEWHERB_DIR / "features"
os.makedirs(FEATURES_DIR, exist_ok=True)

TARGET_COMPONENTS_FILE = FEATURES_DIR / "chemicals_for_smiles.txt"
SMILES_FILE = FEATURES_DIR / "component2smiles.txt"
OUTPUT_FILE = FEATURES_DIR / "component2maccs.txt"
FAILED_FILE = FEATURES_DIR / "component2maccs_failed.txt"

# 可选：对没有命中的成分使用 PubChem 补查（需要安装 pubchempy 且可联网）
ENABLE_PUBCHEM_LOOKUP = True


def read_component_list(path):
    components = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if name:
                components.append(name)
    return components


def read_component2smiles(path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            comp, smiles = parts[0].strip(), parts[1].strip()
            if comp and smiles:
                mapping[comp] = smiles
    return mapping


def normalize_name(name):
    # 统一大小写并去掉非字母数字字符，提升匹配召回率
    return re.sub(r"[^a-z0-9]", "", name.lower())


def alias_candidates(name):
    # 常见别名分隔符：逗号、分号、斜杠
    parts = re.split(r"[,;/]", name)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    return out


def build_lookup_tables(comp2smiles):
    exact = {}
    norm = {}
    for comp, smiles in comp2smiles.items():
        exact[comp] = smiles
        norm[normalize_name(comp)] = smiles

        for alias in alias_candidates(comp):
            exact.setdefault(alias, smiles)
            norm.setdefault(normalize_name(alias), smiles)
    return exact, norm


def query_smiles_pubchem(name):
    if not ENABLE_PUBCHEM_LOOKUP:
        return None

    try:
        import pubchempy as pcp
    except Exception:
        return None

    try:
        results = pcp.get_compounds(name, 'name')
        if not results:
            return None
        smiles = getattr(results[0], 'canonical_smiles', None)
        if smiles and isinstance(smiles, str) and len(smiles) > 1:
            return smiles
        return None
    except Exception:
        return None


def maccs_bitstring(smiles):
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = rdMolDescriptors.GetMACCSKeysFingerprint(mol)
    return fp.ToBitString()


def main():
    print(">>> 开始匹配成分并生成 MACCS 指纹...")

    if not TARGET_COMPONENTS_FILE.exists():
        print(f"错误：找不到 {TARGET_COMPONENTS_FILE}")
        print("请先运行 4_prepare_components.py 和 5_fetch_smiles_newherb.py")
        return

    if not SMILES_FILE.exists():
        print(f"错误：找不到 {SMILES_FILE}")
        print("请先运行 5_fetch_smiles_newherb.py")
        return

    try:
        import rdkit  # noqa: F401
    except Exception:
        print("错误：未安装 rdkit，无法生成 MACCS 指纹。")
        print("可安装: conda install -c conda-forge rdkit")
        return

    target_components = read_component_list(TARGET_COMPONENTS_FILE)
    comp2smiles = read_component2smiles(SMILES_FILE)
    exact_lookup, norm_lookup = build_lookup_tables(comp2smiles)

    print(f"目标成分数: {len(target_components)}")
    print(f"SMILES 条目数: {len(comp2smiles)}")

    success = 0
    no_smiles = []
    invalid_smiles = []
    matched_exact = 0
    matched_norm = 0
    matched_pubchem = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for comp in target_components:
            smiles = exact_lookup.get(comp)
            if smiles is not None:
                matched_exact += 1

            if smiles is None:
                smiles = norm_lookup.get(normalize_name(comp))
                if smiles is not None:
                    matched_norm += 1

            if smiles is None:
                for alias in alias_candidates(comp):
                    smiles = exact_lookup.get(alias)
                    if smiles is not None:
                        matched_norm += 1
                        break

            if smiles is None:
                smiles = query_smiles_pubchem(comp)
                if smiles is not None:
                    matched_pubchem += 1

            if smiles is None:
                no_smiles.append(comp)
                continue

            bits = maccs_bitstring(smiles)
            if bits is None:
                invalid_smiles.append(comp)
                continue

            out_f.write(f"{comp}\t{bits}\n")
            success += 1

    with open(FAILED_FILE, "w", encoding="utf-8") as f:
        for name in no_smiles:
            f.write(f"NO_SMILES\t{name}\n")
        for name in invalid_smiles:
            f.write(f"INVALID_SMILES\t{name}\n")

    print(f"✅ 生成成功: {success}")
    print(f"   其中精确命中: {matched_exact}")
    print(f"   其中归一化/别名命中: {matched_norm}")
    print(f"   其中 PubChem 补查命中: {matched_pubchem}")
    print(f"❌ 无 SMILES: {len(no_smiles)}")
    print(f"❌ SMILES 无法解析: {len(invalid_smiles)}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"失败记录: {FAILED_FILE}")


if __name__ == "__main__":
    main()
