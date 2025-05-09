# tests/test_targets/runtime_error_in_main.py
# This file defines a _main() function that intentionally raises an error
# during its execution.
# This helps test run_main.py's behavior in propagating runtime errors
# from the _main() function of the target module.

def _main(*args):
    print(f"_main in runtime_error_in_main.py called with args: {args}")
    # Intentionally raise an error
    raise ValueError("This is a deliberate runtime error from _main.")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    try:
        _main("test_arg1", "test_arg2")
    except ValueError as e:
        print(f"Direct run caught expected ValueError: {e}")