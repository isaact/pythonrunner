import sys
import json
import importlib.util
import io

def run_user_script(module_name):
    """
    Imports the user's script as a module from its file path,
    captures its stdout, executes its main() function, and prints a
    final JSON object containing the result and the captured stdout.
    """
    module_path = f"/tmp/sandbox/{module_name}.py"

    # Redirect stdout to a string buffer
    old_stdout = sys.stdout
    sys.stdout = captured_stdout = io.StringIO()

    result = None
    stdout_str = ""

    try:
        # Import the user's script from its file path
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        user_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = user_module
        spec.loader.exec_module(user_module)

        if not hasattr(user_module, "main"):
            raise AttributeError("Script must contain a 'main' function")

        # Call the main function to get the result
        result = user_module.main()

    finally:
        # Restore stdout and get the captured value
        sys.stdout = old_stdout
        stdout_str = captured_stdout.getvalue()

    # Final output dictionary
    output = {
        "result": result,
        "stdout": stdout_str
    }

    # Print the final combined JSON to the real stdout
    print(json.dumps(output))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        # This error goes to the real stderr
        print(json.dumps({"error": "Runner script requires a module name."}), file=sys.stderr)
        sys.exit(1)

    module_to_run = sys.argv[1]
    try:
        run_user_script(module_to_run)
    except Exception as e:
        # Catch any error during import or execution and report it
        error_details = f"{type(e).__name__}: {e}"
        print(json.dumps({"error": "Failed to execute script", "details": error_details}), file=sys.stderr)
        sys.exit(1)