# 蒙古萌友 · 项目初始化交付报告

生成时间：2026-11-20　规范版本：v1.0.1　项目根：`MongolMates/`（所有内部路径均相对此目录）

> **2026-11-20 更新**：用户确认嘴替篇为满意版本，该套 16 张已冻结为正式视觉母版（approved / v1.0）。详见 `reports/release_history/master_freeze_2026-11-20.md`。

## 一、已完成（可直接使用的功能）

| 项目 | 内容 |
| --- | --- |
| 目录结构 | 完整建立 docs/config/characters/assets/series/tools/tests/skills/reports/releases 全部核心目录 |
| 规范文档 | 11 份（`docs/`），含角色圣经、美术/构图/背景/修复/交付/QA/工作流/错误案例 |
| 机器可读配置 | `config/` 下 project、characters、visual_rules、export_rules、asset_manifest（48 条）、annex_assets |
| 角色档案 | father/mother/sister/brother 各含 character.yaml + approved/ + references/ |
| 系列工作区 | 三套各含 masters/working/approved/revisions/previews + series.yaml |
| 工具脚本 | 10 个 Python 脚本：审计、图片校验、元数据校验、240 导出、透明度检查、预览、整套打包、局部打包、ZIP 校验、共享库 |
| Skill | `skills/mongol-mates-director/`（SKILL.md + 调用链说明 + 前置检查脚本） |
| 自动化测试 | 4 组 + 零依赖运行器，**26 个用例全部通过**，报告在 `reports/qa/test_results.md` |
| 资产审计 | 扫描 60 张图片，输出 `reports/asset_audit/initial_audit.{md,json}` |
| 可视化总览 | 三套各深/浅底总览图，位于各系列 `previews/` |
| 强制规则 | 根目录 `AGENTS.md` 20 条规则，与 Skill 共用同一规范来源 |

## 二、审计核心结论

- 扫描现有图片 **60 张**；三套标准表情 48 位全部建立索引。
- **48 张均缺已审核的原生高清母版。** 当前登记的成图为 240×240。旧高清版本有质量问题，暂缓纳入母版。
- **被否决候选**：嘴替篇 11「我想静静…」曾有 1200px 版本，但边缘噪点/半透明异常，已否决并记入 rejected_candidates。
- **背景模式对照**：嘴替篇第 10 张「你才是挑战者哦！」为 RGB 白底，符合 `white_scene`（漫画放射线背景应保留）；其余嘴替篇为 RGBA 透明；日常篇/情绪篇现为 RGB 白底（无透明通道）。
- **审核状态**：嘴替篇 16 张 = `approved`（用户确认的正式视觉母版，v1.0）；日常篇 + 情绪篇 32 张 = `needs_review`。
- 角色主色为从 240px 参考图采样的临时值（provisional），未冻结为官方 HEX。
- **48 张源图 SHA-256 与初始扫描 100% 一致，未改动任何原图。**

## 三、缺失素材清单

- 三套共 48 张待补已审核的原生高清母版。
- 附属素材缺口：赞赏引导图 750×560、赞赏致谢图 750×750 尚无文件。

## 四、待人工确认事项

1. ~~母版选择（嘴替篇）~~ ✅ **已解决**：用户 2026-11-20 确认嘴替篇整套满意，16 张已冻结为正式母版 v1.0。
2. ~~「我想静静…」版本取舍~~ ✅ **已解决**：否决有缺陷的 1200px 版，以 240px 认可版为准。
3. **情绪篇文案**：16 张已按成图登记实际中文文案。
4. **日常篇文案**：04、07、16 已按成图更正为「早啊！」「收到！」「开饭啦！」。
5. **日常篇 / 情绪篇母版确认**：两套 32 张仍为 needs_review，待用户确认后冻结。
6. **角色官方色**：须从确认的正式母版提取 HEX 后冻结，替换当前 provisional 值。
7. **正式高清交付**（用户期望"两种尺寸都要有"）：需为嘴替篇补齐**已审核的原生高清母版**。新表情先在原生高清尺寸制作。补齐并审核后，`package_series.py` 才能打出 `original/` + `240x240/` 双版本正式 ZIP。在此之前闸门会正确拒绝——符合规范第 11.1 / 12.3 / 21 节。

## 五、可立即使用的命令

```bash
cd MongolMates
python3 tests/run_tests.py                          # 跑测试（26 项）
python3 tools/audit_assets.py                       # 重新审计
python3 tools/validate_character_metadata.py        # 元数据校验
python3 tools/generate_preview.py --series vol03_reactions   # 生成总览
python3 tools/validate_image.py <图> --background-mode white_scene|transparent
python3 tools/check_transparency.py <图...> --json
python3 skills/mongol-mates-director/scripts/check_task.py vol03_reactions 11  # 任务前置检查
```

## 六、交付压缩包说明

本次为**系统初始化交付**，按指令"不得在初始化时批量重绘/替换原图"，未生成任何正式表情 ZIP（当前缺已审核的原生高清母版）。初始化完成后，按用户指令逐张修复、确认母版，再执行 `package_series.py` / `package_patch.py` 生成可点击下载的正式包。
