#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_240.py — 从“已确认的原生高清母版”生成 240×240 微信尺寸版。
强制约束：来源必须 approval_status=approved 且存在 master_file；禁止用 240px 低清反向放大冒充高清；
禁止 NEAREST 拉伸（使用 LANCZOS）。透明模式保留 Alpha，white_scene 保留白底。
用法：
  python3 export_240.py --series vol03_reactions --sticker 11
  python3 export_240.py --series vol03_reactions --all-dryrun
"""
from __future__ import annotations
import sys, argparse, json
from pathlib import Path
from PIL import Image, ImageFilter
from mm_common import (MIN_MASTER_LONG_EDGE, project_root, resolve, load_manifest, items_by_key, VALID_SERIES)


def add_white_outline(im: Image.Image, width_px: int) -> Image.Image:
    """给透明图主体外侧加白色描边（不改内部原有线描）。"""
    im = im.convert("RGBA")
    a = im.getchannel("A")
    # 膨胀 alpha 作为外描边区域
    k = max(1, width_px | 1)
    dilated = a.filter(ImageFilter.MaxFilter(k))
    outline = Image.new("RGBA", im.size, (255,255,255,0))
    white = Image.new("RGBA", im.size, (255,255,255,255))
    outline.paste(white, (0,0), dilated)
    outline.alpha_composite(im)   # 原图盖在白边上，保留内部深色线描
    return outline


def export_one(root: Path, item: dict, outline_width: int = 5, add_outline: bool = False) -> dict:
    res = {"series_id": item["series_id"], "sticker_id": item["sticker_id"], "ok": False, "reason": None}
    if item.get("approval_status") != "approved":
        res["reason"] = "未批准（approval_status != approved），拒绝导出正式版"; return res
    master_rel = item.get("master_file")
    if not master_rel:
        res["reason"] = "缺少原生高清母版 master_file，拒绝导出（missing_native_master）"; return res
    if not item.get("is_native_master"):
        res["reason"] = "is_native_master=false，拒绝作为正式高清来源"; return res
    master = resolve(root, master_rel)
    if not master or not master.exists():
        res["reason"] = f"母版文件不存在: {master_rel}"; return res
    with Image.open(master) as im0:
        mw, mh = im0.size
        if max(mw, mh) < MIN_MASTER_LONG_EDGE:
            res["reason"] = f"母版分辨率过低 {mw}x{mh}，疑似低清冒充高清"; return res
        im = im0.convert("RGBA")
    # Lanczos 高质量缩小到 240x240（正方形画布，居中，不变形）
    im.thumbnail((240, 240), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (240,240), (255,255,255,0) if item.get("background_mode")=="transparent" else (255,255,255,255))
    canvas.alpha_composite(im, ((240-im.width)//2, (240-im.height)//2))
    if add_outline and item.get("background_mode") == "transparent":
        w240 = max(4, min(6, round(outline_width * 240 / 1200))) if mw >= 1200 else outline_width
        canvas = add_white_outline(canvas, w240)
    out_dir = root / "series" / item["series_id"] / "approved" / "240x240"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{str(item['sticker_id']).zfill(2)}.png"
    canvas.save(out, "PNG", optimize=True)
    kb = out.stat().st_size / 1024
    res.update({"ok": True, "output": str(out.relative_to(root)), "size_kb": round(kb,1)})
    if kb > 500:
        res["warning"] = f"文件 {kb:.0f}KB 超过 500KB，建议做缩小尺寸优化"
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=VALID_SERIES)
    ap.add_argument("--sticker")
    ap.add_argument("--add-outline", action="store_true", help="透明图加白色外描边")
    ap.add_argument("--outline-width", type=int, default=5)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    m = load_manifest(root)
    idx = items_by_key(m)
    if args.series and args.sticker:
        targets = [idx[(args.series, str(args.sticker).zfill(2))]]
    elif args.series:
        targets = [i for i in m["items"] if i["series_id"] == args.series]
    else:
        ap.error("需指定 --series（可加 --sticker）")
    results = [export_one(root, it, args.outline_width, args.add_outline) for it in targets]
    ok = all(r["ok"] for r in results)
    if args.json:
        print(json.dumps({"ok_per_item": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['series_id']}/{r['sticker_id']}: {'OK' if r['ok'] else '拒绝'} {r.get('reason') or r.get('output','')}")
            if r.get("warning"): print("   [警告]", r["warning"])
        print(f"\n{'全部成功' if ok else '存在拒绝项'}（当前已批准母版极少，拒绝属预期行为）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
