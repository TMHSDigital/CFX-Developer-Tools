"""
Manifest generation tool.

Generates a properly formatted fxmanifest.lua based on parameters.
"""

from __future__ import annotations

from tools.manifest_common import FRAMEWORK_DEPS, VALID_GAMES, VALID_LANGUAGES, VALID_FRAMEWORKS, validate_inputs


def generate_manifest(
    name: str,
    game: str,
    language: str,
    framework: str,
    scripts: list[str] | None = None,
    dependencies: list[str] | None = None,
    has_nui: bool = False,
) -> str:
    """Generate fxmanifest.lua content and return it as a string."""

    game = game.strip().lower()
    language = language.strip().lower()
    framework = framework.strip().lower()

    error = validate_inputs(game, language, framework)
    if error:
        return error

    if game == "both":
        games_str = "{ 'gta5', 'rdr3' }"
    else:
        games_str = f"{{ '{game}' }}"

    lines: list[str] = [
        "fx_version 'cerulean'",
        f"games {games_str}",
        "",
        "author 'YourName'",
        f"description '{name}'",
        "version '1.0.0'",
        "",
    ]

    # Dependencies
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

    # Scripts
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
            if "client" in s.lower():
                client_entries.append(f"'{s}'")
            elif "server" in s.lower():
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
