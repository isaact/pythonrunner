import os
import uuid
import subprocess
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 8080))
SANDBOX_PATH = os.getenv("SANDBOX_PATH", "/tmp/sandbox")
NSJAIL_CONFIG = os.getenv("NSJAIL_CONFIG", "/app/nsjail.cfg")

@app.route("/execute", methods=["POST"])
def execute_script():
    data = request.get_json(force=True)
    script = data.get("script")
    if not script:
        return jsonify({"error": "Missing 'script' in request body"}), 400

    # Basic check for 'def main' presence
    if "def main" not in script:
        return jsonify({"error": "Script must contain a 'main' function"}), 400

    script_uuid = uuid.uuid4().hex
    script_filename_in_sandbox = f"/sandbox/{script_uuid}.py"

    # The user's script is not written to the host filesystem.
    # Instead, it's piped into the jail's stdin and written to the tmpfs.
    commands_to_pipe = f"""
cat <<'EOF' > {script_filename_in_sandbox}
{script}
EOF
/usr/local/bin/python /runner/runner.py {script_uuid}
"""

    nsjail_cmd = [
        "nsjail",
        "-C", NSJAIL_CONFIG,
        "--",
        "/bin/sh",
    ]

    try:
        proc = subprocess.run(
            nsjail_cmd,
            input=commands_to_pipe,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 408

    if proc.stderr:
        try:
            # If runner script itself fails, it prints JSON to stderr
            error_data = json.loads(proc.stderr)
            return jsonify(error_data), 400
        except json.JSONDecodeError:
            # For other nsjail errors, return the raw stderr
            return jsonify({"error": "An unexpected error occurred", "details": proc.stderr}), 500

    try:
        # The runner script prints a single JSON object to stdout
        response_data = json.loads(proc.stdout)
        return jsonify(response_data)
    except json.JSONDecodeError:
        return jsonify({
            "error": "Runner script produced invalid JSON",
            "details": "The runner script's output could not be parsed.",
            "stdout": proc.stdout,
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_RUN_PORT)
