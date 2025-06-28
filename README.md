# Python Code Execution Service

This service executes arbitrary Python code within a secure, sandboxed environment using `nsjail`. It exposes a single API endpoint at `/execute`.

## Running Locally

### 1. Build the Docker Image

To avoid creating anonymous images, build the image with a specific tag. This command only needs to be run once, or whenever you make changes to the source code.

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

The project includes a full suite of unit tests. To run them, first build the main image and start the container:

```bash
docker build -t python-code-executor .
docker run -d --name python-executor-container -p 8080:8080 python-code-executor
```

Once the container is running, you can execute the tests inside it:

```bash
docker exec python-executor-container pytest -v
```

When you are finished, you can stop and remove the container:

```bash
docker stop python-executor-container
docker rm python-executor-container
```

## Usage

You can execute a script by sending a `POST` request to the `/execute` endpoint. The script must contain a `main()` function that returns a JSON-serializable dictionary.

### Example `cURL` Request (Local)

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script":"import pandas as pd\n\ndef main():\n  print(\"Hello from stdout!\")\n  df = pd.DataFrame([{\"a\": 1, \"b\": 2}])\n  return {\"result\": df.to_dict()}"}'
```

### Example `cURL` Request (Cloud Run)

Once deployed, you can use the same command with your Google Cloud Run service URL.

```bash
curl -X POST YOUR_CLOUD_RUN_SERVICE_URL/execute \
  -H "Content-Type: application/json" \
  -d '{"script":"import pandas as pd\n\ndef main():\n  print(\"Hello from stdout!\")\n  df = pd.DataFrame([{\"a\": 1, \"b\": 2}])\n  return {\"result\": df.to_dict()}"}'