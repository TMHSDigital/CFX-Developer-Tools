# Roadmap

Upcoming feature tracking issues for CFX Developer Tools. Each entry follows the standard engineering format: Title, Context/Background, Technical Requirements, and Definition of Done.

---

## 1. [FEAT] CFX Environment Context Exporter (MCP Context Optimizer)

### Context / Background

Inspired by the HighwayTrooper workflow video, where AI token consumption spiked due to "environment scouting": the model repeatedly exploring the server tree to figure out which framework, inventory, and database stack was in play. That exploration cost is paid on every session. A one-time, dense context export eliminates it.

### Technical Requirements

- Add a new MCP tool (`export_environment_context_tool`) in `mcp-server/tools/`, following the existing snake_case + `_tool` suffix convention.
- Scan a given server root: walk the `resources/` directory and parse `server.cfg` (`ensure` / `start` lines, convars).
- Detect and report:
  - Active framework (Qbox, QB-Core, ESX, ox_core, VORP, RSG, standalone) - reuse logic from `detect_framework_tool` where possible.
  - Inventory system (ox_inventory, qb-inventory, qs-inventory, etc.).
  - Target/interaction system (ox_target, qb-target, interact).
  - Database wrapper (oxmysql, ghmattimysql, mysql-async).
- Output a highly dense, token-optimized JSON payload (short keys, no prose, deduplicated resource lists) suitable for appending to system prompts or Claude/Cursor workspace context.
- Provide a standalone script entry point so it can run outside MCP (e.g., `python mcp-server/tools/export_context.py <server_path>`).

### Definition of Done

- [ ] Tool registered with `@mcp.tool()` and listed in the CLAUDE.md / README MCP tool tables.
- [ ] Correctly identifies framework, inventory, target, and DB wrapper on at least Qbox, QB-Core, and ESX test fixtures.
- [ ] JSON payload validated against a documented schema and measured under a stated token budget (target: < 500 tokens for a typical server).
- [ ] Unit tests covering `server.cfg` parsing edge cases (comments, `ensure [category]`, missing resources).
- [ ] `validate_plugin.py` passes and docs page added under `docs/`.

---

## 2. [FEAT] Static Vector & Coordinate Sanity Linter

### Context / Background

In the reference video, the AI outputted approximate/broken coordinates for a delivery drop-off point, causing the player to fall through the collision mesh. Bad Z-axis values (clipping planes, flat 0.0 on street-level positions) are a recurring class of AI-generated bug that is cheap to catch statically.

### Technical Requirements

- New rule file `rules/cfx-coordinate-sanity.mdc` scoped to `**/*.lua`, plus an optional standalone lint script under `.github/scripts/` for CI use.
- Extract coordinate literals from Lua source: `vector3(x, y, z)`, `vector4(x, y, z, w)`, and bare coordinate tables/arrays (`{ x = ..., y = ..., z = ... }` and positional triples).
- Sanity logic against Los Santos / San Andreas map bounds:
  - Flag Z values at or near common clipping planes (e.g., `-50.0`, `-100.0`) as "Potential Map Collision/Clip Risk".
  - Flag perfectly flat `z = 0.0` when the X/Y pair falls inside street-level land bounds (not ocean).
  - Flag coordinates entirely outside the playable map bounding box.
- Warnings only, never errors: legitimate underground/interior coordinates exist, so output must be suppressible via inline comment (e.g., `-- cfx-lint: allow-coords`).

### Definition of Done

- [ ] Rule ships in `rules/` with correct frontmatter (`description`, `alwaysApply`, `globs`) and is counted in `plugin.json`.
- [ ] Detects all four documented risk patterns on a test corpus of known-bad snippets with zero false positives on the existing `examples/` and `templates/` Lua files.
- [ ] Suppression comment honored.
- [ ] Documented in the rules table in CLAUDE.md/README and the docs site.

---

## 3. [FEAT] Qbox & Ox-Suite Boilerplate Scaffolder

### Context / Background

Modernizing development boundaries for clean, modular FiveM/CFX resource generation. The existing `scaffold_resource_tool` produces generic skeletons; Qbox + ox-suite projects have specific conventions (ox_lib imports, oxmysql patterns, strict client/server/shared boundaries) that deserve first-class scaffolding.

### Technical Requirements

- Extend `scaffold_resource_tool` (or add a dedicated `scaffold_qbox_resource_tool`) in `mcp-server/tools/`, plus a matching starter template under `templates/`.
- Generated `fxmanifest.lua` must include:
  - `fx_version 'cerulean'` and `games`, with no `lua54` directive (Lua 5.4 is the only runtime).
  - Native Qbox metadata tags and `ox_lib` / `oxmysql` dependency declarations.
  - `shared_scripts { '@ox_lib/init.lua', ... }` import hooks.
- Pre-configured directory boundaries: `client/`, `server/`, `shared/` with entry files wired into the manifest.
- Include a fully formed `oxmysql` query template schema: prepared-statement examples, a `sql/schema.sql` migration file, and a server-side data-access module.
- CLI invocation path documented for non-MCP use.

### Definition of Done

- [ ] Generated resource loads cleanly on a Qbox test server with `ox_lib` and `oxmysql` present.
- [ ] Manifest passes the `fxmanifest-standards.mdc` rule and existing manifest validation.
- [ ] Template added to `templates/` and counted by `validate_plugin.py`.
- [ ] Tool/template documented in CLAUDE.md, README, and the docs site.

---

## 4. [FEAT] Clipboard Position Grabber Snippet Template

### Context / Background

In the reference video test, the human developer won by using a live admin coordinate grabber, while the AI relied on manual configuration editing. A drop-in dev utility closes that gap: grab exact in-game coordinates and paste them straight into Cursor or VS Code.

### Technical Requirements

- New snippet/template (`snippets/` entry plus a runnable dev resource under `templates/` or `examples/`), Lua, dev-only.
- Register a fast command (e.g., `/grabpos`) that:
  - Reads `GetEntityCoords(PlayerPedId())` and `GetEntityHeading(PlayerPedId())`.
  - Formats output as both a Lua vector string (`vector4(x, y, z, heading)` with sensible precision) and a JSON block, selectable via argument (`/grabpos json`).
  - Copies the result to the client clipboard via an NUI `document.execCommand('copy')` / Clipboard API bridge, with an on-screen confirmation.
- Must be safe to leave in a repo but obviously dev-only: guard behind a convar (e.g., `setr cfx_devtools_enable_grabpos 1`) and document that it should not ship to production servers.
- No hardcoded credentials, complies with `security-best-practices.mdc`.

### Definition of Done

- [ ] `/grabpos` returns correctly formatted vector and JSON output on a live FiveM test client, and the value lands on the OS clipboard.
- [ ] Convar guard verified: command inert when the convar is unset.
- [ ] Snippet loads cleanly inside a CFX resource per snippet conventions and is counted by `validate_plugin.py`.
- [ ] Documented in the snippets/templates listings in CLAUDE.md, README, and the docs site.
