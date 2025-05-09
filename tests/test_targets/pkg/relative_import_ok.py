# tests/test_targets/pkg/relative_import_ok.py
# This module is inside the 'pkg' package and performs a successful relative import.
# It's used to test if run_main.py correctly sets up the package context
# to allow relative imports.

from . import sibling # Relative import from the same package

def _main(*args):
    print(f"_main in relative_import_ok.py executed successfully.")
    print(f"Value from sibling module: {sibling.SIBLING_VALUE}")
    print(f"Function call from sibling: {sibling.sibling_function()}")
    if args:
        print(f"Received arguments: {args}")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    # Note: Running this file directly (python relative_import_ok.py)
    # will likely cause an ImportError because the package context isn't set up.
    # This is exactly what run_main.py aims to solve.
    print(f"Attempting to run {__file__} directly (this might fail relative imports).")
    try:
        _main("direct_arg")
    except ImportError as e:
        print(f"Direct run caught expected ImportError: {e}")
        print("This demonstrates why run_main.py is useful for such files.")