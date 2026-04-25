---
title: NUI Development
description: Guide development of NUI (in-game web UI) interfaces for FiveM and RedM
globs: ["**/fxmanifest.lua", "**/*.html", "**/*.css"]
standards-version: 1.7.0
---

# NUI Development

NUI (Natural User Interface) is a Chromium-based embedded browser in the FiveM/RedM game client. It allows resources to render HTML/CSS/JS interfaces overlaid on the game.

## Manifest setup

```lua
ui_page 'html/index.html'

files {
    'html/index.html',
    'html/style.css',
    'html/script.js'
}
```

- `ui_page` sets the HTML entry point
- `files` lists all assets the client needs to download
- Glob patterns work: `'html/**'` includes everything in the html folder

## Communication: Lua to NUI

Send data from a Lua client script to the NUI:

```lua
SendNUIMessage({
    type = 'open',
    data = {
        title = 'My Menu',
        items = {'Item 1', 'Item 2'}
    }
})

SetNuiFocus(true, true)  -- enable keyboard and mouse focus
```

## Communication: NUI to Lua

### JavaScript side (in the browser)

Listen for messages from Lua:

```javascript
window.addEventListener('message', (event) => {
    const data = event.data;

    if (data.type === 'open') {
        // Show UI with data.data
        document.getElementById('app').style.display = 'block';
    }

    if (data.type === 'close') {
        document.getElementById('app').style.display = 'none';
    }
});
```

Send data back to Lua via NUI callbacks:

```javascript
async function closeMenu() {
    await fetch(`https://${GetParentResourceName()}/closeMenu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmed: true })
    });
}
```

`GetParentResourceName()` is a built-in function available in NUI JavaScript that returns the resource name.

### Lua side (register the callback)

```lua
RegisterNUICallback('closeMenu', function(data, cb)
    SetNuiFocus(false, false)
    -- data.confirmed is true
    cb('ok')
end)
```

Always call `cb()` to complete the callback. Failing to call it will hang the NUI fetch request.

## Focus management

```lua
SetNuiFocus(hasFocus, hasCursor)
```

- `hasFocus` -- captures keyboard input (player cannot move)
- `hasCursor` -- shows mouse cursor

Always release focus when the UI closes:

```lua
SetNuiFocus(false, false)
```

And clean up on resource stop:

```lua
AddEventHandler('onResourceStop', function(resourceName)
    if GetCurrentResourceName() ~= resourceName then return end
    SetNuiFocus(false, false)
end)
```

## Framework choices

Any web framework works inside NUI:
- **Svelte 5** -- the most popular NUI framework in the CFX community (2026). Uses Runes (`$state`, `$derived`, `$effect`) instead of stores. Smallest bundle size, excellent for NUI. Use the `nui-svelte` template.
- **React** -- widely used, large ecosystem. Use the `nui-vite` template.
- **Vue** -- popular alternative with good community support
- **Vanilla HTML/CSS/JS** -- simplest, no build step

Keep bundles small. The NUI browser downloads assets from the resource, and large bundles increase load time. Svelte produces the smallest bundles for equivalent functionality.

## Limitations

- **No Node.js APIs** -- NUI runs in a browser context, not Node
- **Limited persistent storage** -- `localStorage` may work in some FiveM/RedM builds but behavior is inconsistent across updates; do not rely on it for important data
- **No cross-origin requests** -- only `https://cfx-nui-*` URLs work
- **No devtools by default** -- use `nui_devtools true` convar in server.cfg for debugging
- **Single page** -- `ui_page` points to one HTML file; use JS routing for multiple views

## Debugging

Enable devtools in server.cfg:
```
set nui_devtools true
```

Once enabled, NUI devtools open in a separate Chromium DevTools window. You can inspect elements, view console logs, and debug CSS. Note: F8 opens the game client console, not the NUI inspector.

## Common patterns

### Toggle UI visibility

```lua
local isOpen = false

RegisterCommand('menu', function()
    isOpen = not isOpen
    SendNUIMessage({ type = isOpen and 'open' or 'close' })
    SetNuiFocus(isOpen, isOpen)
end, false)

RegisterNUICallback('close', function(_, cb)
    isOpen = false
    SetNuiFocus(false, false)
    cb('ok')
end)
```

### Escape key to close

In the NUI JavaScript:

```javascript
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        fetch(`https://${GetParentResourceName()}/close`, { method: 'POST' });
    }
});
```
