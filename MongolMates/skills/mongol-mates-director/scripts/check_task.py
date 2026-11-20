#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务前置检查：读元数据，判断某表情/系列能否进入正式流程，缺什么报什么。"""
from __future__ import annotations
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from mm_common import project_root, load_manifest, items_by_key

def check(root: Path, series: str, sticker: str | None) -> dict:
    m = load_manifest(root); idx = items_by_key(m)
    items = [idx[(series, str(sticker).zfill(2))]] if sticker else [i for i in m["items"] if i["series_id"]==series]
    rep = {"series": series, "sticker": sticker, "ready": True, "items": []}
    for it in items:
        issues = []
        if it.get("approval_status") != "approved": issues.append("未批准(needs_review等)")
        if not it.get("is_native_master"): issues.append("缺原生高清母版")
        if not it.get("master_file"): issues.append("无 master_file")
        if it.get("missing_native_master"): issues.append("missing_native_master=true")
        rep["items"].append({"id": it["sticker_id"], "title": it.get("title"),
                             "bg": it.get("background_mode"), "issues": issues})
        if issues: rep["ready"] = False
    return rep

def main():
    if len(sys.argv) < 2:
        print("用法: check_task.py <series_id> [sticker_id]"); return 2
    root = project_root()
    rep = check(root, sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["ready"] else 1

if __name__ == "__main__":
    sys.exit(main())
