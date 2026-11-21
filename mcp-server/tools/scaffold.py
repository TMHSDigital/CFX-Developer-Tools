"""
Resource scaffolding tool.

Creates a new FiveM/RedM resource directory with boilerplate files
based on the chosen language and framework.
"""

from __future__ import annotations

import os
import json

from tools.manifest_common import (
    FRAMEWORK_DEPS,
    FRAMEWORK_LUA_EXTRAS,
    RESOURCE_NAME_RE,
    csharp_csproj,
    csharp_dll_paths,
    games_block,
    lua_string,
    validate_inputs,
    read_workspace_context,
)

# Optional root directory for scaffolded resources when the caller gives
# neither output_path nor workspace_path.
SCAFFOLD_ROOT_ENV = "CFX_SCAFFOLD_ROOT"

FRAMEWORK_INIT_CLIENT = {
    "esx": "ESX = exports['es_extended']:getSharedObject()\n",
    "qbcore": "QBCore = exports['qb-core']:GetCoreObject()\n",
    "qbox": "local QBX = exports['qbx_core']\n",
    "oxcore": "local Ox = require '@ox_core.lib.init'\n",
    "vorp": "local VORPcore = exports.vorp_core:GetCore()\n",
    "rsg": "RSGCore = exports['rsg-core']:GetCoreObject()\n",
    "standalone": "",
}

FRAMEWORK_INIT_SERVER = {
    "esx": "ESX = exports['es_extended']:getSharedObject()\n",
    "qbcore": "QBCore = exports['qb-core']:GetCoreObject()\n",
    "qbox": "local QBX = exports['qbx_core']\n",
    "oxcore": "local Ox = require '@ox_core.lib.init'\n",
    "vorp": "local VORPcore = exports.vorp_core:GetCore()\n",
    "rsg": "RSGCore = exports['rsg-core']:GetCoreObject()\n",
    "standalone": "",
}


def scaffold_resource(
    name: str,
    game: str,
    language: str,
    framework: str,
    workspace_path: str | None = None,
    output_path: str | None = None,
    overwrite: bool = False,
) -> str:
    """Create resource files and return a summary of what was created.

    The resource directory is created at ``<base>/<name>``, where ``base`` is
    ``output_path``, else ``workspace_path``, else the ``CFX_SCAFFOLD_ROOT``
    environment variable, else the current working directory. Existing
    non-empty directories are never written into unless ``overwrite`` is True.
    """

    name = (name or "").strip().lower().replace(" ", "-")
    game = (game or "").strip().lower()
    language = (language or "").strip().lower()
    framework = (framework or "").strip().lower()

    if not RESOURCE_NAME_RE.match(name):
        return (
            f"Error: invalid resource name '{name}'. Use 1-64 characters: "
            "lowercase letters, digits, '-' or '_', starting with a letter or digit."
        )

    error = validate_inputs(game, language, framework)
    if error:
        return error

    base_dir = output_path or workspace_path or os.environ.get(SCAFFOLD_ROOT_ENV) or os.getcwd()
    base_dir = os.path.realpath(os.path.expanduser(base_dir))
    if not os.path.isdir(base_dir):
        return f"Error: output directory does not exist: {base_dir}"

    target = os.path.realpath(os.path.join(base_dir, name))
    if os.path.commonpath([base_dir, target]) != base_dir or target == base_dir:
        return f"Error: resource path escapes the output directory: {target}"

    if os.path.isdir(target) and os.listdir(target) and not overwrite:
        return (
            f"Error: {target} already exists and is not empty. "
            "Choose another name or pass overwrite=True to replace the generated files."
        )
    if os.path.exists(target) and not os.path.isdir(target):
        return f"Error: {target} exists and is not a directory."

    author = "YourName"
    if workspace_path:
        ctx = read_workspace_context(workspace_path)
        author = ctx.get("author", author)

    games_str = games_block(game)
    files_created: list[str] = []
    mode = "w" if overwrite else "x"

    base = target
    os.makedirs(base, exist_ok=True)

    try:
        manifest = _build_manifest(name, games_str, language, framework, author)
        _write(base, "fxmanifest.lua", manifest, files_created, mode)

        if language == "lua":
            _scaffold_lua(base, framework, files_created, mode)
        elif language == "javascript":
            _scaffold_js(base, files_created, mode)
        elif language == "csharp":
            _scaffold_csharp(base, name, files_created, mode)
    except FileExistsError as exc:
        return f"Error: refusing to overwrite existing file {exc.filename}. Pass overwrite=True to replace it."

    summary = f"Scaffolded resource '{name}' ({language}, {framework}, {game}) at {base}.\n"
    summary += f"Files created ({len(files_created)}):\n"
    for f in files_created:
        summary += f"  - {f}\n"

    return summary


def _build_manifest(
    name: str,
    games_str: str,
    language: str,
    framework: str,
    author: str = "YourName",
) -> str:
    lines = [
        "fx_version 'cerulean'",
        f"games {games_str}",
        "",
        f"author '{lua_string(author)}'",
        f"description '{lua_string(name)}'",
        "version '1.0.0'",
        "",
    ]

    extras = FRAMEWORK_LUA_EXTRAS.get(framework, {}) if language == "lua" else {}
    deps = list(extras.get("dependencies", []))
    dep = FRAMEWORK_DEPS.get(framework)
    if dep:
        deps.append(dep)
    for d in deps:
        lines.append(f"dependency '{d}'")
    if deps:
        lines.append("")

    if language == "lua":
        lines.append("shared_scripts {")
        for script in extras.get("shared_scripts", []):
            lines.append(f"    '{script}',")
        lines.append("    'config.lua'")
        lines.append("}")
        lines.append("")
        lines.append("client_scripts {")
        lines.append("    'client/*.lua'")
        lines.append("}")
        lines.append("")
        lines.append("server_scripts {")
        lines.append("    'server/*.lua'")
        lines.append("}")
    elif language == "javascript":
        lines.append("node_version '22'")
        lines.append("")
        lines.append("client_scripts {")
        lines.append("    'client/*.js'")
        lines.append("}")
        lines.append("")
        lines.append("server_scripts {")
        lines.append("    'server/*.js'")
        lines.append("}")
    elif language == "csharp":
        client_dll, server_dll = csharp_dll_paths(name)
        lines.append("client_scripts {")
        lines.append(f"    '{client_dll}'")
        lines.append("}")
        lines.append("")
        lines.append("server_scripts {")
        lines.append(f"    '{server_dll}'")
        lines.append("}")

    return "\n".join(lines) + "\n"


def _scaffold_lua(
    base: str,
    framework: str,
    files_created: list[str],
    mode: str = "w",
) -> None:
    _write(base, "config.lua", "Config = {}\n\nConfig.Debug = false\n", files_created, mode)

    client_init = FRAMEWORK_INIT_CLIENT.get(framework, "")
    client = client_init + """
CreateThread(function()
    while true do
        Wait(1000)
        -- Main client loop
    end
end)
"""
    os.makedirs(os.path.join(base, "client"), exist_ok=True)
    _write(base, "client/main.lua", client, files_created, mode)

    server_init = FRAMEWORK_INIT_SERVER.get(framework, "")
    server = server_init + """
AddEventHandler('onResourceStart', function(resourceName)
    if GetCurrentResourceName() ~= resourceName then return end
    print(resourceName .. ' started')
end)
"""
    os.makedirs(os.path.join(base, "server"), exist_ok=True)
    _write(base, "server/main.lua", server, files_created, mode)


def _scaffold_js(base: str, files_created: list[str], mode: str = "w") -> None:
    pkg = json.dumps(
        {
            "name": os.path.basename(base),
            "version": "1.0.0",
            "description": "FiveM/RedM JavaScript resource",
            "private": True,
            "devDependencies": {
                "@citizenfx/client": "^2.0.38781-1",
                "@citizenfx/server": "^2.0.38781-1",
            },
        },
        indent=2,
    )
    _write(base, "package.json", pkg + "\n", files_created, mode)

    os.makedirs(os.path.join(base, "client"), exist_ok=True)
    _write(
        base,
        "client/main.js",
        "// FiveM's JS runtime has no built-in Delay; define it once per file.\n"
        "const Delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));\n\n"
        "setTick(async () => {\n    await Delay(1000);\n    // Main client loop\n});\n",
        files_created,
        mode,
    )

    os.makedirs(os.path.join(base, "server"), exist_ok=True)
    _write(
        base,
        "server/main.js",
        "on('onResourceStart', (resourceName) => {\n"
        "    if (GetCurrentResourceName() !== resourceName) return;\n"
        "    console.log(`${resourceName} started`);\n"
        "});\n",
        files_created,
        mode,
    )


def _scaffold_csharp(base: str, name: str, files_created: list[str], mode: str = "w") -> None:
    # One project per side: the client and server CitizenFX.Core assemblies
    # differ, and each project builds dist/<name>.<Side>.net.dll, which is
    # what the manifest lists (see manifest_common.csharp_dll_paths).
    os.makedirs(os.path.join(base, "Client"), exist_ok=True)
    _write(base, f"Client/{name}.Client.csproj", csharp_csproj(name, "Client"), files_created, mode)
    client_cs = """using System.Threading.Tasks;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class ClientMain : BaseScript
{
    public ClientMain() { Tick += OnTick; }

    private async Task OnTick()
    {
        await Delay(1000);
        // Main client loop
    }
}
"""
    _write(base, "Client/ClientMain.cs", client_cs, files_created, mode)

    os.makedirs(os.path.join(base, "Server"), exist_ok=True)
    _write(base, f"Server/{name}.Server.csproj", csharp_csproj(name, "Server"), files_created, mode)
    server_cs = """using System;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class ServerMain : BaseScript
{
    public ServerMain()
    {
        EventHandlers["onResourceStart"] += new Action<string>(OnResourceStart);
    }

    private void OnResourceStart(string resourceName)
    {
        if (GetCurrentResourceName() != resourceName) return;
        Debug.WriteLine($"{resourceName} started");
    }
}
"""
    _write(base, "Server/ServerMain.cs", server_cs, files_created, mode)


def _write(
    base: str,
    path: str,
    content: str,
    files_created: list[str],
    mode: str = "w",
) -> None:
    full = os.path.join(base, path)
    with open(full, mode, encoding="utf-8") as f:
        f.write(content)
    files_created.append(path)
