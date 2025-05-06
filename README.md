# run_main.py: A General-Purpose Python Module Runner for Enhanced Debugging

`run_main.py` is a utility script designed to simplify the execution and debugging of individual Python modules (`.py` files) within a larger project structure, especially those intended to be run as a main entry point by defining a `_main()` function. It mimics the behavior of `python -m <package.module>` for single files, ensuring correct handling of relative imports and providing a "fast-fail" debugging experience.

## The Problem It Solves

Developing and debugging Python projects, especially those organized into packages, can present a few common hurdles when trying to run or debug a single file:

1.  **Relative Import Errors**: Directly running a Python file from within a package (e.g., `python my_package/my_module.py`) often leads to `ImportError: attempted relative import with no known parent package`. This is because Python doesn't automatically establish the correct package context.
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

1.  **Input**: `run_main.py` takes the file path to a target Python module (e.g., `src/A/my_module.py`) as a command-line argument.
2.  **Path to Module Conversion**: It transforms this file path into a standard Python module import path (e.g., `src.A.my_module`).
3.  **Environment Setup & Dynamic Import**: `run_main.py` first modifies the `sys.argv` list by removing its own script name (`run_main.py`). This crucial step ensures that from the target module's perspective, `sys.argv[0]` is its own path, and subsequent elements are the user-provided arguments, mirroring the `sys.argv` behavior of a directly executed script. After this setup, it uses `exec(f"from {module_path} import _main", globals())` to dynamically import the `_main` function from the target module into its own global scope.
4.  **Argument Passing & Execution**: It then calls the imported `_main()` function, passing only the user-supplied arguments (i.e., those arguments that originally followed the target module's path on the command line) to this `_main()` function. The `_main` function therefore receives a clean list of its own arguments, while also being able to rely on a standard-looking `sys.argv` if it inspects it globally.

The deliberate use of `exec()` without extensive try-except blocks around the import and call is key to the "fast-fail" debugging philosophy, allowing original exceptions to propagate cleanly.

## Usage

### Target Module Requirements

The Python module you intend to run via `run_main.py` **must**:
1.  Define a function named `_main()`.
2.  If `_main()` is expected to receive command-line arguments, it should be defined to accept them (e.g., `def _main(*args):`). The `*args` tuple passed to `_main()` will contain *only* the user-supplied arguments that originally followed the module path on the `run_main.py` command line. The module path itself will not be part of `*args`.
    (Note: Independently, due to `run_main.py`'s setup, if the code within the target module inspects `sys.argv` globally, `sys.argv[0]` will correctly be the target module's own path, and `sys.argv[1:]` will be the user-supplied arguments, mimicking direct script execution.)

### Command-Line

```bash
python run_main.py path/to/your_module.py [arg1_for_main arg2_for_main ...]
```

### VS Code `launch.json` Configuration

Add the following configuration to your `.vscode/launch.json` file:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run current file's _main (via run_main.py)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/run_main.py", // Adjust if run_main.py is elsewhere
            "args": [
                "${relativeFile}" // Passes the path of the currently open file
                // You can add more fixed arguments here to be passed to _main(), for example:
                // "--default-config", "config.ini",
                // "some_positional_argument_for_main"
            ],
            "console": "integratedTerminal",
            // Optional: Set PYTHONPATH if your project structure requires it,
            // for example, if your source code is in a 'src' directory that's not
            // automatically on the path when run_main.py is at the workspace root.
            // "env": {
            //     "PYTHONPATH": "${workspaceFolder}" 
            //     // or "${workspaceFolder}/src" if your packages are inside src
            // }
        }
    ]
}
```
With this configuration, you can open any Python file in your project that defines a `_main()` function and simply press F5 (or your debug start key) to run and debug it.

## Examples (`src` directory)

The `src/` directory contains various examples demonstrating the capabilities of `run_main.py`. It's recommended to have `PYTHONPATH` set to include your project's root or `src` directory if your modules are within `src` for these examples to run correctly, especially if you try to run them directly without `run_main.py`. When using `run_main.py` from the project root, it generally handles the paths correctly.

*   **`src/A/file_a.py`**: A simple helper module, imported by others. Does not have `_main()`.
*   **`src/A/error_in_main.py`**: Shows how an error *inside* the `_main()` function of the target module is handled (debugger stops at the error in `error_in_main.py`).
*   **`src/A/error_while_import.py`**: Demonstrates an error occurring at the *top-level* of the target module during its import phase (debugger stops at the error in `error_while_import.py`).
*   **`src/A/indirect_import_error.py`**: Shows an error during the import of a module that *itself* tries to import another module which fails at import time (debugger stops at the original error source in `error_while_import.py`).
*   **`src/A/relative_import.py`**: Example of a successful relative import (`from .file_a import VAL_A`) within the same package (`src.A`).
*   **`src/B/import_neighbor.py`**: Example of a successful relative import from a sibling package (`from ..A.file_a import VAL_A`, importing from `src.A` into `src.B`).
*   **`src/B/C/deep_relative_import.py`**: Example of a successful multi-level relative import (`from ...A.file_a import VAL_A`, importing from `src.A` into `src.B.C`).
*   **`src/main_with_args.py`**: Demonstrates how `_main()` can receive and parse command-line arguments passed via `run_main.py` using `argparse`.
    *   Example usage: `python run_main.py src/main_with_args.py MyPosArg --name Roo --count 3 --verbose`

## A Note on VS Code and `${relativeFileAsModule}`

This `run_main.py` script effectively serves as a workaround for a feature that would be highly beneficial if natively supported by IDEs like VS Code. Currently, VS Code's "Python: Module" debug configuration requires a hardcoded module path (e.g., `"module": "my_package.my_module"`).

If VS Code were to introduce a variable like `${relativeFileAsModule}` that could automatically convert the path of the currently open file (e.g., `${relativeFile}` which gives `src/my_package/my_module.py`) into the dot-separated module string required by `python -m` (e.g., `my_package.my_module`, assuming `src` is on `PYTHONPATH` or is the workspace root), it would streamline the debugging process immensely for individual files within packages. Such a feature would allow developers to use the robust `python -m` execution context directly via a single, generic launch configuration, potentially making helper scripts like `run_main.py` less necessary for this specific purpose.

Until then, `run_main.py` provides a practical solution.

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests. If you encounter any issues or have suggestions, please open an issue.