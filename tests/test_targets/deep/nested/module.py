# tests/test_targets/deep/nested/module.py
# This file is deeply nested within subdirectories.
# It's used to test if run_main.py can correctly form the
# module import string (e.g., tests.test_targets.deep.nested.module)
# and execute such modules.

def _main(*args):
    print(f"_main in tests/test_targets/deep/nested/module.py executed successfully.")
    print(f"Module name is: {__name__}")
    if args:
        print(f"Received arguments: {args}")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    # This direct run won't have the package context set up correctly
    # by default, so relative imports from here might fail if added.
    # run_main.py is designed to solve this.
    print("Running tests/test_targets/deep/nested/module.py directly.")
    _main("direct_arg1", "direct_arg2")