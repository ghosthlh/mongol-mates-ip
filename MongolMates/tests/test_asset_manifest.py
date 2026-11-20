#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""元数据测试：编号唯一、角色/背景/状态合法、路径引用、无自动批准。"""
from __future__ import annotations
import unittest, sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mm_common import (load_manifest, project_root, VALID_ROLES, VALID_BG,
                       VALID_STATUS, VALID_COMP, VALID_SERIES, sha256_file)
from validate_character_metadata import validate


class TestManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = project_root()
        cls.m = load_manifest(cls.root)
        cls.items = cls.m["items"]

    def test_unique_ids(self):
        keys = [(i["series_id"], str(i["sticker_id"]).zfill(2)) for i in self.items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_48_slots(self):
        self.assertEqual(len(self.items), 48)
        for s in VALID_SERIES:
            self.assertEqual(sum(1 for i in self.items if i["series_id"]==s), 16)

    def test_legal_enums(self):
        for i in self.items:
            with self.subTest(item=i["sticker_id"]):
                self.assertTrue(set(i.get("characters") or []) <= VALID_ROLES)
                self.assertIn(i["background_mode"], VALID_BG)
                self.assertIn(i["approval_status"], VALID_STATUS)
                self.assertIn(i["composition"], VALID_COMP)

    def test_approved_only_after_user_confirmation(self):
        # 用户 2026-11-20 明确确认嘴替篇为满意版本 -> 16 张 approved；
        # 其余两套无用户确认，必须保持 needs_review（体现“不自动批准”）
        approved = [i for i in self.items if i["approval_status"]=="approved"]
        self.assertEqual(len(approved), 16)
        self.assertTrue(all(i["series_id"]=="vol03_reactions" for i in approved))
        others = [i for i in self.items if i["series_id"]!="vol03_reactions"]
        self.assertTrue(all(i["approval_status"]=="needs_review" for i in others))

    def test_path_references_exist(self):
        for i in self.items:
            p = (self.root / i["source_file"]).resolve()
            self.assertTrue(p.exists(), f"源文件不存在: {i['source_file']}")

    def test_metadata_validator_clean(self):
        errors, warnings = validate(self.root)
        self.assertEqual(errors, [], errors)
        self.assertEqual(warnings, [], warnings)

    def test_native_master_honest(self):
        for item in self.items:
            with self.subTest(series=item["series_id"], sticker=item["sticker_id"]):
                self.assertNotEqual(item["is_native_master"], item["missing_native_master"])
                if item["is_native_master"]:
                    master = self.root / item["master_file"]
                    self.assertEqual(item["approval_status"], "approved")
                    self.assertEqual(sha256_file(master), item["master_sha256"])
                    with Image.open(master) as im:
                        self.assertEqual(im.format, "PNG")
                        self.assertEqual(f"{im.width}x{im.height}", item["master_resolution"])
        s11 = [i for i in self.items if i["series_id"]=="vol03_reactions" and str(i["sticker_id"])=="11"][0]
        self.assertEqual(s11["approval_status"], "approved")
        self.assertEqual(s11["rejected_candidates"][0]["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
