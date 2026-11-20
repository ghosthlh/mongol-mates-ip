# AGENTS.md — 蒙古萌友项目强制规则

本文件是任何 AI 编码助手（Codex / Claude / WorkBuddy 等）处理《蒙古萌友》任务时的强制行为约束。
项目专用 Skill 见 `skills/mongol-mates-director/SKILL.md`，二者使用同一规范来源（`config/*.yaml` + `docs/`），不得各自复制出冲突规则。

## 必读顺序

1. 本文件。
2. `config/project.yaml`、`config/characters.yaml`、`config/visual_rules.yaml`、`config/export_rules.yaml`、`config/asset_manifest.yaml`。
3. `docs/CHARACTER_BIBLE.md` 及目标角色的 `characters/<id>/character.yaml`。
4. 目标表情的元数据条目（在 asset_manifest.yaml 中按 series_id + sticker_id 查找）。

## 20 条强制规则

1. 所有蒙古萌友任务必须先读项目规范（上述必读顺序）。
2. 所有角色任务必须读对应角色母版及 YAML；无母版时明确说明“尚无确认母版”。
3. 不得自行重设计角色身份、头饰、发型、辫子结构、胡子、基础服装与颜色。
4. 不得自动把候选图片批准为正式版本（approved 只能来自用户明确确认）。
5. 新表情先在原生高清尺寸制作并保留原始 PNG 与来源，审核后再缩小到 240×240。存在质量问题的旧高清暂缓纳入母版。
   已制作表情的标题和文案以现有成图为准。不得将低清放大图登记为原生高清。
6. 不得用拉伸或复制像素行模拟自然身体结构（禁止延长底边、垂直拉长衣服、单色块填充）。
7. 不得覆盖或删除原始输入文件（source_file 只读留档）。
8. 不得未经允许扩大修改范围（只改用户指定的区域）。
9. 不得删除复杂场景应保留的白底（background_mode=white_scene）。
10. 不得误删气团、眼白、牙齿、白色高光、袖口白色装饰等原有白色区域。
11. 必须对导出文件执行完整性检查（verify_zip.py）。
12. 每次按系列交付一个 ZIP（package_series.py），不同系列不得混入同一正式包。
13. 局部修复只交付本次修正的表情（package_patch.py）。
14. 正式包仅包含 `original/` 和 `240x240/` 两套图片目录。
15. 缺少正式母版时必须报告缺失，不得虚构已完成。
16. 用户最新明确批准的修改优先于旧规范；同时更新规范与版本记录（CHANGELOG.md）。
17. 任何会改变角色身份特征的修改都要单独标记并请求审核。
18. 项目路径和脚本应跨平台运行（全部相对路径，无硬编码个人绝对路径）。
19. 不需要修改图片的工程操作不得触发图片重新生成。
20. 输出结果必须区分“已完成 / 待审核 / 缺失素材”，不得混淆。

## 提交与版本

- Git 只管理文本规范、脚本、元数据；大型 PNG 建议 Git LFS。
- 不要在仓库里无差别堆积历史 ZIP。
- 每次重要修正保留旧版、候选版、修改内容/原因/状态（见 `docs/IMAGE_EDITING_RULES.md`）。
