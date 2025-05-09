# src/A/relative_import.py
# Demonstrates relative imports between modules within the same package (src.A).
# This is a core feature of run_main.py: ensuring relative imports work correctly,
# similar to execution with `python -m package.module`.
# When run with run_main.py, the package context is correctly established.
# (中文注解: 演示同包内的相对导入。)

print(f"Loading module: {__file__}")
print("Attempting relative import from .file_a...")
# '.' refers to the current package (src.A)
from .file_a import VAL_A 

def _main():
    print(f"Executing _main in: {__file__}")
    print(f"Successfully imported VAL_A from .file_a (within the same package src.A).")
    print(f"Value of VAL_A: '{VAL_A}'")

if __name__ == "__main__":
    # If this script is run directly (e.g., python src/A/relative_import.py),
    # it might raise an ImportError because Python may not correctly recognize
    # the package context for relative imports.
    # Running via run_main.py resolves this.
    print(f"Running {__file__} directly.")
    _main()