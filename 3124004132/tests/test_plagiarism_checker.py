"""论文文本规范化模块的单元测试。"""

from __future__ import annotations

import unittest

from plagiarism_checker import normalize_text


class NormalizeTextTests(unittest.TestCase):
    """测试查重前的文本规范化规则。"""

    def test_keeps_chinese_content(self) -> None:
        self.assertEqual(normalize_text("今天天气晴"), "今天天气晴")

    def test_normalizes_sunday_expressions(self) -> None:
        expressions = ("星期日", "星期天", "周日", "周天")

        for expression in expressions:
            with self.subTest(expression=expression):
                self.assertEqual(normalize_text(f"今天是{expression}"), "今天是星期日")

    def test_normalizes_full_width_letters_and_numbers(self) -> None:
        self.assertEqual(normalize_text("ＡＢＣ１２３"), "abc123")

    def test_normalizes_english_letter_case(self) -> None:
        self.assertEqual(normalize_text("Python PYTHON python"), "pythonpythonpython")

    def test_removes_spaces_line_breaks_and_tabs(self) -> None:
        self.assertEqual(normalize_text("今天 \n\t 天气晴"), "今天天气晴")

    def test_removes_chinese_and_english_punctuation(self) -> None:
        self.assertEqual(normalize_text("今天，天气晴！Hello, World."), "今天天气晴helloworld")

    def test_preserves_chinese_english_and_numbers(self) -> None:
        self.assertEqual(normalize_text("AI 模型 2026版"), "ai模型2026版")

    def test_preserves_mathematical_symbols(self) -> None:
        self.assertEqual(normalize_text("x+y=2"), "x+y=2")

    def test_rejects_text_without_effective_content(self) -> None:
        for content in ("", "  \n\t", "，。！？"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                normalize_text(content)

    def test_rejects_non_string_input(self) -> None:
        for content in (None, 123, ["文本"]):
            with self.subTest(content=content), self.assertRaises(TypeError):
                normalize_text(content)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
