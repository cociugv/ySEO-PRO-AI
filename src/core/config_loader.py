"""
Configuration Loader — Reads YAML config with environment variable expansion.

Loads config from:
  1. config/default.yaml (base defaults)
  2. config/local.yaml (user overrides, gitignored)
  3. Environment variables (YSEO_* prefix)
"""

import os
import re
from typing import Any


def load_yaml_simple(path: str) -> dict:
    """
    Minimal YAML loader using only stdlib.
    Supports: key: value, nested keys (indentation), lists (- item).
    """
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = {}
    stack = [(result, -1)]  # (dict, indent_level)

    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        content = stripped.lstrip()

        # List item
        if content.startswith("- "):
            value = _parse_value(content[2:])
            parent_dict, _ = stack[-1]
            # Find the last key that should contain this list
            last_key = list(parent_dict.keys())[-1] if parent_dict else None
            if last_key and isinstance(parent_dict[last_key], list):
                parent_dict[last_key].append(value)
            elif last_key and parent_dict[last_key] == "":
                parent_dict[last_key] = [value]
            continue

        # Key: value pair
        if ":" in content:
            key, _, val = content.partition(":")
            key = key.strip()
            val = val.strip()

            # Pop stack to correct level
            while len(stack) > 1 and stack[-1][1] >= indent:
                stack.pop()

            parent_dict, _ = stack[-1]

            if val == "" or val == "|":
                # Nested dict or empty list
                new_dict = {}
                parent_dict[key] = new_dict
                stack.append((new_dict, indent))
            else:
                parent_dict[key] = _parse_value(val)

    return result


def _parse_value(val: str) -> Any:
    """Parse a YAML value to Python type."""
    if not val:
        return ""

    # Remove quotes
    if (val.startswith('"') and val.endswith('"')) or \
       (val.startswith("'") and val.endswith("'")):
        return val[1:-1]

    # Booleans
    if val.lower() in ("true", "yes", "on"):
        return True
    if val.lower() in ("false", "no", "off"):
        return False

    # None
    if val.lower() in ("null", "~"):
        return None

    # Numbers
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        pass

    # Lists inline [a, b, c]
    if val.startswith("[") and val.endswith("]"):
        items = val[1:-1].split(",")
        return [_parse_value(i.strip()) for i in items if i.strip()]

    return val


def expand_env_vars(config: dict) -> dict:
    """Expand ${ENV_VAR} references in config values."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = expand_env_vars(value)
        elif isinstance(value, str):
            result[key] = re.sub(
                r'\$\{(\w+)\}',
                lambda m: os.environ.get(m.group(1), m.group(0)),
                value
            )
        else:
            result[key] = value
    return result


def load_config(base_dir: str = ".") -> dict:
    """
    Load merged configuration.

    Priority: env vars > local.yaml > default.yaml
    """
    config_dir = os.path.join(base_dir, "config")

    # Load base config
    config = load_yaml_simple(os.path.join(config_dir, "default.yaml"))

    # Merge local overrides
    local = load_yaml_simple(os.path.join(config_dir, "local.yaml"))
    config = _deep_merge(config, local)

    # Expand environment variables
    config = expand_env_vars(config)

    # Apply YSEO_* environment overrides
    for key, value in os.environ.items():
        if key.startswith("YSEO_"):
            path = key[5:].lower().split("__")
            _set_nested(config, path, _parse_value(value))

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts, override wins on conflict."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _set_nested(d: dict, path: list, value: Any) -> None:
    """Set a nested dict value using a path list."""
    for key in path[:-1]:
        d = d.setdefault(key, {})
    if path:
        d[path[-1]] = value
