# 任务工具调用链

## 初始化 / 定期审计
```
tools/audit_assets.py
tools/validate_character_metadata.py
→ reports/asset_audit/initial_audit.{md,json}
```

## 新表情制作
```
读 CHARACTER_BIBLE + 同角色已审核表情
→ 产出候选（image 工具/人工）→ 状态 working/candidate
→ tools/generate_preview.py（深/浅底）
→ tools/validate_image.py --background-mode <mode>
→ tools/check_transparency.py（transparent 时）
→ 用户确认 → approved + 冻结母版
→ tools/export_240.py → tools/package_series.py → tools/verify_zip.py
```

## 局部修复
```
读目标图 + 母版 + 元数据 → IMAGE_EDITING_RULES 七步法
→ 只改指定区域 → 对比预览
→ tools/check_transparency.py / validate_image.py
→ 用户确认 → 更新版本
→ tools/package_patch.py --version 新版本 → tools/verify_zip.py
```

## 整套导出
```
前置检查 scripts/check_task.py <series>
→ tools/export_240.py（逐张或全部）
→ tools/package_series.py <series> --version V
→ tools/verify_zip.py <zip> --expect-count 16
→ 交付下载链接
```

## 白边专项检查
```
tools/check_transparency.py <图...> --json --out reports/qa/whiteedge.json
→ 结合深/浅底预览人工复核同系列观感是否统一
```
