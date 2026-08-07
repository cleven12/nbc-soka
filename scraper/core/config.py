"""Load source config from config/*.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scraper.utils.jsonio import read_json

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONFIG = REPO_ROOT / "config" / "ligikuu.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data"


def load_source_config(path: Path | str | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_SOURCE_CONFIG
    if not config_path.is_file():
        raise FileNotFoundError(f"Source config not found: {config_path}")
    data = read_json(config_path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid source config (expected object): {config_path}")
    return data


def enabled_resources(config: dict[str, Any]) -> list[dict[str, Any]]:
    resources = config.get("sportspress", {}).get("resources") or []
    enabled = [r for r in resources if r.get("enabled", True)]
    return sorted(enabled, key=lambda r: int(r.get("priority") or 99))


def http_settings(config: dict[str, Any]) -> dict[str, Any]:
    return dict(config.get("http") or {})


def output_dir(config: dict[str, Any], override: Path | str | None = None) -> Path:
    if override:
        return Path(override)
    relative = (config.get("output") or {}).get("dir") or "data/ligikuu"
    path = Path(relative)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path
