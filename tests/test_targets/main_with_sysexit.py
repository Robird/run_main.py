# tests/test_targets/main_with_sysexit.py
# This file defines a _main() function that calls sys.exit() with a specific code.
# It's used to test if run_main.py correctly propagates the exit code
# from the target module's _main function.

import sys

def _main(*args):
    exit_code = 0
    if args:
        try:
            exit_code = int(args[0])
            print(f"_main in main_with_sysexit.py called. Will exit with code: {exit_code}")
        except ValueError:
            print(f"Error: Argument '{args[0]}' is not a valid integer for exit code. Exiting with 1.", file=sys.stderr)
            exit_code = 1 # Default error exit code if argument is bad
    else:
        print("_main in main_with_sysexit.py called. No exit code arg, will exit with 0.")
    
    sys.exit(exit_code)

# If run directly (for testing the file itself):
if __name__ == "__main__":
    # Example: python main_with_sysexit.py 5
    # The script would then exit with code 5.
    if len(sys.argv) > 1:
        _main(sys.argv[1])
    else:
        _main() # Exits with 0