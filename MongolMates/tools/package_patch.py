#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""package_patch.py — 局部修复交付：只打包指定编号的表情（原图+240两版）。
绝不加入未修改的图片。同样受 approved + 原生母版闸门约束。
用法：python3 package_patch.py vol03_reactions 01 11 --version 1.1
"""
from __future__ import annotations
import sys, argparse, json, zipfile
from pathlib import Path
from mm_common import project_root, resolve, load_manifest, items_by_key, VALID_SERIES
from package_series import downscale


def package_patch(root: Path, series_id: str, ids: list[str], version: str, out_path: Path,
                  allow_candidate: bool = False, candidate_source_dir: str | None = None) -> dict:
    m = load_manifest(root)
    idx = items_by_key(m)
    rep = {"series": series_id, "ids": ids, "ok": False, "rejected": [], "packed": [], "zip": None}
    top = f"MongolMates_{series_id}_Patch_v{version}"
    zf = zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED)
    for raw in ids:
        st = str(raw).zfill(2)
        it = idx.get((series_id, st))
        tag = f"{st} {it.get('title') if it else '?'}"
        if not it:
            rep["rejected"].append(f"{tag}: 清单中不存在"); continue
        if not allow_candidate:
            if it.get("approval_status") != "approved":
                rep["rejected"].append(f"{tag}: 未批准"); continue
            if not it.get("is_native_master") or not it.get("master_file"):
                rep["rejected"].append(f"{tag}: 缺少原生高清母版"); continue
            master = resolve(root, it["master_file"])
        else:
            master = None
            if candidate_source_dir:
                master = resolve(root, candidate_source_dir) / f"{st}.png"
            master = master or resolve(root, it.get("master_file") or it.get("source_file"))
        if not master or not master.exists():
            rep["rejected"].append(f"{tag}: 文件不存在"); continue
        borig, b240 = downscale(master, it.get("background_mode", "transparent"))
        name = f"{st}.png"
        zf.writestr(f"{top}/original/{name}", borig)
        zf.writestr(f"{top}/240x240/{name}", b240)
        rep["packed"].append(tag)
    zf.close()
    if rep["rejected"]:
        try: out_path.unlink()
        except Exception: pass
        return rep
    rep["ok"] = True; rep["zip"] = str(out_path.relative_to(root))
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("series", choices=VALID_SERIES)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--version", default="1.1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-candidate", action="store_true")
    ap.add_argument("--candidate-source-dir", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else project_root()
    ids_s = "".join(str(i).zfill(2) for i in args.ids)
    out = Path(args.out).resolve() if args.out else root / "releases" / "patches" / f"MongolMates_{args.series}_Patch_{ids_s}_v{args.version}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    rep = package_patch(root, args.series, args.ids, args.version, out, args.allow_candidate, args.candidate_source_dir)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"局部包 {args.series} {args.ids}: {'成功' if rep['ok'] else '已拒绝'}")
        if rep["zip"]: print("  ZIP:", rep["zip"])
        print(f"  打包 {len(rep['packed'])} 张 / 拒绝 {len(rep['rejected'])} 张")
        for r in rep["rejected"]: print("   [拒绝]", r)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
