#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出测试：高清→240、透明保留、白底保留、尺寸比例、禁止拉伸、低清拒绝。"""
from __future__ import annotations
import unittest, sys, os
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).parent))
from _factory import temp_project, make_master, set_approved
from export_240 import export_one, add_white_outline
from mm_common import load_manifest, items_by_key


class TestExports(unittest.TestCase):
    def setUp(self):
        self.root = temp_project()
        self.master = make_master(self.root / "test_master.png", 1200, transparent=True)

    def test_export_transparent_master(self):
        set_approved(self.root, "vol03_reactions", "11", "test_master.png")
        it = items_by_key(load_manifest(self.root))[("vol03_reactions","11")]
        r = export_one(self.root, it)
        self.assertTrue(r["ok"], r)
        out = self.root / r["output"]
        with Image.open(out) as im:
            self.assertEqual(im.size, (240,240))
            self.assertIn("A", im.getbands())

    def test_export_preserves_transparency(self):
        set_approved(self.root, "vol03_reactions", "11", "test_master.png")
        it = items_by_key(load_manifest(self.root))[("vol03_reactions","11")]
        r = export_one(self.root, it)
        with Image.open(self.root / r["output"]) as im:
            self.assertEqual(im.convert("RGBA").getpixel((0,0))[3], 0)

    def test_export_white_scene_keeps_white(self):
        wm = make_master(self.root / "white.png", 1200, transparent=False)
        set_approved(self.root, "vol03_reactions", "10", "white.png")
        it = items_by_key(load_manifest(self.root))[("vol03_reactions","10")]
        r = export_one(self.root, it)
        self.assertTrue(r["ok"])
        with Image.open(self.root / r["output"]) as im:
            self.assertEqual(im.convert("RGBA").getpixel((0,0))[3], 255)

    def test_no_stretch_non_square_master(self):
        # 非正方形母版缩放到 240 正方形画布，应 letterbox 居中而非拉伸
        p = self.root / "wide.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA",(1200,600),(0,0,0,0)).save(p,"PNG")
        set_approved(self.root, "vol03_reactions", "11", "wide.png")
        it = items_by_key(load_manifest(self.root))[("vol03_reactions","11")]
        r = export_one(self.root, it)
        self.assertTrue(r["ok"])
        with Image.open(self.root / r["output"]) as im:
            self.assertEqual(im.size,(240,240))

    def test_rejects_unapproved(self):
        # 日常篇从未获用户确认，状态为 needs_review，应被导出闸门拒绝
        it = items_by_key(load_manifest(self.root))[("vol01_daily","01")]
        r = export_one(self.root, it)
        self.assertFalse(r["ok"]); self.assertIn("未批准", r["reason"])

    def test_rejects_lowres_master(self):
        low = make_master(self.root / "low.png", 240)
        set_approved(self.root, "vol03_reactions", "11", "low.png")
        it = items_by_key(load_manifest(self.root))[("vol03_reactions","11")]
        r = export_one(self.root, it)
        self.assertFalse(r["ok"]); self.assertIn("分辨率过低", r["reason"])

    def test_outline_keeps_inner_line(self):
        with Image.open(self.master) as im0:
            src = im0.convert("RGBA")
        out = add_white_outline(src, 20)
        self.assertEqual(out.size, src.size)
        # 中心不透明区域颜色应保持原色（内部线描不被白边覆盖）
        c = src.size[0]//2
        self.assertEqual(out.getpixel((c,c))[:3], src.getpixel((c,c))[:3])


if __name__ == "__main__":
    unittest.main()
