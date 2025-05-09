# tests/test_targets/main_access_sys_argv.py
# This file's _main function will inspect sys.argv to verify
# how run_main.py sets it up for the target module.

import sys

def _main(*args_tuple):
    print(f"_main in main_access_sys_argv.py executed.")
    print(f"Received *args_tuple in _main: {args_tuple}")
    print(f"sys.argv inside module: {sys.argv}")
    
    # For run_main.py, we expect:
    # sys.argv[0] to be the path to this script (main_access_sys_argv.py)
    # sys.argv[1:] to be the arguments passed after the script path to run_main.py
    
    # This helps verify the claim in run_main.py's documentation:
    # "run_main.py adjusts the global sys.argv list before importing
    # this module. As a result, sys.argv[0] within this module will be the
    # path to [the target module] itself, and subsequent elements will be the
    # user arguments."

# If run directly (for testing the file itself):
if __name__ == "__main__":
    print(f"Running {__file__} directly.")
    print(f"Initial sys.argv: {sys.argv}")
    # When run directly, sys.argv[0] is the script name.
    # We pass sys.argv[1:] to _main.
    _main(*sys.argv[1:])