"""
Shared manifest generation constants and utilities.

Used by both scaffold.py and manifest_gen.py to avoid duplication.
"""

from __future__ import annotations

import os
import re

FRAMEWORK_DEPS = {
    "esx": "es_extended",
    "qbcore": "qb-core",
    "qbox": "qbx_core",
    "oxcore": "ox_core",
    "vorp": "vorp_core",
    "rsg": "rsg-core",
}

VALID_GAMES = {"gta5", "rdr3", "both"}
VALID_LANGUAGES = {"lua", "javascript", "csharp"}
VALID_FRAMEWORKS = {"standalone", "esx", "qbcore", "qbox", "oxcore", "vorp", "rsg"}

# Match the opening quote so values like "O'Brien" are read whole.
AUTHOR_RE = re.compile(r"""author\s+(?P<q>['"])(?P<value>.*?)(?P=q)""")
DESC_RE = re.compile(r"""description\s+(?P<q>['"])(?P<value>.*?)(?P=q)""")


RESOURCE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def lua_string(value: str) -> str:
    """Escape a value for use inside a single-quoted Lua string literal."""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


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
        return f"Error: invalid framework '{framework}'. Use standalone, esx, qbcore, qbox, oxcore, vorp, or rsg."
    return None


def substitute_variables(template: str, variables: dict[str, str]) -> str:
    """Replace {{key}} placeholders in a template string."""
    for key, value in variables.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def read_workspace_context(workspace_path: str) -> dict[str, str]:
    """Scan a workspace directory for author/description from an existing fxmanifest.lua.

    Returns a dict with 'author' and 'description' if found.
    """
    context: dict[str, str] = {}

    for root, _dirs, files in os.walk(workspace_path):
        if "node_modules" in root or ".git" in root:
            continue

        for fname in files:
            if fname != "fxmanifest.lua":
                continue

            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(8192)
            except OSError:
                continue

            author_match = AUTHOR_RE.search(content)
            if author_match and "author" not in context:
                context["author"] = author_match.group("value")

            desc_match = DESC_RE.search(content)
            if desc_match and "description" not in context:
                context["description"] = desc_match.group("value")

            if "author" in context:
                return context

    return context


def scan_script_files(directory: str) -> dict[str, list[str]]:
    """Scan a directory for script files and categorize them by client/server/shared.

    Returns dict with keys 'client', 'server', 'shared' each containing a list of
    relative file paths.
    """
    scripts: dict[str, list[str]] = {"client": [], "server": [], "shared": []}

    if not os.path.isdir(directory):
        return scripts

    for item in sorted(os.listdir(directory)):
        full = os.path.join(directory, item)
        if os.path.isdir(full):
            sub_items = sorted(os.listdir(full))
            for sub in sub_items:
                ext = os.path.splitext(sub)[1].lower()
                if ext not in (".lua", ".js", ".ts"):
                    continue
                rel = f"{item}/{sub}"
                if item.lower() in ("client", "cl"):
                    scripts["client"].append(rel)
                elif item.lower() in ("server", "sv"):
                    scripts["server"].append(rel)
                elif item.lower() in ("shared", "common", "config"):
                    scripts["shared"].append(rel)
        else:
            ext = os.path.splitext(item)[1].lower()
            if ext not in (".lua", ".js", ".ts"):
                continue
            name_lower = item.lower()
            if name_lower.startswith("cl_") or name_lower.startswith("client"):
                scripts["client"].append(item)
            elif name_lower.startswith("sv_") or name_lower.startswith("server"):
                scripts["server"].append(item)
            elif name_lower.startswith("sh_") or name_lower.startswith("config"):
                scripts["shared"].append(item)

    return scripts


def find_nui_page(directory: str) -> str | None:
    """Return the relative path of the NUI entry page in a resource, or None.

    Built output (``<dir>/dist/index.html``) is preferred over a source
    ``index.html`` in the same folder, since that is what FXServer serves.
    """
    for nui_dir in ("html", "ui", "web", "nui"):
        candidate = os.path.join(directory, nui_dir)
        if not os.path.isdir(candidate):
            continue
        for sub in ("dist", ""):
            folder = os.path.join(candidate, sub) if sub else candidate
            if not os.path.isdir(folder):
                continue
            for f in sorted(os.listdir(folder)):
                if f.lower() in ("index.html", "index.htm"):
                    return "/".join(p for p in (nui_dir, sub, f) if p)
        if os.path.isdir(os.path.join(candidate, "dist")):
            return f"{nui_dir}/dist/index.html"
    if os.path.exists(os.path.join(directory, "index.html")):
        return "index.html"
    return None


def detect_nui_presence(directory: str) -> bool:
    """Check if a directory contains NUI files (index.html, ui/, html/, web/)."""
    return find_nui_page(directory) is not None
