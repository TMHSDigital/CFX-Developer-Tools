"""
Shared, cached loading of the JSON data files (natives, events, docs index).

Each file is parsed once per process and re-read only when its size or
modification time changes on disk.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache


@lru_cache(maxsize=16)
def _load(path: str, mtime_ns: int, size: int) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset(path: str, label: str) -> list | str:
    """Return the parsed JSON list at ``path``, or an ``Error: ...`` string.

    The result is shared between calls: callers must not mutate it.
    """
    try:
        st = os.stat(path)
    except OSError:
        return f"Error: {label} not found at {path}"
    try:
        data = _load(path, st.st_mtime_ns, st.st_size)
    except (OSError, ValueError) as exc:
        return f"Error: could not read {label} at {path}: {exc}"
    if not isinstance(data, list):
        return f"Error: could not read {label} at {path}: expected a JSON array"
    return data
