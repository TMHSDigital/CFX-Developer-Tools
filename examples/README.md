# Examples

Complete, ready-to-use CFX resources that demonstrate the skills and rules in this repo. Unlike `templates/` (blank per-framework skeletons), each folder here is a finished resource you can drop into a server and run.

Every example follows the repo conventions: `fxmanifest.lua` declares `fx_version 'cerulean'`, `games { 'gta5' }`, and `lua54 true`; logic is server-authoritative; and no credentials are hardcoded.

| Example | Demonstrates | Notes |
|---------|--------------|-------|
| [`drug-sell`](drug-sell/) | client-server patterns, server-side anti-cheat | Sell drugs to nearby peds. Server owns the cooldown, drug selection, payout, and cop-alert. ESX / QBCore / standalone bridge. |
| [`doorlock`](doorlock/) | `state-bags` | Lock/unlock doors via replicated `GlobalState` and a `AddStateBagChangeHandler`. Server validates range. Pure Lua, no dependencies. |
| [`playtime-tracker`](playtime-tracker/) | `database-integration` | Tracks lifetime playtime in MySQL via oxmysql with parameterised queries and a migration. Requires `oxmysql`. |
| [`speedometer-hud`](speedometer-hud/) | `nui-development`, `performance-optimization` | Vanilla NUI HUD fed by rate-limited, change-gated `SendNUIMessage`, in-vehicle only. No build tooling. |
| [`secure-shop`](secure-shop/) | `client-server-patterns`, `security-best-practices` | Server-authoritative purchase flow. The client sends only an item id and quantity; the server owns prices and validates everything. |

Each example has its own `README.md` with install steps and the specific pattern it teaches.
