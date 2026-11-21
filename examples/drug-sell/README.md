# drug-sell

A minimal FiveM example resource that demonstrates **client-server patterns** with a server-owned outcome: the client asks to sell, and the server decides what happens.

## What it demonstrates

- A keybind built with `RegisterCommand` + `RegisterKeyMapping` (rebindable, no per-frame key polling).
- A server-enforced per-player cooldown. The client cooldown is only for feedback; the server rejects requests that arrive too fast.
- Server-side outcome: the server picks which held drug is sold, rolls the result (`Config.Chances`), computes the payout from `Config.Drugs`, and removes the item before paying.
- A police-alert hook (`Config.PoliceAlertEvent`) that other resources can listen to with `AddEventHandler`.
- An ESX / QBCore inventory and money bridge with a standalone fallback (`Config.StandaloneInfiniteStock`).
- Cleanup of per-player state on `playerDropped` so the cooldown table cannot grow without bound.

## Install

1. Copy the `drug-sell` folder into your server's `resources` directory.
2. Add `ensure drug-sell` to your `server.cfg` (after your framework).
3. Edit `config.lua`: drugs and prices (`Config.Drugs`), chances, cooldown, payout account and key.
4. Restart the server, stand next to a pedestrian and press the sell key (default `E`).

No database or credentials required.

## Files

| File | Purpose |
|------|---------|
| `fxmanifest.lua` | Resource manifest (cerulean, gta5) |
| `config.lua` | Shared settings: framework, key, distances, cooldown, chances, drugs, payout account |
| `client/main.lua` | Keybind, nearby-ped lookup and feedback |
| `server/main.lua` | Cooldown, sale outcome, inventory and money bridge, police alert |
