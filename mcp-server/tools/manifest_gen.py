"""
Manifest generation tool.

Generates a properly formatted fxmanifest.lua based on parameters.
Can optionally scan a workspace directory to auto-populate scripts and NUI.
"""

from __future__ import annotations

import difflib
import os
import posixpath

from tools.manifest_common import (
    FRAMEWORK_DEPS,
    FRAMEWORK_LUA_EXTRAS,
    csharp_dll_paths,
    find_nui_page,
    lua_string,
    validate_inputs,
    read_workspace_context,
    scan_script_files,
)

DEFAULT_UI_PAGE = "html/index.html"


def _classify_script(path: str) -> str:
    """Return 'client', 'server' or 'shared' for a caller-supplied script path."""
    lower = path.replace("\\", "/").lower()
    base = lower.rsplit("/", 1)[-1]
    parts = lower.split("/")
    if base.startswith("cl_") or "client" in parts[:-1] or base.startswith("client"):
        return "client"
    if base.startswith("sv_") or "server" in parts[:-1] or base.startswith("server"):
        return "server"
    return "shared"


def _block(directive: str, entries: list[str]) -> list[str]:
    """Render a Lua table directive with comma-separated quoted entries."""
    lines = [f"{directive} {{"]
    for i, entry in enumerate(entries):
        comma = "," if i < len(entries) - 1 else ""
        lines.append(f"    '{lua_string(entry)}'{comma}")
    lines.append("}")
    return lines


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def generate_manifest(
    name: str,
    game: str,
    language: str,
    framework: str,
    scripts: list[str] | None = None,
    dependencies: list[str] | None = None,
    has_nui: bool = False,
    workspace_path: str | None = None,
    exports: list[str] | None = None,
    server_exports: list[str] | None = None,
    mode: str = "create",
) -> str:
    """Generate fxmanifest.lua content and return it as a string.

    mode="update" reads ``workspace_path``/fxmanifest.lua instead, adds the
    given scripts, dependencies and exports that are not already declared
    (keeping every existing line and comment), and returns the new content
    with a unified diff. The file is never written.
    """
    if (mode or "create").strip().lower() == "update":
        return update_manifest(workspace_path, scripts, dependencies, exports, server_exports)

    game = (game or "").strip().lower()
    language = (language or "").strip().lower()
    framework = (framework or "").strip().lower()

    error = validate_inputs(game, language, framework)
    if error:
        return error

    author = "YourName"
    description = name
    ui_page = DEFAULT_UI_PAGE

    client: list[str] = []
    server: list[str] = []
    shared: list[str] = []
    scanned_any = False

    if workspace_path:
        ctx = read_workspace_context(workspace_path)
        author = ctx.get("author", author)
        description = ctx.get("description", description)

        if not scripts:
            scanned = scan_script_files(workspace_path)
            if any(scanned.values()):
                scanned_any = True
                client = list(scanned.get("client", []))
                server = list(scanned.get("server", []))
                shared = list(scanned.get("shared", []))

        detected_page = find_nui_page(workspace_path)
        if detected_page:
            has_nui = True
            ui_page = detected_page

    if scripts:
        for s in scripts:
            {"client": client, "server": server, "shared": shared}[_classify_script(s)].append(s)

    # Default entries only for sides that have no scanned or caller-supplied
    # scripts; an explicit file list already names its scripts, so adding the
    # glob as well would list the same files twice.
    if not scanned_any:
        cs_client, cs_server = csharp_dll_paths(name)
        defaults = {
            "lua": (["config.lua"], ["client/*.lua"], ["server/*.lua"]),
            "javascript": ([], ["client/*.js"], ["server/*.js"]),
            "csharp": ([], [cs_client], [cs_server]),
        }[language]
        shared = shared or list(defaults[0])
        client = client or list(defaults[1])
        server = server or list(defaults[2])

    extras = FRAMEWORK_LUA_EXTRAS.get(framework, {}) if language == "lua" else {}
    shared = list(extras.get("shared_scripts", [])) + shared

    lines: list[str] = [
        "fx_version 'cerulean'",
        "games { 'gta5', 'rdr3' }" if game == "both" else f"games {{ '{game}' }}",
        "",
        f"author '{lua_string(author)}'",
        f"description '{lua_string(description)}'",
        "version '1.0.0'",
        "",
    ]

    all_deps: list[str] = list(extras.get("dependencies", []))
    fw_dep = FRAMEWORK_DEPS.get(framework)
    if fw_dep:
        all_deps.append(fw_dep)
    if dependencies:
        all_deps.extend(dependencies)
    all_deps = _dedupe(all_deps)

    for dep in all_deps:
        lines.append(f"dependency '{lua_string(dep)}'")
    if all_deps:
        lines.append("")

    if language == "javascript":
        lines.append("node_version '22'")
        lines.append("")

    blocks: list[list[str]] = []
    for directive, entries in (
        ("shared_scripts", _dedupe(shared)),
        ("client_scripts", _dedupe(client)),
        ("server_scripts", _dedupe(server)),
    ):
        if entries:
            blocks.append(_block(directive, entries))

    for i, block in enumerate(blocks):
        if i:
            lines.append("")
        lines.extend(block)

    for directive, entries in (("exports", exports or []), ("server_exports", server_exports or [])):
        entries = _dedupe(list(entries))
        if entries:
            lines.append("")
            lines.extend(_block(directive, entries))

    if has_nui:
        nui_root = posixpath.dirname(ui_page)
        lines.append("")
        lines.append(f"ui_page '{lua_string(ui_page)}'")
        lines.append("")
        lines.extend(_block("files", [f"{nui_root}/**" if nui_root else ui_page]))

    return "\n".join(lines) + "\n"


def update_manifest(
    workspace_path: str | None,
    scripts: list[str] | None = None,
    dependencies: list[str] | None = None,
    exports: list[str] | None = None,
    server_exports: list[str] | None = None,
) -> str:
    """Add entries to an existing manifest without touching its other lines."""
    from tools.manifest_validate import parse_manifest

    if not workspace_path:
        return "Error: mode='update' needs workspace_path (the resource folder or its fxmanifest.lua)."
    path = workspace_path if workspace_path.endswith("fxmanifest.lua") else os.path.join(workspace_path, "fxmanifest.lua")
    if not os.path.isfile(path):
        return f"Error: fxmanifest.lua not found at {path}"
    with open(path, encoding="utf-8") as f:
        original = f.read()

    declared = parse_manifest(original)

    def existing(*names: str) -> set[str]:
        return {v for n in names for v in declared.get(n, [])}

    single = {"client": "client_script", "server": "server_script", "shared": "shared_script"}
    plural = {k: v + "s" for k, v in single.items()}
    additions: list[str] = []
    for dep in _dedupe(list(dependencies or [])):
        if dep not in existing("dependency", "dependencies"):
            additions.append(f"dependency '{lua_string(dep)}'")
    for script in _dedupe(list(scripts or [])):
        side = _classify_script(script)
        if script not in existing(single[side], plural[side]):
            additions.append(f"{single[side]} '{lua_string(script)}'")
    for name in _dedupe(list(exports or [])):
        if name not in existing("export", "exports"):
            additions.append(f"export '{lua_string(name)}'")
    for name in _dedupe(list(server_exports or [])):
        if name not in existing("server_export", "server_exports"):
            additions.append(f"server_export '{lua_string(name)}'")

    if not additions:
        return f"No changes: everything requested is already declared in {path}."

    nl = chr(10)
    updated = original if original.endswith(nl) else original + nl
    updated += nl + nl.join(additions) + nl
    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), updated.splitlines(keepends=True),
        fromfile="fxmanifest.lua", tofile="fxmanifest.lua (updated)",
    ))
    return (
        f"Updated manifest for {path} (not written; apply it yourself):{nl}{nl}"
        f"```diff{nl}{diff}```{nl}{nl}Full content:{nl}{nl}```lua{nl}{updated}```{nl}"
    )
