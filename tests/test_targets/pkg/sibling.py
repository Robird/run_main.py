# tests/test_targets/pkg/sibling.py
# This is a helper module within the 'pkg' package.
# It will be imported by relative_import_ok.py.

SIBLING_VALUE = "Value from sibling.py"

def sibling_function():
    return "sibling_function was called"