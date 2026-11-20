# QA 测试报告

- 测试用例总数：26
- 通过：26
- 失败/错误：0
- 总体：**通过**

## 明细

```text
test_48_slots (test_asset_manifest.TestManifest.test_48_slots) ... ok
test_approved_only_after_user_confirmation (test_asset_manifest.TestManifest.test_approved_only_after_user_confirmation) ... ok
test_legal_enums (test_asset_manifest.TestManifest.test_legal_enums) ... ok
test_metadata_validator_clean (test_asset_manifest.TestManifest.test_metadata_validator_clean) ... ok
test_native_master_honest (test_asset_manifest.TestManifest.test_native_master_honest) ... ok
test_path_references_exist (test_asset_manifest.TestManifest.test_path_references_exist) ... ok
test_unique_ids (test_asset_manifest.TestManifest.test_unique_ids) ... ok
test_export_preserves_transparency (test_exports.TestExports.test_export_preserves_transparency) ... ok
test_export_transparent_master (test_exports.TestExports.test_export_transparent_master) ... ok
test_export_white_scene_keeps_white (test_exports.TestExports.test_export_white_scene_keeps_white) ... ok
test_no_stretch_non_square_master (test_exports.TestExports.test_no_stretch_non_square_master) ... ok
test_outline_keeps_inner_line (test_exports.TestExports.test_outline_keeps_inner_line) ... ok
test_rejects_lowres_master (test_exports.TestExports.test_rejects_lowres_master) ... ok
test_rejects_unapproved (test_exports.TestExports.test_rejects_unapproved) ... ok
test_240_size_constraint (test_packaging.TestPackaging.test_240_size_constraint) ... ok
test_patch_only_requested_items (test_packaging.TestPackaging.test_patch_only_requested_items) ... ok
test_patch_refuses_unapproved (test_packaging.TestPackaging.test_patch_refuses_unapproved) ... ok
test_refuses_full_when_not_all_approved (test_packaging.TestPackaging.test_refuses_full_when_not_all_approved) ... ok
test_source_master_not_modified (test_packaging.TestPackaging.test_source_master_not_modified) ... ok
test_verify_rejects_wrong_count (test_packaging.TestPackaging.test_verify_rejects_wrong_count) ... ok
test_zip_structure_and_verify (test_packaging.TestPackaging.test_zip_structure_and_verify) ... ok
test_opaque_white_fill_detected (test_transparency.TestTransparency.test_opaque_white_fill_detected) ... ok
test_transparent_bg_ok (test_transparency.TestTransparency.test_transparent_bg_ok) ... ok
test_transparent_mode_flags_white_bg (test_transparency.TestTransparency.test_transparent_mode_flags_white_bg) ... ok
test_white_background_corner_fails (test_transparency.TestTransparency.test_white_background_corner_fails) ... ok
test_white_scene_exception (test_transparency.TestTransparency.test_white_scene_exception) ... ok

----------------------------------------------------------------------
Ran 26 tests in 5.762s

OK
```

## 覆盖说明

- 导出：高清→240、透明保留、白底保留、非正方形不变形、拒绝未批准/低清母版、白边不覆盖内部线。
- 透明度：透明/白底检测、四角、white_scene 例外、纯白气团填充统计。
- 打包：整套闸门、局部只含指定图、目录结构、ZIP 校验、240 尺寸、源文件不被修改。
- 元数据：编号唯一、48 位、枚举合法、路径有效、无自动批准、高清母版诚实。
- 文件保护：打包前后源母版 SHA-256 不变。