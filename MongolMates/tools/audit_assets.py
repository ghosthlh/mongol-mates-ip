#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_assets.py — 资产审计（只读，不修改任何原图）。
功能：识别格式/尺寸/Alpha、计算 SHA-256、系列映射、重复检测、原生/低清/来源不明分类、
缺失清单、歧义版本清单、可视化总览路径清单。输出 initial_audit.md/json。
"""
from __future__ import annotations
import sys, argparse, json, hashlib
from pathlib import Path
from collections import defaultdict
from PIL import Image
from mm_common import project_root, load_manifest, load_yaml, stamp

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()


def probe(p: Path, root: Path) -> dict:
    rec = {"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha(p)}
    try:
        with Image.open(p) as im:
            im.load()
            rec.update({"format": im.format, "size": list(im.size), "mode": im.mode})
            bands = im.getbands()
            ha = "A" in bands or (im.mode == "P" and "transparency" in im.info)
            rec["has_alpha"] = ha
            if ha:
                rec["alpha_min"], rec["alpha_max"] = im.convert("RGBA").getchannel("A").getextrema()
    except Exception as e:
        rec["error"] = repr(e)
    return rec


def classify(rec: dict) -> str:
    if not rec.get("size"): return "来源不明/无法解码"
    w,h = rec["size"]
    if max(w,h) >= 600: return "原生高清候选"
    if max(w,h) <= 240: return "低清（240级）"
    return "中等分辨率"


def run(root: Path) -> dict:
    proj = load_yaml(root / "config" / "project.yaml")
    src = (root / proj["paths"]["source_scan_dir"]).resolve()
    files = [p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXT and "_claude_work" not in p.parts]
    recs = [probe(p, root.parent) for p in files]

    # 重复（按 sha）
    by_sha = defaultdict(list)
    for r in recs: by_sha[r["sha256"]].append(r["path"])
    dupes = {k:v for k,v in by_sha.items() if len(v) > 1}

    manifest = load_manifest(root)
    items = manifest["items"]
    indexed = {Path(i["source_file"]).name for i in items if i.get("source_file")}
    indexed |= {Path(i["master_file"]).name for i in items if i.get("master_file")}
    unindexed = [r for r in recs if Path(r["path"]).name not in indexed and "横幅封面等" not in r["path"] and not any(x in r["path"] for x in ["红包","角色表"])]

    native = [i for i in items if i.get("is_native_master")]
    missing = [i for i in items if i.get("missing_native_master")]
    ambiguous = [i for i in items if i.get("approval_status") == "needs_review"]

    return {
        "generated_at": stamp(),
        "source_scan_dir": proj["paths"]["source_scan_dir"],
        "scanned_count": len(recs),
        "classification": {c: sum(1 for r in recs if classify(r)==c) for c in ["原生高清候选","中等分辨率","低清（240级）","来源不明/无法解码"]},
        "records": recs,
        "duplicates": dupes,
        "unindexed_candidates": [r["path"] for r in unindexed],
        "native_master_items": [{"series":i["series_id"],"id":i["sticker_id"],"title":i["title"],"file":i.get("master_file")} for i in native],
        "missing_native_master_count": len(missing),
        "ambiguous_items": len(ambiguous),
        "series_counts": {s: sum(1 for i in items if i["series_id"]==s) for s in ["vol01_daily","vol02_emotions","vol03_reactions"]},
    }


def write_report(root: Path, data: dict):
    d = root / "reports" / "asset_audit"
    d.mkdir(parents=True, exist_ok=True)
    (d / "initial_audit.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    L = []
    L.append("# 蒙古萌友 · 初始资产审计报告\n")
    L.append(f"- 生成时间：{data['generated_at']}")
    L.append(f"- 扫描目录：`{data['source_scan_dir']}`（只读，未修改任何原图）")
    L.append(f"- 扫描图片数：**{data['scanned_count']}**")
    L.append(f"- 三套标准表情索引：日常篇 {data['series_counts']['vol01_daily']} / 情绪篇 {data['series_counts']['vol02_emotions']} / 嘴替篇 {data['series_counts']['vol03_reactions']}\n")
    L.append("## 分辨率分类\n")
    for k,v in data["classification"].items(): L.append(f"- {k}：{v}")
    L.append("\n## 高清母版缺失清单（重点）\n")
    L.append(f"48 个标准表情位中，**{data['missing_native_master_count']} 个缺少原生高清母版**；"
             f"存在原生高清母版 {len(data['native_master_items'])} 个。")
    if data["native_master_items"]:
        L.append("")
        for n in data["native_master_items"]:
            L.append(f"- {n['series']} / {n['id']} {n['title']} → `{n['file']}`")
    L.append("\n> 据用户确认：现有表情均为 240px 直出，无 1200px 原生高清。"
             "按规范不得放大冒充 `original`，缺高清档位者**不得通过正式高清交付验收**。\n")
    L.append("## 审核状态与待确认版本\n")
    from collections import Counter as _C
    sc = _C(i.get("approval_status") for i in load_manifest(root)["items"])
    for k, v in sorted(sc.items()):
        L.append(f"- 状态 `{k}`：{v} 张")
    L.append("")
    L.append("- 嘴替篇 16 张经用户 2026-11-20 明确确认满意，已冻结为正式视觉母版（approved，v1.0）。")
    L.append("- 曾有缺陷的 1200px「我想静静…」已被否决，记录在该条目的 rejected_candidates 中。")
    L.append("- 情绪篇 16 张仅有英文标识，真实中文文案须读图登记，不得当作已核实文字。")
    L.append("- 日常篇文件名与规范文字存在差异（04 zao_a/兄弟、07 shoudao/对、16 kaifanla/那达慕），须核对。\n")
    L.append("## 重复文件（按 SHA-256）\n")
    if data["duplicates"]:
        for k,v in data["duplicates"].items(): L.append(f"- {k[:12]}… → {v}")
    else: L.append("- 未发现完全重复的图片。")
    L.append("\n## 未编入标准清单的候选素材\n")
    for p in data["unindexed_candidates"][:30]: L.append(f"- `{p}`")
    L.append("\n## 母版冻结记录\n")
    L.append("- 2026-11-20：用户确认嘴替篇整套（16 张）为满意版本，已冻结为正式视觉母版（approved / v1.0）。")
    L.append("- 日常篇、情绪篇仍待用户确认，保持 needs_review。")
    (d / "initial_audit.md").write_text("\n".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    data = run(root)
    write_report(root, data)
    if args.json:
        print(json.dumps({k:data[k] for k in ["generated_at","scanned_count","classification","native_master_items","missing_native_master_count","ambiguous_items","series_counts"]}, ensure_ascii=False, indent=2))
    else:
        print(f"审计完成：扫描 {data['scanned_count']} 张；缺失高清母版 {data['missing_native_master_count']}/48；"
              f"存在的 1200px 母版 {len(data['native_master_items'])} 个；待确认 {data['ambiguous_items']} 张")
        print("报告：reports/asset_audit/initial_audit.md 与 .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
