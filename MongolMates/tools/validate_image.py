#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_image.py — 单图技术校验：格式/尺寸/Alpha/异常边框/四角白底/残留线/杂点。
对 white_scene 自动放宽“白底/白边”判据，避免误判复杂场景白背景。
退出码：0=通过，1=失败。"""
from __future__ import annotations
import sys, argparse, json
from pathlib import Path
from PIL import Image
import numpy as np
from mm_common import image_info


def check(path: Path, background_mode: str = "transparent",
          expect_size: tuple[int,int] | None = None, max_kb: int | None = None) -> dict:
    rep = {"file": str(path), "background_mode": background_mode, "ok": True, "issues": [], "warnings": []}
    info = image_info(path)
    if not info.get("exists") or not info.get("ok"):
        rep["ok"] = False; rep["issues"].append(f"文件不存在或无法解码: {info.get('error','')}")
        return rep
    size = tuple(info["size"])
    rep["size"] = list(size); rep["mode"] = info["mode"]; rep["format"] = info["format"]
    if info["format"] != "PNG":
        rep["ok"] = False; rep["issues"].append(f"格式应为 PNG，实际 {info['format']}")
    if expect_size and size != expect_size:
        rep["ok"] = False; rep["issues"].append(f"尺寸应为 {expect_size}，实际 {size}")
    if max_kb and path.stat().st_size > max_kb * 1024:
        rep["warnings"].append(f"文件大小 {path.stat().st_size//1024}KB 超过建议 {max_kb}KB")

    im = Image.open(path).convert("RGBA")
    a = np.asarray(im.getchannel("A"), dtype=np.uint8)
    rgb = np.asarray(im.convert("RGB"), dtype=np.uint8)
    h, w = a.shape
    has_transparent = bool((a < 255).any())

    if background_mode == "transparent":
        if not has_transparent:
            rep["ok"] = False; rep["issues"].append("透明背景模式但图片无任何透明像素（疑似白底未抠除）")
        # 四角应为透明
        corners = [a[0,0], a[0,-1], a[-1,0], a[-1,-1]]
        bad_corners = [int(c) for c in corners if c > 8]
        if bad_corners:
            rep["ok"] = False; rep["issues"].append(f"透明模式但四角非透明 Alpha={bad_corners}（残留白底）")
        # 全透明区域是否残留可见 RGB 杂色
        fully_t = a == 0
        if fully_t.any():
            vis = rgb[fully_t]
            nonwhite = np.any(vis < 245, axis=1)
            if nonwhite.mean() > 0.01:
                rep["warnings"].append(f"完全透明区域存在非白 RGB 数据比例 {nonwhite.mean():.1%}（可能是残影）")
    elif background_mode == "white_scene":
        if has_transparent:
            rep["warnings"].append("white_scene 模式但检测到透明像素，请确认是否应保留白底")
        # 四角应接近白
        corners = [rgb[0,0], rgb[0,-1], rgb[-1,0], rgb[-1,-1]]
        if any(int(c.min()) < 240 for c in corners):
            rep["warnings"].append("white_scene 四角非纯白，请人工确认背景")

    # 异常矩形边框 / 过长残留直线：检测整行或整列高度一致且颜色单一的情况
    def uniform_rows(arr):
        uniq_per_row = [len(np.unique(arr[r], axis=0)) for r in range(arr.shape[0])]
        return [r for r,u in enumerate(uniq_per_row) if u == 1]
    rep["_uniform_row_count"] = len(uniform_rows(rgb))
    rep["_uniform_col_count"] = len(uniform_rows(rgb.transpose(1,0,2)))
    if rep["_uniform_col_count"] >= max(3, h//4):
        rep["warnings"].append("检测到较多整列单色像素，疑似历史拉伸/像素复制风险（仅风险提示，需人工确认结构）")
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image")
    ap.add_argument("--background-mode", default="transparent", choices=["transparent","white_scene"])
    ap.add_argument("--expect-size", default=None, help="WxH")
    ap.add_argument("--max-kb", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    expect = tuple(map(int, args.expect_size.split("x"))) if args.expect_size else None
    rep = check(Path(args.image), args.background_mode, expect, args.max_kb)
    rep.pop("_uniform_row_count", None); rep.pop("_uniform_col_count", None)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"校验 {rep['file']} -> {'通过' if rep['ok'] else '失败'}")
        for i in rep["issues"]: print("  [错误]", i)
        for w in rep["warnings"]: print("  [警告]", w)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
