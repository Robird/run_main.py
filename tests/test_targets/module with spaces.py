# tests/test_targets/module with spaces.py
# This file has spaces in its name.
# It's used to test if run_main.py can correctly handle
# target module paths that contain spaces.

def _main(*args):
    print(f"_main in 'module with spaces.py' executed successfully.")
    if args:
        print(f"Received arguments: {args}")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    _main("test_arg_direct_run")