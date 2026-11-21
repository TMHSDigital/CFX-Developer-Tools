"""
Manifest generation tool.

Generates a properly formatted fxmanifest.lua based on parameters.
Can optionally scan a workspace directory to auto-populate scripts and NUI.
"""

from __future__ import annotations

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
) -> str:
    """Generate fxmanifest.lua content and return it as a string."""

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

    if has_nui:
        nui_root = posixpath.dirname(ui_page)
        lines.append("")
        lines.append(f"ui_page '{lua_string(ui_page)}'")
        lines.append("")
        lines.extend(_block("files", [f"{nui_root}/**" if nui_root else ui_page]))

    return "\n".join(lines) + "\n"
