"""论文查重程序命令行入口。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Optional

from file_utils import read_text, write_result
from plagiarism_checker import calculate_similarity

USAGE = "用法：python main.py [原文文件] [抄袭版论文文件] [答案文件]"


def main(argv: Optional[Iterable[str]] = None) -> int:
    """读取命令行参数，完成查重并返回程序退出状态。"""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 3:
        print(USAGE, file=sys.stderr)
        return 2

    original_path, suspicious_path, answer_path = arguments

    try:
        answer_location = Path(answer_path).resolve()
        input_locations = {
            Path(original_path).resolve(),
            Path(suspicious_path).resolve(),
        }
        if answer_location in input_locations:
            raise ValueError("答案文件不能覆盖原文或抄袭版论文")

        original = read_text(original_path)
        suspicious = read_text(suspicious_path)
        similarity = calculate_similarity(original, suspicious)
        write_result(answer_path, similarity)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover - 由子进程集成测试验证
    raise SystemExit(main())
