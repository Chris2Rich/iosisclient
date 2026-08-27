# iosisClient

Thin Python client for the [Iosis](https://tryiosis.vercel.app) API. Zero dependencies, stdlib only.

```bash
pip install iosisclient
```

## Setup

Get an API key at [tryiosis.vercel.app](https://tryiosis.vercel.app) (Billing page, API keys section).

```python
from iosisclient import IosisClient

# reads IOSIS_API_KEY from environment
client = IosisClient()

# or pass explicitly
client = IosisClient(api_key="iosis_...")

# or use a custom base URL
client = IosisClient(base_url="http://localhost:3000")
```

Environment variables:

- `IOSIS_API_KEY` -- your API key
- `IOSIS_BASE_URL` -- API base URL (defaults to `https://tryiosis.vercel.app`)

---

## Runs

### `submit_run(yaml, idempotency_key=None)`

Submit a strategy YAML document for execution. Pass a file path or a YAML string. Returns the queued run:

```python
run = client.submit_run("strategy.yaml")
# {"id": "8f3c...", "status": "queued"}
```

Auto-generates an idempotency key (UUID) per call. Pass `idempotency_key=` to reuse one and avoid duplicate runs on retry.

**Endpoint:** `POST /api/runs` (Content-Type: `application/yaml`)

### `get_run(run_id)`

Get run status and result artifacts:

```python
run = client.get_run("8f3c...")
# {"run": {"id": "8f3c...", "status": "succeeded", "result": {...}, "artifacts": [...]}}
```

Status is one of `queued`, `running`, `succeeded`, or `failed`. Artifact URLs are signed and expire after 60 seconds.

**Endpoint:** `GET /api/runs/:runId`

### `wait_for_run(run_id, max_wait=300, initial_delay=2, max_delay=30)`

Poll `get_run()` with exponential backoff until the run succeeds or fails:

```python
result = client.wait_for_run(run["id"])
```

Raises `TimeoutError` if the run does not complete within `max_wait` seconds.

---

## Charts

### `get_charts(run_id)`

Get signed SVG chart URLs for a completed run:

```python
charts = client.get_charts("8f3c...")
# {"charts": [{"name": "close", "chartUrl": "https://...svg...", "expiresAt": "..."}]}
```

URLs expire after 5 minutes. Download immediately.

**Endpoint:** `GET /api/runs/:runId/charts`

---

## Datasets

### `list_datasets()`

List all published dataset names and versions:

```python
datasets = client.list_datasets()
# {"datasets": [{"name": "prices", "versions": ["2026-01-15"], "latestVersion": "2026-01-15"}]}
```

**Endpoint:** `GET /api/datasets`

The `name` field from these results can be used directly as the `path` parameter in `source.parquet` nodes in strategy YAML (see Strategy Format below).

### `list_dataset_manifests()`

List datasets with full manifests (schema, row count, resolution, coverage window, S3 location):

```python
manifests = client.list_dataset_manifests()
# {"datasets": [{"name": "prices", "versions": [...], "manifest": {"rows": 50000, "schema": {...}, ...}}]}
```

**Endpoint:** `GET /api/datasets/manifest`

### `lookup_dataset(name, version="latest")`

Look up a single dataset by name. Pass `"latest"` or an ISO-8601 date for calendar versioning:

```python
info = client.lookup_dataset("prices", version="2026-01-15")
# {"dataset": {"name": "prices", "version": "2026-01-15", "rows": 50000, "schema": {...}}}
```

**Endpoint:** `GET /api/datasets/lookup?name=:name&data_version=:version`

---

## TSFN Catalog

### `list_tsfns()`

Get the catalog of time-series function nodes allowed in strategy YAML:

```python
catalog = client.list_tsfns()
# {"format": "iosis.tsfn-catalog", "tsfns": [{"op": "transform.pct_change", "version": "0.1.0", ...}]}
```

Each entry includes the operation name, version, category, parameters, and input/output frame signature.

**Endpoint:** `GET /api/tsfns`

---

## Graph Rendering

### `render_graph(yaml)`

Render a strategy YAML document as an SVG graph (nodes, ports, edges):

```python
svg = client.render_graph("strategy.yaml")
# "<svg xmlns=\"...\">...</svg>"
```

Write to file:

```python
with open("graph.svg", "w") as f:
    f.write(svg)
```

**Endpoint:** `POST /api/graphs/render` (Content-Type: `application/yaml`, returns `image/svg+xml`)

---

## Errors

API errors raise `IosisError` with `.status`, `.code`, and `.message`:

```python
from iosisclient import IosisError

try:
    client.get_run("bad-id")
except IosisError as e:
    print(e.status)    # 400
    print(e.code)      # "invalid_run_id"
    print(e.message)   # "Run ID must be a valid UUID."
```

Common status codes:

| Status | Meaning |
| --- | --- |
| 400 | Malformed request (bad YAML, missing parameter, invalid ID) |
| 401 | Missing or invalid API key |
| 403 | Account not approved or credits exhausted |
| 404 | Run or dataset not found |
| 429 | Rate limited (retry after backoff) |

---

## License

MIT
