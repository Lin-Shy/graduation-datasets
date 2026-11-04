# blastFoam 原始语料

本目录统一保存 blastFoam 原始语料，供各章题集设计、检索与仿真应用共用。2026-10-14 从工作区根目录迁入，保留文件内容和原目录名称。

| 目录 | 内容 |
| --- | --- |
| `blastFoam_tutorials/` | 教程算例、OpenFOAM 字典与运行脚本 |
| `blastFoam_user_guide/` | 用户手册 PDF 及现有 Markdown 转换内容 |

原始语料与题目、参考答案、评分标注分开维护。构图结果、索引、运行产物与报告不写入本目录。不要直接在教程原件上运行仿真，应复制算例到运行目录。

应用通过 `BLASTFOAM_TUTORIALS` 指向本目录下的 `blastFoam_tutorials/`；相对工作区根目录的路径为 `graduation-datasets/raw-corpus/blastfoam/blastFoam_tutorials/`。历史实验清单中的旧路径保持不变，复现时显式配置新语料根目录。

迁移前后逐文件 SHA-256 已核对，记录见 `migration-manifest.json`。此次只调整归档位置，不补充尚未核实的上游版本或来源信息。
