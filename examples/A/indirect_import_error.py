# src/A/indirect_import_error.py
# (Previously fast_fail_import.py)
# Demonstrates how run_main.py handles errors that occur when importing a module
# (this module) which itself attempts to import another module (error_while_import.py)
# that fails during its own import process.
# This tests the "fast-fail" characteristic for indirect import errors.
# (中文注解: 演示间接导入错误。错误源头应被准确定位到 error_while_import.py。)

print(f"Loading module: {__file__}")
print(f"Attempting to import from .error_while_import (which is expected to fail during its import)...")

# The following import statement will trigger the loading of error_while_import.py.
# error_while_import.py contains top-level code that raises a ZeroDivisionError.
# run_main.py's use of exec() should allow this original error to propagate,
# and a debugger should halt at the error's origin in error_while_import.py,
# not here or in run_main.py.
from .error_while_import import DIV_BY_ZERO_AT_IMPORT

print(f"This line in {__file__} will NOT be reached if the import above fails.")

def _main():
    # This function will not be called if the import fails.
    print(f"Executing _main in: {__file__} (This should not be printed).")
    print(f"Value imported from error_while_import (if successful): {DIV_BY_ZERO_AT_IMPORT}")

if __name__ == "__main__":
    # This block executes if the script is run directly.
    # The import error from error_while_import.py will also occur here.
    print(f"Running {__file__} directly (expecting indirect import-time error).")
    _main()