"""文件读写模块的单元测试。"""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from file_utils import read_text, write_result


class ReadTextTests(unittest.TestCase):
    """测试论文文本读取行为。"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_reads_utf8_chinese_text(self) -> None:
        input_path = self.base_path / "paper.txt"
        input_path.write_text("今天是星期日。", encoding="utf-8")

        self.assertEqual(read_text(input_path), "今天是星期日。")

    def test_reads_utf8_text_with_bom(self) -> None:
        input_path = self.base_path / "paper_with_bom.txt"
        input_path.write_text("今天是周天。", encoding="utf-8-sig")

        self.assertEqual(read_text(input_path), "今天是周天。")

    def test_preserves_line_breaks_and_spaces(self) -> None:
        input_path = self.base_path / "multiline.txt"
        content = "第一段。\n\n  第二段。\n"
        input_path.write_text(content, encoding="utf-8")

        self.assertEqual(read_text(input_path), content)

    def test_rejects_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_text(self.base_path / "missing.txt")

    def test_rejects_directory_path(self) -> None:
        with self.assertRaises(IsADirectoryError):
            read_text(self.base_path)

    def test_rejects_empty_file(self) -> None:
        input_path = self.base_path / "empty.txt"
        input_path.write_text("", encoding="utf-8")

        with self.assertRaises(ValueError):
            read_text(input_path)

    def test_rejects_whitespace_only_file(self) -> None:
        input_path = self.base_path / "whitespace.txt"
        input_path.write_text(" \n\t", encoding="utf-8")

        with self.assertRaises(ValueError):
            read_text(input_path)


class WriteResultTests(unittest.TestCase):
    """测试重复率结果写入行为。"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_writes_similarity_with_two_decimal_places(self) -> None:
        output_path = self.base_path / "answer.txt"

        write_result(output_path, 0.376)

        self.assertEqual(output_path.read_text(encoding="utf-8"), "0.38")

    def test_writes_zero_boundary(self) -> None:
        output_path = self.base_path / "zero.txt"

        write_result(output_path, 0)

        self.assertEqual(output_path.read_text(encoding="utf-8"), "0.00")

    def test_writes_one_boundary(self) -> None:
        output_path = self.base_path / "one.txt"

        write_result(output_path, 1)

        self.assertEqual(output_path.read_text(encoding="utf-8"), "1.00")

    def test_rejects_values_outside_valid_range(self) -> None:
        output_path = self.base_path / "answer.txt"
        for value in (-0.01, 1.01):
            with self.subTest(value=value), self.assertRaises(ValueError):
                write_result(output_path, value)

    def test_rejects_non_finite_values(self) -> None:
        output_path = self.base_path / "answer.txt"
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                write_result(output_path, value)

    def test_rejects_non_numeric_values(self) -> None:
        output_path = self.base_path / "answer.txt"
        for value in ("0.5", None, True):
            with self.subTest(value=value), self.assertRaises(TypeError):
                write_result(output_path, value)  # type: ignore[arg-type]

    def test_rejects_directory_as_output_path(self) -> None:
        with self.assertRaises(IsADirectoryError):
            write_result(self.base_path, 0.5)

    def test_rejects_missing_output_directory(self) -> None:
        output_path = self.base_path / "missing" / "answer.txt"

        with self.assertRaises(FileNotFoundError):
            write_result(output_path, 0.5)
