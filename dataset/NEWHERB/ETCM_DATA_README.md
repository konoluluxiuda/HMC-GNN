# ETCM 数据整理说明

本目录中的 ETCM 数据用于在保留原有 NEWHERB 疾病集合的前提下，补充疾病-基因、草药-基因、草药-成分、成分-基因关系。

## 保留原则

- 原始核心实体文件不覆盖：`entities/disease.csv`、`entities/herb.csv`、`entities/gene.csv`、`entities/chemical.csv` 保留原样。
- 疾病实体只保留原 `disease.csv` 中已有的 2703 条；ETCM 中未匹配到原疾病名的疾病不进入 `disease_completed_etcm.csv`，也不进入最终 disease-gene 关系。
- 草药实体只保留原 `herb.csv` 中已有的 406 条；ETCM 中未匹配到原草药名的草药不进入 `herb_completed_etcm.csv`，也不进入最终 herb-gene / herb-chemical 关系。
- `*_matched.csv` 是最终图谱可直接使用的二列关系文件。
- `*_matched_full.csv` 是对应关系的可追溯版本，保留来源 ID、gene symbol、score、chemical name 等元信息。

## 实体文件

| 文件 | 记录数 | 说明 |
| --- | ---: | --- |
| `entities/disease_completed_etcm.csv` | 2703 | 与原 `disease.csv` 一致，只保留原有疾病实体 |
| `entities/herb_completed_etcm.csv` | 406 | 与原 `herb.csv` 一致，只保留原有草药实体 |
| `entities/gene_completed_etcm.csv` | 5655 | 原基因 + ETCM disease/herb 页面新增 gene symbol |
| `entities/chemical_completed_etcm.csv` | 7135 | 原成分 + ETCM 草药页成分匹配/补充 |
| `entities/disease_etcm_4539.csv` | 4322 | ETCM 疾病页原始抓取结果，扫描 ID 范围 1..4539 |
| `entities/herb_etcm_full.csv` | 402 | ETCM 草药页原始抓取结果 |
| `entities/gene_etcm_from_disease.csv` | 4885 | 疾病页原始 gene 实体 |
| `entities/gene_etcm_from_herb.csv` | 1635 | 草药页原始 gene 实体 |
| `entities/chemical_etcm_full.csv` | 7244 | 草药页原始成分实体 |

## 关系文件

| 文件 | 唯一边数 | 说明 |
| --- | ---: | --- |
| `relation/diseaseTOgene_etcm_matched.csv` | 68955 | 仅保留能按名称匹配到原有 disease 的 disease-gene 边 |
| `relation/herbTOgene_etcm_matched.csv` | 46955 | 仅保留能按名称匹配到原有 herb 的 herb-gene 边 |
| `relation/herbTOchemical_etcm_matched.csv` | 10203 | 仅保留能按名称匹配到原有 herb 的 herb-chemical 边 |
| `relation/chemicalTOgene_etcm_matched.csv` | 74455 | 草药页 Candidate Target Genes 表得到的 chemical-gene 边 |

对应的 `*_matched_full.csv` 文件保留完整来源信息：

- `source_start_id` / `source_end_id`：ETCM 抓取阶段的原始 ID。
- `source`：ETCM 来源字段。
- `gene_symbol`：基因符号。
- `score`：ETCM 草药页 candidate target 的分数，仅 chemical-gene 中存在。
- `chemical_name`：成分名称，仅草药/成分相关关系中存在。

## 匹配规则

疾病匹配：

- 不按 `ETCM_disease_id_*` 直接匹配，因为 ETCM 页面 ID 和原项目 disease ID 不是同一套连续编号。
- 使用标准化后的 disease name 匹配。
- 未匹配疾病只保留在 `disease_etcm_4539.csv` 中用于溯源，不进入最终实体和最终 disease-gene 关系。

草药匹配：

- 优先按中文名匹配原 `herb.csv`。
- 未匹配的 2 个草药只保留在 `herb_etcm_full.csv` 中用于溯源，不进入最终实体和最终 herb 相关关系。

基因匹配：

- 按 gene symbol 匹配。
- 原有 gene 使用原 ID；未匹配 gene 使用 `ETCM_GeneSymbol_*`。

成分匹配：

- 按成分名称及逗号分隔别名匹配。
- 原有成分使用原 ID；未匹配成分保留 ETCM 成分 ID。

## 已清理的中间数据

以下过程数据已删除，避免后续误用：

- 旧版 `4323` 疾病抓取文件。
- failed id 列表。
- 逐项匹配过程明细目录。
- 未匹配前的 raw relation 文件。

最终建议使用 `*_completed_etcm.csv` 作为实体集合，使用 `*_matched.csv` 作为图谱关系；需要检查来源时再查看 `*_matched_full.csv` 和原始 ETCM 实体文件。
