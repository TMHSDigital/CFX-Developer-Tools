"""
fxmanifest.lua validator.

Shared by the `validate_manifest_tool` MCP tool and CI:

    python mcp-server/tools/manifest_validate.py templates examples

parses each manifest's directives (string, table and multi-line table forms)
and reports errors and warnings.
"""

from __future__ import annotations

import fnmatch
import glob
import json
import os
import re
import sys

if __package__ in (None, ""):  # run as a script from CI
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.manifest_common import FRAMEWORK_DEPS, FRAMEWORK_GAMES, PRUNED_DIRS

VALID_MANIFEST_GAMES = {"gta5", "rdr3", "ny"}
SCRIPT_DIRECTIVES = {
    "client_script", "client_scripts", "server_script", "server_scripts",
    "shared_script", "shared_scripts", "files", "file",
}

_COMMENT_RE = re.compile(r"--\[(=*)\[.*?\]\1\]|--[^\n]*", re.S)
_STRING_RE = re.compile(r"'([^'\\]*(?:\\.[^'\\]*)*)'|\"([^\"\\]*(?:\\.[^\"\\]*)*)\"")
_DIRECTIVE_RE = re.compile(
    r"^[ \t]*([A-Za-z_]\w*)[ \t]*(\{.*?\}|'[^'\n]*'|\"[^\"\n]*\")",
    re.M | re.S,
)


def _strip_comments(text: str) -> str:
    # Keep quoted strings intact: only remove "--" outside quotes.
    out, i = [], 0
    for m in _STRING_RE.finditer(text):
        out.append(_COMMENT_RE.sub("", text[i:m.start()]))
        out.append(m.group(0))
        i = m.end()
    out.append(_COMMENT_RE.sub("", text[i:]))
    return "".join(out)


def parse_manifest(text: str) -> dict[str, list[str]]:
    """Return directive name -> list of string values (repeated directives append)."""
    directives: dict[str, list[str]] = {}
    for name, raw in _DIRECTIVE_RE.findall(_strip_comments(text)):
        values = [a if a else b for a, b in _STRING_RE.findall(raw)]
        directives.setdefault(name, []).extend(values)
    return directives


def _is_build_output(path: str) -> bool:
    p = path.replace("\\", "/")
    return p.startswith("dist/") or "/dist/" in p or p.endswith(".net.dll")


def _resolves(resource_dir: str, pattern: str) -> bool:
    return bool(glob.glob(os.path.join(resource_dir, pattern), recursive=True))


def validate_manifest(path: str) -> dict:
    """Validate a resource directory or fxmanifest.lua path.

    Returns {"manifest": str, "errors": [...], "warnings": [...]}.
    """
    manifest = path if os.path.basename(path) == "fxmanifest.lua" else os.path.join(path, "fxmanifest.lua")
    resource_dir = os.path.dirname(os.path.abspath(manifest))
    result = {"manifest": manifest, "errors": [], "warnings": []}
    errors, warnings = result["errors"], result["warnings"]

    if not os.path.isfile(manifest):
        if os.path.isfile(os.path.join(resource_dir, "__resource.lua")):
            errors.append("uses the deprecated __resource.lua; rename it to fxmanifest.lua and add fx_version 'cerulean'")
        else:
            errors.append(f"fxmanifest.lua not found at {manifest}")
        return result
    if os.path.isfile(os.path.join(resource_dir, "__resource.lua")):
        errors.append("__resource.lua is deprecated; delete it (fxmanifest.lua takes precedence)")

    with open(manifest, encoding="utf-8", errors="replace") as f:
        text = f.read()
    d = parse_manifest(text)

    fx = d.get("fx_version", [])
    if not fx:
        errors.append("missing fx_version")
    elif fx[-1] != "cerulean":
        errors.append(f"fx_version is '{fx[-1]}'; use 'cerulean'")

    games = d.get("games", []) + d.get("game", [])
    if not games:
        errors.append("missing games (for example games { 'gta5' })")
    for g in games:
        if g not in VALID_MANIFEST_GAMES:
            errors.append(f"invalid game '{g}' (use gta5, rdr3 or ny)")

    if re.search(r"^\s*lua54\b", _strip_comments(text), re.M):
        errors.append("remove the lua54 directive: Lua 5.4 is the only runtime ('yes' is ignored, true is invalid Lua)")

    for directive in sorted(SCRIPT_DIRECTIVES & d.keys()):
        for entry in d[directive]:
            if entry.startswith("@") or "://" in entry:
                continue  # file from another resource, or a URL
            if _resolves(resource_dir, entry):
                continue
            message = f"{directive} entry '{entry}' does not match any file"
            if _is_build_output(entry):
                warnings.append(message + " (build output; build the resource first)")
            else:
                errors.append(message)

    ui_pages = d.get("ui_page", [])
    if ui_pages:
        ui = ui_pages[-1]
        if "://" not in ui:
            if not _resolves(resource_dir, ui):
                (warnings if _is_build_output(ui) else errors).append(f"ui_page '{ui}' does not exist")
            file_globs = d.get("files", []) + d.get("file", [])
            if not any(fnmatch.fnmatch(ui, g.replace("**", "*")) for g in file_globs):
                errors.append(f"ui_page '{ui}' is not covered by a files entry, so clients cannot load it")

    deps = set(d.get("dependency", []) + d.get("dependencies", []))
    for framework, dep in FRAMEWORK_DEPS.items():
        if dep in deps and games:
            supported = FRAMEWORK_GAMES.get(framework, set())
            wrong = [g for g in games if g not in supported]
            if wrong:
                errors.append(f"depends on {dep} ({framework}), which does not run on {', '.join(wrong)}")

    return result


def format_result(result: dict) -> str:
    lines = [f"{result['manifest']}: {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)"]
    lines += [f"  ERROR: {e}" for e in result["errors"]]
    lines += [f"  WARN:  {w}" for w in result["warnings"]]
    if not result["errors"] and not result["warnings"]:
        lines.append("  OK")
    return "\n".join(lines)


def validate_manifest_report(path: str, format: str = "text") -> str:
    result = validate_manifest(path)
    if (format or "text").lower() == "json":
        return json.dumps(result)
    return format_result(result)


def _find_manifests(roots: list[str]) -> list[str]:
    found = []
    for root in roots:
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = sorted(x for x in dirs if x not in PRUNED_DIRS)
            if "fxmanifest.lua" in files:
                found.append(os.path.join(dirpath, "fxmanifest.lua"))
    return found


def main(argv: list[str]) -> int:
    manifests = _find_manifests(argv or ["."])
    failed = 0
    for m in manifests:
        result = validate_manifest(m)
        print(format_result(result))
        for e in result["errors"]:
            print(f"::error file={m}::{e}")
        failed += bool(result["errors"])
    print(f"{len(manifests)} manifest(s) checked, {failed} with errors")
    return 1 if failed or not manifests else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
