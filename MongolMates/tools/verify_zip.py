#!/usr/bin/env python3
"""验证表情 ZIP 的目录、编号、图片格式、解码与尺寸。"""
from __future__ import annotations

import argparse
import io
import json
import zipfile
from pathlib import Path

from PIL import Image

from mm_common import MIN_MASTER_LONG_EDGE

FORBIDDEN = {"__MACOSX", ".DS_Store", "Thumbs.db"}
IMAGE_DIRS = ("original", "240x240")


def verify(zip_path: Path, expect_pairs: int | None = None) -> dict:
    rep = {"file": str(zip_path), "ok": False, "issues": [], "warnings": [], "files": []}
    issues = rep["issues"]
    if not zip_path.exists():
        issues.append("ZIP 不存在")
        return rep

    try:
        with zipfile.ZipFile(zip_path) as archive:
            bad = archive.testzip()
            if bad:
                issues.append(f"ZIP 校验失败，损坏文件: {bad}")
                return rep

            names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
            rep["files"] = names
            if len(names) != len(set(names)):
                issues.append("ZIP 含重名文件")

            top_dirs = set()
            grouped = {directory: [] for directory in IMAGE_DIRS}
            for name in names:
                parts = name.split("/")
                if (
                    len(parts) != 3
                    or any(part in FORBIDDEN or part in {"", ".", ".."} for part in parts)
                    or "\\" in name
                    or parts[1] not in IMAGE_DIRS
                    or Path(parts[2]).suffix.lower() != ".png"
                ):
                    issues.append(f"ZIP 内文件路径或扩展名不符合规范: {name}")
                    continue
                top_dirs.add(parts[0])
                grouped[parts[1]].append(name)

            if len(top_dirs) != 1:
                issues.append("ZIP 应包含一个顶层目录")
            original_ids = {Path(name).stem for name in grouped["original"]}
            small_ids = {Path(name).stem for name in grouped["240x240"]}
            if original_ids != small_ids:
                issues.append(f"两目录编号不对应: original={sorted(original_ids)} 240={sorted(small_ids)}")
            if any(len(grouped[directory]) != len({Path(name).stem for name in grouped[directory]})
                   for directory in IMAGE_DIRS):
                issues.append("同一目录内表情编号重复")
            pairs = len(original_ids & small_ids)
            if not pairs:
                issues.append("ZIP 至少应包含一对表情图片")
            if expect_pairs is not None and pairs != expect_pairs:
                issues.append(f"应含 {expect_pairs} 对图片，实际 {pairs} 对")

            for directory, images in grouped.items():
                for name in images:
                    data = archive.read(name)
                    try:
                        with Image.open(io.BytesIO(data), formats=("PNG",)) as im:
                            im.load()
                            size = im.size
                    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
                        issues.append(f"{name} 无法解码为 PNG: {exc}")
                        continue

                    if directory == "original":
                        if max(size) < MIN_MASTER_LONG_EDGE:
                            issues.append(f"{name} 高清版尺寸过小: {size[0]}×{size[1]}")
                    else:
                        if size != (240, 240):
                            issues.append(f"{name} 尺寸非 240×240: {size[0]}×{size[1]}")
                        if len(data) > 500 * 1024:
                            rep["warnings"].append(f"{name} 超过 500KB")

            rep["summary"] = {
                "pairs": pairs,
                "original": len(grouped["original"]),
                "240x240": len(grouped["240x240"]),
            }
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        issues.append(f"ZIP 无法读取: {exc}")
        return rep

    rep["ok"] = not issues
    return rep


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("--expect-count", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rep = verify(Path(args.zipfile), args.expect_count)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        status = "通过" if rep["ok"] else "失败"
        print(f"{rep['file']} -> {status}  {rep.get('summary', '')}")
        for issue in rep["issues"]:
            print("  [错误]", issue)
        for warning in rep["warnings"]:
            print("  [警告]", warning)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
