#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_character_metadata.py — 校验角色/系列/清单元数据的合法性与引用有效性。
退出码：0=全部合法，1=存在错误。"""
from __future__ import annotations
import sys, argparse
from pathlib import Path
from mm_common import (project_root, load_yaml, load_manifest, VALID_STATUS, VALID_BG,
                       VALID_COMP, VALID_ROLES, VALID_SERIES, resolve)


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    manifest = load_manifest(root)
    items = manifest.get("items", [])

    seen_keys, seen_paths = {}, {}
    for idx, it in enumerate(items):
        tag = f"items[{idx}] {it.get('series_id')}/{it.get('sticker_id')}"
        sid, st = it.get("series_id"), str(it.get("sticker_id"))
        if sid not in VALID_SERIES:
            errors.append(f"{tag}: 非法 series_id={sid}")
        if not st:
            errors.append(f"{tag}: 缺少 sticker_id")
        key = (sid, st.zfill(2))
        if key in seen_keys:
            errors.append(f"{tag}: 系列内 sticker_id 重复（首次见 {seen_keys[key]}）")
        seen_keys[key] = tag

        for r in it.get("characters") or []:
            if r not in VALID_ROLES:
                errors.append(f"{tag}: 非法角色 ID={r}")
        bg = it.get("background_mode")
        if bg not in VALID_BG:
            errors.append(f"{tag}: 非法 background_mode={bg}")
        comp = it.get("composition")
        if comp not in VALID_COMP:
            errors.append(f"{tag}: 非法 composition={comp}")
        status = it.get("approval_status")
        if status not in VALID_STATUS:
            errors.append(f"{tag}: 非法 approval_status={status}")
        if status == "approved" and not it.get("master_file"):
            errors.append(f"{tag}: 状态为 approved 但无 master_file")

        for fld in ("source_file",):
            rel = it.get(fld)
            if rel:
                p = resolve(root, rel)
                if p and not p.exists():
                    warnings.append(f"{tag}: {fld} 指向的文件不存在（可能尚未导入）: {rel}")
                    prev = seen_paths.get(str(p))
                    if prev:
                        warnings.append(f"{tag}: 与 {prev} 引用同一文件（疑似重复素材）")
                    seen_paths[str(p)] = tag

        if it.get("outline_required") and bg == "white_scene":
            warnings.append(f"{tag}: white_scene 却标记 outline_required=true，请人工核对")

    # 系列数量
    for sid in VALID_SERIES:
        cnt = sum(1 for i in items if i.get("series_id") == sid)
        if cnt != 16:
            warnings.append(f"系列 {sid} 应有 16 张，实际 {cnt} 张")

    # 角色 YAML
    for rid in VALID_ROLES:
        p = root / "characters" / rid / "character.yaml"
        if not p.exists():
            errors.append(f"角色档案缺失: characters/{rid}/character.yaml")
        else:
            obj = load_yaml(p)
            if obj.get("id") != rid:
                errors.append(f"characters/{rid}/character.yaml: id 字段不匹配")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=None, help="项目根目录（默认自动推断）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    errors, warnings = validate(root)
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"元数据校验：{len(errors)} 错误，{len(warnings)} 警告")
        for e in errors: print("  [错误]", e)
        for w in warnings: print("  [警告]", w)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
