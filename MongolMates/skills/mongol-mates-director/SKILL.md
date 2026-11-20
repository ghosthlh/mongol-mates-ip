---
name: mongol-mates-director
description: 蒙古萌友 IP 资产与 AI 制作总监。当任务涉及《蒙古萌友》角色的新表情制作、局部修复、背景/白边处理、角色一致性检查、审核状态管理、240px 导出、ZIP 打包与验证时使用。读取项目规范而非自造规则，确保跨 AI 一致。
---

# Mongol Mates Director

《蒙古萌友》IP 的项目专用 Skill。它是规范的**执行者**，不是规范本身的来源——所有规则来自 `config/*.yaml` 与 `docs/`，本文件不得复制出与之冲突的独立规则。

## 第一步：强制读取（每次都要）

按顺序读取项目根目录下：

1. `AGENTS.md`（20 条强制规则）
2. `config/project.yaml`（枚举、路径、原则）
3. `config/characters.yaml` + 目标角色 `characters/<id>/character.yaml`
4. `config/visual_rules.yaml`、`config/export_rules.yaml`
5. `config/asset_manifest.yaml` 中目标表情条目（series_id + sticker_id）
6. `docs/CHARACTER_BIBLE.md`、`docs/IMAGE_EDITING_RULES.md`、`docs/DELIVERY_STANDARD.md`

根目录定位：本 Skill 位于 `skills/mongol-mates-director/`，项目根为其上两级。所有工具脚本用相对路径，不硬编码个人绝对路径。

## 任务判定

| 用户意图 | 判定 | 入口 |
| --- | --- | --- |
| 做一张新表情 | 新制作 | CHARACTER_BIBLE + 同角色已审核表情参考 |
| 修某张的某区域 | 局部修复 | IMAGE_EDITING_RULES 七步法 |
| 导出/发布一套 | 正式导出 | DELIVERY_STANDARD + package_series |
| 修完几张要交付 | 局部交付 | package_patch |
| 检查资产 | 审计 | audit / validate / check_transparency |

## 执行规程

### 1. 准备约束
- 明确目标 series_id / sticker_id / 角色 / 文字。
- 读该表情元数据：`background_mode`、`composition`、`approval_status`、`source_resolution`。
- 若 `approval_status != approved` 或缺 `master_file`，**明确报告“无正式母版”**，不得虚构。

### 2. 一致性检查（产出候选后）
- 角色身份/头饰/辫子/胡子/配色是否符合 CHARACTER_BIBLE。
- `background_mode`：transparent 是否有透明通道与白边；white_scene 是否保留白底。
- 文字是否完整准确、未被裁切、艺术字风格。
- 结构：半身不拉伸、坐姿六层分明、动态不贴底。
- 气团/眼白等白色区域是否保留。

### 3. 审核状态管理
- 新产出只能是 `working` 或 `candidate`；**绝不自动置为 approved**。
- 生成对比预览（原始/修复/深底/浅底），交用户确认。
- 用户确认后，才把状态改为 approved、冻结母版、更新 CHANGELOG。

### 4. 导出与打包
```bash
python3 tools/export_240.py --series <sid> --sticker <id>
python3 tools/package_series.py <sid>            # 整套，需全部 approved + 高清母版
python3 tools/package_patch.py <sid> <id...> --version <v>   # 局部
python3 tools/verify_zip.py <zip> --expect-count <n>
```
- 正式包只含 `original/` 与 `240x240/`。
- 缺原生高清时工具会拒绝：如实报告缺失，不放宽闸门、不放宽冒充。
- 完成后提供可点击 ZIP 下载链接。

## 红线

- 不重生成相似角色替换原版；不低清冒充高清；不拉伸/复制像素补身体。
- 不覆盖原始输入；不扩大修改范围；不删复杂场景白底；不误删白色区域。
- 不自动批准；不同系列不混包；局部交付只含修改项。
- 不需要改图的工程操作不触发图片重新生成。

## 参考

- `references/CHAINS.md`：各任务的工具调用链。
- `scripts/check_task.py`：任务前置检查（读元数据 → 判断能否进行/缺什么）。
