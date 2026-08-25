# iosissdk

Thin Python client for the [Iosis](https://tryiosis.vercel.app) cloud API. Zero dependencies, stdlib only.

## Install

```bash
pip install iosissdk
```

## Quick start

Set your API key:

```bash
export IOSIS_API_KEY=iosis_xxxxxxxx_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Use the client:

```python
from iosissdk import IosisClient

client = IosisClient()  # reads IOSIS_API_KEY from env

# Submit a strategy run
run = client.submit_run("strategy.yaml")
print(run["id"], run["status"])

# Wait for it to finish
result = client.wait_for_run(run["id"])

# Get chart URLs
charts = client.get_charts(run["id"])

# List available datasets
datasets = client.list_datasets()

# Look up a specific dataset
info = client.lookup_dataset("prices", version="latest")

# Get the TSFN catalog
catalog = client.list_tsfns()

# Render a strategy graph as SVG
svg = client.render_graph("strategy.yaml")
```

## Configuration

```python
# Explicit key
client = IosisClient(api_key="iosis_...")

# Custom base URL (defaults to https://tryiosis.vercel.app)
client = IosisClient(base_url="http://localhost:3000")
```

Or via environment variables:

- `IOSIS_API_KEY` - your API key
- `IOSIS_BASE_URL` - API base URL

## Methods

| Method | Description |
| --- | --- |
| `submit_run(yaml, idempotency_key=)` | Submit a strategy YAML as a run. Pass a file path or YAML string. |
| `get_run(run_id)` | Get run status and artifacts. |
| `wait_for_run(run_id, max_wait=300)` | Poll until the run succeeds or fails. |
| `get_charts(run_id)` | Get signed SVG chart URLs for a run. |
| `list_datasets()` | List published dataset names and versions. |
| `list_dataset_manifests()` | List datasets with full manifests (schema, rows, etc). |
| `lookup_dataset(name, version="latest")` | Look up a single dataset by name. |
| `list_tsfns()` | Get the catalog of allowed time-series function nodes. |
| `render_graph(yaml)` | Render a strategy as an SVG graph. |

## Errors

API errors raise `IosisError` with `.status`, `.code`, and `.message`:

```python
from iosissdk import IosisClient, IosisError

try:
    client.get_run("bad-id")
except IosisError as e:
    print(e.status)    # 400
    print(e.code)      # "invalid_run_id"
    print(e.message)   # "Run ID must be a valid UUID."
```

## License

MIT
