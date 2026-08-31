from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from iosisclient.config import Config


def _resolve_cache_dir(config: Config) -> Path | None:
    cache_dir = config.local.cache_dir
    if not cache_dir:
        return None
    p = Path(cache_dir)
    if not p.is_dir():
        return None
    return p


def _count_entries(cache_dir: Path) -> int:
    count = 0
    for manifest in cache_dir.rglob("manifest.json"):
        try:
            data = json.loads(manifest.read_text())
            if data.get("success"):
                count += 1
        except Exception:
            pass
    return count


def _cache_size(cache_dir: Path) -> int:
    total = 0
    for f in cache_dir.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total


def cache(args: object, config: Config) -> int:
    action = getattr(args, "cache_action", None)
    if not action:
        print("Usage: iosis cache {info|clear}", file=sys.stderr)
        return 1

    cache_dir = _resolve_cache_dir(config)

    if action == "info":
        if cache_dir is None:
            print("Cache not configured.")
            print("Set [local] cache_dir in config or IOSIS_CACHE_DIR env var.")
            return 0
        entries = _count_entries(cache_dir)
        size = _cache_size(cache_dir)
        print(f"Directory: {cache_dir}")
        print(f"Entries:   {entries}")
        print(f"Size:      {size / 1024:.1f} KB")
        return 0

    if action == "clear":
        if cache_dir is None:
            print("Cache not configured. Nothing to clear.")
            return 0
        entries = _count_entries(cache_dir)
        shutil.rmtree(cache_dir)
        print(f"Cleared {entries} cache entry(ies) from {cache_dir}")
        return 0

    print(f"Unknown cache action: {action}", file=sys.stderr)
    return 1
