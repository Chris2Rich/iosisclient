# Repository Guidelines

## Project Purpose

iosisClient is a thin Python CLI and API client for the Iosis strategy platform. The `client` module uses only stdlib (`urllib.request`); the package depends on `iosislib` for local graph execution and strategy validation. The HTTP client is intentionally dependency-free so it runs anywhere Python does.

Keep the client thin. It authenticates with API keys, talks to the iosisweb REST API over JSON, and shells out to `iosislib` for local-only operations (strategy parsing, graph execution, validation). Do not add HTTP frameworks, async runtimes, or re-implementation of server-side logic.

## Source Layout And Imports

- `src/iosisclient/__init__.py`: public re-exports (`IosisClient`, `IosisError`, `RunResult`, `Artifact`, `DatasetManifest`).
- `src/iosisclient/client.py`: `IosisClient` HTTP library (stdlib only), `IosisError`, `RunResult`, `DatasetManifest`.
- `src/iosisclient/cli.py`: `iosis` CLI entry point (`main()`), argument parsing, command dispatch.
- `src/iosisclient/config.py`: `Config` TOML-based config management (`~/.iosis/config.toml`).
- `src/iosisclient/commands/`: CLI subcommands (`init`, `run`, `validate`, `catalog`, `datasets`, `status`, `render`, `cache`).

The `client.py` module must remain stdlib-only. Do not import `requests`, `httpx`, or any third-party HTTP library. The `commands/` module may import `iosislib` for local execution and validation.

## Architectural Invariants

### HTTP Client Is Stdlib Only

`IosisClient` uses `urllib.request` for all HTTP. Authentication is `Authorization: Bearer <api_key>`. Idempotency keys are sent via `Idempotency-Key` header. Content types are `application/yaml` for strategy submission and `application/json` for everything else. The client does not parse YAML; it passes it through as bytes.

### Response Format Alignment

The server returns camelCase field names (`computeMs`, `createdAt`, `resultSummary`). The client must map these correctly. Artifact objects have the shape `{kind, name, url, sha256, expiresAt}` — presigned S3 URLs, not raw S3 paths. The `download_artifacts` method iterates `run.artifacts` and filters by `kind`.

### Config Is TOML

`Config` reads `~/.iosis/config.toml`. The `[cloud]` section holds `api_key` and `base_url`. The `[local]` section holds `cache_dir`. The `init` command writes this file. Never store secrets in environment variables when config is available; env vars are fallback only.

### CLI Commands Are Stateless

Each CLI command function receives `(args, config)` and returns an exit code (0 = success, 1 = error). Commands print to stdout/stderr and do not carry state between invocations. The `run local` command imports `iosislib` for graph execution; `run cloud` uses `IosisClient` for API submission.

### Local Execution Delegates To iosislib

`run local` calls `parse_and_lower()` (which imports `iosislib.strategy`) and `LocalExecutor.execute()`. Do not re-implement strategy parsing, graph validation, or execution in iosisclient. The client is a wrapper, not a second engine.

## Development Workflow

- `python -m pip install -e ".[dev]"`: install package and development extras.
- `python -m ruff check src`: lint production source.
- `python -m mypy src/iosisclient`: type-check the client and commands.
- `python -m pytest`: run tracked tests under `tests/`.
- `python -m build`: build wheel and source distributions under `dist/`.

Use Python 3.11+, four-space indentation, type hints, `PascalCase` classes, `snake_case` functions/variables, and uppercase constants. Keep comments sparse and explanatory.

Tests belong in `tests/test_*.py`. Cover CLI argument parsing, config read/write, HTTP error handling, response parsing, and the full `run cloud` flow with mocked HTTP responses. Do not test iosislib internals; that is iosislib's job.

Keep commits imperative and specific, for example `Fix artifact download path`. Pull requests should explain behavior changes and link issues where available. Do not commit secrets, generated distributions, caches, or machine-specific paths.
