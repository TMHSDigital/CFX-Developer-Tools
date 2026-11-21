"""
Expose the plugin's skills and rules over MCP for clients without Cursor's
plugin loader (Claude Code, other MCP clients).

Each skills/<name>/SKILL.md becomes a resource ``cfx://skills/<name>`` and a
prompt ``cfx-<name>``; each rules/<name>.mdc becomes a resource
``cfx://rules/<name>``. Files are read on every request, so edits show up
without restarting, and new skill directories are picked up at startup with
no code change. Paths are resolved from the plugin root (the parent of
mcp-server/), so the server must run from a full checkout of the repo.
"""

from __future__ import annotations

import os
import re

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.M)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _description(path: str, fallback: str) -> str:
    try:
        m = _FRONTMATTER_RE.match(_read(path))
    except OSError:
        return fallback
    d = _DESC_RE.search(m.group(1)) if m else None
    return d.group(1).strip("'\"") if d else fallback


def discover(root: str = PLUGIN_ROOT) -> tuple[dict[str, str], dict[str, str]]:
    """Return ({skill name: SKILL.md path}, {rule name: .mdc path})."""
    skills: dict[str, str] = {}
    skills_dir = os.path.join(root, "skills")
    if os.path.isdir(skills_dir):
        for name in sorted(os.listdir(skills_dir)):
            path = os.path.join(skills_dir, name, "SKILL.md")
            if os.path.isfile(path):
                skills[name] = path
    rules: dict[str, str] = {}
    rules_dir = os.path.join(root, "rules")
    if os.path.isdir(rules_dir):
        for fname in sorted(os.listdir(rules_dir)):
            if fname.endswith(".mdc"):
                rules[fname[:-4]] = os.path.join(rules_dir, fname)
    return skills, rules


def _reader(path: str):
    def read() -> str:
        return _read(path)
    return read


def _prompt(path: str):
    def prompt() -> str:
        return (
            "Use the following CFX Developer Tools skill as guidance for this task."
            + chr(10) + chr(10) + _read(path)
        )
    return prompt


def register(mcp, root: str = PLUGIN_ROOT) -> None:
    """Register skill/rule resources and skill prompts on a FastMCP server."""
    skills, rules = discover(root)

    for name, path in skills.items():
        description = _description(path, f"CFX skill: {name}")
        mcp.resource(f"cfx://skills/{name}", name=f"skill-{name}",
                     description=description, mime_type="text/markdown")(_reader(path))
        mcp.prompt(name=f"cfx-{name}", description=description)(_prompt(path))

    for name, path in rules.items():
        description = _description(path, f"CFX rule: {name}")
        mcp.resource(f"cfx://rules/{name}", name=f"rule-{name}",
                     description=description, mime_type="text/markdown")(_reader(path))
