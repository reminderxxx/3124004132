"""论文文本规范化模块的单元测试。"""

from __future__ import annotations

import unittest

from plagiarism_checker import extract_features, normalize_text


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
        self.assertEqual(
            normalize_text("今天，天气晴！Hello, World."),
            "今天天气晴helloworld",
        )

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


class ExtractFeaturesTests(unittest.TestCase):
    """测试多粒度字符特征提取。"""

    def test_extracts_unigram_features(self) -> None:
        features = extract_features("天气晴", (1,))

        self.assertEqual(features, {"1:天": 1, "1:气": 1, "1:晴": 1})

    def test_extracts_bigram_features(self) -> None:
        features = extract_features("天气晴", (2,))

        self.assertEqual(features, {"2:天气": 1, "2:气晴": 1})

    def test_extracts_default_multi_granularity_features(self) -> None:
        features = extract_features("天气晴")

        self.assertEqual(
            features,
            {
                "1:天": 1,
                "1:气": 1,
                "1:晴": 1,
                "2:天气": 1,
                "2:气晴": 1,
            },
        )

    def test_counts_repeated_features(self) -> None:
        features = extract_features("天天天")

        self.assertEqual(features["1:天"], 3)
        self.assertEqual(features["2:天天"], 2)

    def test_supports_single_character_text(self) -> None:
        self.assertEqual(extract_features("天"), {"1:天": 1})

    def test_supports_custom_ngram_size(self) -> None:
        self.assertEqual(extract_features("天气晴", (3,)), {"3:天气晴": 1})

    def test_removes_duplicate_ngram_sizes(self) -> None:
        self.assertEqual(extract_features("天气", (1, 1)), {"1:天": 1, "1:气": 1})

    def test_uses_normalized_equivalent_expressions(self) -> None:
        self.assertEqual(
            extract_features("今天是星期天"),
            extract_features("今天是周天"),
        )

    def test_rejects_empty_ngram_sizes(self) -> None:
        with self.assertRaises(ValueError):
            extract_features("天气晴", ())

    def test_rejects_non_integer_ngram_sizes(self) -> None:
        for sizes in ((1, 2.0), (True,), ("2",)):
            with self.subTest(sizes=sizes), self.assertRaises(TypeError):
                extract_features("天气晴", sizes)  # type: ignore[arg-type]

    def test_rejects_non_positive_ngram_sizes(self) -> None:
        for sizes in ((0,), (-1,)):
            with self.subTest(sizes=sizes), self.assertRaises(ValueError):
                extract_features("天气晴", sizes)

    def test_rejects_text_shorter_than_requested_ngram(self) -> None:
        with self.assertRaises(ValueError):
            extract_features("天", (2,))


if __name__ == "__main__":
    unittest.main()
