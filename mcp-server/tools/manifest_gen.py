"""
Manifest generation tool.

Generates a properly formatted fxmanifest.lua based on parameters.
Can optionally scan a workspace directory to auto-populate scripts and NUI.
"""

from __future__ import annotations

from tools.manifest_common import (
    FRAMEWORK_DEPS,
    validate_inputs,
    read_workspace_context,
    scan_script_files,
    detect_nui_presence,
)


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

    game = game.strip().lower()
    language = language.strip().lower()
    framework = framework.strip().lower()

    error = validate_inputs(game, language, framework)
    if error:
        return error

    author = "YourName"
    description = name

    if workspace_path:
        ctx = read_workspace_context(workspace_path)
        author = ctx.get("author", author)
        description = ctx.get("description", description)

        scanned = scan_script_files(workspace_path)
        if not scripts and any(scanned.values()):
            scripts = []
            for f in scanned.get("client", []):
                scripts.append(f)
            for f in scanned.get("server", []):
                scripts.append(f)

        if not has_nui:
            has_nui = detect_nui_presence(workspace_path)

    if game == "both":
        games_str = "{ 'gta5', 'rdr3' }"
    else:
        games_str = f"{{ '{game}' }}"

    lines: list[str] = [
        "fx_version 'cerulean'",
        f"games {games_str}",
        "",
        f"author '{author}'",
        f"description '{description}'",
        "version '1.0.0'",
        "",
    ]

    all_deps: list[str] = []
    fw_dep = FRAMEWORK_DEPS.get(framework)
    if fw_dep:
        all_deps.append(fw_dep)
    if dependencies:
        all_deps.extend(dependencies)

    for dep in all_deps:
        lines.append(f"dependency '{dep}'")
    if all_deps:
        lines.append("")

    if language == "lua":
        lines.append("shared_scripts {")
        lines.append("    'config.lua'")
        lines.append("}")
        lines.append("")
        client_entries = ["'client/*.lua'"]
        server_entries = ["'server/*.lua'"]
    elif language == "javascript":
        client_entries = ["'client/*.js'"]
        server_entries = ["'server/*.js'"]
    elif language == "csharp":
        client_entries = [f"'{name}.net.dll'"]
        server_entries = [f"'{name}.net.dll'"]

    if scripts:
        for s in scripts:
            if "client" in s.lower() or s.startswith("cl_"):
                client_entries.append(f"'{s}'")
            elif "server" in s.lower() or s.startswith("sv_"):
                server_entries.append(f"'{s}'")
            else:
                client_entries.append(f"'{s}'")

    lines.append("client_scripts {")
    for entry in client_entries:
        lines.append(f"    {entry}")
    lines.append("}")
    lines.append("")
    lines.append("server_scripts {")
    for entry in server_entries:
        lines.append(f"    {entry}")
    lines.append("}")

    if has_nui:
        lines.append("")
        lines.append("ui_page 'html/index.html'")
        lines.append("")
        lines.append("files {")
        lines.append("    'html/**'")
        lines.append("}")

    return "\n".join(lines) + "\n"
