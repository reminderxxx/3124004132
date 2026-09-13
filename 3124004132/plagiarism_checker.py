"""论文文本规范化与相似度计算模块。"""

from __future__ import annotations

import unicodedata


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
