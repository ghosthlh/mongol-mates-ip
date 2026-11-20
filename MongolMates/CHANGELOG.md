# 变更记录 CHANGELOG

## v1.0.1 (2026-11-20) — 嘴替篇母版冻结

- 用户确认「蒙古萌友03嘴替篇」16 张为满意版本，`approval_status` 由 needs_review 升为 **approved**，版本 v0.1 → v1.0。
- 16 张 master_file 指向认可的 240px 源图；视觉母版正式冻结，防止缺陷旧版回用。
- 否决有缺陷的 1200px「我想静静…」（边缘噪点/半透明异常），记入 rejected_candidates。
- 如实保留 `missing_native_master=true`（用户确认现有均为 240px 直出，无原生高清）；正式高清交付闸门保持不变。
- 更新审计工具使其动态反映审核状态；审计/QA 报告刷新；测试断言更新后 26 项全部通过。
- 冻结记录见 `reports/release_history/master_freeze_2026-11-20.md`。

## v1.0 (2026-11-20) — 项目初始化

- 建立完整项目目录结构（docs/config/characters/assets/series/tools/tests/skills/reports/releases）。
- 建立机器可读唯一事实来源：`config/project.yaml`、`characters.yaml`、`visual_rules.yaml`、`export_rules.yaml`、`asset_manifest.yaml`（48 条）、`annex_assets.yaml`。
- 建立四位角色结构化档案与三套系列 YAML。
- 开发 10 个工具脚本（审计、图片校验、元数据校验、240 导出、透明度检查、预览、整套打包、局部打包、ZIP 校验、共享库）。
- 完成初始资产审计：扫描 60 张图片，48 个表情位建立索引；**47/48 缺原生高清母版**，仅「我想静静…」有 1200px 版本；全部处于待审核。
- 创建 `mongol-mates-director` Skill 与 20 条 AGENTS.md 强制规则。
- 建立 4 组自动化测试与零依赖运行器。
- **未生成、未替换、未修改任何角色图片**。
