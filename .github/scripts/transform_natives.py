"""
Transform native function databases from the citizenfx/natives upstream
format into the flat array schema used by the MCP server.

Upstream format (GTA5.json / RDR3.json):
{
  "NAMESPACE": {
    "0xHASH": {
      "name": "NATIVE_NAME",
      "params": [{"type": "type", "name": "name"}],
      "return_type": "type",
      "description": "...",
      ...
    }
  }
}

Our format (natives_gta5.json / natives_rdr3.json):
[
  {
    "name": "NativeName",
    "params": [{"type": "type", "name": "name"}],
    "return_type": "type",
    "description": "...",
    "side": "client|server|shared",
    "category": "NAMESPACE"
  }
]
"""

from __future__ import annotations

import json
import os
import re

SERVER_ONLY_NAMESPACES = {"SERVER", "ADMIN"}

CLIENT_HEAVY_NAMESPACES = {
    "GRAPHICS", "HUD", "UI", "CAM", "CONTROLS", "AUDIO",
    "STREAMING", "INTERIOR", "CUTSCENE", "DECISIONEVENT",
}

SERVER_SIDE_PATTERNS = re.compile(
    r"(GetPlayerIdentifier|GetPlayerEndpoint|GetPlayerPing|GetPlayerLastMsg|"
    r"GetNumPlayerIdentifiers|GetNumPlayerTokens|GetPlayerToken|"
    r"DropPlayer|TempBanPlayer|GetPlayers|"
    r"TriggerClientEvent|TriggerLatentClientEvent|"
    r"PerformHttpRequest|GetConvar|SetConvar|"
    r"RegisterServerEvent|WasEventCanceled|CancelEvent)",
    re.IGNORECASE,
)

SHARED_PATTERNS = re.compile(
    r"(GetHashKey|Wait|CreateThread|GetGameTimer|"
    r"GetCurrentResourceName|GetResourceState|"
    r"RegisterCommand|TriggerEvent|RegisterNetEvent|"
    r"GetEntityCoords|GetEntityHeading|GetEntityModel|"
    r"DoesEntityExist|GetEntityHealth|GetPlayerPed|"
    r"GetPlayerName|DeleteEntity|GetNumResources|"
    r"GetResourceByFindIndex)",
    re.IGNORECASE,
)


def classify_side(name: str, category: str) -> str:
    """Determine if a native is client, server, or shared."""
    if category.upper() in SERVER_ONLY_NAMESPACES:
        return "server"

    if SERVER_SIDE_PATTERNS.search(name):
        return "server"

    if SHARED_PATTERNS.search(name):
        return "shared"

    if category.upper() in CLIENT_HEAVY_NAMESPACES:
        return "client"

    if category.upper() == "CFX":
        return "shared"

    return "client"


def to_pascal_case(name: str) -> str:
    """Convert SCREAMING_SNAKE or _0xHASH to PascalCase if possible."""
    if name.startswith("0x") or name.startswith("_0x"):
        return name
    parts = name.split("_")
    return "".join(p.capitalize() for p in parts if p)


def transform_file(input_path: str, output_path: str) -> int:
    """Transform upstream natives JSON to our flat schema."""
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    natives: list[dict] = []

    for namespace, entries in raw.items():
        if not isinstance(entries, dict):
            continue

        for _hash, native in entries.items():
            if not isinstance(native, dict):
                continue

            raw_name = native.get("name", "")
            if not raw_name or raw_name.startswith("_0x"):
                continue

            name = to_pascal_case(raw_name)
            category = namespace.upper()

            params = []
            for p in native.get("params", []):
                params.append({
                    "name": p.get("name", ""),
                    "type": p.get("type", ""),
                })

            description = native.get("description", "")
            if description:
                description = description.split("\n")[0].strip()
                if len(description) > 200:
                    description = description[:197] + "..."

            entry = {
                "name": name,
                "params": params,
                "return_type": native.get("return_type", "void"),
                "description": description,
                "side": classify_side(name, category),
                "category": category,
            }

            natives.append(entry)

    natives.sort(key=lambda n: (n["category"], n["name"]))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(natives, f, indent=2, ensure_ascii=False)

    return len(natives)


def main() -> None:
    gta5_in = "/tmp/gta5_raw.json"
    rdr3_in = "/tmp/rdr3_raw.json"
    gta5_out = "mcp-server/data/natives_gta5.json"
    rdr3_out = "mcp-server/data/natives_rdr3.json"

    if os.path.exists(gta5_in):
        count = transform_file(gta5_in, gta5_out)
        print(f"GTA5: transformed {count} natives")
    else:
        print("GTA5 raw file not found, skipping")

    if os.path.exists(rdr3_in):
        count = transform_file(rdr3_in, rdr3_out)
        print(f"RDR3: transformed {count} natives")
    else:
        print("RDR3 raw file not found, skipping")


if __name__ == "__main__":
    main()
