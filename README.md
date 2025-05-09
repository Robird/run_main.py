# run-main: A General-Purpose Python Module Runner for Enhanced Debugging

**In Python projects, it is highly recommended to prioritize relative imports (e.g., `from . import sibling_module` or `from ..package import other_module`) for organizing dependencies between modules. This practice significantly enhances code maintainability and project portability.**

The `run-main` utility (now installable as the `run-main` package) is designed precisely to help you conveniently follow this best practice. It simplifies the execution and debugging of individual Python modules (`.py` files) within a larger project structure, especially those intended to be run as a main entry point by defining a `_main()` function. `run-main` not only mimics the behavior of `python -m <package.module>` for single files but, **more crucially, it ensures that relative imports are correctly resolved at runtime, thus avoiding the common `ImportError` encountered when directly running sub-modules.** It also provides a "fast-fail" debugging experience.

## Quick Start

1.  **Define `_main()` in your target module**:
    Your Python file (`your_module.py`) should define a function named `_main()`:
    ```python
    # In your_module.py
    def _main(*args):
        print(f"Hello from _main in {__file__}!")
        if args:
            print(f"Received arguments: {args}")

    # Optional: To also allow direct execution via `python your_module.py`
    # if __name__ == "__main__":
    #     import sys
    #     _main(*sys.argv[1:])
    ```
**Why `_main()`?** When a Python file is run directly, its `__name__` becomes `__main__`. This standard approach can cause `ImportError` with relative imports (e.g., `from . import utils`) because the package context is missing. `run-main` executes your file as part of a package and calls `_main()`, ensuring relative imports work. Think of `_main()` as the `run-main`-aware entry point.

        **Migrating from `if __name__ == "__main__"`:** Simply move the logic from your `if __name__ == "__main__":` block into the `def _main(*args):` function. `run-main` passes command-line arguments to `_main` via `*args`. You can keep the `if __name__ == "__main__": _main(*sys.argv[1:])` block for optional direct execution, but `run-main` is recommended for package-aware execution.

2.  **Install `run-main`**:
    ```bash
    pip install run-main
    ```

3.  **Run from Command Line**:
    Execute your module using the `run-main` command:
    ```bash
    run-main path/to/your_module.py arg1 arg2
    ```

4.  **Debug in VS Code (Recommended `launch.json`)**:
    Create or update `.vscode/launch.json` in your project:
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Debug with run-main",
                "type": "debugpy",
                "request": "launch",
                "module": "run_main", // Use the installed run_main module
                "args": [
                    "${file}", // Path to the currently open .py file to be run
                    // Add other arguments for your _main() function here, e.g.:
                    // "my_arg1",
                    // "--my-option", "value"
                ],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}" // Or the root of the project containing the file
            }
        ]
    }
    ```
    Open the Python file containing `_main()` and press F5 to debug.

## The Problem It Solves

Developing and debugging Python projects, especially those organized into packages, can present a few common hurdles when trying to run or debug a single file:

1.  **Relative Import Errors and the `run-main` Solution**:
    *   **What are Relative Imports? Why Are They Recommended?**
        In Python packages, relative imports (e.g., `from . import sibling_module`, `from ..parent_package import another_module`) are a way to refer to other modules within the same package. It is strongly recommended to prioritize relative imports within your packages for several key reasons:
        *   **Enhanced Refactorability and Portability**: When your entire package is moved to a different location within a project, or if the top-level name of the package changes, internal references based on relative imports typically require no modification because they are resolved relative to the current module's own location.
        *   **Avoidance of Namespace Conflicts**: Relative imports only look for modules within the package, reducing the risk of accidental name clashes with Python standard library modules or third-party library modules.
        *   **Clear Dependency Indication**: The code clearly expresses that an import is a dependency on an intra-package module, rather than a global or absolute path dependency.
    *   **How Does Python Handle Relative Imports?**
        When the Python interpreter executes an import statement, it checks the module's `__package__` attribute. If `__package__` is correctly set (i.e., the module is recognized as part of its containing package), relative imports can be resolved based on this package context. Typically, when you load a module via `import my_package.my_module` or `python -m my_package.my_module`, the `__package__` attribute is set correctly.
    *   **Why Does Directly Running a Script Cause Relative Imports to Fail?**
        When you attempt to run a Python file directly from within a package (e.g., by executing `python my_package/my_module.py`), Python sets that script's `__name__` attribute to `__main__`. In this scenario, the script's `__package__` attribute is usually `None` or not the expected package name. Lacking the correct package context, any relative imports attempted within that script (like `from . import sibling`) will fail, typically raising an `ImportError: attempted relative import with no known parent package`.
    *   **How Does `run-main` Solve This?**
        The `run-main` tool executes your target module in a more intelligent way. When you use `run-main path/to/your_module.py`:
        1.  It is usually invoked from your project root (or a suitable parent directory).
        2.  It converts the file path (e.g., `path/to/your_module.py`) into a Python module import path (e.g., `path.to.your_module`).
        3.  It dynamically adds your project root (or its parent, depending on `PYTHONPATH` settings and invocation) to `sys.path` if necessary.
        4.  Most importantly, it loads and executes your specified module's code (specifically the `_main()` function) in a manner similar to a module import. This allows the Python interpreter to correctly identify the package to which the target module belongs and set its `__package__` attribute appropriately.
        Consequently, within the execution context provided by `run-main`, relative imports inside your target module work correctly, just as they would if executed via `python -m`. This makes `run-main` an ideal choice for conveniently running modules within packages during development and debugging while ensuring relative imports succeed, especially when used with IDEs (like with the `${file}` variable in VSCode), where it's more convenient than manually configuring `python -m` commands for each file.
2.  **Debugger Misdirection**: When an error occurs during the import phase of a module (e.g., a `SyntaxError` or a `NameError` in top-level code), standard import mechanisms like `importlib.import_module()` might wrap the original exception in an `ImportError`. This can cause debuggers to stop at the import call site instead of the actual line of code causing the error in the target module.
3.  **IDE Configuration Overhead**: While IDEs like VS Code offer "Python: Module" debug configurations (using `python -m`), they typically require hardcoding the module path (e.g., `my_package.my_module`). This means creating or updating a configuration for each file you want to debug in this manner, which is inconvenient.

`run_main.py` addresses these issues.

## Core Advantages

*   **Effortless Module Execution**: Run any `.py` file defining a `_main()` function as if it were the main program.
*   **Correct Relative Import Handling**: Ensures that relative imports (e.g., `from . import sibling`, `from ..package import another`) work as expected by establishing the proper package context.
*   **"Fast-Fail" Debugging Experience**:
    *   Errors occurring during the import phase of the target module are reported directly, allowing debuggers to pinpoint the exact line of failure in the target module's source.
    *   Errors occurring within the target module's `_main()` function also propagate directly for precise debugging.
*   **Simplified IDE Debugging**: Use a single, reusable VS Code `launch.json` configuration (or similar for other IDEs) to debug the currently active Python file, thanks to variables like `${relativeFile}`.
*   **Argument Passing**: Supports passing command-line arguments to the target module's `_main()` function.

## How It Works

1.  **Input**: The `run-main` command (or when used as a module `python -m run_main`) takes the file path to a target Python module (e.g., `examples/A/my_module.py`) as a command-line argument.
2.  **Path to Module Conversion**: It transforms this file path into a standard Python module import path (e.g., `examples.A.my_module`).
3.  **Environment Setup & Dynamic Import**:
    *   The script ensures the current working directory is in `sys.path` to aid in resolving the target module, especially when `run-main` is invoked as an installed command.
    *   It then uses `exec(f"from {module_path} import _main", globals())` to dynamically import the `_main` function from the target module into its own global scope.
4.  **Argument Passing & Execution**: It calls the imported `_main()` function, passing any arguments that followed the target module's path on the command line.

The deliberate use of `exec()` without extensive try-except blocks around the import and call is key to the "fast-fail" debugging philosophy, allowing original exceptions to propagate cleanly.

## Usage

### Target Module Requirements

The Python module you intend to run via `run-main` **must**:
1.  Define a function named `_main()`.
2.  If `_main()` is expected to receive command-line arguments, it should be defined to accept them (e.g., `def _main(*args):`). The `*args` tuple passed to `_main()` will contain the arguments that followed the module path on the `run-main` command line.
    (Note: If the code within the target module inspects `sys.argv` globally, `sys.argv[0]` will be the target module's path, and `sys.argv[1:]` will be the user-supplied arguments, mimicking direct script execution.)

### Command-Line

```bash
run-main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```
Or, if you prefer to invoke it via the Python interpreter directly (less common for an installed tool but possible):
```bash
python -m run_main path/to/your_module.py [arg1_for_main arg2_for_main ...]
```

### VS Code `launch.json` Configuration

Add or update the following configuration in your project's `.vscode/launch.json` file. This is the recommended way to debug files using `run-main`.

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug with run-main", // Or any descriptive name
            "type": "debugpy",
            "request": "launch",
            "module": "run_main", // Tells VS Code to run "python -m run_main"
            "args": [
                "${file}", // Passes the path of the currently open file to run_main
                // You can add more fixed arguments here to be passed to your _main(), e.g.:
                // "--config", "my_config.json",
                // "positional_arg"
            ],
            "console": "integratedTerminal",
            // Ensure 'cwd' is set correctly if your target script relies on it.
            // For most cases, workspaceFolder is appropriate.
            "cwd": "${workspaceFolder}"
        }
    ]
}
```
With this configuration, open any Python file in your project that defines a `_main()` function, ensure it's the active editor tab, and press F5 (or your debug start key) to run and debug it. VS Code will pass the path of this active file as the first argument to `run_main`.

## Examples (`examples` directory)

The `examples/` directory contains various examples demonstrating the capabilities of `run-main`. When using `run-main` from the project root (where the `examples` directory resides), it generally handles the paths correctly for these examples.

*   **`examples/A/file_a.py`**: A simple helper module, imported by others. Does not have `_main()`.
*   **`examples/A/error_in_main.py`**: Shows how an error *inside* the `_main()` function of the target module is handled (debugger stops at the error in `error_in_main.py`).
*   **`examples/A/error_while_import.py`**: Demonstrates an error occurring at the *top-level* of the target module during its import phase (debugger stops at the error in `error_while_import.py`).
*   **`examples/A/indirect_import_error.py`**: Shows an error during the import of a module that *itself* tries to import another module which fails at import time (debugger stops at the original error source in `error_while_import.py`).
*   **`examples/A/relative_import.py`**: Example of a successful relative import (`from .file_a import VAL_A`) within the same package (`examples.A`).
*   **`examples/B/import_neighbor.py`**: Example of a successful relative import from a sibling package (`from ..A.file_a import VAL_A`, importing from `examples.A` into `examples.B`).
*   **`examples/B/C/deep_relative_import.py`**: Example of a successful multi-level relative import (`from ...A.file_a import VAL_A`, importing from `examples.A` into `examples.B.C`).
*   **`examples/main_with_args.py`**: Demonstrates how `_main()` can receive and parse command-line arguments passed via `run-main` using `argparse`.
    *   Example usage: `run-main examples/main_with_args.py MyPosArg --name Roo --count 3 --verbose`

## A Note on VS Code and `${relativeFileAsModule}`

The `run-main` tool (formerly `run_main.py` script) effectively serves as a workaround for a feature that would be highly beneficial if natively supported by IDEs like VS Code. Currently, VS Code's "Python: Module" debug configuration (when not using a helper like `run-main`) requires a hardcoded module path (e.g., `"module": "my_package.my_module"`).

If VS Code were to introduce a variable like `${relativeFileAsModule}` that could automatically convert the path of the currently open file (e.g., `${relativeFile}` which gives `examples/my_package/my_module.py`) into the dot-separated module string required by `python -m` (e.g., `examples.my_package.my_module`), it would streamline the debugging process immensely for individual files within packages. Such a feature would allow developers to use the robust `python -m` execution context directly via a single, generic launch configuration, potentially making helper tools like `run-main` less necessary for this specific purpose.

Until then, `run-main` provides a practical solution.

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests. If you encounter any issues or have suggestions, please open an issue.