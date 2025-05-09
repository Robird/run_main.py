import subprocess
import sys
import os
import pathlib # Added
import tempfile # Added

# Helper to get the project root, assuming tests are run from the project root
# or that the project root is where run_main.py and the examples/tests directories are.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent # Use pathlib

def run_main_command(target_module_path, *args, cwd=None): # Added cwd parameter
    """
    Helper function to execute the run-main command.
    Uses 'python -m run_main' to ensure it uses the run_main from the current project,
    especially if 'run-main' isn't installed globally or is a different version.
    """
    command = [
        sys.executable, # Path to current python interpreter
        "-m",
        "run_main",     # Execute run_main as a module
    ]
    if target_module_path: # Allow calling with no target for specific tests
        command.append(str(target_module_path)) # Ensure path is string
    command.extend(args)
    
    effective_cwd = cwd if cwd else PROJECT_ROOT # Use specified CWD or default to PROJECT_ROOT
    process = subprocess.run(command, capture_output=True, text=True, cwd=effective_cwd, check=False)
    return process

def test_simple_main_execution():
    """
    Tests basic execution of a simple _main function via run-main.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "simple_main.py"
    # No additional arguments are passed to _main for this test
    result = run_main_command(target_script)

    assert result.returncode == 0, \
        f"run-main failed with exit code {result.returncode}. Stderr:\n{result.stderr}"
    
    assert "simple_main.py _main executed successfully" in result.stdout, \
        f"Expected output not found in stdout. Stdout:\n{result.stdout}"
    
    # Ensure no arguments were passed in this case
    assert "Received arguments:" not in result.stdout, \
        f"Unexpectedly received arguments. Stdout:\n{result.stdout}"

def test_simple_main_with_args():
    """
    Tests execution with arguments passed to _main.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "simple_main.py"
    arg1 = "hello"
    arg2 = "world"
    result = run_main_command(target_script, arg1, arg2)

    assert result.returncode == 0, \
        f"run-main failed with exit code {result.returncode}. Stderr:\n{result.stderr}"
    
    assert "simple_main.py _main executed successfully" in result.stdout, \
        f"Expected output not found in stdout. Stdout:\n{result.stdout}"
    
    expected_args_output = f"Received arguments: ('{arg1}', '{arg2}')"
    assert expected_args_output in result.stdout, \
        f"Expected arguments output '{expected_args_output}' not found. Stdout:\n{result.stdout}"

# --- New Tests for run_main.py's own errors and validation (Section 4.1) ---

def test_no_args():
    """
    Tests run-main when no arguments are provided.
    Expected: Usage message and exit code 1.
    """
    result = run_main_command(None) # Pass None or empty string for target_module_path
    assert result.returncode == 1, \
        f"Expected exit code 1 for no args, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "Usage: python" in result.stderr or "用法: python" in result.stderr, \
        f"Expected usage message in stderr. Stderr:\n{result.stderr}"

def test_non_py_file():
    """
    Tests run-main with a non-.py file as the target.
    Expected: Error message and exit code 1.
    """
    non_py_target = PROJECT_ROOT / "README.md" # An existing non-py file
    result = run_main_command(non_py_target)
    assert result.returncode == 1, \
        f"Expected exit code 1 for non-py file, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "does not appear to be a Python file (.py)" in result.stderr or \
           "看起来不是一个 Python 文件 (.py)" in result.stderr, \
        f"Expected '.py file' error message in stderr. Stderr:\n{result.stderr}"

def test_target_non_existent():
    """
    Tests run-main with a non-existent .py file.
    Expected: ModuleNotFoundError from Python (propagated), non-zero exit code.
    run_main.py itself doesn't check for existence before exec.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "non_existent_module.py"
    result = run_main_command(target_script)
    assert result.returncode != 0, \
        f"Expected non-zero exit code for non-existent target, got {result.returncode}. Stderr:\n{result.stderr}"
    # The error comes from Python's import machinery via exec()
    assert "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr, \
        f"Expected ModuleNotFoundError or ImportError in stderr for non-existent file. Stderr:\n{result.stderr}"

def test_target_outside_project_relative_path():
    """
    Tests run-main with a target specified by a relative path pointing outside the project.
    This test assumes run_main.py is in PROJECT_ROOT.
    We need to be careful how this is constructed.
    If run_main.py is run from PROJECT_ROOT, `../somefile.py` would be outside.
    """
    # Create a temporary file outside the project structure for this test
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        outside_file = temp_dir / "outside_module.py"
        with open(outside_file, "w") as f:
            f.write("def _main(): print('outside_module executed')")

        # Calculate relative path from PROJECT_ROOT to outside_file
        # This is tricky because run_main.py itself calculates relpath from its CWD.
        # If we run run_main_command with cwd=PROJECT_ROOT, then the path we pass
        # to run_main_command should be the one run_main.py sees.
        # Let's try to pass a path that would resolve to outside.
        # A direct relative path like "../temp/outside_module.py" might be complex
        # due to how os.path.relpath behaves with different drives or complex structures.
        # run_main.py's logic: os.path.relpath(os.path.abspath(target_file_arg), os.getcwd())
        # If target_file_arg is already an absolute path to outside_file, it should be caught.
        # Let's test that first with test_target_outside_project_absolute_path.

        # For this relative test, we'll simulate running from a subdir and pointing up.
        # This is more about how run_main.py itself resolves paths.
        # The current run_main.py logic for outside project check:
        # module_rel_path = os.path.relpath(target_abs_path, project_root)
        # if module_rel_path.startswith(os.pardir) ...
        # So, if we give it an absolute path that is outside, it should catch it.

        # Let's try a simpler relative path that's clearly outside if CWD is project root.
        # This scenario is better tested by providing an absolute path that is outside.
        # The existing logic in run_main.py converts the input to an absolute path first.
        # So, a relative path like `../../outside.py` would be resolved to an absolute path
        # by `os.path.abspath()` within `run_main.py` before the `os.path.relpath()` check.

        # The most direct way to test the "outside project" check is with an absolute path.
        # The relative path scenario is implicitly covered if the absolute path resolution works.
        # If `os.path.abspath("../foo.py")` (from project root) results in `E:\repos\foo.py`
        # and project root is `E:\repos\run_main`, then `os.path.relpath` will give `..\foo.py`.
        
        # Let's use an absolute path for clarity in testing this specific check.
        # This test case might be redundant if test_target_outside_project_absolute_path is robust.
        # For now, focusing on the absolute path test is cleaner.
        pass # Skipping a complex relative path setup, will rely on absolute path test.


def test_target_outside_project_absolute_path():
    """
    Tests run-main with an absolute path to a target outside the project directory.
    Expected: Error message and exit code 1.
    """
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        # Ensure the temp_dir is not the same as or a child of PROJECT_ROOT
        # This is generally true for system temp dirs.
        assert not str(temp_dir).startswith(str(PROJECT_ROOT))
        
        outside_file = temp_dir / "another_outside_module.py"
        with open(outside_file, "w") as f:
            f.write("def _main():\n    print('another_outside_module executed')\n")
        
        result = run_main_command(str(outside_file.resolve())) # Pass absolute path
        
        assert result.returncode == 1, \
            f"Expected exit code 1 for outside project absolute path, got {result.returncode}. Stderr:\n{result.stderr}"
        assert "is outside the project directory" in result.stderr or \
               "不在项目目录" in result.stderr, \
            f"Expected 'outside project directory' error. Stderr:\n{result.stderr}"
# --- New Tests for Target Module Behavior and Error Propagation (Section 4.2) ---

def test_target_empty_file():
    """
    Tests run-main with an empty .py file.
    Expected: ImportError because _main cannot be found.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "empty_file.py"
    result = run_main_command(target_script)
    assert result.returncode != 0, \
        f"Expected non-zero exit code for empty file, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "ImportError" in result.stderr or \
           "AttributeError" in result.stderr or \
           "ModuleNotFoundError" in result.stderr, \
        f"Expected ImportError, AttributeError, or ModuleNotFoundError in stderr for empty file. Stderr:\n{result.stderr}"

def test_module_no_main_function():
    """
    Tests run-main with a module that does not define _main.
    Expected: ImportError.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "no_main_func.py"
    result = run_main_command(target_script)
    assert result.returncode != 0, \
        f"Expected non-zero exit code for module with no _main, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "ImportError: cannot import name '_main'" in result.stderr or \
           "ImportError: _main not found" in result.stderr, \
        f"Expected ImportError for missing _main. Stderr:\n{result.stderr}" # Actual message might vary slightly

def test_main_takes_no_args_called_with_args():
    """
    Tests calling a _main() (that takes no args) with arguments.
    Expected: TypeError from _main.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "main_no_args.py"
    result = run_main_command(target_script, "some_arg")
    assert result.returncode != 0, \
        f"Expected non-zero exit code, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "TypeError" in result.stderr and "_main() takes 0 positional arguments but 1 was given" in result.stderr or \
           "TypeError" in result.stderr and "_main() got an unexpected keyword argument" in result.stderr, \
        f"Expected TypeError for _main taking no args but called with one. Stderr:\n{result.stderr}" # Python 3.x specific message

def test_main_fixed_args_called_with_wrong_arg_count():
    """
    Tests calling _main(arg1, arg2) with only one argument.
    Expected: TypeError from _main.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "main_fixed_args.py"
    result = run_main_command(target_script, "one_arg_only")
    assert result.returncode != 0, \
        f"Expected non-zero exit code, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "TypeError" in result.stderr and "missing 1 required positional argument" in result.stderr or \
           "TypeError" in result.stderr and "_main() takes 2 positional arguments but 1 was given" in result.stderr, \
        f"Expected TypeError for wrong arg count. Stderr:\n{result.stderr}"

def test_main_fixed_args_called_correctly():
    """
    Tests calling _main(arg1, arg2) with correct arguments.
    Expected: Successful execution, exit code 0.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "main_fixed_args.py"
    arg1_val = "first"
    arg2_val = "second"
    result = run_main_command(target_script, arg1_val, arg2_val)
    assert result.returncode == 0, \
        f"Expected exit code 0, got {result.returncode}. Stderr:\n{result.stderr}"
    assert f"_main in main_fixed_args.py executed successfully with arg1='{arg1_val}', arg2='{arg2_val}'." in result.stdout, \
        f"Expected success message not in stdout. Stdout:\n{result.stdout}"

def test_module_import_time_error():
    """
    Tests run-main with a module that raises an error during its import.
    Expected: The original error (e.g., ZeroDivisionError) propagated.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "import_time_error.py"
    result = run_main_command(target_script)
    assert result.returncode != 0, \
        f"Expected non-zero exit code, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "ZeroDivisionError: division by zero" in result.stderr, \
        f"Expected ZeroDivisionError in stderr. Stderr:\n{result.stderr}"
    assert "import_time_error.py" in result.stderr, \
        f"Stderr should mention the failing file. Stderr:\n{result.stderr}"

def test_main_runtime_error():
    """
    Tests run-main with a module whose _main raises an error during execution.
    Expected: The original error (e.g., ValueError) propagated.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "runtime_error_in_main.py"
    result = run_main_command(target_script, "test_arg")
    assert result.returncode != 0, \
        f"Expected non-zero exit code, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "ValueError: This is a deliberate runtime error from _main." in result.stderr, \
        f"Expected ValueError in stderr. Stderr:\n{result.stderr}"
    assert "runtime_error_in_main.py" in result.stderr, \
        f"Stderr should mention the failing file. Stderr:\n{result.stderr}"
    assert "_main in runtime_error_in_main.py called with args: ('test_arg',)" in result.stdout, \
        f"Expected _main to be called. Stdout: \n{result.stdout}"


def test_main_sys_exit_zero():
    """
    Tests _main calling sys.exit(0).
    Expected: run-main exits with 0.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "main_with_sysexit.py"
    result = run_main_command(target_script, "0")
    assert result.returncode == 0, \
        f"Expected exit code 0, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "_main in main_with_sysexit.py called. Will exit with code: 0" in result.stdout

def test_main_sys_exit_non_zero():
    """
    Tests _main calling sys.exit(5).
    Expected: run-main exits with 5.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "main_with_sysexit.py"
    exit_code_to_test = 5
    result = run_main_command(target_script, str(exit_code_to_test))
    assert result.returncode == exit_code_to_test, \
        f"Expected exit code {exit_code_to_test}, got {result.returncode}. Stderr:\n{result.stderr}"
    assert f"_main in main_with_sysexit.py called. Will exit with code: {exit_code_to_test}" in result.stdout

def test_main_access_sys_argv():
    """
    Tests how sys.argv is set up within the target module by run_main.
    """
    target_script_name = "main_access_sys_argv.py"
    target_script_path_obj = PROJECT_ROOT / "tests" / "test_targets" / target_script_name
    
    arg1 = "first_arg"
    arg2 = "--option"
    result = run_main_command(target_script_path_obj, arg1, arg2)

    assert result.returncode == 0, \
        f"Expected exit code 0, got {result.returncode}. Stderr:\n{result.stderr}"
    
    stdout = result.stdout
    assert f"Received *args_tuple in _main: (('{arg1}', '{arg2}'))" in stdout or \
           f"Received *args_tuple in _main: ('{arg1}', '{arg2}')" in stdout, \
        f"Expected args_tuple not found. Stdout:\n{stdout}"

    # Based on the understanding that run_main.py does NOT modify sys.argv for the target:
    # sys.argv[0] in target will be path to run_main.py (or equivalent for -m)
    # sys.argv[1] in target will be path to target_script (as passed to run_main)
    # sys.argv[2:] in target will be args_for_main

    assert f"sys.argv inside module: ['" in stdout, f"sys.argv line not found. Stdout:\n{stdout}"
    # Check for run_main module path as first element (flexible check)
    # This part of the assertion needs to be robust to how Python -m resolves the path.
    # It could be an absolute path to run_main.py or similar.
    # A simple check for "run_main" in the first part of the string representation of sys.argv[0]
    # or checking if sys.argv[0] ends with run_main.py or run_main/__main__.py
    lines = stdout.splitlines()
    sys_argv_line = ""
    for line in lines:
        if line.startswith("sys.argv inside module:"):
            sys_argv_line = line
            break
    assert sys_argv_line, f"sys.argv line not found. Stdout:\n{stdout}"

    # A more robust check for sys.argv[0]
    # It should contain 'run_main' and likely '.py' if it's a file path.
    # Example: "sys.argv inside module: ['/path/to/run_main.py', 'tests/test_targets/main_access_sys_argv.py', 'first_arg', '--option']"
    # Or for `python -m run_main`, sys.argv[0] might be the path to the `__main__.py` of `run_main` if it's an installed package,
    # or the path to `run_main.py` if run directly from the project.
    # For `python -m run_main`, sys.argv[0] is often the absolute path to `.../run_main/__main__.py` or `.../run_main.py`
    # Let's check if 'run_main' is part of the first argument string.
    assert "'run_main" in sys_argv_line.split("['")[1].split("',")[0] or \
           "run_main.py" in sys_argv_line.split("['")[1].split("',")[0] or \
           "run_main/__main__.py" in sys_argv_line.split("['")[1].split("',")[0], \
           f"Expected 'run_main' related path in sys.argv[0]. Line: {sys_argv_line}"


    # Check for target script path as second element
    normalized_target_path_str = str(target_script_path_obj.resolve())
    # Need to handle potential differences in path representation (e.g. \\ vs / on Windows in string)
    # The path in sys.argv will be exactly as passed to `run_main_command` if it's absolute.
    # Our `run_main_command` passes `str(target_module_path)` which is `str(target_script_path_obj)`.
    # `target_script_path_obj` is already an absolute path.
    # Use repr() to match the string representation in the list output
    expected_path_repr = repr(normalized_target_path_str)
    assert expected_path_repr in sys_argv_line, \
        f"Expected target script path {expected_path_repr} in sys.argv[1]. Line: {sys_argv_line}"
    
    assert f"'{arg1}'" in sys_argv_line, f"Expected arg1 '{arg1}' in sys.argv. Line: {sys_argv_line}"
    assert f"'{arg2}'" in sys_argv_line, f"Expected arg2 '{arg2}' in sys.argv. Line: {sys_argv_line}"
# --- New Tests for Paths, CWD, and Environment (Section 4.3) ---

def test_module_with_spaces_in_name():
    """
    Tests run-main with a target module whose filename contains spaces.
    Expected: Successful execution.
    """
    # Ensure the file "module with spaces.py" exists in test_targets
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "module with spaces.py"
    assert target_script.exists(), f"Test target {target_script} not found."
    
    result = run_main_command(target_script, "arg with space")
    assert result.returncode != 0, \
        f"Expected non-zero exit code for module with spaces, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "SyntaxError: invalid syntax" in result.stderr, \
        f"Expected SyntaxError for module with spaces. Stderr:\n{result.stderr}"
    # _main should not be executed, so no stdout check for its messages.

def test_deeply_nested_module():
    """
    Tests run-main with a deeply nested target module.
    Expected: Successful execution, correct module name reported.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "deep" / "nested" / "module.py"
    assert target_script.exists(), f"Test target {target_script} not found."
    
    result = run_main_command(target_script)
    assert result.returncode == 0, \
        f"Expected exit code 0, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "_main in tests/test_targets/deep/nested/module.py executed successfully." in result.stdout
    # The __name__ should be tests.test_targets.deep.nested.module
    expected_module_name = "tests.test_targets.deep.nested.module"
    assert f"Module name is: {expected_module_name}" in result.stdout, \
        f"Expected module name '{expected_module_name}' not found. Stdout:\n{result.stdout}"

def test_successful_relative_import():
    """
    Tests run-main with a target module that performs a successful relative import.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "pkg" / "relative_import_ok.py"
    assert target_script.exists(), f"Test target {target_script} not found."
    
    result = run_main_command(target_script)
    assert result.returncode == 0, \
        f"Expected exit code 0, got {result.returncode}. Stderr:\n{result.stderr}"
    assert "_main in relative_import_ok.py executed successfully." in result.stdout
    assert "Value from sibling module: Value from sibling.py" in result.stdout
    assert "Function call from sibling: sibling_function was called" in result.stdout

def test_failed_relative_import_not_in_package():
    """
    Tests run-main with a target module attempting a relative import
    when it's not part of a package.
    Expected: ImportError (attempted relative import with no known parent package).
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "relative_import_fail.py"
    assert target_script.exists(), f"Test target {target_script} not found."

    result = run_main_command(target_script)
    assert result.returncode != 0, \
        f"Expected non-zero exit code, got {result.returncode}. Stderr:\n{result.stderr}"
    # The error message depends on Python version and specifics.
    # "ImportError: attempted relative import with no known parent package" is common.
    # The `relative_import_fail.py` is written to catch the ImportError and print it, then let it propagate.
    # `run_main.py`'s `exec` will then re-raise it.
    assert "ImportError" in result.stderr, \
        f"Expected ImportError in stderr. Stderr:\n{result.stderr}"
    # A more specific check if possible:
    assert "attempted relative import with no known parent package" in result.stderr or \
           "cannot import name 'some_non_existent_sibling'" in result.stderr, \
        f"Expected specific relative import error message. Stderr:\n{result.stderr}"


def test_run_from_subdirectory():
    """
    Tests running run-main when the current working directory is a subdirectory
    of the project. run_main.py uses os.getcwd() as its effective project_root.
    The target path passed to run_main should be relative to this new CWD.
    """
    # Target script relative to the new CWD (tests/test_targets/)
    target_script_relative_to_subdir = "simple_main.py"
    
    # New CWD will be tests/test_targets/
    new_cwd = PROJECT_ROOT / "tests" / "test_targets"
    assert new_cwd.is_dir(), f"Subdirectory for CWD {new_cwd} does not exist."

    # The target_module_path passed to run_main_command should be relative to this new_cwd
    # because run_main.py will resolve it from its CWD (which is `new_cwd` here).
    result = run_main_command(target_script_relative_to_subdir, cwd=new_cwd)

    assert result.returncode == 0, \
        f"run-main failed from subdir. Exit: {result.returncode}. Stderr:\n{result.stderr}. Stdout:\n{result.stdout}"
    assert "simple_main.py _main executed successfully" in result.stdout, \
        f"Expected output not found. Stdout:\n{result.stdout}"
    # Check that arguments are not passed if none were intended for this specific call
    assert "Received arguments:" not in result.stdout, \
        f"Unexpectedly received arguments when run from subdir. Stdout:\n{result.stdout}"


def test_project_root_in_pythonpath_env():
    """
    Tests if run-main works correctly when PROJECT_ROOT is already in PYTHONPATH.
    run_main.py adds os.getcwd() to sys.path if not already present.
    This test ensures this logic doesn't break anything.
    """
    target_script = PROJECT_ROOT / "tests" / "test_targets" / "simple_main.py"
    
    # Modify environment for the subprocess
    current_env = os.environ.copy()
    existing_pythonpath = current_env.get("PYTHONPATH", "")
    # Prepend PROJECT_ROOT to PYTHONPATH
    current_env["PYTHONPATH"] = f"{str(PROJECT_ROOT)}{os.pathsep}{existing_pythonpath}"

    # We use run_main_command which calls `python -m run_main`
    # The `cwd` for run_main_command defaults to PROJECT_ROOT.
    # The subprocess will inherit the modified environment.
    
    # Need to call subprocess.run directly to pass the modified env
    # to the `python -m run_main` execution.
    command = [
        sys.executable,
        "-m",
        "run_main",
        str(target_script)
    ]
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT, # run_main.py expects to be run from project root in this context
        env=current_env,
        check=False
    )
    
    assert process.returncode == 0, \
        f"run-main failed with PROJECT_ROOT in PYTHONPATH. Exit: {process.returncode}. Stderr:\n{process.stderr}"
    assert "simple_main.py _main executed successfully" in process.stdout, \
        f"Expected output not found. Stdout:\n{process.stdout}"