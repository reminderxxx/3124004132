"""论文文本规范化与相似度计算模块。"""

from __future__ import annotations

import math
import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from numbers import Real

EQUIVALENT_EXPRESSIONS = {
    "星期天": "星期日",
    "周日": "星期日",
    "周天": "星期日",
}

# 一元特征负责看“内容还剩多少”，二元、三元特征补充局部顺序。
NGRAM_WEIGHTS = {1: 0.75, 2: 0.20, 3: 0.05}
COVERAGE_WEIGHT = 0.80
COSINE_WEIGHT = 0.20


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


def _validate_feature_vector(
    features: Mapping[str, Real], vector_name: str
) -> None:
    """检查特征向量是否可以参与余弦相似度计算。"""

    if not isinstance(features, Mapping):
        raise TypeError(f"{vector_name}必须是特征映射")
    if not features:
        raise ValueError(f"{vector_name}不能为空")

    has_positive_value = False
    for feature, value in features.items():
        if not isinstance(feature, str):
            raise TypeError(f"{vector_name}的特征名称必须是字符串")
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{vector_name}的特征值必须是数值")

        numeric_value = float(value)
        if not math.isfinite(numeric_value) or numeric_value < 0:
            raise ValueError(f"{vector_name}的特征值必须是非负有限数值")
        has_positive_value = has_positive_value or numeric_value > 0

    if not has_positive_value:
        raise ValueError(f"{vector_name}不能是零向量")


def cosine_similarity(
    left_features: Mapping[str, Real], right_features: Mapping[str, Real]
) -> float:
    """计算两个非负特征向量的余弦相似度。"""

    _validate_feature_vector(left_features, "左侧特征向量")
    _validate_feature_vector(right_features, "右侧特征向量")

    dot_product = math.fsum(
        float(value) * float(right_features.get(feature, 0))
        for feature, value in left_features.items()
    )
    left_norm = math.sqrt(
        math.fsum(float(value) ** 2 for value in left_features.values())
    )
    right_norm = math.sqrt(
        math.fsum(float(value) ** 2 for value in right_features.values())
    )
    similarity = dot_product / (left_norm * right_norm)
    return min(1.0, max(0.0, similarity))


def feature_overlap(
    left_features: Mapping[str, Real], right_features: Mapping[str, Real]
) -> float:
    """计算重复特征数占较大特征集合的比例。"""

    _validate_feature_vector(left_features, "左侧特征向量")
    _validate_feature_vector(right_features, "右侧特征向量")

    common_count = math.fsum(
        min(float(value), float(right_features.get(feature, 0)))
        for feature, value in left_features.items()
    )
    left_count = math.fsum(float(value) for value in left_features.values())
    right_count = math.fsum(float(value) for value in right_features.values())
    return common_count / max(left_count, right_count)


def calculate_similarity(original: str, suspicious: str) -> float:
    """规范化两篇文本、提取特征并返回 0 到 1 之间的重复率。"""

    normalized_original = normalize_text(original)
    normalized_suspicious = normalize_text(suspicious)
    shortest_length = min(len(normalized_original), len(normalized_suspicious))
    available_weights = {
        size: weight
        for size, weight in NGRAM_WEIGHTS.items()
        if size <= shortest_length
    }

    original_features: Counter[str] = Counter()
    suspicious_features: Counter[str] = Counter()
    coverage_score = 0.0
    total_weight = sum(available_weights.values())

    for size, weight in available_weights.items():
        original_part = extract_features(normalized_original, (size,))
        suspicious_part = extract_features(normalized_suspicious, (size,))
        original_features.update(original_part)
        suspicious_features.update(suspicious_part)
        coverage_score += weight * feature_overlap(original_part, suspicious_part)

    coverage_score /= total_weight
    distribution_score = cosine_similarity(original_features, suspicious_features)
    similarity = (
        COVERAGE_WEIGHT * coverage_score + COSINE_WEIGHT * distribution_score
    )
    return min(1.0, max(0.0, similarity))
