---
title: Native Function Lookup
description: Help the AI agent find and correctly use FiveM and RedM native functions
globs: ["**/*.lua", "**/*.js", "**/*.cs"]
standards-version: 1.7.0
---

# Native Function Lookup

Natives are built-in functions provided by the GTA5/RDR3 game engine and the CFX platform. They expose game functionality like entity management, player data, vehicle spawning, UI rendering, and more.

## Reference

- GTA5 (FiveM) natives: https://docs.fivem.net/natives/
- RDR3 (RedM) natives: https://rdr3natives.com/
- CFX natives (shared platform functions): included in both native references above

## Calling conventions

Natives use the same function names across all three runtimes, but the syntax differs:

### Lua

```lua
local coords = GetEntityCoords(playerPed)
local vehicle = CreateVehicle(modelHash, x, y, z, heading, true, true)
```

### JavaScript

```javascript
const coords = GetEntityCoords(playerPed, false);
const vehicle = CreateVehicle(modelHash, x, y, z, heading, true, true);
```

### C#

```csharp
Vector3 coords = API.GetEntityCoords(playerPed, false);
int vehicle = API.CreateVehicle((uint)modelHash, x, y, z, heading, true, true);
```

In C#, all natives are called through the `API` class from `CitizenFX.Core`.

## Client vs server vs shared

- **Client-only natives**: rendering, input, camera, HUD, most entity manipulation
- **Server-only natives**: player management, server info, ACE permissions
- **Shared natives**: some entity getters, math, hash functions

Calling a server native on the client (or vice versa) will error silently or crash. Always check the native reference for which side it runs on.

## Commonly used natives

### Player and ped

| Native | Side | Description |
|--------|------|-------------|
| `PlayerPedId()` | client | Get the local player's ped entity |
| `GetPlayerPed(serverId)` | server | Get a player's ped by server ID |
| `GetEntityCoords(entity)` | shared | Get position as vector3 |
| `GetPlayerName(playerId)` | shared | Get player name |
| `GetPlayerIdentifiers(playerId)` | server | Get all identifiers (license, steam, discord, etc.) |

### Vehicles

| Native | Side | Description |
|--------|------|-------------|
| `CreateVehicle(hash, x, y, z, heading, isNetwork, netMissionEntity)` | client | Spawn a vehicle |
| `SetEntityHeading(entity, heading)` | shared | Set entity rotation |
| `DeleteEntity(entity)` | shared | Delete an entity |
| `GetVehiclePedIsIn(ped, lastVehicle)` | client | Get the vehicle a ped is in |

### Commands and events

| Native | Side | Description |
|--------|------|-------------|
| `RegisterCommand(name, handler, restricted)` | shared | Register a chat command |
| `TriggerServerEvent(name, ...)` | client | Send event to server |
| `TriggerClientEvent(name, target, ...)` | server | Send event to a client |
| `TriggerEvent(name, ...)` | shared | Trigger a local event |

### Utility

| Native | Side | Description |
|--------|------|-------------|
| `GetHashKey(string)` | shared | Hash a string at runtime |
| `Wait(ms)` | shared | Yield the current thread |
| `GetGameTimer()` | shared | Milliseconds since game start |
| `GetResourceState(name)` | shared | Check if a resource is started |

## Hash optimization

In Lua, use backtick syntax for compile-time hashing of string literals:

```lua
-- Good: compile-time hash (faster)
local hash = `adder`

-- Bad: runtime hash (slower)
local hash = GetHashKey('adder')
```

Backtick hashing only works with literal strings, not variables. For dynamic strings, `GetHashKey()` is still required.

## Tips

- Always check the return type; some natives return vectors, others return individual x/y/z values
- Many natives that accept a "player" parameter expect different IDs on client (local index) vs server (server ID / source)
- Use the MCP `lookup_native` tool to search by name or keyword if you are unsure which native to use
- Deprecated natives still work but may be removed; prefer the replacement listed in the docs
