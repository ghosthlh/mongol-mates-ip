#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_zip.py — ZIP 交付校验：存在/可打开/可完整解压/文件数/编号对应/240尺寸/无系统文件。
用法：python3 verify_zip.py path/to.zip [--expect-count 16] [--json]
"""
from __future__ import annotations
import sys, argparse, json, io
from pathlib import Path
from PIL import Image
import zipfile

FORBIDDEN = {"__MACOSX", ".DS_Store", "Thumbs.db"}


def verify(zip_path: Path, expect_pairs: int | None = None) -> dict:
    rep = {"file": str(zip_path), "ok": True, "issues": [], "warnings": [], "files": []}
    if not zip_path.exists():
        rep["ok"] = False; rep["issues"].append("ZIP 不存在"); return rep
    try:
        zf = zipfile.ZipFile(zip_path)
        bad = zf.testzip()
        if bad:
            rep["ok"] = False; rep["issues"].append(f"ZIP 校验失败，损坏文件: {bad}")
    except Exception as e:
        rep["ok"] = False; rep["issues"].append(f"ZIP 无法打开: {e!r}"); return rep

    names = [n for n in zf.namelist() if not n.endswith("/")]
    rep["files"] = names
    for n in names:
        parts = Path(n).parts
        if any(p in FORBIDDEN or p.startswith("__MACOSX") for p in parts):
            rep["ok"] = False; rep["issues"].append(f"含系统文件: {n}")
        if Path(n).suffix.lower() != ".png":
            rep["ok"] = False; rep["issues"].append(f"非 PNG 文件: {n}")
    dirs = {Path(n).parts[0] for n in names if len(Path(n).parts) >= 2}
    if len(dirs) != 1:
        rep["ok"] = False; rep["issues"].append(f"ZIP 应只有一个顶层目录，实际: {dirs}")
    subdirs = {Path(n).parts[1] for n in names if len(Path(n).parts) >= 2}
    if not subdirs.issubset({"original", "240x240"}):
        rep["ok"] = False; rep["issues"].append(f"正式包只允许 original/ 和 240x240/，实际: {subdirs}")

    orig = sorted(n for n in names if "/original/" in n or n.startswith("original/"))
    small = sorted(n for n in names if "/240x240/" in n or n.startswith("240x240/"))
    def num(n): return Path(n).stem
    no, ns = set(map(num, orig)), set(map(num, small))
    if no != ns:
        rep["ok"] = False; rep["issues"].append(f"两目录编号不对应: original={sorted(no)} 240={sorted(ns)}")
    if expect_pairs is not None and len(no) != expect_pairs:
        rep["ok"] = False; rep["issues"].append(f"应含 {expect_pairs} 对图片，实际 {len(no)} 对")
    if len(orig) != len(set(orig)):
        rep["ok"] = False; rep["issues"].append("存在重名文件")

    for n in small:
        try:
            data = zf.read(n)
            if len(data) == 0:
                rep["ok"] = False; rep["issues"].append(f"空文件: {n}"); continue
            with Image.open(io.BytesIO(data)) as im:
                if im.size != (240,240):
                    rep["ok"] = False; rep["issues"].append(f"{n} 尺寸非 240x240: {im.size}")
                if len(data) > 500*1024:
                    rep["warnings"].append(f"{n} 超过 500KB")
        except Exception as e:
            rep["ok"] = False; rep["issues"].append(f"{n} 无法解码: {e!r}")
    for n in orig:
        data = zf.read(n)
        if len(data) == 0:
            rep["ok"] = False; rep["issues"].append(f"空文件: {n}")
    rep["summary"] = {"pairs": len(no), "original": len(orig), "240x240": len(small)}
    zf.close()
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("zipfile")
    ap.add_argument("--expect-count", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = verify(Path(args.zipfile), args.expect_count)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"{rep['file']} -> {'通过' if rep['ok'] else '失败'}  {rep.get('summary','')}")
        for i in rep["issues"]: print("  [错误]", i)
        for w in rep["warnings"]: print("  [警告]", w)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
