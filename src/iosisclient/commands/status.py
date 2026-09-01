from __future__ import annotations

import sys

from iosisclient.client import IosisClient
from iosisclient.config import Config


def status(args: object, config: Config) -> int:
    run_id = getattr(args, "run_id", None)
    if not run_id:
        print("Error: provide a run ID: iosis status <run-id>", file=sys.stderr)
        return 1

    if not config.cloud.api_key:
        print("Error: no API key. Run `iosis init` or set IOSIS_API_KEY.", file=sys.stderr)
        return 1

    client = IosisClient(api_key=config.cloud.api_key, base_url=config.cloud.base_url)
    run_result = client.get_run(run_id)

    print(f"Run:   {run_result.id}")
    print(f"Status: {run_result.status}")

    run_data = run_result.run
    if run_data.get("createdAt"):
        print(f"Created: {run_data['createdAt']}")
    if run_data.get("computeMs"):
        print(f"Compute: {run_data['computeMs']}ms")
    result = run_data.get("result")
    if result and result.get("url"):
        print(f"Result:  {result['url'][:80]}...")
    if run_data.get("error"):
        print(f"Error:   {run_data['error']}")

    return 0
