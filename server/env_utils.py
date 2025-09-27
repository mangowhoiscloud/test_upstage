"""Helpers for loading environment variables from .env files."""
from __future__ import annotations

import os
from typing import Dict


def load_env_file(path: str = ".env") -> Dict[str, str]:
    """Load key/value pairs from a dotenv-style file into ``os.environ``.

    Returns a mapping of keys that were newly inserted. Existing environment
    variables are not overwritten so that real environment configuration takes
    precedence over the file.
    """

    updated: Dict[str, str] = {}

    if not os.path.exists(path):
        return updated

    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key and key not in os.environ:
                    os.environ[key] = value
                    updated[key] = value
    except OSError:
        # Silently ignore file read issues; the proxy will error later if
        # required environment variables are missing.
        return updated

    return updated
