"""
Compute artifact counts from the working tree and check docs against them.

Single source of truth for the counts quoted in README.md, CLAUDE.md,
AGENTS.md, .cursorrules, the docs site and the GitHub "About" description.

Usage (from the repository root):
    python .github/scripts/counts.py --json
    python .github/scripts/counts.py --description
    python .github/scripts/counts.py --check README.md CLAUDE.md ...
    python .github/scripts/counts.py --require README.md --check README.md ...

A line containing ``counts:ignore`` (for example an HTML comment
``<!-- counts:ignore -->`` at the end of a historical table row) is skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _path(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


def compute_counts() -> dict[str, int]:
    plugin = json.load(open(_path(".cursor-plugin", "plugin.json"), encoding="utf-8"))
    snippets = sum(len(files) for _, _, files in os.walk(_path("snippets")) if files)
    templates = sum(
        1 for d in os.listdir(_path("templates"))
        if os.path.isfile(_path("templates", d, "fxmanifest.lua"))
    )
    examples = sum(
        1 for d in os.listdir(_path("examples"))
        if os.path.isfile(_path("examples", d, "fxmanifest.lua"))
    )
    with open(_path("mcp-server", "server.py"), encoding="utf-8") as f:
        tools = len(re.findall(r"^@mcp\.tool\(", f.read(), re.M))
    events = len(json.load(open(_path("mcp-server", "data", "events.json"), encoding="utf-8")))
    gta5 = len(json.load(open(_path("mcp-server", "data", "natives_gta5.json"), encoding="utf-8")))
    rdr3 = len(json.load(open(_path("mcp-server", "data", "natives_rdr3.json"), encoding="utf-8")))
    return {
        "skills": len(plugin.get("skills", [])),
        "rules": len(plugin.get("rules", [])),
        "snippets": snippets,
        "templates": templates,
        "examples": examples,
        "tools": tools,
        "events": events,
        "natives_gta5": gta5,
        "natives_rdr3": rdr3,
        "natives": gta5 + rdr3,
    }


def natives_floor(total: int, step: int = 500) -> str:
    """Round down for '<n>+ natives' claims, e.g. 11737 -> '11,500+'."""
    return f"{(total // step) * step:,}+"


def description(c: dict[str, int]) -> str:
    return (
        "AI-powered Cursor IDE plugin for FiveM and RedM resource development. "
        f"{c['skills']} skills, {c['rules']} rules, {c['tools']} MCP tools, "
        f"{natives_floor(c['natives'])} natives, {c['events']} events, "
        f"{c['snippets']} snippets, {c['templates']} templates."
    )


# "<n> <noun>" claims to verify. Exact counts must match; "<n>+ natives"
# is a lower bound on the total native count.
CLAIM_RE = re.compile(
    r"\b(?P<num>\d[\d,]*)(?P<plus>\+)?\s+"
    r"(?:code\s+|starter\s+|MCP\s+|runnable\s+)?"
    r"(?P<noun>skills|rules|snippets|templates|tools|examples|events|natives|native functions)\b",
    re.IGNORECASE,
)


def check_files(paths: list[str], c: dict[str, int]) -> list[str]:
    errors: list[str] = []
    for rel in paths:
        with open(_path(rel), encoding="utf-8") as f:
            lines = f.read().splitlines()
        for lineno, line in enumerate(lines, 1):
            if "counts:ignore" in line:
                continue
            for m in CLAIM_RE.finditer(line):
                num = int(m.group("num").replace(",", ""))
                noun = "natives" if m.group("noun").lower().startswith("native") else m.group("noun").lower()
                if noun == "natives":
                    if m.group("plus") and num > c["natives"]:
                        errors.append(f"{rel}:{lineno}: claims {m.group(0)!r} but there are {c['natives']} natives")
                    continue
                if num != c[noun]:
                    errors.append(f"{rel}:{lineno}: says {m.group(0)!r} but the tree has {c[noun]} {noun}")
    return errors


def require_counts(path: str, c: dict[str, int]) -> list[str]:
    text = open(_path(path), encoding="utf-8").read()
    needed = [f"{c[k]} {k}" for k in ("skills", "rules", "snippets", "templates")]
    return [f"{path}: missing '{n}'" for n in needed if n not in text]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json", action="store_true", help="print counts as JSON")
    parser.add_argument("--description", action="store_true", help="print the GitHub About description")
    parser.add_argument("--require", metavar="FILE", help="file that must state the skill/rule/snippet/template counts")
    parser.add_argument("--check", nargs="*", metavar="FILE", default=[], help="files whose count claims must match")
    args = parser.parse_args()

    counts = compute_counts()
    if args.json:
        print(json.dumps(counts, indent=2))
    if args.description:
        print(description(counts))

    errors: list[str] = []
    if args.require:
        errors += require_counts(args.require, counts)
    if args.check:
        errors += check_files(args.check, counts)
    for e in errors:
        print(f"::error::{e}", file=sys.stderr)
    if args.check or args.require:
        if not errors:
            print(f"Counts verified in {len(args.check)} file(s): " + ", ".join(
                f"{counts[k]} {k}" for k in ("skills", "rules", "snippets", "templates", "examples", "tools", "events")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
