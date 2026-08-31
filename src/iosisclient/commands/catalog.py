from __future__ import annotations

import sys

from iosisclient.commands import print_table
from iosisclient.client import IosisClient
from iosisclient.config import Config


def catalog_local(args: object, config: Config) -> int:
    from iosislib.catalog import dump_tsfn_catalog

    catalog = dump_tsfn_catalog()
    rows = []
    for op in sorted(catalog, key=lambda x: x["operation"]):
        rows.append([
            op["operation"],
            op["version"],
            op.get("category", ""),
            op.get("description", "")[:60],
        ])
    print_table(rows, ["Operation", "Version", "Category", "Description"])
    return 0


def catalog_cloud(args: object, config: Config) -> int:
    if not config.cloud.api_key:
        print("Error: no API key. Run `iosis init` or set IOSIS_API_KEY.", file=sys.stderr)
        return 1

    client = IosisClient(api_key=config.cloud.api_key, base_url=config.cloud.base_url)
    tsfns = client.list_tsfns()
    items = tsfns.get("tsfns", tsfns) if isinstance(tsfns, dict) else tsfns

    rows = []
    for op in items:
        rows.append([
            op.get("operation", op.get("name", "")),
            op.get("version", ""),
            op.get("category", ""),
            op.get("description", "")[:60],
        ])
    print_table(rows, ["Operation", "Version", "Category", "Description"])
    return 0


def catalog(args: object, config: Config) -> int:
    mode = getattr(args, "mode", None) or config.effective_mode
    if mode == "cloud":
        return catalog_cloud(args, config)
    return catalog_local(args, config)
