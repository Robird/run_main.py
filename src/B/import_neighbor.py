# src/B/import_neighbor.py
# Demonstrates a relative import from a subpackage (src.B) to a module
# in a sibling subpackage (src.A) under the same parent package (src).
# (中文注解: 演示从兄弟包 (src.A) 进行相对导入。)

print(f"Loading module: {__file__}")
print("Attempting relative import from ..A.file_a...")
# '..' refers to the parent package (src), so '..A.file_a' resolves to 'src.A.file_a'.
from ..A.file_a import VAL_A

VAL_B_SPECIFIC = "Value specific to import_neighbor in package B"

def _main():
    print(f"Executing _main in: {__file__}")
    print(f"Successfully imported VAL_A from ..A.file_a (from sibling package src.A).")
    print(f"Value of VAL_A: '{VAL_A}'")
    print(f"Value of VAL_B_SPECIFIC (defined in this module): '{VAL_B_SPECIFIC}'")

if __name__ == "__main__":
    # If this script is run directly (e.g., python src/B/import_neighbor.py),
    # it will likely raise an ImportError due to the relative import '..A'.
    # Running via run_main.py establishes the correct package context.
    print(f"Running {__file__} directly.")
    _main()