# tests/test_targets/no_main_func.py
# This file defines a function, but not _main.
# It's used to test how run_main.py handles modules
# that are missing the required _main function.

def some_other_function():
    print("some_other_function in no_main_func.py was called.")

# No _main() function defined here.