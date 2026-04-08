"""
Resource scaffolding tool.

Creates a new FiveM/RedM resource directory with boilerplate files
based on the chosen language and framework.
"""

from __future__ import annotations

import os
import json

from tools.manifest_common import FRAMEWORK_DEPS, games_block, validate_inputs, read_workspace_context

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
) -> str:
    """Create resource files and return a summary of what was created."""

    name = name.strip().lower().replace(" ", "-")
    game = game.strip().lower()
    language = language.strip().lower()
    framework = framework.strip().lower()

    error = validate_inputs(game, language, framework)
    if error:
        return error

    author = "YourName"
    if workspace_path:
        ctx = read_workspace_context(workspace_path)
        author = ctx.get("author", author)

    games_str = games_block(game)
    files_created: list[str] = []

    base = name

    os.makedirs(base, exist_ok=True)

    manifest = _build_manifest(name, games_str, language, framework, author)
    _write(base, "fxmanifest.lua", manifest, files_created)

    if language == "lua":
        _scaffold_lua(base, framework, files_created)
    elif language == "javascript":
        _scaffold_js(base, files_created)
    elif language == "csharp":
        _scaffold_csharp(base, name, files_created)

    summary = f"Scaffolded resource '{name}' ({language}, {framework}, {game}).\n"
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
        f"author '{author}'",
        f"description '{name}'",
        "version '1.0.0'",
        "",
    ]

    dep = FRAMEWORK_DEPS.get(framework)
    if dep:
        lines.append(f"dependency '{dep}'")
        lines.append("")

    if language == "lua":
        lines.append("shared_scripts {")
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
        lines.append("client_scripts {")
        lines.append("    'Client/ClientMain.net.dll'")
        lines.append("}")
        lines.append("")
        lines.append("server_scripts {")
        lines.append("    'Server/ServerMain.net.dll'")
        lines.append("}")

    return "\n".join(lines) + "\n"


def _scaffold_lua(
    base: str,
    framework: str,
    files_created: list[str],
) -> None:
    _write(base, "config.lua", "Config = {}\n\nConfig.Debug = false\n", files_created)

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
    _write(base, "client/main.lua", client, files_created)

    server_init = FRAMEWORK_INIT_SERVER.get(framework, "")
    server = server_init + """
AddEventHandler('onResourceStart', function(resourceName)
    if GetCurrentResourceName() ~= resourceName then return end
    print(resourceName .. ' started')
end)
"""
    os.makedirs(os.path.join(base, "server"), exist_ok=True)
    _write(base, "server/main.lua", server, files_created)


def _scaffold_js(base: str, files_created: list[str]) -> None:
    pkg = json.dumps(
        {
            "name": os.path.basename(base),
            "version": "1.0.0",
            "description": "FiveM/RedM JavaScript resource",
            "private": True,
            "devDependencies": {
                "@citizenfx/client": "latest",
                "@citizenfx/server": "latest",
            },
        },
        indent=2,
    )
    _write(base, "package.json", pkg + "\n", files_created)

    os.makedirs(os.path.join(base, "client"), exist_ok=True)
    _write(
        base,
        "client/main.js",
        "setTick(async () => {\n    await Delay(1000);\n    // Main client loop\n});\n",
        files_created,
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
    )


def _scaffold_csharp(base: str, name: str, files_created: list[str]) -> None:
    csproj = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="CitizenFX.Core">
      <Private>false</Private>
    </Reference>
  </ItemGroup>
</Project>
"""
    _write(base, f"{name}.csproj", csproj, files_created)

    os.makedirs(os.path.join(base, "Client"), exist_ok=True)
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
    _write(base, "Client/ClientMain.cs", client_cs, files_created)

    os.makedirs(os.path.join(base, "Server"), exist_ok=True)
    server_cs = """using System;
using CitizenFX.Core;

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
    _write(base, "Server/ServerMain.cs", server_cs, files_created)


def _write(base: str, path: str, content: str, files_created: list[str]) -> None:
    full = os.path.join(base, path)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    files_created.append(path)
