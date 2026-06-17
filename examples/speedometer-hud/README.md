# speedometer-hud

A minimal FiveM example resource that demonstrates **NUI development** with a passive, rate-limited speedometer HUD. It uses plain vanilla HTML, CSS, and JavaScript with no build tooling, so it runs as-is.

## What it demonstrates

- A NUI overlay fed entirely by `SendNUIMessage` (no NUI callbacks, no `SetNuiFocus`).
- Message routing in `html/app.js` keyed on `event.data.action` (`display` and `speed`).
- A single self-pacing client thread that converts `GetEntitySpeed` (m/s) to mph or km/h.

## File layout

```
speedometer-hud/
  fxmanifest.lua      # fx_version 'cerulean', games { 'gta5' }, lua54 true, ui_page + files
  config.lua          # shared_script: Config.Unit ('mph' or 'kmh')
  client/main.lua     # speed loop + rate-limited SendNUIMessage
  html/index.html     # ui_page, links style.css and app.js
  html/style.css      # bottom-right readout, transparent body
  html/app.js         # window 'message' listener routing on action
```

## Install

1. Copy the `speedometer-hud` folder into your server `resources/` directory.
2. Add `ensure speedometer-hud` to your `server.cfg`.
3. (Optional) Set `Config.Unit` in `config.lua` to `'mph'` or `'kmh'`.
4. Start the server and get into any vehicle. The HUD appears bottom-right and hides on foot.

## Performance notes

This resource follows the repo's performance rules. Two choices keep it cheap:

1. **In-vehicle-only work.** The thread runs `Wait(0)` (per-frame) only while the player is in a vehicle. On foot it switches to `Wait(500)` and hides the HUD, so the resource idles near 0.00ms whenever you are not driving.
2. **Change-gated messages.** A `speed` message is only sent when the displayed integer speed actually changes, or at most once every ~100ms. The `display` message is sent only when visibility flips. NUI traffic, not the Lua loop, is the expensive part, so gating messages is what keeps the HUD light.

## Why the transparent body matters

NUI pages render on top of the game. In `html/style.css` the page sets `body { background: transparent; }`. Without it, the page background would paint over the entire screen and black out the game. Only the small speedometer box is drawn; everything else stays see-through.
