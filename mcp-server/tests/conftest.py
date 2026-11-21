"""Shared pytest setup: make the mcp-server package importable and expose paths."""

from __future__ import annotations

import os
import sys

import pytest

MCP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.dirname(MCP_DIR)
DATA_DIR = os.path.join(MCP_DIR, "data")

if MCP_DIR not in sys.path:
    sys.path.insert(0, MCP_DIR)


@pytest.fixture
def repo_dir() -> str:
    return REPO_DIR


@pytest.fixture
def data_dir() -> str:
    return DATA_DIR


def write_files(base, files: dict[str, str]) -> None:
    """Create files (relative path -> content) under base."""
    for rel, content in files.items():
        path = os.path.join(str(base), rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
