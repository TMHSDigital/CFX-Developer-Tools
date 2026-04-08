---
title: Resource Scaffolding
description: Guide the AI agent through creating a new FiveM or RedM resource from scratch
globs: ["**/fxmanifest.lua"]
---

# Resource Scaffolding

This skill walks through creating a new FiveM or RedM resource with the correct directory structure, manifest, and boilerplate code.

## Gather requirements

Before generating any files, ask the user for:

1. **Resource name** - lowercase, alphanumeric with hyphens (e.g. `my-resource`)
2. **Game target** - `gta5` (FiveM), `rdr3` (RedM), or both
3. **Language runtime** - Lua, JavaScript, or C#
4. **Framework** - ESX, QBCore, Qbox, ox_core, VORP (RedM), RSG (RedM), or standalone (none)
5. **Database needed?** - yes/no (determines oxmysql dependency)

## Directory structure

Generate the following structure based on language choice:

### Lua (default)

```
resource-name/
  fxmanifest.lua
  config.lua
  client/
    main.lua
  server/
    main.lua
  README.md
```

### JavaScript

```
resource-name/
  fxmanifest.lua
  package.json
  client/
    main.js
  server/
    main.js
  README.md
```

### C#

```
resource-name/
  fxmanifest.lua
  MyResource.csproj
  Client/
    ClientMain.cs
  Server/
    ServerMain.cs
  README.md
```

## fxmanifest.lua generation

Always use this base structure:

```lua
fx_version 'cerulean'
games { 'gta5' }          -- or { 'rdr3' } or { 'gta5', 'rdr3' }

author 'AuthorName'
description 'Resource description'
version '1.0.0'
```

Note: Do not add `lua54 'yes'` -- it is deprecated and ignored. All scripts run on Lua 5.4 by default.

### Script declarations by language

**Lua:**
```lua
shared_scripts {
    'config.lua'
}

client_scripts {
    'client/*.lua'
}

server_scripts {
    'server/*.lua'
}
```

**JavaScript:**
```lua
client_scripts {
    'client/*.js'
}

server_scripts {
    'server/*.js'
}
```

**C#:**
```lua
client_scripts {
    'Client/ClientMain.net.dll'
}

server_scripts {
    'Server/ServerMain.net.dll'
}
```

### Framework dependencies

Add the correct `dependency` directive based on the chosen framework:

- **ESX**: `dependency 'es_extended'`
- **QBCore**: `dependency 'qb-core'`
- **Qbox**: `dependency 'qbx_core'`
- **ox_core**: `dependency 'ox_core'`
- **VORP** (RedM): `dependency 'vorp_core'`
- **RSG** (RedM): `dependency 'rsg-core'`
- **Standalone**: no dependency directive

### Database dependency

If the user needs database access, add to `server_scripts`:

```lua
server_scripts {
    '@oxmysql/lib/MySQL.lua',
    'server/*.lua'
}
```

## Starter script content

### Lua client boilerplate

```lua
local Config = Config or {}

CreateThread(function()
    while true do
        Wait(1000)
        -- Main client loop
    end
end)
```

### Lua server boilerplate

```lua
local Config = Config or {}

RegisterNetEvent('resourceName:serverEvent', function(data)
    local source = source
    -- Validate source and handle event
end)
```

### Config file

```lua
Config = {}

Config.Debug = false
-- Add configurable values here
```

## Post-generation checklist

After scaffolding, remind the user to:

1. Update the `author` field in fxmanifest.lua
2. Update the `description` field
3. Add the resource folder to their server's `resources/` directory
4. Add `ensure resource-name` to their server.cfg
5. Customize config.lua with their settings
