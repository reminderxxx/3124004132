"""论文查重命令行入口的单元测试和集成测试。"""

from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from main import main


class MainTests(unittest.TestCase):
    """测试三个文件参数组成的完整运行流程。"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.original_path = self.base_path / "orig.txt"
        self.suspicious_path = self.base_path / "copy.txt"
        self.answer_path = self.base_path / "answer.txt"
        self.original_path.write_text("今天是星期日，天气晴。", encoding="utf-8")
        self.suspicious_path.write_text("今天是周天，天气晴朗。", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_main(self, arguments: list[str]) -> tuple[int, str]:
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            exit_code = main(arguments)
        return exit_code, error_output.getvalue()

    def test_writes_answer_for_valid_arguments(self) -> None:
        exit_code, error_message = self.run_main(
            [str(self.original_path), str(self.suspicious_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(error_message, "")
        self.assertRegex(self.answer_path.read_text(encoding="utf-8"), r"^\d\.\d{2}$")

    def test_writes_one_for_identical_papers(self) -> None:
        self.suspicious_path.write_text(
            self.original_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        exit_code, _ = self.run_main(
            [str(self.original_path), str(self.suspicious_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(self.answer_path.read_text(encoding="utf-8"), "1.00")

    def test_writes_zero_for_unrelated_papers(self) -> None:
        self.suspicious_path.write_text("计算机网络采用分层结构。", encoding="utf-8")

        exit_code, _ = self.run_main(
            [str(self.original_path), str(self.suspicious_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(self.answer_path.read_text(encoding="utf-8"), "0.00")

    def test_rejects_wrong_argument_count(self) -> None:
        argument_groups = (
            [],
            ["orig.txt", "copy.txt"],
            ["a.txt", "b.txt", "c.txt", "d.txt"],
        )

        for arguments in argument_groups:
            with self.subTest(arguments=arguments):
                exit_code, error_message = self.run_main(arguments)
                self.assertEqual(exit_code, 2)
                self.assertIn("用法", error_message)

    def test_reports_missing_original_file(self) -> None:
        missing_path = self.base_path / "missing.txt"

        exit_code, error_message = self.run_main(
            [str(missing_path), str(self.suspicious_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("输入文件不存在", error_message)
        self.assertFalse(self.answer_path.exists())

    def test_reports_missing_suspicious_file(self) -> None:
        missing_path = self.base_path / "missing.txt"

        exit_code, error_message = self.run_main(
            [str(self.original_path), str(missing_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("输入文件不存在", error_message)
        self.assertFalse(self.answer_path.exists())

    def test_reports_empty_input_file(self) -> None:
        self.suspicious_path.write_text("", encoding="utf-8")

        exit_code, error_message = self.run_main(
            [str(self.original_path), str(self.suspicious_path), str(self.answer_path)]
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("没有有效内容", error_message)
        self.assertFalse(self.answer_path.exists())

    def test_reports_missing_output_directory(self) -> None:
        answer_path = self.base_path / "missing" / "answer.txt"

        exit_code, error_message = self.run_main(
            [str(self.original_path), str(self.suspicious_path), str(answer_path)]
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("输出目录不存在", error_message)
        self.assertFalse(answer_path.exists())

    def test_does_not_overwrite_input_files(self) -> None:
        for answer_path in (self.original_path, self.suspicious_path):
            with self.subTest(answer_path=answer_path):
                previous_content = answer_path.read_text(encoding="utf-8")
                exit_code, error_message = self.run_main(
                    [
                        str(self.original_path),
                        str(self.suspicious_path),
                        str(answer_path),
                    ]
                )
                self.assertEqual(exit_code, 1)
                self.assertIn("不能覆盖", error_message)
                self.assertEqual(
                    answer_path.read_text(encoding="utf-8"),
                    previous_content,
                )

    def test_real_command_line_execution(self) -> None:
        project_dir = Path(__file__).resolve().parent.parent
        completed = subprocess.run(
            [
                sys.executable,
                str(project_dir / "main.py"),
                str(self.original_path),
                str(self.suspicious_path),
                str(self.answer_path),
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")
        self.assertIsNotNone(
            re.fullmatch(r"\d\.\d{2}", self.answer_path.read_text(encoding="utf-8"))
        )


if __name__ == "__main__":
    unittest.main()
