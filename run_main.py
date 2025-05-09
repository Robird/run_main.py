"""
run_main.py - A General-Purpose Python Module Runner for Enhanced Debugging (一个用于增强调试的通用 Python 模块运行器)

Purpose (目的):
This script enables any Python file that defines an `_main()` function to be
executed as if it were the main entry point of a program. It is designed to
mimic the behavior of `python -m <module>` for individual files, ensuring that
relative imports (相对导入) within the target module function correctly. Its primary use case
is to facilitate convenient debugging of individual modules within larger projects,
especially when used with IDE debuggers like VSCode (via launch.json).

Core Mechanism (核心机制):
1.  Accepts the path to a target Python module (`.py` file) as a command-line
    argument.
2.  Transforms this file path into a standard Python module import path (e.g.,
    `path/to/file.py` becomes `path.to.file`).
3.  Dynamically imports the `_main` function from this target module into the
    global scope using `exec("from <module_path> import _main")`.
4.  Calls the imported `_main()` function, passing any subsequent command-line
    arguments received by `run_main.py` to it.

Design Philosophy - Prioritizing "Fast Fail" for Direct Debugging (设计哲学 - 优先“快速失败”以实现直接调试):
This script intentionally minimizes its own exception handling around the core
`exec()` and `_main()` calls. The goal is to allow Python's default error
reporting and the IDE's debugger to intervene as directly as possible when an
error occurs. This means:
  - Exceptions originating from the target module (either during its import/loading
    phase or during the execution of its `_main()` function) will propagate.
  - The debugger should then halt at or very near the original site of the error,
    providing the most direct debugging experience.
Custom error messages from `run_main.py` itself are limited to pre-flight checks
(e.g., argument parsing, file type validation).

Why This Approach? (Rationale for design choices) (为何采用此方法？设计选择的基本原理):

  - Why use `exec()` instead of `importlib.import_module()`? (为何使用 `exec()` 而非 `importlib.import_module()`?)
    While `importlib.import_module()` is the standard and safer way for programmatic
    imports, it has a drawback for this script's specific debugging goal. If the
    target module encounters an internal runtime error during its loading phase
    (e.g., a `ZeroDivisionError` in its top-level code), `importlib.import_module()`
    wraps this original error within an `ImportError`. This causes the debugger to
    stop at the `importlib.import_module()` call site in `run_main.py`, rather
    than directly at the original error line within the target module.
    Using `exec()` in this controlled context allows the original exception (like
    `ZeroDivisionError`) to propagate directly, enabling the debugger to pinpoint
    the exact failure location within the target module, which is crucial for a
    "fast fail" (快速失败) debugging experience.

  - Why not just use `if __name__ == '__main__':` in every file? (为何不直接在每个文件中使用 `if __name__ == '__main__':`?)
    Directly running a Python file located within a package structure (e.g.,
    `python my_package/my_module.py`) sets that file's `__name__` to `__main__`
    but often fails to correctly establish its `__package__` context. This leads
    to `ImportError` (typically "attempted relative import with no known parent
    package") when the file tries to use relative imports (e.g., `from . import
    sibling`). This `run_main.py` script, by being run from a higher level (usually
    the project root) and dynamically importing the target as a module, ensures
    the correct package context is established, thus resolving relative import issues.

  - Why not just use VSCode's "Python: Module" debug configuration (which uses `python -m`)? (为何不直接使用 VSCode 的 "Python: Module" 调试配置 (它使用 `python -m`)?)
    The standard `python -m package.module` command is excellent for running modules
    and correctly handles relative imports. VSCode's "Python: Module" launch
    configuration allows you to specify a fixed module string (e.g., `"module":
    "my_package.my_module"`). However, VSCode currently lacks a built-in variable
    (like a hypothetical `${relativeFileAsModule}`) that can automatically convert
    the path of the *currently open file* (e.g., `${relativeFile}` which gives
    `src/my_package/my_module.py`) into the dot-separated module string required by
    `python -m` (e.g., `my_package.my_module`, assuming `src` is on PYTHONPATH).
    Without such a variable, one would need to manually create or update a launch
    configuration for each file they wish to debug using the `-m` style, which is
    inconvenient. This `run_main.py` script bridges that gap by taking
    `${relativeFile}` as input, programmatically performing the path-to-module
    conversion, and then using `exec()` to achieve a similar execution context,
    all through a single, reusable launch configuration.

Usage Conventions (使用约定):
- The Python module intended to be run via this script must define a function
  named `_main()`.
- If this `_main()` function is expected to receive command-line arguments, it
  should be defined to accept them (e.g., `def _main(*args):` or with a
  specific parameter signature matching the arguments passed after the module
  path to `run_main.py`).
- Developers should rely on Python's standard traceback output and their
  debugger's capabilities for diagnosing errors that originate from within the
  target module or its import process.

Example VSCode `launch.json` Configuration (VSCode `launch.json` 配置示例):
{
    "name": "Run current file's _main (via run_main.py)",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/run_main.py", // Adjust path if needed (如果需要，请调整路径)
    "args": [
        "${relativeFile}" // Passes the currently open file to run_main.py (将当前打开的文件传递给 run_main.py)
        // Add other fixed arguments for _main here if needed, e.g., "--debug-mode"
        // (如果需要，可在此处为 _main 添加其他固定参数，例如 "--debug-mode")
    ],
    "console": "integratedTerminal"
    // Optional: Set PYTHONPATH if your project structure requires it
    // (可选: 如果项目结构需要，请设置 PYTHONPATH)
    // "env": { "PYTHONPATH": "${workspaceFolder}/src" }
}
"""
def main():
    import sys
    import os
    # 1. Check for the minimum number of arguments (检查基本参数数量)
    if len(sys.argv) < 2: # At least the script name and target module path are required (至少需要脚本名和目标模块路径)
        script_name = sys.argv[0] # Get script name for usage message
        print(f"Usage: python {script_name} <path_to_your_module.py> [optional_args_for_module_main...]", file=sys.stderr)
        print(f"用法: python {script_name} <你的模块.py路径> [可选的模块_main函数参数...]", file=sys.stderr)
        sys.exit(1)

    # sys.argv[0] is the command/script name
    # sys.argv[1] is the file path of the target module (dst_fn)
    # sys.argv[2:] are the arguments to be passed to the target module's _main function
    target_file_arg = sys.argv[1]
    args_for_main = sys.argv[2:] # Arguments for the target _main

    # 2. Validate target file
    if not target_file_arg.endswith(".py"):
        print(f"Error: Target file '{target_file_arg}' does not appear to be a Python file (.py). Please provide a .py file.", file=sys.stderr)
        print(f"错误: 目标文件 '{target_file_arg}' 看起来不是一个 Python 文件 (.py)。请输入一个 .py 文件。", file=sys.stderr)
        sys.exit(1)

    project_root = os.path.normpath(os.getcwd())
    target_abs_path = os.path.normpath(os.path.abspath(target_file_arg))

    try:
        module_rel_path = os.path.relpath(target_abs_path, project_root)
    except ValueError: # Handles cases like different drives on Windows
        print(f"Error: Target file '{target_abs_path}' is outside the project directory '{project_root}'.", file=sys.stderr)
        print(f"错误: 目标文件 '{target_abs_path}' 不在项目目录 '{project_root}' 内。", file=sys.stderr)
        sys.exit(1)

    if module_rel_path.startswith(os.pardir) or os.path.isabs(module_rel_path):
        # os.path.isabs() check is a safeguard, relpath should not return abs path if start is provided
        print(f"Error: Target file '{target_abs_path}' is outside the project directory '{project_root}'.", file=sys.stderr)
        print(f"错误: 目标文件 '{target_abs_path}' 不在项目目录 '{project_root}' 内。", file=sys.stderr)
        sys.exit(1)
    
    # Ensure project_root (current working directory) is in sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    module_import_str = module_rel_path[:-3].replace(os.sep, ".")
    code = f"from {module_import_str} import _main"
    # No try-except around exec to allow direct debugging of import-time errors in the target module
    # (不使用 try-except 包裹 exec，以便直接调试目标模块中导入时发生的错误)
    exec(code,globals())  # noqa: F821
    # No try-except around _main call to allow direct debugging of runtime errors in _main
    # (不使用 try-except 包裹 _main 调用，以便直接调试 _main 中发生的运行时错误)
    # Call the target module's _main function with arguments
    # that appear after the target module's path.
    _main(*args_for_main)  # noqa: F821

if __name__ == "__main__":
    main()