# 第一次个人编程作业：论文查重

## 作业目标

设计一个论文查重程序。程序读取原文和经过增删改的抄袭版论文，计算两篇文章的重复率，并将结果写入指定的答案文件。

## 基本要求

程序使用 Python 3 实现，入口文件为 `main.py`。

运行方式：

```bash
python main.py [原文文件绝对路径] [抄袭版文件绝对路径] [答案文件绝对路径]
```

答案文件中的重复率使用浮点数表示，并保留两位小数。

程序运行只使用 Python 3 标准库，无需额外安装第三方依赖。进入学号目录后可以执行：

```bash
python main.py /绝对路径/orig.txt /绝对路径/copy.txt /绝对路径/answer.txt
```

开发阶段的覆盖率和代码质量工具可以安装到独立环境：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/coverage run -m unittest discover -s tests
.venv/bin/coverage report -m
.venv/bin/ruff check .
```

## 开发计划

本项目计划按照以下阶段逐步完成：

1. 分析需求并填写 PSP 预计时间。
2. 设计文本相似度计算方案。
3. 实现命令行参数和文件读写。
4. 实现论文相似度计算模块。
5. 完成异常处理和单元测试。
6. 检查测试覆盖率和代码质量。
7. 进行性能分析和优化。
8. 填写 PSP 实际耗时并整理博客材料。

## 当前进度

已完成需求整理、开发前 PSP 预估、模块设计、文件读写、文本规范化、多粒度特征、组合重复率计算、命令行主程序、分支覆盖率、代码质量检查和第一轮性能优化。目前程序已经可以按照作业要求接收三个路径并输出两位小数结果。

算法从单独使用余弦相似度调整为“特征覆盖率为主、余弦相似度为辅”的组合方式，改进过程记录在 [ALGORITHM_NOTES.md](./ALGORITHM_NOTES.md)。

测试覆盖率和 Ruff 检查过程记录在 [QUALITY_REPORT.md](./QUALITY_REPORT.md)。

性能瓶颈的定位和优化前后对比记录在 [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md)。
