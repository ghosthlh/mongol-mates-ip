#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""透明度测试：透明通道检测、四角、白边、气团纯白填充、white_scene 例外。"""
from __future__ import annotations
import unittest, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_transparency import check as check_t
from validate_image import check as check_img


class TestTransparency(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="mm_tr_"))

    def test_transparent_bg_ok(self):
        p = self.d/"t.png"
        im = Image.new("RGBA",(240,240),(0,0,0,0))
        ImageDraw.Draw(im).ellipse([40,40,200,200], fill=(30,90,160,255))
        im.save(p)
        r = check_t(p)
        self.assertTrue(r["ok"], r)
        self.assertGreater(r["metrics"]["transparent_ratio"], 0.3)

    def test_white_background_corner_fails(self):
        p = self.d/"w.png"
        Image.new("RGBA",(240,240),(255,255,255,255)).save(p)
        r = check_t(p)
        self.assertFalse(r["ok"])
        self.assertTrue(any("四角非透明" in i for i in r["issues"]))

    def test_white_scene_exception(self):
        p = self.d/"scene.png"
        Image.new("RGB",(240,240),(255,255,255)).save(p,"PNG")
        r = check_img(p, background_mode="white_scene")
        self.assertTrue(r["ok"], r)

    def test_transparent_mode_flags_white_bg(self):
        p = self.d/"whitebuttransparent.png"
        Image.new("RGB",(240,240),(255,255,255)).save(p,"PNG")
        r = check_img(p, background_mode="transparent")
        self.assertFalse(r["ok"])
        self.assertTrue(any("无任何透明像素" in i for i in r["issues"]))

    def test_opaque_white_fill_detected(self):
        # 模拟气团：主体外有纯白不透明区域（内部填充保留）
        p = self.d/"gas.png"
        im = Image.new("RGBA",(240,240),(0,0,0,0))
        d = ImageDraw.Draw(im)
        d.ellipse([40,40,200,200], fill=(30,90,160,255))
        d.ellipse([150,20,220,90], fill=(255,255,255,255))  # 纯白气团
        im.save(p)
        r = check_t(p)
        self.assertGreater(r["metrics"]["opaque_white_fill_ratio"], 0.01)


if __name__ == "__main__":
    unittest.main()
