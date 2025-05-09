# tests/test_targets/main_no_args.py
# This file defines a _main() function that takes no arguments.
# It's used to test how run_main.py handles calling a _main
# function that is not designed to accept arguments, especially
# when run_main.py might pass arguments to it.

def _main():
    print("_main in main_no_args.py executed successfully.")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    _main()