from __future__ import annotations

import sys
from pathlib import Path

from iosisclient.commands import validate_strategy
from iosisclient.config import Config


def validate(args: object, config: Config) -> int:
    yaml_path = Path(args.yaml)
    if not yaml_path.is_file():
        print(f"Error: file not found: {yaml_path}", file=sys.stderr)
        return 1

    valid = validate_strategy(yaml_path)
    return 0 if valid else 1
