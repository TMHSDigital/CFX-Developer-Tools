"""
Transform native function databases from the upstream runtime.fivem.net
format into the flat array schema used by the MCP server.

Upstream format (natives.json / natives_rdr3.json / natives_cfx.json):
{
  "NAMESPACE": {
    "0xHASH": {
      "name": "NATIVE_NAME",
      "hash": "0xHASH",
      "params": [{"type": "type", "name": "name"}],
      "results": "return_type",
      "description": "...",
      "examples": [...],
      "ns": "NAMESPACE",
      "apiset": "client|server|shared",  (CFX natives only)
      ...
    }
  }
}

Our output format (natives_gta5.json / natives_rdr3.json):
[
  {
    "name": "NativeName",
    "hash": "0xHASH",
    "params": [{"type": "type", "name": "name"}],
    "return_type": "type",
    "description": "...",
    "side": "client|server|shared",
    "category": "NAMESPACE",
    "deprecated": false,
    "examples": null
  }
]
"""

from __future__ import annotations

import json
import os
import re
import html

SERVER_ONLY_NAMESPACES = {"SERVER", "ADMIN"}

CLIENT_HEAVY_NAMESPACES = {
    "GRAPHICS", "HUD", "UI", "CAM", "CONTROLS", "AUDIO",
    "STREAMING", "INTERIOR", "CUTSCENE", "DECISIONEVENT",
    "LOADINGSCREEN", "MOBILE", "RECORDING", "REPLAY",
}

SERVER_SIDE_PATTERNS = re.compile(
    r"^(GetPlayerIdentifier|GetPlayerEndpoint|GetPlayerPing|GetPlayerLastMsg|"
    r"GetNumPlayerIdentifiers|GetNumPlayerTokens|GetPlayerToken|"
    r"GetPlayerFromServerId|GetHostId|"
    r"DropPlayer|TempBanPlayer|GetPlayers|"
    r"TriggerClientEvent|TriggerLatentClientEvent|"
    r"PerformHttpRequest|GetConvar|SetConvar|SetConvarReplicated|"
    r"RegisterServerEvent|WasEventCanceled|CancelEvent|"
    r"GetPlayerMaxArmour|GetPlayerMaxHealth)$",
    re.IGNORECASE,
)

SHARED_PATTERNS = re.compile(
    r"^(GetHashKey|Wait|CreateThread|Citizen.*Thread|"
    r"GetGameTimer|GetCurrentResourceName|GetResourceState|"
    r"RegisterCommand|TriggerEvent|RegisterNetEvent|AddEventHandler|"
    r"GetEntityCoords|GetEntityHeading|GetEntityModel|"
    r"DoesEntityExist|GetEntityHealth|GetPlayerPed|"
    r"GetPlayerName|DeleteEntity|GetNumResources|"
    r"GetResourceByFindIndex|GetInvokingResource|"
    r"IsPlayerPlaying|GetPlayerServerId|"
    r"Exports|AddStateBagChangeHandler|"
    r"GetResourceMetadata|LoadResourceFile|SaveResourceFile)$",
    re.IGNORECASE,
)

CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
HTML_TAG_RE = re.compile(r"<[^>]+>")
DEPRECATED_RE = re.compile(r"\b(deprecated|obsolete)\b", re.IGNORECASE)


def classify_side(name: str, category: str, apiset: str | None = None) -> str:
    """Determine if a native is client, server, or shared."""
    if apiset and apiset in ("client", "server", "shared"):
        return apiset

    if category.upper() in SERVER_ONLY_NAMESPACES:
        return "server"

    if SERVER_SIDE_PATTERNS.match(name):
        return "server"

    if SHARED_PATTERNS.match(name):
        return "shared"

    if category.upper() in CLIENT_HEAVY_NAMESPACES:
        return "client"

    if category.upper() == "CFX":
        return "shared"

    return "client"


def to_pascal_case(name: str) -> str:
    """Convert SCREAMING_SNAKE to PascalCase. Keep hash names as-is."""
    if name.startswith("0x") or name.startswith("_0x"):
        return name
    parts = name.split("_")
    return "".join(p.capitalize() for p in parts if p)


def clean_description(raw: str) -> tuple[str, str | None]:
    """Clean description text: strip HTML, extract code examples.

    Returns (cleaned_description, examples_string_or_None).
    """
    if not raw:
        return ("", None)

    code_blocks = CODE_BLOCK_RE.findall(raw)
    examples = "\n\n".join(code_blocks).strip() if code_blocks else None

    desc = CODE_BLOCK_RE.sub("", raw)
    desc = HTML_TAG_RE.sub("", desc)
    desc = html.unescape(desc)
    desc = re.sub(r"\n{3,}", "\n\n", desc).strip()

    return (desc, examples)


def transform_file(input_path: str, output_path: str, cfx_data: dict | None = None) -> int:
    """Transform upstream natives JSON to our flat schema.

    If cfx_data is provided, CFX natives are merged into the output.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if cfx_data:
        for ns, entries in cfx_data.items():
            if ns not in raw:
                raw[ns] = {}
            raw[ns].update(entries)

    natives: list[dict] = []

    for namespace, entries in raw.items():
        if not isinstance(entries, dict):
            continue

        for hash_key, native in entries.items():
            if not isinstance(native, dict):
                continue

            raw_name = native.get("name", "")
            if not raw_name or raw_name.startswith("_0x"):
                continue

            name = to_pascal_case(raw_name)
            category = namespace.upper()
            native_hash = native.get("hash", hash_key)

            params = []
            for p in native.get("params", []):
                params.append({
                    "name": p.get("name", ""),
                    "type": p.get("type", ""),
                })

            raw_desc = native.get("description", "")
            description, examples_from_desc = clean_description(raw_desc)

            upstream_examples = native.get("examples", [])
            if upstream_examples and isinstance(upstream_examples, list):
                ex_parts = []
                for ex in upstream_examples:
                    if isinstance(ex, dict):
                        lang = ex.get("lang", "")
                        code = ex.get("code", "")
                        if code:
                            ex_parts.append(f"```{lang}\n{code}\n```")
                    elif isinstance(ex, str) and ex.strip():
                        ex_parts.append(ex.strip())
                if ex_parts:
                    examples_from_desc = "\n\n".join(ex_parts)

            apiset = native.get("apiset")
            side = classify_side(name, category, apiset)

            return_type = native.get("results", native.get("return_type", "void"))
            if return_type is None:
                return_type = "void"

            deprecated = bool(DEPRECATED_RE.search(raw_desc))

            entry = {
                "name": name,
                "hash": native_hash,
                "params": params,
                "return_type": return_type,
                "description": description,
                "side": side,
                "category": category,
                "deprecated": deprecated,
                "examples": examples_from_desc,
            }

            natives.append(entry)

    natives.sort(key=lambda n: (n["category"], n["name"]))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(natives, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return len(natives)


def main() -> None:
    gta5_in = "/tmp/gta5_raw.json"
    rdr3_in = "/tmp/rdr3_raw.json"
    cfx_in = "/tmp/cfx_raw.json"
    gta5_out = "mcp-server/data/natives_gta5.json"
    rdr3_out = "mcp-server/data/natives_rdr3.json"

    cfx_data = None
    if os.path.exists(cfx_in):
        with open(cfx_in, "r", encoding="utf-8") as f:
            cfx_data = json.load(f)
        cfx_total = sum(len(v) for v in cfx_data.values())
        print(f"CFX: loaded {cfx_total} platform natives")

    if os.path.exists(gta5_in):
        count = transform_file(gta5_in, gta5_out, cfx_data)
        print(f"GTA5: transformed {count} natives")
    else:
        print("GTA5 raw file not found, skipping")

    if os.path.exists(rdr3_in):
        count = transform_file(rdr3_in, rdr3_out, cfx_data)
        print(f"RDR3: transformed {count} natives")
    else:
        print("RDR3 raw file not found, skipping")


if __name__ == "__main__":
    main()
