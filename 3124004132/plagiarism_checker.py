"""论文文本规范化与相似度计算模块。"""

from __future__ import annotations

import unicodedata
from collections import Counter
from collections.abc import Iterable


EQUIVALENT_EXPRESSIONS = {
    "星期天": "星期日",
    "周日": "星期日",
    "周天": "星期日",
}


def normalize_text(text: str) -> str:
    """统一文本形式，并移除不参与查重的空白和标点。

    只归一化含义明确的少量等价表达，避免使用范围过大的手工
    同义词表改变原文含义。数学符号等非标点字符会被保留。
    """

    if not isinstance(text, str):
        raise TypeError("待规范化的内容必须是字符串")

    normalized = unicodedata.normalize("NFKC", text).lower()
    for expression, canonical_expression in EQUIVALENT_EXPRESSIONS.items():
        normalized = normalized.replace(expression, canonical_expression)

    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character)[0] not in {"P", "Z", "C"}
    )
    if not normalized:
        raise ValueError("文本规范化后没有有效内容")
    return normalized


def extract_features(
    text: str, ngram_sizes: Iterable[int] = (1, 2)
) -> Counter[str]:
    """提取带频次的一元、二元或指定长度的字符 n-gram 特征。"""

    sizes = tuple(ngram_sizes)
    if not sizes:
        raise ValueError("至少需要指定一种 n-gram 长度")
    if any(isinstance(size, bool) or not isinstance(size, int) for size in sizes):
        raise TypeError("n-gram 长度必须是整数")
    if any(size <= 0 for size in sizes):
        raise ValueError("n-gram 长度必须大于 0")

    normalized = normalize_text(text)
    features: Counter[str] = Counter()
    for size in sorted(set(sizes)):
        for start in range(len(normalized) - size + 1):
            ngram = normalized[start : start + size]
            features[f"{size}:{ngram}"] += 1

    if not features:
        raise ValueError("文本长度不足以生成指定的 n-gram 特征")
    return features
