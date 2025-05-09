# src/A/error_in_main.py
# Demonstrates a scenario where an unhandled error occurs within the _main() function.
# run_main.py is designed for "fast-fail" debugging; it does not catch exceptions
# thrown from the target module's _main() function.
# Therefore, when running this file with run_main.py via a debugger,
# the debugger should halt directly at the line causing the ZeroDivisionError below.
# (中文注解: 演示 _main() 函数内部错误。调试器应停在错误行。)

def _main():
    print(f"Executing _main in: {__file__}")
    print("Attempting a risky operation that will cause an error...")
    result = 1 / 0  # This will raise a ZeroDivisionError
    # The following line will not be executed due to the error above.
    print(f"Result of risky operation: {result}") 

if __name__ == "__main__":
    # This block executes if the script is run directly, e.g., python src/A/error_in_main.py
    # The error will also occur here and be reported by the Python interpreter.
    print(f"Running {__file__} directly.")
    _main()