# `run-main` 用法场景详解

本文档详细说明了 `run-main` 工具在不同场景下的使用方法和预期行为。

## 1. 作为命令行工具使用 `run-main`

`run-main` 最常见的用法是直接在命令行中调用。

### 基本调用

```bash
run-main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```

*   `path/to/your_module.py`: 指向包含 `_main()` 函数的目标 Python 文件。
*   `[arg1_for_main ...]`：可选参数，这些参数会按原样传递给目标模块的 `_main()` 函数。

### 路径输入的行为

`run-main` 对作为第一个参数传入的目标模块路径有特定的处理逻辑：

*   **相对路径 (Relative Paths)**
    *   **示例**: `run-main examples/A/relative_import.py`
    *   **行为**: 如果您从项目根目录（例如，包含 `examples` 文件夹的目录）运行此命令，`run-main` 会将相对路径 `examples/A/relative_import.py` 转换为模块路径 `examples.A.relative_import`。它通过获取当前工作目录 (`os.getcwd()`) 作为基础，并将该目录添加到 `sys.path` 中，然后将文件路径转换为点分隔的模块字符串。
    *   **前提**: `run-main` 执行时的当前工作目录必须是 Python 能够从中找到该相对路径所指向模块的顶级目录（通常是项目根目录）。

*   **绝对路径 (Absolute Paths)**
    *   **示例 (Linux/macOS)**: `run-main /home/user/my_project/examples/A/relative_import.py`
    *   **示例 (Windows)**: `run-main C:\Users\user\my_project\examples\A\relative_import.py`
    *   **行为**: 当提供绝对路径时，`run-main` 首先会获取其执行时的当前工作目录 (`project_root = os.getcwd()`)。然后，它计算所提供绝对路径相对于这个 `project_root` 的相对路径。如果目标文件确实位于 `project_root` 之下，那么这个计算出的相对路径会被用来构造模块导入字符串（例如，如果 `project_root` 是 `/home/user/my_project`，则上述 Linux 示例会得到 `examples.A.relative_import`）。
    *   **关键点**: 即使输入是绝对路径，最终的模块导入路径也是相对于 `run-main` **执行时的工作目录**的。

*   **工作目录外的路径 (Paths Outside the Working Directory)**
    *   **示例**: 假设 `run-main` 在 `/home/user/my_project/` 中执行，但您尝试运行 `/opt/other_project/module.py`。
    *   **行为**: `run-main` 会检测到目标路径 (`/opt/other_project/module.py`) 解析后位于其当前工作目录 (`/home/user/my_project/`) 之外。在这种情况下，`run-main` 会打印一条错误消息并退出。
    *   **原因**: `run-main` 的设计目的是模拟在特定项目上下文中执行模块（类似于 `python -m package.module`）。它依赖于当前工作目录作为项目根目录来正确解析模块和处理相对导入。允许执行项目外部的任意文件会偏离此设计目标，并可能导致不可预测的导入行为。

## 2. 作为 Python 模块使用 `run-main`

您也可以通过 `python -m run_main` 来调用它，这在某些自动化脚本或特定环境中可能有用。

```bash
python -m run_main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```

*   **行为**: 这种调用方式与直接作为命令行工具 (`run-main ...`) 的行为在路径解析和参数传递方面是基本一致的。Python 解释器会首先找到 `run_main` 模块，然后执行它，此时 `run_main` 内部的 `os.getcwd()` 仍然是命令执行时的当前工作目录。

## 3. 在 IDE 中配置 (以 VS Code 为例)

在 IDE 中配置 `run-main` 可以极大地提升调试单个模块的体验。

### VS Code `launch.json` 配置

以下是推荐的 `.vscode/launch.json` 配置：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug with run-main",
            "type": "debugpy",
            "request": "launch",
            "module": "run_main", // 告诉 VS Code 运行 "python -m run_main"
            "args": [
                "${file}", // 或 "${relativeFile}" - 将当前打开文件的路径传递给 run_main
                // 在此处为您的 _main() 函数添加其他固定参数，例如：
                // "my_custom_arg",
                // "--option", "value"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}" // 非常重要！
        }
    ]
}
```

### 配置详解:

*   `"module": "run_main"`: 指示 VS Code 使用 `python -m run_main` 来启动调试会话。
*   `"args": ["${file}", ... ]`:
    *   `${file}`: 这是一个 VS Code 变量，会被替换为当前活动编辑器中打开文件的**绝对路径**。
    *   `${relativeFile}`: 另一个 VS Code 变量，会被替换为当前活动编辑器中打开文件相对于 `${workspaceFolder}` 的**相对路径**。
    *   两者都可以工作。当 `${file}` (绝对路径) 被传递给 `run-main` 时，`run-main` 会根据下面的 `cwd` 设置来计算其相对于项目根的模块路径。
*   `"cwd": "${workspaceFolder}"`:
    *   **至关重要**: 这个设置定义了 `run-main` 执行时的当前工作目录 (Current Working Directory)。VS Code 会将 `${workspaceFolder}` 解析为当前打开的工作区的根目录。
    *   `run-main` 使用这个 `cwd` 作为其“项目根目录”的基准，来解析传递给它的文件路径（无论是绝对的 `${file}` 还是相对的 `${relativeFile}`），并将其转换为模块导入路径。它也会将这个 `cwd` 添加到 `sys.path` 中。
    *   **如果 `cwd` 设置不当**（例如，指向了某个子目录），`run-main` 可能无法正确地将文件路径转换为预期的模块路径，导致 `ImportError`。

### 其他 IDE

对于其他 IDE（如 PyCharm, Spyder 等），配置思路是类似的：
1.  找到一种方式来运行一个 Python 模块 (`run_main`)。
2.  配置传递给该模块的参数，使其包含当前正在编辑或选定的文件的路径。
3.  确保执行时的当前工作目录 (CWD) 设置为项目的根目录。

---

理解 `run-main` 如何处理路径以及 `cwd` 的重要性，是确保其按预期工作的关键。