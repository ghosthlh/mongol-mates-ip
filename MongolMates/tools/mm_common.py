#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mongolmates 工具共享库：路径解析（相对项目，绝不写死绝对路径）、清单加载、通用校验。"""
from __future__ import annotations
import os, sys, hashlib, yaml
from pathlib import Path
from PIL import Image

VALID_STATUS = {"imported","needs_review","working","candidate","approved","rejected","archived"}
VALID_BG = {"transparent","white_scene"}
VALID_COMP = {"bust","full_body","seated","scene"}
VALID_ROLES = {"father","mother","sister","brother"}
VALID_SERIES = {"vol01_daily","vol02_emotions","vol03_reactions"}


def project_root() -> Path:
    """项目根目录 = 本文件所在 tools/ 的上一级。可在环境变量覆盖（便于测试）。"""
    env = os.environ.get("MM_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def resolve(root: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    p = Path(rel)
    return p if p.is_absolute() else (root / p)


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_manifest(root: Path | None = None) -> dict:
    root = root or project_root()
    return load_yaml(root / "config" / "asset_manifest.yaml")


def items_by_key(manifest: dict) -> dict:
    return {(i["series_id"], str(i["sticker_id"]).zfill(2)): i for i in manifest["items"]}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def image_info(path: Path) -> dict:
    """读取图片真实规格。返回 dict，含 ok/format/size/mode/has_alpha/alpha_min/max。"""
    info = {"path": str(path), "exists": path.exists(), "ok": False}
    if not path.exists():
        return info
    try:
        with Image.open(path) as im:
            im.load()
            info.update({"format": im.format, "size": list(im.size), "mode": im.mode})
            bands = im.getbands()
            has_alpha = "A" in bands or (im.mode == "P" and "transparency" in im.info)
            info["has_alpha"] = has_alpha
            if has_alpha:
                a = im.convert("RGBA").getchannel("A")
                info["alpha_min"], info["alpha_max"] = a.getextrema()
            info["ok"] = True
    except Exception as e:
        info["error"] = repr(e)
    return info


def stamp() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
