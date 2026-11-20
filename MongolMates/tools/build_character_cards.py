#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_character_cards.py — 从“已认可的嘴替篇视觉母版”整理四角色表情总览卡。

性质：零风险整理。只读取现有已 approved 的表情图做拼版，绝不重画、不生成、不改源图。
输出：characters/<role>/references/expression_sheet.png（浅底，附中文标注）。
说明：这是“表情/头饰角度参考卡”，不是全身结构母版，也不是可交付表情。
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from mm_common import project_root, resolve, load_manifest

ROLE_CN = {"father": "爸爸", "mother": "妈妈", "sister": "姐姐", "brother": "弟弟"}
LIGHT = (248, 246, 242)
CARD_BG = (255, 255, 255)
INK = (60, 52, 46)
SUB = (140, 130, 120)
CELL = 200
COLS = 4
PAD = 16
LABEL_H = 34
HEAD_H = 70
FOOT_H = 48


def load_font(size):
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
                if f.getbbox("测")[2] > 0:
                    return f
            except Exception:
                break
    return ImageFont.load_default()


def center_text(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - w) / 2 - bb[0], y0 + (y1 - y0 - h) / 2 - bb[1]), text, font=font, fill=fill)


def build(root: Path, role: str) -> dict:
    m = load_manifest(root)
    items = [i for i in m["items"]
             if i["series_id"] == "vol03_reactions"
             and role in i.get("characters", [])
             and i.get("approval_status") == "approved"]
    items = sorted(items, key=lambda x: int(x["sticker_id"]))
    if not items:
        return {"role": role, "ok": False, "reason": "无已批准表情"}

    rows = (len(items) + COLS - 1) // COLS
    W = COLS * (CELL + PAD) + PAD
    H = HEAD_H + rows * (CELL + LABEL_H + PAD) + FOOT_H
    sheet = Image.new("RGB", (W, H), LIGHT)
    d = ImageDraw.Draw(sheet)
    f_title = load_font(26)
    f_sub = load_font(14)
    f_label = load_font(16)

    cn = ROLE_CN[role]
    d.text((PAD, 14), f"蒙古萌友 · {cn}｜表情参考卡", font=f_title, fill=INK)
    d.text((PAD, 46), "源自已认可的嘴替篇视觉母版（240px）· 纯整理未重画 · 非全身结构母版", font=f_sub, fill=SUB)

    for k, it in enumerate(items):
        rel = it.get("master_file") or it.get("source_file")
        p = resolve(root, rel)
        if not p or not p.exists():
            continue
        r, c = divmod(k, COLS)
        x = PAD + c * (CELL + PAD)
        y = HEAD_H + r * (CELL + LABEL_H + PAD)

        # 白底卡片 + 合成透明图（不烘焙进源图）
        card = Image.new("RGBA", (CELL, CELL), CARD_BG + (255,))
        im = Image.open(p).convert("RGBA")
        im.thumbnail((CELL - 20, CELL - 20), Image.Resampling.LANCZOS)
        card.alpha_composite(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
        sheet.paste(card.convert("RGB"), (x, y))
        d.rectangle([x, y, x + CELL - 1, y + CELL - 1], outline=(224, 218, 210), width=1)

        tag = f"{int(it['sticker_id']):02d} {it['title']}"
        if len(it.get("characters", [])) > 1:
            tag += "（合照）"
        center_text(d, (x, y + CELL, x + CELL, y + CELL + LABEL_H), tag, f_label, INK)

    d.text((PAD, H - FOOT_H + 12),
           "用途：跨 AI 传递时的角色表情/头饰角度参考。身份特征以已批准母版为准；此卡不得作为交付表情。",
           font=f_sub, fill=SUB)

    out_dir = root / "characters" / role / "references"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "expression_sheet.png"
    sheet.save(out)
    return {"role": role, "ok": True, "file": str(out.relative_to(root)), "count": len(items),
            "size": [W, H], "items": [int(i["sticker_id"]) for i in items]}


def main():
    root = project_root()
    results = []
    for role in ROLE_CN:
        r = build(root, role)
        results.append(r)
        print(f"[{role}] {'OK' if r['ok'] else 'SKIP'} " +
              (f"{r.get('count')}张 -> {r.get('file')} {r.get('size')}" if r["ok"] else r.get("reason", "")))
    import json
    print(json.dumps({"cards": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
