from __future__ import annotations

import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_CONFIG_DIR_NAME = "iosis"
_CONFIG_FILE_NAME = "config.toml"


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / _CONFIG_DIR_NAME
        return Path.home() / "AppData" / "Roaming" / _CONFIG_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / _CONFIG_DIR_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / _CONFIG_DIR_NAME
    return Path.home() / ".config" / _CONFIG_DIR_NAME


def config_path() -> Path:
    return _config_dir() / _CONFIG_FILE_NAME


@dataclass(frozen=True)
class CloudConfig:
    api_key: str | None = None
    base_url: str = "https://tryiosis.vercel.app"


@dataclass(frozen=True)
class LocalConfig:
    cache_dir: str | None = None


@dataclass(frozen=True)
class Config:
    default_mode: str = "local"
    cloud: CloudConfig = field(default_factory=CloudConfig)
    local: LocalConfig = field(default_factory=LocalConfig)

    @property
    def effective_mode(self) -> str:
        return os.environ.get("IOSIS_MODE", self.default_mode)


def load_config(path: Path | None = None) -> Config:
    p = path or config_path()
    raw: dict[str, Any] = {}
    if p.is_file():
        with open(p, "rb") as f:
            raw = tomllib.load(f)

    default_mode = raw.get("default_mode", "local")
    cloud_raw = raw.get("cloud", {})
    local_raw = raw.get("local", {})

    api_key = cloud_raw.get("api_key") or os.environ.get("IOSIS_API_KEY")
    base_url = (
        os.environ.get("IOSIS_BASE_URL")
        or cloud_raw.get("base_url")
        or "https://tryiosis.vercel.app"
    )

    cache_dir = local_raw.get("cache_dir") or os.environ.get("IOSIS_CACHE_DIR")

    return Config(
        default_mode=default_mode,
        cloud=CloudConfig(api_key=api_key, base_url=base_url),
        local=LocalConfig(cache_dir=cache_dir),
    )


def save_config(config: Config, path: Path | None = None) -> Path:
    p = path or config_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [f"default_mode = {config.default_mode!r}", ""]
    if config.cloud.api_key or config.cloud.base_url != "https://tryiosis.vercel.app":
        lines.append("[cloud]")
        if config.cloud.api_key:
            lines.append(f'api_key = {config.cloud.api_key!r}')
        if config.cloud.base_url != "https://tryiosis.vercel.app":
            lines.append(f'base_url = {config.cloud.base_url!r}')
        lines.append("")
    if config.local.cache_dir:
        lines.append("[local]")
        lines.append(f'cache_dir = {config.local.cache_dir!r}')
        lines.append("")

    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
