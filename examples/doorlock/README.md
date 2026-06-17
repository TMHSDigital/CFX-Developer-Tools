# doorlock

A minimal FiveM example resource that demonstrates **replicated StateBags** (the
repo's `state-bags` skill) for server-authoritative door locking.

## What it demonstrates

- Storing shared state in `GlobalState`, a replicated StateBag that the server
  owns and every client reads.
- Seeding `GlobalState` from config on resource start so the value exists before
  any client reads it and late joiners get it automatically.
- Reacting to state changes with `AddStateBagChangeHandler(...)` instead of
  polling, so the resource idles at 0.00ms.
- A server-authoritative flow: clients only request a toggle, and the server
  validates the id, validates range with `GetEntityCoords(GetPlayerPed(src))`,
  and applies a per-player anti-spam cooldown before flipping the state.
- A `RegisterCommand` + `RegisterKeyMapping` keybind (rebindable, no per-frame
  poll).
- An ESX / QBCore notification bridge with a standalone fallback.

## Install

1. Copy the `doorlock` folder into your server's `resources` directory.
2. Add `ensure doorlock` to your `server.cfg`.
3. Edit `config.lua` to set your door `coords` (and optional `doorHash`).
4. Restart the server (or `ensure doorlock`) and walk up to a door, then press
   the toggle key (default `E`).

No database or credentials required.

## State-bag keys used

Each configured door mirrors its lock state into one replicated GlobalState key:

| Key | Type | Owner | Meaning |
|-----|------|-------|---------|
| `doorlock:<id>` | boolean | server | `true` = locked, `false` = unlocked |

For the default config that is `doorlock:ld_front` and `doorlock:ld_back`.

Read a value anywhere on the client or server with:

```lua
local locked = GlobalState['doorlock:ld_front']
```

Only the server writes these keys (in `server/main.lua`). Clients never write
them; they call the `doorlock:server:toggle` net event instead.

## How to add doors

Append an entry to `Config.Doors` in `config.lua`:

```lua
{
    id       = 'ld_garage',                 -- unique; becomes 'doorlock:ld_garage'
    label    = 'Garage Door',
    doorHash = nil,                         -- or a hash registered via AddDoorToSystem
    coords   = vec3(-805.0, 172.0, 76.74),
    distance = 2.0,
    locked   = true,                        -- initial state seeded into GlobalState
},
```

Restart the resource. The new door's GlobalState key is seeded on start and a
change handler is registered for it automatically. If you set `doorHash` to a
door registered with the GTA door system (via `AddDoorToSystem`), the example
will also drive the physical door with `DoorSystemSetDoorState`.
