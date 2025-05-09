# run-main: 一个用于增强调试的通用 Python 模块运行器

**在 Python 项目中，我们强烈推荐优先使用相对导入（例如 `from . import sibling_module` 或 `from ..package import other_module`）来组织模块间的依赖关系，这有助于提升代码的可维护性和项目的可移植性。**

`run-main` 这个实用工具（现在可以作为 `run-main` 包安装）正是为了让您能便捷地遵循这一最佳实践而设计。它旨在简化大型项目结构中单个 Python 模块（`.py` 文件）的执行和调试，特别是那些通过定义 `_main()` 函数作为主入口点的模块。`run-main` 不仅模拟了 `python -m <package.module>` 对于单个文件的行为，**更关键的是，它能确保在执行时正确解析相对导入，从而避免了直接运行子模块时常见的 `ImportError`**。同时，它也提供了“快速失败”的调试体验。

## 快速上手

1.  **在您的目标模块中定义 `_main()` 函数**：
    您的 Python 文件 (`your_module.py`) 应该定义一个名为 `_main()` 的函数：
    ```python
    # 在 your_module.py 中
    def _main(*args):
        print(f"你好，来自 {__file__} 中的 _main 函数！")
        if args:
            print(f"收到的参数: {args}")

    # 可选：如果也希望通过 `python your_module.py` 直接执行
    # if __name__ == "__main__":
    #     import sys
    #     _main(*sys.argv[1:])
    ```
**为何使用 `_main()`？** 当直接运行 Python 文件时，其 `__name__` 会变为 `__main__`。这种标准方式在使用相对导入（例如 `from . import utils`）时可能导致 `ImportError`，因为缺少包上下文。`run-main` 将您的文件作为包的一部分执行，并调用 `_main()`，从而确保相对导入正常工作。可将 `_main()` 理解为 `run-main` 感知的主入口点。

        **从 `if __name__ == "__main__"` 迁移：** 只需将 `if __name__ == "__main__":` 代码块中的逻辑移至 `def _main(*args):` 函数内。`run-main` 会通过 `*args` 将命令行参数传递给 `_main`。您可以保留 `if __name__ == "__main__": _main(*sys.argv[1:])` 代码块以实现可选的直接执行，但推荐使用 `run-main` 以进行包感知的执行。

2.  **安装 `run-main`**:
    ```bash
    pip install run-main
    ```

3.  **从命令行运行**:
    使用 `run-main` 命令执行您的模块：
    ```bash
    run-main path/to/your_module.py 参数1 参数2
    ```

4.  **在 VS Code 中调试 (推荐的 `launch.json` 配置)**:
    在您的项目中创建或更新 `.vscode/launch.json` 文件：
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: 使用 run-main 调试",
                "type": "debugpy",
                "request": "launch",
                "module": "run_main", // 使用已安装的 run_main 模块
                "args": [
                    "${file}", // 指向当前打开的、要运行的 .py 文件的路径，${relativeFile}也行
                    // 在此处为您的 _main() 函数添加其他参数，例如：
                    // "我的参数1",
                    // "--我的选项", "值"
                ],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}" // 或包含目标文件的项目的根目录
            }
        ]
    }
    ```
    打开包含 `_main()` 的 Python 文件，然后按 F5 开始调试。

[English Version (英文版)](README.md)

## 它解决的问题

在开发和调试 Python 项目时，尤其是那些组织成包（package）的项目，当试图运行或调试单个文件时，可能会遇到一些常见障碍：

1.  **相对导入错误 (Relative Import Errors) 与 `run-main` 的解决方案**：
    *   **什么是相对导入？为何推荐使用？**
        在 Python 包（package）中，相对导入（如 `from . import sibling_module`，`from ..parent_package import another_module`）是一种引用同一包内其他模块的方式。我们强烈推荐在包内优先使用相对导入，主要基于以下理由：
        *   **增强可重构性与可移植性**：当您的整个包被移动到项目的不同位置，或者包的顶层名称发生改变时，包内部基于相对导入的模块间引用通常无需任何修改，因为它们是相对于当前模块自身位置进行解析的。
        *   **避免命名空间冲突**：相对导入仅在包内查找模块，减少了与 Python 标准库模块或第三方库模块意外同名而引发冲突的风险。
        *   **明确依赖关系**：代码能清晰地表达出某个导入是针对包内模块的依赖，而不是一个全局的或绝对路径的依赖。
    *   **Python 如何处理相对导入？**
        Python 解释器在执行导入语句时，会检查模块的 `__package__` 属性。如果 `__package__` 被正确设置（即模块被识别为其所属包的一部分），相对导入就能基于这个包上下文进行解析。通常，当您通过 `import my_package.my_module` 或 `python -m my_package.my_module` 的方式加载模块时，`__package__` 属性会被正确设置。
    *   **直接运行脚本为何导致相对导入失败？**
        当您试图直接运行包内的一个 Python 文件（例如执行 `python my_package/my_module.py`）时，Python 会将该脚本的 `__name__` 属性设置为 `__main__`。在这种情况下，该脚本的 `__package__` 属性通常是 `None` 或者不是预期的包名。由于缺乏正确的包上下文，任何在该脚本中尝试进行的相对导入（如 `from . import sibling`）都会失败，并抛出类似 `ImportError: attempted relative import with no known parent package` 的错误。
    *   **`run-main` 如何解决此问题？**
        `run-main` 工具通过一种更智能的方式来执行您的目标模块。当您使用 `run-main path/to/your_module.py` 时：
        1.  它通常从您的项目根目录（或一个合适的上层目录）被调用。
        2.  它将文件路径（如 `path/to/your_module.py`）转换为 Python 的模块导入路径（如 `path.to.your_module`）。
        3.  它动态地将您的项目根目录（或其父目录，取决于您的 `PYTHONPATH` 设置和执行方式）添加到 `sys.path`（如果需要）。
        4.  最关键的是，它通过类似模块导入的方式来加载和执行您指定的模块代码（特别是 `_main()` 函数），这使得 Python 解释器能够正确识别目标模块所属的包，并设定其 `__package__` 属性。
        因此，在 `run-main` 的执行上下文中，目标模块内的相对导入就能像通过 `python -m` 执行时一样正确工作。这使得 `run-main` 成为在开发和调试过程中便捷运行包内模块并确保相对导入成功的理想选择，尤其是在配合 IDE（如 VSCode 中的 `${file}` 变量）时，它比为每个文件手动配置 `python -m` 命令更为方便。
2.  **调试器误导 (Debugger Misdirection)**：当模块的导入阶段发生错误（例如，顶层代码中的 `SyntaxError` 或 `NameError`），标准的导入机制（如 `importlib.import_module()`）可能会将原始异常包装在 `ImportError` 中。这可能导致调试器停在导入调用处，而不是目标模块中实际导致错误的代码行。
3.  **IDE 配置开销 (IDE Configuration Overhead)**：虽然像 VS Code 这样的 IDE 提供了 "Python: Module" 调试配置（使用 `python -m`），但它们通常需要硬编码模块路径（例如 `"module": "my_package.my_module"`）。这意味着需要为每个希望以此方式调试的文件创建或更新配置，这很不方便。

`run_main.py` 旨在解决这些问题。

## 核心优势

*   **轻松执行模块**：将任何定义了 `_main()` 函数的 `.py` 文件当作主程序一样运行。
*   **正确的相对导入处理**：通过建立适当的包上下文，确保相对导入（例如 `from . import sibling`，`from ..package import another`）按预期工作。
*   **“快速失败”的调试体验**：
    *   目标模块导入阶段发生的错误会被直接报告，允许调试器精确定位到目标模块源代码中的确切失败行。
    *   目标模块 `_main()` 函数内部发生的错误也会直接传播，以便精确调试。
*   **简化的 IDE 调试**：借助 `${relativeFile}` 这样的变量，使用单个、可重用的 VS Code `launch.json` 配置（或其他 IDE 的类似配置）来调试当前活动的 Python 文件。
*   **参数传递**：支持向目标模块的 `_main()` 函数传递命令行参数。

## 工作原理

1.  **输入 (Input)**：`run-main` 命令（或作为模块使用 `python -m run_main` 时）接收一个目标 Python 模块的文件路径（例如 `examples/A/my_module.py`）作为命令行参数。
2.  **路径到模块的转换 (Path to Module Conversion)**：它将此文件路径转换为标准的 Python 模块导入路径（例如 `examples.A.my_module`）。
3.  **环境设置与动态导入 (Environment Setup & Dynamic Import)**：
    *   脚本会确保当前工作目录在 `sys.path` 中，以帮助解析目标模块，特别是当 `run-main` 作为已安装命令被调用时。
    *   然后它使用 `exec(f"from {module_path} import _main", globals())` 从目标模块动态导入 `_main` 函数到其自身的全局作用域。
4.  **参数传递与执行 (Argument Passing & Execution)**：随后，它调用导入的 `_main()` 函数，并将命令行中跟随目标模块路径的任何参数传递给它。

在导入和调用周围刻意不使用过多的 try-except 块来包裹 `exec()`，是实现“快速失败”调试理念的关键，它允许原始异常干净地传播。

## 使用方法

### 对目标模块的要求

您打算通过 `run-main` 运行的 Python 模块 **必须**：
1.  定义一个名为 `_main()` 的函数。
2.  如果 `_main()` 函数期望接收命令行参数，它应该被定义为能够接受这些参数（例如 `def _main(*args):`）。传递给 `_main()` 的 `*args` 元组将包含在 `run-main` 命令行中跟随模块路径的参数。
    （注意：如果目标模块内的代码在全局范围检查 `sys.argv`，`sys.argv[0]` 将是目标模块的路径，而 `sys.argv[1:]` 将是用户提供的参数，这模拟了直接脚本执行的行为。）

### 命令行

```bash
run-main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```
或者，如果您希望直接通过 Python 解释器调用（对于已安装的工具来说不太常见，但可行）：
```bash
python -m run_main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```

### VS Code `launch.json` 配置

在您项目的 `.vscode/launch.json` 文件中添加或更新以下配置。这是使用 `run-main` 调试文件的推荐方法。

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: 使用 run-main 调试", // 或其他描述性名称
            "type": "debugpy",
            "request": "launch",
            "module": "run_main", // 告诉 VS Code 运行 "python -m run_main"
            "args": [
                "${file}" // 将当前打开文件的路径传递给 run_main
                // 您可以在此处为您的 _main() 添加更多固定参数，例如：
                // "--config", "my_config.json",
                // "positional_arg"
            ],
            "console": "integratedTerminal",
            // 如果目标脚本依赖当前工作目录，请确保 'cwd' 设置正确。
            // 大多数情况下，workspaceFolder 是合适的。
            "cwd": "${workspaceFolder}"
        }
    ]
}
```
通过此配置，打开项目中任何定义了 `_main()` 函数的 Python 文件，确保它是当前活动的编辑器选项卡，然后按 F5（或您的调试启动键）即可运行和调试它。VS Code 会将此活动文件的路径作为第一个参数传递给 `run_main`。

## 示例 (`examples` 目录)

`examples/` 目录包含各种演示 `run-main` 功能的示例。当从项目根目录（`examples` 目录所在的位置）使用 `run-main` 时，它通常能正确处理这些示例的路径。

*   **`examples/A/file_a.py`**: 一个简单的辅助模块，被其他模块导入。没有 `_main()` 函数。
*   **`examples/A/error_in_main.py`**: 展示目标模块 `_main()` 函数*内部*的错误是如何被处理的（调试器停在 `error_in_main.py` 中的错误处）。
*   **`examples/A/error_while_import.py`**: 演示在目标模块导入阶段其*顶层代码*发生错误的情况（调试器停在 `error_while_import.py` 中的错误处）。
*   **`examples/A/indirect_import_error.py`**: 展示一个模块在导入过程中发生错误，而这个模块本身又试图导入另一个在导入时就失败的模块（调试器停在 `error_while_import.py` 中的原始错误源）。
*   **`examples/A/relative_import.py`**: 在同一包 (`examples.A`) 内成功进行相对导入 (`from .file_a import VAL_A`) 的示例。
*   **`examples/B/import_neighbor.py`**: 从兄弟包成功进行相对导入 (`from ..A.file_a import VAL_A`，从 `examples.A` 导入到 `examples.B`) 的示例。
*   **`examples/B/C/deep_relative_import.py`**: 成功进行多级相对导入 (`from ...A.file_a import VAL_A`，从 `examples.A` 导入到 `examples.B.C`) 的示例。
*   **`examples/main_with_args.py`**: 演示 `_main()` 如何接收和解析通过 `run-main` 传递的命令行参数（使用 `argparse`）。
    *   示例用法: `run-main examples/main_with_args.py 我的位置参数 --name 小明 --count 3 --verbose`

## 关于 VS Code 和 `${relativeFileAsModule}` 的说明

`run-main` 工具（前身为 `run_main.py` 脚本）有效地充当了一种变通方法，以实现一个如果能得到像 VS Code 这样的 IDE 原生支持将会非常有益的功能。目前，VS Code 的 "Python: Module" 调试配置（如果不使用像 `run-main` 这样的辅助工具）需要硬编码模块路径（例如 `"module": "my_package.my_module"`）。

如果 VS Code 将来能引入一个类似 `${relativeFileAsModule}` 的变量，该变量能够自动将当前打开文件的路径（例如 `${relativeFile}` 给出 `examples/my_package/my_module.py`）转换为 `python -m` 所需的点分隔模块字符串（例如 `examples.my_package.my_module`），这将极大地简化包内单个文件的调试过程。这样的功能将允许开发人员通过单个通用的启动配置直接使用健壮的 `python -m` 执行上下文，从而可能使得像 `run-main` 这样的辅助工具在这种特定用途下不再那么必要。

在此之前，`run-main` 提供了一个实用的解决方案。

## 贡献

欢迎 Fork 本仓库、进行改进并提交 Pull Request。如果您遇到任何问题或有建议，请提交 Issue。