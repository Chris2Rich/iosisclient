from __future__ import annotations

import sys
from pathlib import Path

from iosisclient.commands import parse_and_lower, validate_strategy
from iosisclient.client import IosisClient
from iosisclient.config import Config


def run_local(args: object, config: Config) -> int:
    yaml_path = Path(args.yaml)
    if not yaml_path.is_file():
        print(f"Error: file not found: {yaml_path}", file=sys.stderr)
        return 1

    lowered = parse_and_lower(yaml_path)
    output_name = next(iter(lowered.outputs))
    graph = lowered.graph(output_name)

    from iosislib.core.graph import Graph, GraphValidationError, LocalExecutor
    report = Graph.validate(graph.root_node)
    if not report.is_valid:
        print(f"Validation failed ({len(report.issues)} issue(s)):", file=sys.stderr)
        for i, issue in enumerate(report.issues, 1):
            print(f"  {i}. [{issue.code}] {issue.message}", file=sys.stderr)
        return 1

    no_cache = getattr(args, "no_cache", False)
    cache_dir = getattr(args, "cache_dir", None)
    if cache_dir is None and not no_cache:
        cache_dir = config.local.cache_dir

    executor = LocalExecutor(
        cache_dir=cache_dir,
        no_cache=no_cache,
    )
    result = executor.execute(graph)

    print(f"Result: {result.shape[0]} rows x {result.shape[1]} columns")
    print(f"Columns: {result.columns}")
    if result.shape[0] > 0:
        print(result.head(5))

    if getattr(args, "output", None):
        out = Path(args.output)
        result.write_parquet(out)
        print(f"Written to {out}")

    return 0


def run_cloud(args: object, config: Config) -> int:
    yaml_path = Path(args.yaml)
    if not yaml_path.is_file():
        print(f"Error: file not found: {yaml_path}", file=sys.stderr)
        return 1

    try:
        validate_strategy(yaml_path)
    except SystemExit:
        return 1

    if not config.cloud.api_key:
        print("Error: no API key. Run `iosis init` or set IOSIS_API_KEY.", file=sys.stderr)
        return 1

    client = IosisClient(api_key=config.cloud.api_key, base_url=config.cloud.base_url)

    print("Submitting run...")
    run_result = client.submit_run(yaml_path)
    print(f"Run {run_result.id} submitted (status: {run_result.status})")

    print("Waiting for completion...")

    def on_status(status: str) -> None:
        print(f"  status: {status}")

    try:
        final = client.wait_for_run(run_result.id, on_status=on_status)
    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if final.status == "succeeded":
        print("Succeeded.")
    else:
        print(f"Failed: {final.run.get('error', 'unknown')}", file=sys.stderr)
        return 1

    output_dir = getattr(args, "output_dir", None)
    if output_dir:
        downloaded = client.download_artifacts(final.id, output_dir)
        print(f"Downloaded {len(downloaded)} artifact(s) to {output_dir}")

    return 0
