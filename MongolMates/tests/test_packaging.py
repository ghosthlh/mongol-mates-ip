#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包测试：整套数量、局部只含指定图、目录名、缺高清拒绝、ZIP 可解压、240 尺寸约束、源保护。"""
from __future__ import annotations
import unittest, sys, tempfile, zipfile, io
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).parent))
from _factory import temp_project, make_master, set_approved
from package_series import package as package_series
from package_patch import package_patch
from verify_zip import verify
from mm_common import sha256_file


class TestPackaging(unittest.TestCase):
    def setUp(self):
        self.root = temp_project()
        self.master = make_master(self.root / "m.png", 1200, transparent=True)
        # 批准第 11 张并给母版
        set_approved(self.root, "vol03_reactions", "11", "m.png")

    def test_refuses_full_when_not_all_approved(self):
        out = self.root/"full.zip"
        r = package_series(self.root, "vol03_reactions", "1.0", out)
        self.assertFalse(r["ok"])
        self.assertFalse(out.exists(), "被拒时不应留下半成品 ZIP")

    def test_patch_only_requested_items(self):
        out = self.root/"patch.zip"
        r = package_patch(self.root, "vol03_reactions", ["11"], "1.1", out)
        self.assertTrue(r["ok"], r)
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
        self.assertEqual(len([n for n in names if n.endswith(".png")]), 2)  # 一原一240
        self.assertTrue(all("/11.png" in n for n in names if n.endswith(".png")))

    def test_patch_refuses_unapproved(self):
        out = self.root/"p2.zip"
        r = package_patch(self.root, "vol03_reactions", ["01"], "1.1", out)
        self.assertFalse(r["ok"]); self.assertFalse(out.exists())

    def test_zip_structure_and_verify(self):
        out = self.root/"p3.zip"
        package_patch(self.root, "vol03_reactions", ["11"], "1.1", out)
        rep = verify(out, expect_pairs=1)
        self.assertTrue(rep["ok"], rep)
        self.assertEqual(rep["summary"]["pairs"], 1)
        with zipfile.ZipFile(out) as zf:
            self.assertTrue(all(Path(n).parts[1] in ("original","240x240") for n in zf.namelist()))

    def test_240_size_constraint(self):
        out = self.root/"p4.zip"
        package_patch(self.root, "vol03_reactions", ["11"], "1.1", out)
        with zipfile.ZipFile(out) as zf:
            n = [x for x in zf.namelist() if "240x240" in x][0]
            with Image.open(io.BytesIO(zf.read(n))) as im:
                self.assertEqual(im.size,(240,240))

    def test_verify_rejects_wrong_count(self):
        out = self.root/"p5.zip"
        package_patch(self.root, "vol03_reactions", ["11"], "1.1", out)
        rep = verify(out, expect_pairs=16)
        self.assertFalse(rep["ok"])

    def test_source_master_not_modified(self):
        before = sha256_file(self.master)
        out = self.root/"p6.zip"
        package_patch(self.root, "vol03_reactions", ["11"], "1.1", out)
        self.assertEqual(sha256_file(self.master), before, "打包不得修改源母版")


if __name__ == "__main__":
    unittest.main()
