# tests/test_targets/relative_import_fail.py
# This module is NOT part of a package (no __init__.py in its direct parent,
# or it's at the top level of test_targets).
# It attempts a relative import, which should fail.
# This tests that run_main.py doesn't magically make invalid relative imports work.

from . import some_non_existent_sibling # Attempting a relative import that should fail

def _main(*args):
    print(f"_main in relative_import_fail.py executed.")
    # This part should not be reached if the import error is fatal.
    print("This line should ideally not be printed if the relative import fails as expected.")

if __name__ == "__main__":
    print(f"Running {__file__} directly.")
    # This will almost certainly raise an ImportError.
    _main()