# tests/test_targets/main_fixed_args.py
# This file defines a _main() function that takes a fixed number of arguments.
# It's used to test how run_main.py handles calling a _main
# function with a specific signature, ensuring arguments are passed correctly
# or that errors are raised if the argument count mismatches.

def _main(arg1, arg2):
    print(f"_main in main_fixed_args.py executed successfully with arg1='{arg1}', arg2='{arg2}'.")

# If run directly (for testing the file itself):
if __name__ == "__main__":
    # Example direct call
    try:
        _main("test1", "test2")
        # _main("test_only_one_arg") # This would cause a TypeError
    except TypeError as e:
        print(f"Direct run caught expected TypeError: {e}")