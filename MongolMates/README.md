# 蒙古萌友 IP 制作与资产管理系统

原创角色 IP / 微信静态表情包的跨 AI 一致性生产系统。

## 快速开始

1. 先读 [`docs/00_START_HERE.md`](docs/00_START_HERE.md)。
2. 角色规范见 [`docs/CHARACTER_BIBLE.md`](docs/CHARACTER_BIBLE.md) 与 `config/characters.yaml`。
3. 任何 AI 接手本任务，先读 [`AGENTS.md`](AGENTS.md)。
4. 初始资产审计结论见 [`reports/asset_audit/initial_audit.md`](reports/asset_audit/initial_audit.md)。

## 核心原则（不可违反）

- **图片是最终外观依据**，文字规范只负责描述与约束，不得用重新生成的相似角色替换原版。
- **唯一事实来源**：用户确认的母版 > 用户确认的修订 > CHARACTER_BIBLE > 同系列已审核表情 > AI 方案。
- **不自动批准**：任何工具不得仅凭文件存在或导出成功就把图片设为 `approved`。
- **不伪造高清**：240px 低清图不得放大冒充 `original`。
- **原生高清 + 240×240 两套版本**，每套独立 ZIP；局部修复只交付修改的图片。

## 目录一览

| 目录 | 用途 |
| --- | --- |
| `docs/` | 11 份规范文档（人读） |
| `config/` | 机器可读规范与资产清单（机器读，唯一事实来源） |
| `characters/` | 四位角色档案与母版/参考目录 |
| `assets/` | inbox / 原始件 / 共享参考 / 隔离区 |
| `series/` | 三套系列的工作区（masters/working/approved/revisions/previews） |
| `tools/` | 审计、校验、导出、预览、打包、ZIP 校验脚本 |
| `tests/` | 自动化测试 |
| `skills/` | `mongol-mates-director` 项目专用 Skill |
| `reports/` | 审计与 QA 报告 |
| `releases/` | 正式 ZIP 发布 |

## 工具速查

```bash
python3 tools/validate_character_metadata.py        # 元数据合法性
python3 tools/audit_assets.py                       # 资产审计（只读）
python3 tools/validate_image.py <图> --background-mode transparent|white_scene
python3 tools/check_transparency.py <图...> --json
python3 tools/generate_preview.py --series vol03_reactions
python3 tools/export_240.py --series vol03_reactions --sticker 11   # 需先 approved
python3 tools/package_series.py vol03_reactions                     # 需全部 approved + 高清
python3 tools/package_patch.py vol03_reactions 01 11 --version 1.1
python3 tools/verify_zip.py <包.zip> --expect-count 16
python3 tests/run_tests.py                          # 测试，依赖 Pillow 和 PyYAML
```

## 当前状态摘要

- 三套共 48 张已建立索引，标题和文案以现有成图为准。
- **48 张均缺已审核的原生高清母版。** 当前登记的成图为 240×240。旧高清版本有质量问题，暂缓纳入母版。
- **嘴替篇 16 张已冻结为正式视觉母版**（`approved` / v1.0，用户 2026-11-20 确认满意）；详见 `reports/release_history/master_freeze_2026-11-20.md`。日常篇/情绪篇 32 张仍为 `needs_review`。
- 角色主色为低清参考图采样值（provisional），需由正式母版重新提取后冻结。
- 新表情直接制作原生高清 PNG，以 1200×1200 为默认母版尺寸。审核通过后生成 `240x240/`，随 `original/` 一同交付。

## Git 仓库与跨设备共享

- 仓库根在 **`表情包/`**（即 `MongolMates/` 与 `蒙古萌友/` 的上一级），一次 clone 同时得到规范系统 + 全部原始母版，脚本相对路径全部有效。
- 纳入：`MongolMates/` 全部文本/脚本/报告 + `蒙古萌友/` 全部 60 张原始母版图（约 20MB，直接入库，不用 LFS）。
- 排除：项目内可再生成的派生预览图、表情参考卡、ZIP、`.workbuddy/`、`.DS_Store`（见仓库根 `.gitignore`）。
- 远程：GitHub `ghosthlh/mongol-mates-ip`（SSH `git@github.com:ghosthlh/mongol-mates-ip.git`）。
- 换设备后：`git clone <远程地址>`，`cd MongolMates && python3 tests/run_tests.py` 即可验证完整性。
- 注意：原始图片是官方母版，push/pull 前确认本地为最新，避免覆盖他人已确认的修订。
