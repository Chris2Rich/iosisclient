from __future__ import annotations

import sys

from iosisclient.commands import print_table
from iosisclient.client import IosisClient
from iosisclient.config import Config


def datasets(args: object, config: Config) -> int:
    if not config.cloud.api_key:
        print("Error: no API key. Run `iosis init` or set IOSIS_API_KEY.", file=sys.stderr)
        return 1

    client = IosisClient(api_key=config.cloud.api_key, base_url=config.cloud.base_url)
    result = client.list_dataset_manifests()
    items = result.get("datasets", result) if isinstance(result, dict) else result

    rows = []
    for ds in items:
        rows.append([
            ds.get("name", ""),
            ds.get("version", ""),
            str(ds.get("row_count", "")),
            ds.get("path", "")[:50],
        ])
    print_table(rows, ["Name", "Version", "Rows", "Path"])
    return 0
