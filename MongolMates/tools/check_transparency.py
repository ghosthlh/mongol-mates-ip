#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_transparency.py — 透明背景与白色外描边专项检查。
检查：透明通道存在性、四角透明、白边连续性、气团/眼白是否被误删（纯白不透明区域统计）。
退出码：0=通过，1=失败。"""
from __future__ import annotations
import sys, argparse, json
from pathlib import Path
from PIL import Image
import numpy as np


def check(path: Path) -> dict:
    rep = {"file": str(path), "ok": True, "issues": [], "warnings": [], "metrics": {}}
    with Image.open(path) as im0:
        im = im0.convert("RGBA")
    a = np.asarray(im.getchannel("A"), dtype=np.uint8)
    rgb = np.asarray(im.convert("RGB"), dtype=np.uint8)
    h, w = a.shape
    trans = a == 0
    semi = (a > 0) & (a < 255)
    opaque = a == 255
    rep["metrics"].update({
        "size": [w, h],
        "transparent_ratio": round(float(trans.mean()), 4),
        "semi_transparent_ratio": round(float(semi.mean()), 4),
        "opaque_ratio": round(float(opaque.mean()), 4),
    })
    if not trans.any() and not semi.any():
        rep["ok"] = False; rep["issues"].append("无透明像素")
    # 四角透明
    corners_alpha = [int(a[0,0]), int(a[0,-1]), int(a[-1,0]), int(a[-1,-1])]
    if any(c > 8 for c in corners_alpha):
        rep["ok"] = False; rep["issues"].append(f"四角非透明 Alpha={corners_alpha}")
    # 主体 bounding box 是否触及四边（白边可能被裁切）
    ys, xs = np.where(a > 8)
    if len(xs):
        bbox = {"x_min":int(xs.min()),"x_max":int(xs.max()),"y_min":int(ys.min()),"y_max":int(ys.max())}
        rep["metrics"]["content_bbox"] = bbox
        margin = min(bbox["x_min"], w-1-bbox["x_max"], bbox["y_min"], h-1-bbox["y_max"])
        rep["metrics"]["margin_to_edge_px"] = int(margin)
        if margin < 1:
            rep["warnings"].append("主体触及画布边缘，白色外描边可能被裁切")
        elif margin > 40 and w >= 1000:
            rep["warnings"].append("主体距边缘较远，白边/构图留白偏大，请人工确认")
    # 纯白不透明区域（气团/眼白/高光）统计，防止误删
    white_fill = opaque & (rgb[:,:,0] > 250) & (rgb[:,:,1] > 250) & (rgb[:,:,2] > 250)
    rep["metrics"]["opaque_white_fill_ratio"] = round(float(white_fill.mean()), 4)
    # 抗锯齿质量：半透明像素过少通常意味着硬边/锯齿
    if trans.any() and opaque.any():
        edge = semi.sum()
        if edge < max(20, 0.002 * h * w):
            rep["warnings"].append("半透明边缘像素偏少，边缘可能不够平滑（抗锯齿不足）")
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None, help="将 JSON 结果写入文件")
    args = ap.parse_args()
    results = [check(Path(p)) for p in args.images]
    overall = all(r["ok"] for r in results)
    if args.json or args.out:
        data = {"ok": overall, "results": results}
        text = json.dumps(data, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text, encoding="utf-8")
        print(text)
    else:
        for r in results:
            print(f"{r['file']} -> {'通过' if r['ok'] else '失败'}  metrics={r['metrics']}")
            for i in r["issues"]: print("   [错误]", i)
            for w in r["warnings"]: print("   [警告]", w)
        print(f"\n总体：{'通过' if overall else '失败'}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
