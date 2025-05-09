# src/main_with_args.py
# Demonstrates how _main() can receive and process command-line arguments
# passed via run_main.py.
# (中文注解: 演示 _main 如何处理通过 run_main.py 传递的参数。)
import argparse
import sys # Import sys to use sys.argv for direct execution testing

def _main(*args_tuple):
    """
    _main receives only the user-supplied arguments forwarded by run_main.py
    (i.e., arguments that followed the target module's path on the command line).

    Note: `run_main.py` adjusts the global `sys.argv` list before importing
    this module. As a result, `sys.argv[0]` within this module will be the
    path to `main_with_args.py` itself, and subsequent elements will be the
    user arguments. This makes the behavior of `sys.argv` (and thus how
    `argparse` defaults to using it if no args are passed to `parse_args()`)
    consistent with direct execution (e.g., `python src/main_with_args.py arg1`).

    (中文注解: `_main` 函数仅接收由 `run_main.py` 转发的用户提供的参数
    (即命令行中跟在目标模块路径之后的参数)。

    注意: `run_main.py` 在导入此模块前会调整全局 `sys.argv` 列表。
    因此，在此模块内部 `sys.argv[0]` 将是 `main_with_args.py` 自身的路径，
    后续元素为用户参数。这使得 `sys.argv` 的行为 (以及因此 `argparse`
    在未传递参数给 `parse_args()` 时默认如何使用它) 与直接执行
    (例如 `python src/main_with_args.py arg1`) 时保持一致。)
    """
    print(f"Executing _main in: {__file__}")
    print(f"Raw arguments received by _main (as a tuple): {args_tuple}")

    # Convert the tuple of arguments to a list for argparse
    args_list = list(args_tuple)

    parser = argparse.ArgumentParser(
        description="Example for run_main.py: _main function argument processing.",
        prog=f"{__file__} (via run_main.py)" # Shows in help message
    )
    parser.add_argument(
        "positional_arg",
        nargs="?", # Makes the positional argument optional
        default="DefaultPositionalValue",
        help="An example positional argument."
    )
    parser.add_argument(
        "--name",
        default="Guest",
        help="A name to greet (e.g., --name Roo)."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of times to greet (e.g., --count 3)."
    )
    parser.add_argument(
        "--verbose",
        action="store_true", # Boolean flag
        help="Enable verbose output."
    )

    # If no arguments are passed (e.g. run_main.py src/main_with_args.py),
    # args_list will be empty, and parse_args([]) works fine, using defaults.
    parsed_args = parser.parse_args(args_list)

    if parsed_args.verbose:
        print(f"Parsed arguments: {parsed_args}")

    print(f"Positional argument value: {parsed_args.positional_arg}")
    for i in range(parsed_args.count):
        print(f"Hello, {parsed_args.name}! (Greeting {i+1} of {parsed_args.count})")

if __name__ == "__main__":
    # This block allows direct execution for testing, e.g.:
    # python src/main_with_args.py MyPositionalArg --name "Direct Run" --count 2 --verbose
    print(f"Running {__file__} directly.")
    # When run directly, sys.argv[0] is the script name.
    # We pass sys.argv[1:] to _main, similar to how run_main.py would pass its relevant slice.
    _main(*sys.argv[1:])