from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import git
from jsonschema import Draft202012Validator

from .errors import ConfigError
from .schema import load_schema
from .types import ConfigDict


DEFAULT_CONFIG: ConfigDict = {
    "timezone": "local",
    "identity_source": "author",
    "output": {
        "format": "json",
        "path": None,
    },
    "filters": {
        "since": None,
        "until": None,
        "branch": None,
        "no_merges": False,
    },
    "members": [],
}


def _load_json_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Config file must contain a JSON object: {path}")
    return data


def _deep_merge(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in incoming.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _find_repo_root(path: Path) -> Path | None:
    try:
        repo = git.Repo(path, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None

    root = repo.working_tree_dir
    if root is None:
        return None
    return Path(root)


def _validate_config(config: dict[str, Any]) -> None:
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(config), key=lambda error: list(error.path))
    if not errors:
        return

    lines = ["Configuration validation failed:"]
    for error in errors:
        loc = ".".join(str(part) for part in error.path)
        lines.append(f"- {loc or '<root>'}: {error.message}")
    raise ConfigError("\n".join(lines))


def resolve_config(
    *,
    repo_path: str | Path,
    explicit_config_path: str | Path | None,
    cli_overrides: dict[str, Any],
) -> ConfigDict:
    resolved: dict[str, Any] = deepcopy(DEFAULT_CONFIG)

    repo_root = _find_repo_root(Path(repo_path))
    if repo_root is not None:
        repo_config = repo_root / "nightowls.json"
        if repo_config.is_file():
            resolved = _deep_merge(resolved, _load_json_file(repo_config))

    if explicit_config_path is not None:
        resolved = _deep_merge(resolved, _load_json_file(Path(explicit_config_path)))

    resolved = _deep_merge(resolved, cli_overrides)
    _validate_config(resolved)
    return resolved  # type: ignore[return-value]
