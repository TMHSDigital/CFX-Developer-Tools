---
title: Framework Detection
description: Detect which framework a project is using and adapt code generation accordingly
globs: ["**/fxmanifest.lua", "**/*.lua"]
---

# Framework Detection

CFX resources may target a specific framework (ESX, QBCore, ox_core) or run standalone. This skill detects which one is in use and adapts generated code accordingly.

## Detection logic

Scan the workspace for these indicators, in priority order:

### 1. Check fxmanifest.lua for dependency directives

```lua
dependency 'es_extended'    --> ESX
dependency 'qb-core'        --> QBCore
dependency 'ox_core'        --> ox_core
```

### 2. Check script imports for framework references

```lua
'@es_extended/...'          --> ESX
'@qb-core/...'              --> QBCore
'@ox_core/...'              --> ox_core
```

### 3. Check Lua files for framework initialization patterns

```lua
exports['es_extended']:getSharedObject()   --> ESX
exports['qb-core']:GetCoreObject()         --> QBCore
require '@ox_core.lib.init'                --> ox_core
```

### 4. No matches

If none of the above patterns are found, assume **standalone** (no framework).

## Framework initialization patterns

### ESX

```lua
-- Recommended (modern ESX)
ESX = exports['es_extended']:getSharedObject()

-- Legacy (older ESX versions, still works)
ESX = nil
TriggerEvent('esx:getSharedObject', function(obj) ESX = obj end)
```

Common ESX patterns:
```lua
-- Get player data
local xPlayer = ESX.GetPlayerData()          -- client
local xPlayer = ESX.GetPlayerFromId(source)  -- server

-- Show notification
ESX.ShowNotification('Message here')

-- Register a usable item (server)
ESX.RegisterUsableItem('itemname', function(source)
    local xPlayer = ESX.GetPlayerFromId(source)
    -- item logic
end)
```

### QBCore

```lua
QBCore = exports['qb-core']:GetCoreObject()
```

Common QBCore patterns:
```lua
-- Get player data
local PlayerData = QBCore.Functions.GetPlayerData()          -- client
local Player = QBCore.Functions.GetPlayer(source)            -- server

-- Show notification
QBCore.Functions.Notify('Message here', 'success')

-- Register a usable item (server)
QBCore.Functions.CreateUseableItem('itemname', function(source, item)
    local Player = QBCore.Functions.GetPlayer(source)
    -- item logic
end)

-- Callback (client request, server response)
QBCore.Functions.TriggerCallback('myResource:getData', function(result)
    -- handle result
end)
```

### ox_core

```lua
local Ox = require '@ox_core.lib.init'
```

ox_core uses a module system with `require`:
```lua
local player = Ox.GetPlayer(source)         -- server
local player = Ox.GetPlayer()               -- client (self)
```

ox_core resources typically also use ox_lib for utilities:
```lua
local lib = require '@ox_lib.init'
```

## Adapting generated code

When generating code, use the detected framework to:

1. **Add the correct dependency** in fxmanifest.lua
2. **Use the correct initialization** at the top of client and server scripts
3. **Use framework-specific APIs** for player data, notifications, items, and callbacks
4. **Match the project's existing patterns** -- if the codebase uses ESX legacy style, do not switch to modern style mid-resource

## When multiple frameworks are detected

This should not happen in a well-structured resource. If it does, warn the user and ask which framework they intend to use. A single resource should only depend on one framework.
