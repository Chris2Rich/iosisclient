from __future__ import annotations

import sys

from iosisclient.config import Config, CloudConfig, save_config


def init(args: object, config: Config) -> int:
    api_key = getattr(args, "api_key", None)
    if not api_key:
        print("Error: provide an API key: iosis init <api_key>", file=sys.stderr)
        return 1

    updated = Config(
        default_mode=config.default_mode,
        cloud=CloudConfig(api_key=api_key, base_url=config.cloud.base_url),
    )
    path = save_config(updated)
    print(f"API key saved to {path}")
    return 0
