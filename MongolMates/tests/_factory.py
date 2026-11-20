#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用临时素材工厂：生成测试用高清母版、透明图、白底图、临时项目副本。"""
from __future__ import annotations
import tempfile, shutil, yaml
from pathlib import Path
from PIL import Image

PROJ = Path(__file__).resolve().parents[1]


def make_master(path: Path, size=1200, transparent=True, color=(40,90,160,255)):
    path.parent.mkdir(parents=True, exist_ok=True)
    bg = (255,255,255,0) if transparent else (255,255,255,255)
    im = Image.new("RGBA", (size,size), bg)
    # 画一个居中实心块，带透明边缘（模拟角色）
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    d.ellipse([size*0.2,size*0.2,size*0.8,size*0.8], fill=color)
    im.save(path, "PNG")
    return path


def make_240_lowres(path: Path, color=(40,90,160,255)):
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGBA", (240,240), (0,0,0,0))
    from PIL import ImageDraw
    ImageDraw.Draw(im).ellipse([40,40,200,200], fill=color)
    im.save(path, "PNG")
    return path


def temp_project() -> Path:
    """复制项目文本配置到临时目录（不含真实大图），用于非破坏性测试。"""
    tmp = Path(tempfile.mkdtemp(prefix="mm_test_"))
    for name in ["config", "tools", "characters", "series"]:
        src = PROJ / name
        dst = tmp / name
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.png","*.jpg","__pycache__"))
    return tmp


def set_approved(root: Path, series: str, sticker: str, master_rel: str):
    p = root / "config" / "asset_manifest.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    for it in data["items"]:
        if it["series_id"]==series and str(it["sticker_id"]).zfill(2)==str(sticker).zfill(2):
            it["approval_status"]="approved"
            it["is_native_master"]=True
            it["missing_native_master"]=False
            it["master_file"]=master_rel
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
