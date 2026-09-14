"""论文文本规范化模块的单元测试。"""

from __future__ import annotations

import math
import unittest

from plagiarism_checker import (
    calculate_similarity,
    cosine_similarity,
    extract_features,
    normalize_text,
)


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


class CosineSimilarityTests(unittest.TestCase):
    """测试特征向量的余弦相似度。"""

    def test_returns_one_for_identical_vectors(self) -> None:
        self.assertAlmostEqual(
            cosine_similarity({"a": 2, "b": 1}, {"a": 2, "b": 1}),
            1.0,
        )

    def test_returns_zero_for_vectors_without_common_features(self) -> None:
        self.assertEqual(cosine_similarity({"a": 1}, {"b": 1}), 0.0)

    def test_calculates_partial_similarity(self) -> None:
        similarity = cosine_similarity({"a": 1, "b": 1}, {"a": 1})

        self.assertAlmostEqual(similarity, 1 / math.sqrt(2))

    def test_is_symmetric(self) -> None:
        left = {"a": 3, "b": 1}
        right = {"a": 1, "c": 2}

        self.assertAlmostEqual(
            cosine_similarity(left, right),
            cosine_similarity(right, left),
        )

    def test_rejects_empty_vectors(self) -> None:
        with self.assertRaises(ValueError):
            cosine_similarity({}, {"a": 1})

    def test_rejects_non_mapping_vectors(self) -> None:
        with self.assertRaises(TypeError):
            cosine_similarity([("a", 1)], {"a": 1})  # type: ignore[arg-type]

    def test_rejects_non_string_feature_names(self) -> None:
        with self.assertRaises(TypeError):
            cosine_similarity({1: 1}, {"a": 1})  # type: ignore[dict-item]

    def test_rejects_non_numeric_feature_values(self) -> None:
        for value in ("1", None, True):
            with self.subTest(value=value), self.assertRaises(TypeError):
                cosine_similarity({"a": value}, {"a": 1})  # type: ignore[dict-item]

    def test_rejects_invalid_numeric_feature_values(self) -> None:
        for value in (-1, math.nan, math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cosine_similarity({"a": value}, {"a": 1})

    def test_rejects_zero_vector(self) -> None:
        with self.assertRaises(ValueError):
            cosine_similarity({"a": 0}, {"a": 1})


class CalculateSimilarityTests(unittest.TestCase):
    """测试完整的论文文本重复率计算。"""

    def test_returns_one_for_identical_text(self) -> None:
        self.assertAlmostEqual(calculate_similarity("今天天气晴", "今天天气晴"), 1.0)

    def test_recognizes_equivalent_sunday_expressions(self) -> None:
        self.assertAlmostEqual(
            calculate_similarity("今天是星期日", "今天是周天"),
            1.0,
        )

    def test_ignores_punctuation_and_letter_case(self) -> None:
        self.assertAlmostEqual(
            calculate_similarity("Hello，世界！", "hello 世界"),
            1.0,
        )

    def test_returns_partial_similarity_for_added_content(self) -> None:
        similarity = calculate_similarity("今天天气晴", "今天天气晴朗适合散步")

        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)

    def test_scores_related_text_higher_than_unrelated_text(self) -> None:
        original = "今天是星期日天气晴"
        related = "今天是周天天气晴朗"
        unrelated = "计算机网络使用分层体系结构"

        self.assertGreater(
            calculate_similarity(original, related),
            calculate_similarity(original, unrelated),
        )

    def test_text_similarity_is_symmetric(self) -> None:
        left = "今天晚上我要去看电影"
        right = "今天我要去电影院看电影"

        self.assertAlmostEqual(
            calculate_similarity(left, right),
            calculate_similarity(right, left),
        )


if __name__ == "__main__":
    unittest.main()
