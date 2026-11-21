---
title: State Bags
description: Modern data synchronization using State Bags instead of TriggerClientEvent patterns
globs: ["**/*.lua", "**/*.js", "**/*.cs"]
standards-version: 1.10.0
---

# State Bags

State Bags are the modern way to synchronize data across clients and server in FiveM/RedM. They replace many traditional `TriggerClientEvent` patterns for syncing persistent entity/player data. Requires OneSync.

## Three types of State Bags

### Entity State

Attach key-value pairs to any networked entity (vehicle, ped, object).

```lua
-- Server: set state on a vehicle (replicated to all clients by default)
local vehicle = GetVehiclePedIsIn(GetPlayerPed(source), false)
Entity(vehicle).state.fuel = 100

-- Client: read state
local vehicle = GetVehiclePedIsIn(PlayerPedId(), false)
local fuel = Entity(vehicle).state.fuel
```

### Player State

Attach key-value pairs to a player. The server can read/write any player's state. A client can also write its own player bag (and bags of entities it owns), and those writes replicate, so treat player-bag values as display data, not as proof of anything (see Security).

```lua
-- Server: set player state
Player(source).state.job = 'police'
Player(source).state.onDuty = true

-- Client: read own state
local myJob = LocalPlayer.state.job

-- Client: read another player's state (if replicated)
local otherJob = Player(serverId).state.job
```

### Global State

Server-wide state. Server sets, all clients can read.

```lua
-- Server: set global state
GlobalState.weather = 'RAIN'
GlobalState.serverLocked = false

-- Client: read global state
local weather = GlobalState.weather
```

Clients cannot write to GlobalState.

## Replication rules

By default:
- Server-set state **is replicated** to all clients
- Client-set state **is not replicated** to other clients

Override replication with `:set()`:

```lua
-- Server: set without replicating (server-only data)
Entity(vehicle).state:set('internalId', 12345, false)

-- Client: set with replication (use carefully)
Entity(vehicle).state:set('customColor', '#ff0000', true)
```

## Change handlers

Listen for state changes with `AddStateBagChangeHandler`:

```lua
AddStateBagChangeHandler('fuel', nil, function(bagName, key, value, _reserved, replicated)
    local entity = GetEntityFromStateBagName(bagName)
    if entity == 0 then return end

    -- value is the new fuel level
    if value and value < 10 then
        -- low fuel warning
    end
end)
```

Parameters:
- `bagName` -- identifies the bag (e.g., `"entity:12345"` or `"player:1"`)
- `key` -- the state key that changed
- `value` -- the new value
- `_reserved` -- unused, always 0
- `replicated` -- true if change came from the network

### Scoped handlers

```lua
-- Listen for changes to 'fuel' on ANY entity
AddStateBagChangeHandler('fuel', nil, handler)

-- Listen for ANY key change on a specific entity bag
AddStateBagChangeHandler(nil, 'entity:12345', handler)

-- Listen for 'job' changes on ANY player
AddStateBagChangeHandler('job', nil, handler)
```

### Getting entity from bag name

```lua
local entity = GetEntityFromStateBagName(bagName)
if entity == 0 then return end  -- entity doesn't exist locally
```

## JavaScript patterns

```javascript
// Server: set entity state
const vehicle = GetVehiclePedIsIn(GetPlayerPed(source), false);
Entity(vehicle).state.set('fuel', 100, true);

// Client: read
const fuel = Entity(vehicle).state.fuel;

// Player state (server)
Player(source).state.set('job', 'police', true);

// Global state (server)
GlobalState.set('weather', 'RAIN', true);

// Change handler (client or server)
AddStateBagChangeHandler('fuel', null, (bagName, key, value, _reserved, replicated) => {
    const entity = GetEntityFromStateBagName(bagName);
    if (entity === 0) return;
    // handle change
});
```

## When to use State Bags vs Events

| Use case | Use State Bags | Use Events |
|----------|---------------|------------|
| Sync persistent entity data (fuel, damage, color) | Yes | No |
| Sync player status (job, duty, handcuffed) | Yes | No |
| Server-wide config (weather, locked) | Yes (GlobalState) | No |
| One-time actions (play sound, show notification) | No | Yes |
| Request/response patterns | No | Yes |
| Data that changes every frame | No | Yes (or natives) |

**Rule of thumb:** If the data represents *state* that persists while the entity exists, use State Bags. If it's a *command* or *event* that happens once, use events.

## Security

- Clients can write keys on bags they own (their own player bag and entities they own), and those writes replicate. A value set by the server can be overwritten by the owning client.
- Keep authority data (job, duty, permissions, money, ownership) in server-held state: framework player data, server-side tables, or a database. Read it from there when making server-side decisions; never read it back from a player or entity bag.
- A change handler is a notification. Returning from it does not reject or undo the change. If a client changes a key it should not, the server must set the authoritative value again (and can flag or log the player).
- Use bags to *publish* server decisions to clients (for UI and client logic), not to receive decisions from clients. Check docs.fivem.net for any server options that restrict client state bag writes in your server version.

```lua
-- Server: the authoritative job lives in a server-only table; the player
-- bag is just a replicated copy for clients to read.
local jobs = {}

local function setJob(src, job)
    jobs[src] = job                               -- authority first
    Player(src).state:set('job', job, true)       -- then publish
end

-- If the bag value ever differs from the server's value (for example a
-- client overwrote its own bag), put the server value back.
AddStateBagChangeHandler('job', nil, function(bagName, key, value)
    local src = GetPlayerFromStateBagName(bagName)
    if src == 0 or jobs[src] == nil then return end
    if value ~= jobs[src] then
        Player(src).state:set('job', jobs[src], true)
        print(('[state] restored job for player %d'):format(src))
    end
end)

AddEventHandler('playerDropped', function()
    jobs[source] = nil
end)

-- Server-side checks read jobs[src], never Player(src).state.job.
```

## Best practices

1. **Namespace your keys** -- use `resourceName:key` to avoid collisions (e.g., `garage:fuel` not just `fuel`)
2. **Keep values shallow** -- state bags serialize the entire value on each set; don't nest deeply
3. **Don't overuse** -- frequent updates (every frame) are expensive; use state bags for data that changes infrequently
4. **Clean up** -- state bags are automatically cleaned when the entity is deleted, but clear custom state if needed
5. **Use `:set()` for control** -- the shorthand `entity.state.key = value` always uses default replication; use `:set()` when you need explicit control

## Common patterns

### Vehicle fuel system

```lua
-- Server: initialize fuel on vehicle spawn
local vehicle = CreateVehicle(model, x, y, z, heading, true, true)
Entity(vehicle).state.fuel = 100.0

-- Server: consume fuel periodically
CreateThread(function()
    while true do
        Wait(10000)
        for _, vehicle in ipairs(GetAllVehicles()) do
            local fuel = Entity(vehicle).state.fuel
            if fuel and fuel > 0 then
                Entity(vehicle).state.fuel = fuel - 0.5
            end
        end
    end
end)

-- Client: display fuel in HUD
CreateThread(function()
    while true do
        Wait(500)
        local vehicle = GetVehiclePedIsIn(PlayerPedId(), false)
        if vehicle ~= 0 then
            local fuel = Entity(vehicle).state.fuel
            -- update HUD with fuel value
        end
    end
end)
```

### Player job sync

```lua
-- Server: set job on player load
RegisterNetEvent('myResource:playerLoaded', function()
    local source = source
    local job = getPlayerJobFromDB(source)
    Player(source).state.job = job
    Player(source).state.onDuty = false
end)

-- Client: react to job changes
AddStateBagChangeHandler('job', 'player:' .. GetPlayerServerId(PlayerId()), function(_, _, value)
    if value then
        -- update local UI, blips, etc.
    end
end)
```
