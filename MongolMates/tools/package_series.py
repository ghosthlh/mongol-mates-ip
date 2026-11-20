#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""package_series.py — 整套系列交付打包（16 张）。
硬闸门：每张必须 approval_status=approved 且有原生高清母版，否则拒绝并列出缺失项。
正式包只含 original/ 与 240x240/。缺少原生高清时拒绝“虚假正式发布”。
"""
from __future__ import annotations
import sys, argparse, json, io, zipfile
from pathlib import Path
from PIL import Image
from mm_common import (project_root, resolve, load_manifest, VALID_SERIES, sha256_file)


def downscale(master: Path, bg_mode: str) -> tuple[bytes, bytes]:
    with Image.open(master) as im0:
        im = im0.convert("RGBA")
        bg = (255,255,255,0) if bg_mode == "transparent" else (255,255,255,255)
        canvas = Image.new("RGBA", (240,240), bg)
        c = im.copy(); c.thumbnail((240,240), Image.Resampling.LANCZOS)
        canvas.alpha_composite(c, ((240-c.width)//2, (240-c.height)//2))
    b240 = io.BytesIO(); canvas.save(b240, "PNG", optimize=True)
    borig = master.read_bytes()
    return borig, b240.getvalue()


def package(root: Path, series_id: str, version: str, out_path: Path,
            allow_candidate: bool = False, candidate_source_dir: str | None = None) -> dict:
    m = load_manifest(root)
    items = [i for i in m["items"] if i["series_id"] == series_id]
    rep = {"series": series_id, "ok": False, "rejected": [], "packed": [], "zip": None}
    if len(items) != 16:
        rep["rejected"].append(f"系列应有 16 张，实际 {len(items)}"); return rep
    top = f"MongolMates_{series_id}_v{version}"
    try:
        zf = zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED)
    except Exception as e:
        rep["rejected"].append(f"无法创建 ZIP: {e!r}"); return rep

    for it in sorted(items, key=lambda x: int(x["sticker_id"])):
        tag = f"{it['sticker_id']} {it.get('title')}"
        if not allow_candidate:
            if it.get("approval_status") != "approved":
                rep["rejected"].append(f"{tag}: 未批准，不能进入正式包"); continue
            if not it.get("is_native_master") or not it.get("master_file"):
                rep["rejected"].append(f"{tag}: 缺少原生高清母版，拒绝虚假高清交付"); continue
            master = resolve(root, it["master_file"])
        else:
            master = None
            if candidate_source_dir:
                master = resolve(root, candidate_source_dir) / f"{str(it['sticker_id']).zfill(2)}.png"
            master = master or resolve(root, it.get("master_file") or it.get("source_file"))
        if not master or not master.exists():
            rep["rejected"].append(f"{tag}: 图片文件不存在 {master}"); continue
        borig, b240 = downscale(master, it.get("background_mode", "transparent"))
        name = f"{str(it['sticker_id']).zfill(2)}.png"
        zf.writestr(f"{top}/original/{name}", borig)
        zf.writestr(f"{top}/240x240/{name}", b240)
        rep["packed"].append(tag)
    zf.close()

    if rep["rejected"]:
        # 正式包被拒：删除半成品，绝不留下看似成功的文件
        try: out_path.unlink()
        except Exception: pass
        rep["zip"] = None
        return rep
    rep["ok"] = True; rep["zip"] = str(out_path.relative_to(root))
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("series", choices=VALID_SERIES)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-candidate", action="store_true", help="仅用于自检演示，非正式发布")
    ap.add_argument("--candidate-source-dir", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    out = Path(args.out).resolve() if args.out else root / "releases" / args.series / f"MongolMates_{args.series}_v{args.version}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    rep = package(root, args.series, args.version, out, args.allow_candidate, args.candidate_source_dir)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"系列 {args.series}: {'打包成功' if rep['ok'] else '已拒绝（未生成正式ZIP）'}")
        if rep["zip"]: print("  ZIP:", rep["zip"])
        print(f"  已打包 {len(rep['packed'])} 张，拒绝 {len(rep['rejected'])} 张")
        for r in rep["rejected"][:20]: print("   [拒绝]", r)
        if not args.allow_candidate:
            print("  提示：需逐张人工确认并把 approval_status 改为 approved 后方可正式发布。")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
