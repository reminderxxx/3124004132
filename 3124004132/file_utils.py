"""论文文件读取和查重结果写入工具。"""

from __future__ import annotations

import math
from numbers import Real
from pathlib import Path
from typing import Union


PathLike = Union[str, Path]


def read_text(path: PathLike) -> str:
    """读取非空的 UTF-8 论文文本。

    ``utf-8-sig`` 同时兼容普通 UTF-8 文件和带 BOM 的 UTF-8 文件。
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"输入文件不存在：{file_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"输入路径不是文件：{file_path}")

    text = file_path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ValueError(f"输入文件没有有效内容：{file_path}")
    return text


def write_result(path: PathLike, similarity: Real) -> None:
    """将 0 到 1 之间的重复率按两位小数写入指定文件。"""

    if isinstance(similarity, bool) or not isinstance(similarity, Real):
        raise TypeError("重复率必须是数值")

    value = float(similarity)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("重复率必须是 0 到 1 之间的有限数值")

    output_path = Path(path)
    if output_path.exists() and not output_path.is_file():
        raise IsADirectoryError(f"输出路径不是文件：{output_path}")
    if not output_path.parent.exists():
        raise FileNotFoundError(f"输出目录不存在：{output_path.parent}")

    output_path.write_text(f"{value:.2f}", encoding="utf-8")
