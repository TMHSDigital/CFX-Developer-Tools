"""
Shared manifest generation constants and utilities.

Used by both scaffold.py and manifest_gen.py to avoid duplication.
"""

from __future__ import annotations

FRAMEWORK_DEPS = {
    "esx": "es_extended",
    "qbcore": "qb-core",
    "oxcore": "ox_core",
}

VALID_GAMES = {"gta5", "rdr3", "both"}
VALID_LANGUAGES = {"lua", "javascript", "csharp"}
VALID_FRAMEWORKS = {"standalone", "esx", "qbcore", "oxcore"}


def games_block(game: str) -> str:
    """Return the Lua games directive string."""
    if game == "both":
        return "{ 'gta5', 'rdr3' }"
    return f"{{ '{game}' }}"


def validate_inputs(game: str, language: str, framework: str) -> str | None:
    """Return an error string if inputs are invalid, or None if valid."""
    if game not in VALID_GAMES:
        return f"Error: invalid game '{game}'. Use gta5, rdr3, or both."
    if language not in VALID_LANGUAGES:
        return f"Error: invalid language '{language}'. Use lua, javascript, or csharp."
    if framework not in VALID_FRAMEWORKS:
        return f"Error: invalid framework '{framework}'. Use standalone, esx, qbcore, or oxcore."
    return None
