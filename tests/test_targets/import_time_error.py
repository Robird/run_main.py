# tests/test_targets/import_time_error.py
# This file is designed to raise an error when it's imported.
# This helps test run_main.py's "fast-fail" behavior, ensuring that
# import-time errors from the target module are propagated directly.

# Example of an error that occurs at the top level of the module
# (i.e., during the import process).
error_variable = 1 / 0

def _main():
    # This function will not be reached if the import-time error occurs.
    print("_main in import_time_error.py was called (this should not happen).")