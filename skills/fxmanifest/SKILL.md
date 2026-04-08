---
title: fxmanifest.lua Expert
description: Expert knowledge on writing and editing FiveM/RedM resource manifest files
globs: ["**/fxmanifest.lua"]
---

# fxmanifest.lua Expert

The resource manifest file (`fxmanifest.lua`) defines metadata, dependencies, and file includes for every CFX resource. It replaced the deprecated `__resource.lua` format.

## Required fields

Every manifest must include at minimum:

```lua
fx_version 'cerulean'
games { 'gta5', 'rdr3' }
```

- `fx_version` must always be `'cerulean'` -- this is the current and only supported version
- `games` accepts `'gta5'` (FiveM), `'rdr3'` (RedM), or both: `{ 'gta5', 'rdr3' }`
- Use both when your resource works on either platform; use one if it depends on game-specific natives

## Metadata fields

```lua
author 'YourName'
description 'What this resource does'
version '1.0.0'
```

These are optional but strongly recommended.

## Script declarations

```lua
client_scripts {
    'client/*.lua'
}

server_scripts {
    'server/*.lua'
}

shared_scripts {
    'config.lua'
}
```

- Glob patterns are supported: `'client/*.lua'` matches all Lua files in the client folder
- `shared_scripts` run on both client and server
- Order matters: files are loaded in the order listed

## Lua 5.4

Lua 5.4 is the only runtime as of June 2025. Lua 5.3 has been fully removed from FiveM/RedM.

The `lua54 'yes'` directive is **deprecated and ignored**. Do not include it in new manifests. All Lua scripts automatically run on Lua 5.4 (v5.4.8) regardless of manifest settings.

Key Lua 5.4 features available by default: integers, bitwise operators, `<const>`, `<close>`, and the updated `math.random` algorithm.

## Dependencies

```lua
dependency 'es_extended'
dependency 'oxmysql'
```

Declares that this resource requires another resource to be started first. The server will warn if a dependency is missing.

Multiple dependencies can also be declared in a block:

```lua
dependencies {
    'es_extended',
    'oxmysql'
}
```

## Provide and replace

```lua
provide 'old-resource-name'
replace 'old-resource-name'
```

- `provide` tells the server this resource satisfies the dependency for another resource name
- `replace` prevents the named resource from starting if this one is active

## NUI (web UI)

```lua
ui_page 'html/index.html'

files {
    'html/index.html',
    'html/style.css',
    'html/script.js',
    'html/**'
}
```

- `ui_page` sets the entry point for the in-game browser
- `files` lists assets that need to be sent to the client
- Glob patterns work in `files` blocks too

## Data files

```lua
data_file 'DLC_ITYP_REQUEST' 'stream/*.ytyp'
```

Used for streaming custom game assets (maps, models, textures).

## JavaScript / Node.js

For JS resources, use the same script declarations but with `.js` extensions:

```lua
client_scripts { 'client/*.js' }
server_scripts { 'server/*.js' }
```

To specify the Node.js version for server scripts:

```lua
node_version '22'
```

## C#

C# resources reference compiled DLLs:

```lua
client_scripts { 'Client/ClientMain.net.dll' }
server_scripts { 'Server/ServerMain.net.dll' }
```

## Recommended field order

1. `fx_version`
2. `games`
3. `author`, `description`, `version`
4. `dependency` / `dependencies`
5. `shared_scripts`
6. `client_scripts`
7. `server_scripts`
8. `files`
9. `ui_page`

## Common mistakes

- Using `__resource.lua` instead of `fxmanifest.lua` (deprecated)
- Forgetting `fx_version` (resource will not load)
- Forgetting `games` (resource will not load)
- Listing files that do not exist (silent failure, scripts not loaded)
- Wrong glob pattern (e.g. `client/**` instead of `client/*.lua`)
- Including `lua54 'yes'` (deprecated, ignored -- Lua 5.4 is the only runtime)
