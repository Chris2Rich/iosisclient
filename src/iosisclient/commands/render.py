from __future__ import annotations

import sys
from pathlib import Path

from iosisclient.client import IosisClient
from iosisclient.config import Config


def render(args: object, config: Config) -> int:
    yaml_path = Path(args.yaml)
    if not yaml_path.is_file():
        print(f"Error: file not found: {yaml_path}", file=sys.stderr)
        return 1

    if not config.cloud.api_key:
        print("Error: no API key. Run `iosis init` or set IOSIS_API_KEY.", file=sys.stderr)
        return 1

    client = IosisClient(api_key=config.cloud.api_key, base_url=config.cloud.base_url)

    output_path = getattr(args, "output", None)
    svg = client.render_graph(yaml_path, output_path=output_path)

    if output_path:
        print(f"Graph written to {output_path}")
    else:
        print(svg)

    return 0
