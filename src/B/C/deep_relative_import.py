# src/B/C/deep_relative_import.py
# (Previously import_outside.py)
# Demonstrates a multi-level relative import ('...') from a deeper subpackage (src.B.C)
# to a module in another subpackage (src.A) under the top-level package (src).
# (中文注解: 演示从深层子包进行多级相对导入到顶层包下的其他子包。)

print(f"Loading module: {__file__}")
print("Attempting relative import from ...A.file_a...")
# '...' from src.B.C goes up two levels to the 'src' package.
# So, '...A.file_a' resolves to 'src.A.file_a'.
from ...A.file_a import VAL_A

VAL_C_SPECIFIC = "Value specific to deep_relative_import in package B.C"

def _main():
    print(f"Executing _main in: {__file__}")
    print(f"Successfully imported VAL_A from ...A.file_a (from package src.A via multi-level relative import).")
    print(f"Value of VAL_A: '{VAL_A}'")
    print(f"Value of VAL_C_SPECIFIC (defined in this module): '{VAL_C_SPECIFIC}'")

if __name__ == "__main__":
    # If this script is run directly (e.g., python src/B/C/deep_relative_import.py),
    # it will likely raise an ImportError due to the relative import '...A'.
    # Running via run_main.py establishes the correct package context.
    print(f"Running {__file__} directly.")
    _main()