# src/A/error_while_import.py
# Demonstrates a scenario where an error occurs in the top-level code of a module
# during its import (loading) phase. This happens before _main() is ever called.
# (中文注解: 演示模块加载时顶层代码发生错误。)

_DESCRIPTION = "This module intentionally raises an error in its top-level code during import."
print(f"Loading module: {__file__}. This print statement will execute.")

_ZERO = 0
# The line below executes when the Python interpreter loads this module.
# It will raise a ZeroDivisionError immediately.
# run_main.py uses exec() to import the _main function from this module.
# This approach allows such an original import-time error to propagate directly,
# rather than being wrapped in an ImportError (as might happen with importlib.import_module()).
# Consequently, a debugger should pinpoint the error at this exact line.
# (中文注解: 调试器应能准确定位到下面这行发生的原始导入时错误。)
DIV_BY_ZERO_AT_IMPORT = 1 / _ZERO

print(f"This line in {__file__} will NOT be reached due to the error above.")

def _main():
    # This function will not be called if the module fails to import.
    print(f"Executing _main in: {__file__} (This should not be printed if import fails).")
    print(f"Calculated value (if import succeeded): {DIV_BY_ZERO_AT_IMPORT}")

if __name__ == "__main__":
    # This block executes if the script is run directly, e.g., python src/A/error_while_import.py
    # The error will also occur here during module loading and be reported by the Python interpreter.
    print(f"Running {__file__} directly (expecting import-time error).")
    _main()
