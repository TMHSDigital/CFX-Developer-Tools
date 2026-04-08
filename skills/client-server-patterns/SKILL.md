---
title: Client-Server Patterns
description: Correct patterns for client/server scripting in Lua, JavaScript, and C# for CFX
globs: ["**/*.lua", "**/*.js", "**/*.cs"]
---

# Client-Server Patterns

FiveM and RedM resources run code on two sides: the **client** (each player's game) and the **server** (the central authority). Communication between them uses network events.

## Lua patterns

### Thread with proper Wait

```lua
CreateThread(function()
    while true do
        Wait(1000)  -- NEVER use Wait(0) unless drawing or checking input
        -- your logic here
    end
end)
```

### Registering a client event

```lua
RegisterNetEvent('myResource:clientEvent', function(data)
    -- handle event from server
end)
```

`RegisterNetEvent` must be called before the handler can receive network events. The callback is the handler.

### Triggering a server event from client

```lua
TriggerServerEvent('myResource:serverEvent', someData)
```

### Registering a server event

```lua
RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source  -- capture the player source immediately
    -- validate source, then handle event
end)
```

Always capture `source` as a local on the first line. The global `source` can change between yields.

### Exports

```lua
exports('MyFunction', function(param)
    return result
end)
```

Other resources call this with `exports['resource-name']:MyFunction(param)`.

### Callbacks (using server callbacks)

For request/response patterns, use a callback library or implement one with paired events:

```lua
-- Client: request data
TriggerServerEvent('myResource:getData', requestId)

-- Client: receive response
RegisterNetEvent('myResource:dataResponse', function(requestId, data)
    -- handle response
end)

-- Server: handle request and respond
RegisterNetEvent('myResource:getData', function(requestId)
    local source = source
    local data = fetchData(source)
    TriggerClientEvent('myResource:dataResponse', source, requestId, data)
end)
```

## JavaScript patterns

### Thread equivalent

```javascript
setTick(async () => {
    await Delay(1000);
    // your logic
});
```

### Event handling (client)

```javascript
onNet('myResource:clientEvent', (data) => {
    // handle event from server
});
```

### Trigger server event

```javascript
emitNet('myResource:serverEvent', someData);
```

### Server event with source

```javascript
onNet('myResource:serverEvent', (data) => {
    const src = global.source;
    // validate src, handle event
});
```

### Local events

```javascript
on('myResource:localEvent', (data) => {
    // only fires within this runtime
});

emit('myResource:localEvent', data);
```

## C# patterns

### Base script class

```csharp
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class MyScript : BaseScript
{
    public MyScript()
    {
        EventHandlers["myResource:clientEvent"] += new Action<dynamic>(OnClientEvent);
        Tick += OnTick;
    }

    private void OnClientEvent(dynamic data)
    {
        // handle event
    }

    private async Task OnTick()
    {
        await Delay(1000);
        // your logic
    }
}
```

### Triggering events from C#

```csharp
TriggerServerEvent("myResource:serverEvent", data);
TriggerClientEvent("myResource:clientEvent", targetPlayer, data);
TriggerEvent("myResource:localEvent", data);
```

## Event naming conventions

Always prefix events with the resource name to avoid collisions:

- `myResource:playerLoaded`
- `myResource:vehicleSpawned`
- `myResource:adminAction`

Never use generic names like `onPlayerDeath` or `getData` -- they will collide with other resources.

## Key rules

1. **Never trust the client** -- always validate `source` and all parameters on the server
2. **Capture `source` immediately** in Lua server handlers before any `Wait()` or async call
3. **Use `Wait()` in every loop** -- a `while true` loop without `Wait()` will freeze the game
4. **Clean up on stop** -- listen for `onResourceStop` to remove blips, entities, and NUI focus
5. **Rate-limit events** -- do not fire net events more than once per second per player unless necessary
