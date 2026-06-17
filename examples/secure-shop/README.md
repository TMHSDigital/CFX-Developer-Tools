# secure-shop

A minimal FiveM example that demonstrates **server-authoritative client-server
patterns** and **input validation / security best practices** for CFX resource
development.

It pairs the repo's `client-server-patterns` and `security-best-practices`
skills with runnable code.

## What it demonstrates

- The client sends **only an item id and a quantity** over the wire.
- The **server owns the prices** (in `config.lua`), looks them up by id,
  validates every field, checks funds, deducts money, and grants the item.
- Per-player, server-enforced anti-spam cooldown, cleaned up on `playerDropped`.
- A command + `RegisterKeyMapping` instead of a per-frame input poll, plus a
  low-frequency proximity thread (Wait 500/1000) so the resource idles cheaply.
- An ESX / QBCore bridge with a standalone fallback for money, inventory, and
  notifications.

## The trust model (read this)

> The client is attacker-controlled. Never trust it with anything that matters.

A cheater can fire `TriggerServerEvent('secure-shop:server:buy', ...)` with any
values they like. So the client sends the **minimum**: an `itemId` and a `qty`.

The server then:

1. Confirms the event came from a real player (`src > 0`).
2. Confirms `itemId` is a string naming a real entry in `Config.Items`.
3. Confirms `qty` is a finite, positive **integer** within `Config.MaxQuantity`
   - rejecting `nil`, strings, tables, `NaN`, `inf`, floats, zero, and negatives.
4. Computes `total = item.price * qty` from **its own config**.
5. Checks the player can afford `total`, deducts it, then grants the item
   (refunding if the grant fails).

If the client were trusted to send a price, an attacker would send `price = 0`
(or a negative price) and take items for free or even gain money. That is why
**the price is never read from the wire** - only the id and quantity are.

## Files

| File | Role |
|------|------|
| `fxmanifest.lua` | Resource manifest (cerulean, gta5, lua54) |
| `config.lua` | Shared config - the catalogue and the authoritative prices |
| `server/main.lua` | NetEvent handler, validation, funds, cooldown |
| `client/main.lua` | Keybind, proximity gate, result notifications |

## Install

1. Copy the `secure-shop` folder into your server `resources/` directory.
2. Add `ensure secure-shop` to your `server.cfg`.
3. (Optional) Make sure `es_extended` or `qb-core` starts before this resource,
   or set `Config.Framework` explicitly to `'esx'`, `'qb'`, or `'standalone'`.
4. Make sure the inventory item names in `Config.Items` (`item = ...`) exist in
   your framework's item database, or purchases will be charged but the grant
   step will fail (and refund).

## Try it

Walk to `Config.ShopCoords` (the 24/7 store on Innocence Blvd by default) and
press `E`. The demo buys 1x the first configured item (`Water`). Watch the
server validate the request and the notification report the price.

Standalone mode has no money or inventory backend, so `Config.StandaloneAlwaysAfford`
lets the purchase "succeed" for testing only. Leave it `false` in production.

## How to extend with NUI

This example deliberately has no UI so the security flow stays readable. To turn
it into a real shop:

1. Add an `html/` folder and declare `ui_page` + `files` in `fxmanifest.lua`.
2. Open the NUI on the keybind (`SetNuiFocus(true, true)` and a
   `SendNUIMessage`) instead of buying immediately.
3. From the UI, on "buy" call `fetch('https://secure-shop/buy', ...)` and handle
   it with `RegisterNUICallback('buy', ...)`.
4. In that callback, forward **only** `{ itemId, qty }` to
   `secure-shop:server:buy`. **Never** send the price from the UI - the server
   still owns it. The entire server side stays exactly as it is.
