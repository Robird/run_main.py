# tests/test_targets/simple_main.py
# A simple module for basic execution tests.

def _main(*args):
    print("simple_main.py _main executed successfully")
    if args:
        print(f"Received arguments: {args}")

if __name__ == "__main__":
    _main("test_arg1", "test_arg2")