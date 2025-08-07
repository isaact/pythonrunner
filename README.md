# Python Code Execution Service

This service executes arbitrary Python code within a secure, sandboxed environment using `nsjail`. It exposes a single API endpoint at `/execute`.

## Running Locally

### 1. Build the Docker Image

```bash
docker build -t python-code-executor .
```

### 2. Run the Docker Container

Run the container, mapping port 8080 on your local machine to port 8080 inside the container.

```bash
docker run --rm -p 8080:8080 python-code-executor
```

The service will now be running and accessible at `http://localhost:8080`.

## Running Tests

The project includes a full suite of integration tests. The following command provides a convenient way to build the latest version of the code, run the tests, and automatically clean up the test container.

```bash
docker build -t python-code-executor . && \
docker run --rm python-code-executor pytest -v
```

## Usage

You can execute a script by sending a `POST` request to the `/execute` endpoint. The script must contain a `main()` function that returns a JSON-serializable dictionary.

### Example `cURL` Request (Local)

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script":"import pandas as pd\n\ndef main():\n  print(\"Hello from stdout!\")\n  df = pd.DataFrame([{\"a\": 1, \"b\": 2}])\n  return {\"result\": df.to_dict()}"}'
```
