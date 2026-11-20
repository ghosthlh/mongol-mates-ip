#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_preview.py — 生成浅色/深色背景总览与单张预览（仅检查资产，非母版）。
关键：预览通过“合成到临时背景”实现，绝不把背景色烘焙进透明 PNG 母版。
"""
from __future__ import annotations
import sys, argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from mm_common import project_root, resolve, load_manifest, VALID_SERIES

LIGHT = (245, 245, 245, 255)
DARK  = (38, 42, 50, 255)


def load_font(size):
    # 优先中文字体；TTC 可能含多个 face，逐个 index 尝试直到能渲染中文
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if not Path(p).exists():
            continue
        for idx in range(0, 4):
            try:
                f = ImageFont.truetype(p, size, index=idx)
                # 用 getbbox 验证该 face 能渲染中文（宽大于 ASCII 的占位符）
                if f.getbbox("测")[2] > 0:
                    return f
            except Exception:
                break
    return ImageFont.load_default()


def composite_on(im: Image.Image, bg: tuple, cell: int) -> Image.Image:
    im = im.convert("RGBA")
    im.thumbnail((cell-16, cell-40), Image.Resampling.LANCZOS)
    base = Image.new("RGBA", (cell, cell), bg)
    base.alpha_composite(im, ((cell-im.width)//2, 6))
    return base.convert("RGB")


def build_sheet(root: Path, series_id: str, bg: tuple, label: str, cell: int = 180, cols: int = 4) -> Path | None:
    m = load_manifest(root)
    items = [i for i in m["items"] if i["series_id"] == series_id]
    if not items: return None
    rows = (len(items)+cols-1)//cols
    sheet = Image.new("RGB", (cols*cell, rows*(cell+26)), bg[:3])
    d = ImageDraw.Draw(sheet)
    font = load_font(15)
    for k, it in enumerate(items):
        rel = it.get("master_file") or it.get("source_file")
        p = resolve(root, rel)
        if not p or not p.exists():
            continue
        try:
            with Image.open(p) as im0: im = im0.convert("RGBA")
            tile = composite_on(im, bg, cell)
            r, c = divmod(k, cols)
            x, y = c*cell, r*(cell+26)
            sheet.paste(tile, (x,y))
            title = f"{str(it['sticker_id']).zfill(2)} {it.get('title') or ''}"
            d.text((x+6, y+cell+3), title, fill=(20,20,20) if bg==LIGHT else (240,240,240), font=font)
        except Exception:
            continue
    out_dir = root / "series" / series_id / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"overview_{label}.png"
    sheet.save(out, "PNG")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=VALID_SERIES, required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    outs = {}
    for label, bg in [("light", LIGHT), ("dark", DARK)]:
        p = build_sheet(root, args.series, bg, label)
        outs[label] = str(p.relative_to(root)) if p else None
    if args.json:
        print(json.dumps(outs, ensure_ascii=False, indent=2))
    else:
        for k,v in outs.items(): print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
