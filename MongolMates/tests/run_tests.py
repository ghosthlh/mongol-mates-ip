#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""零依赖测试运行器：发现 tests/test_*.py 并运行，把结果写入 reports/qa/test_results.md。"""
from __future__ import annotations
import unittest, sys, io, contextlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern="test_*.py")
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    text = buf.getvalue()
    print(text)

    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed
    lines = [
        "# QA 测试报告", "",
        f"- 测试用例总数：{total}",
        f"- 通过：{passed}",
        f"- 失败/错误：{failed}",
        f"- 总体：**{'通过' if failed == 0 else '失败'}**", "",
        "## 明细", "", "```text", text.rstrip(), "```", "",
        "## 覆盖说明", "",
        "- 导出：高清→240、透明保留、白底保留、非正方形不变形、拒绝未批准/低清母版、白边不覆盖内部线。",
        "- 透明度：透明/白底检测、四角、white_scene 例外、纯白气团填充统计。",
        "- 打包：整套闸门、局部只含指定图、目录结构、ZIP 校验、240 尺寸、源文件不被修改。",
        "- 元数据：编号唯一、48 位、枚举合法、路径有效、无自动批准、高清母版诚实。",
        "- 文件保护：打包前后源母版 SHA-256 不变。",
    ]
    out = ROOT / "reports" / "qa" / "test_results.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n报告已写入: {out.relative_to(ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
