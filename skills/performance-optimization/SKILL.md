---
title: Performance Optimization
description: CFX-specific performance best practices for FiveM and RedM resources
globs: ["**/*.lua", "**/*.js", "**/*.cs"]
---

# Performance Optimization

FiveM and RedM resources share a single game thread. A poorly optimized resource can degrade the entire server's performance and player experience.

## Critical rules

### 1. Never use Wait(0) in loops unless necessary

`Wait(0)` runs your code every single frame (~60 times per second). Only use it for:
- Drawing markers, text, or other per-frame visuals
- Checking input state every frame

For everything else, use the longest wait time that still meets your requirements:

```lua
-- Bad: checking every frame for no reason
CreateThread(function()
    while true do
        Wait(0)
        if someCondition then doThing() end
    end
end)

-- Good: check every second
CreateThread(function()
    while true do
        Wait(1000)
        if someCondition then doThing() end
    end
end)
```

### 2. Use dynamic wait times

Scale your wait time based on proximity or relevance:

```lua
CreateThread(function()
    while true do
        local sleep = 1000
        local playerCoords = GetEntityCoords(PlayerPedId())
        local distance = #(playerCoords - targetCoords)

        if distance < 50.0 then
            sleep = 100
            -- Player is close, do detailed checks
        elseif distance < 200.0 then
            sleep = 500
            -- Player is in range, do occasional checks
        end

        Wait(sleep)
    end
end)
```

### 3. Use compile-time hashing

```lua
-- Good: hash computed at compile time
local hash = `adder`

-- Bad: hash computed at runtime every call
local hash = GetHashKey('adder')
```

Backtick hashing only works with string literals in Lua. For variables, `GetHashKey()` is still needed -- but cache the result instead of calling it repeatedly.

### 4. Use vector math

```lua
-- Good: native vector math, fast
local distance = #(vec1 - vec2)

-- Bad: wrapper function, slower
local distance = GetDistanceBetweenCoords(x1, y1, z1, x2, y2, z2)
-- Also bad:
local distance = Vdist(x1, y1, z1, x2, y2, z2)
```

### 5. Use global aliases

```lua
-- Good: shorter, preferred
CreateThread(function() end)
Wait(1000)

-- Bad: verbose, deprecated style
Citizen.CreateThread(function() end)
Citizen.Wait(1000)
```

### 6. Avoid table.insert in hot loops

```lua
-- Good: indexed assignment
local results = {}
local count = 0
for i = 1, #entities do
    count = count + 1
    results[count] = entities[i]
end

-- Bad: function call overhead in hot loop
local results = {}
for i = 1, #entities do
    table.insert(results, entities[i])
end
```

### 7. Clean up on resource stop

```lua
local blips = {}
local entities = {}

AddEventHandler('onResourceStop', function(resourceName)
    if GetCurrentResourceName() ~= resourceName then return end

    for _, blip in ipairs(blips) do
        RemoveBlip(blip)
    end

    for _, entity in ipairs(entities) do
        DeleteEntity(entity)
    end

    SetNuiFocus(false, false)
end)
```

Leaked entities and blips persist until the player disconnects, causing visual clutter and performance issues.

### 8. State bags over frequent net events

For data that changes often and needs to be synced (e.g. player status, job info):

```lua
-- Good: state bag, synced automatically
Player(source).state:set('duty', true, true)
-- Read on client:
local onDuty = LocalPlayer.state.duty

-- Bad: firing events constantly
TriggerClientEvent('myResource:setDuty', source, true)
```

State bags use the native replication system and are more efficient than custom net events for frequent updates.

### 9. Profile with resmon

In the server console or F8:
```
resmon 1
```

This shows per-resource CPU time. Target under **0.2ms idle** for a well-optimized resource. Resources consistently above 1ms should be investigated.

## JavaScript-specific tips

- Use `await Delay(ms)` instead of `Delay(0)` in `setTick`
- Client-side JS does not have access to Node.js APIs -- keep it lightweight
- Avoid heavy npm packages on the client side

## C#-specific tips

- Always `await Delay(ms)` in `Tick` handlers -- never skip it
- Use `async`/`await` to avoid blocking the game thread
- Minimize allocations in tick handlers to reduce GC pressure
