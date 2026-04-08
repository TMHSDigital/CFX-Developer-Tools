# Roadmap

## Milestone 1 - Foundation (current)

Core plugin scaffolding and content that enables basic CFX resource development in Cursor.

### Deliverables

- [x] Repository structure and Cursor plugin manifest (`.cursor-plugin/plugin.json`)
- [x] MCP server configuration (`.cursor/mcp.json`)
- [x] Resource scaffolding skill and templates for all languages (Lua, JavaScript, C#)
- [x] Resource scaffolding templates for all frameworks (standalone, ESX, QBCore, ox_core)
- [x] fxmanifest.lua generation skill with full directive coverage
- [x] Client-server patterns skill covering all three runtimes
- [x] Framework detection skill (ESX, QBCore, ox_core, standalone)
- [x] Performance optimization skill with CFX-specific rules
- [x] NUI development skill
- [x] Database integration skill (oxmysql, mysql-async)
- [x] 6 coding convention and safety rules (.mdc files)
- [x] 15 code snippets (7 Lua, 5 JavaScript, 3 C#)
- [x] MCP server stub with 4 tool definitions (scaffold, native lookup, manifest gen, event search)
- [x] Native function database stubs (GTA5: 50 natives, RDR3: 10 natives)
- [x] Common events reference database (20 events)
- [x] Documentation: Getting Started, Architecture, Contributing, Roadmap, Changelog
- [x] CI/CD: PR validation workflow (JSON lint, manifest checks, em dash detection, template validation, Python syntax)
- [x] CI/CD: Auto version bump + tag + GitHub Release on merge to main (conventional commits)
- [x] CI/CD: Scheduled weekly native database update from citizenfx/natives (auto-merge)
- [x] CI/CD: Stale issue/PR cleanup workflow

### Out of scope for M1

- MCP tools are defined but not yet fully tested end-to-end
- Native databases are stubs until the first scheduled update runs

---

## Milestone 2 - Intelligence

Make the MCP server useful for real development by expanding the data layer and adding live documentation features.

### Native function database

- [ ] Expand GTA5 native database to 500+ commonly used natives
- [ ] Expand RDR3 native database to 200+ natives
- [ ] Add full parameter type annotations and usage examples for each native
- [ ] Add deprecation flags and replacement recommendations
- [ ] Add namespace/category browsing (PLAYER, VEHICLE, ENTITY, PED, HUD, etc.)

### Documentation search

- [ ] Implement `docs_search` MCP tool that queries the FiveM documentation site
- [ ] Cache frequently accessed doc pages locally for offline use
- [ ] Support searching by topic, function name, or keyword

### Event reference

- [ ] Expand events.json to 100+ events (base game, CFX, and popular framework events)
- [ ] Add ESX-specific events (esx:playerLoaded, esx:setJob, etc.)
- [ ] Add QBCore-specific events (QBCore:Client:OnPlayerLoaded, etc.)
- [ ] Add ox_core events

### Framework auto-detection

- [ ] Implement workspace scanning in the MCP server (not just skill instructions)
- [ ] Auto-detect framework from fxmanifest.lua and script imports
- [ ] Expose detection result as an MCP tool: `detect_framework`
- [ ] Cache detection result per workspace session

### Code generation improvements

- [ ] Context-aware boilerplate generation that reads existing code style
- [ ] Smarter manifest generation that scans existing files for script paths
- [ ] Template variable substitution (resource name, author, etc.)

---

## Milestone 3 - Integration

Connect the plugin to live FiveM/RedM server infrastructure for real-time development workflows.

### txAdmin API integration

txAdmin exposes a REST API on port 40120 (default) with session cookie authentication.

- [ ] Add MCP tool: `txadmin_server_control` (start, stop, restart FXServer)
- [ ] Add MCP tool: `txadmin_resource_control` (start, stop, restart, refresh individual resources)
- [ ] Add MCP tool: `txadmin_player_search` (search connected players by name or identifier)
- [ ] Add MCP tool: `txadmin_kick_player` (kick with reason)
- [ ] Add connection configuration (host, port, session token via environment variable)
- [ ] Add skill for txAdmin setup and authentication

### RCON and server commands

- [ ] Add MCP tool: `execute_rcon` (run server console commands)
- [ ] Common commands skill: refresh, ensure, stop, start, restart resources
- [ ] Server convar management (get/set convars)

### Live development workflow

- [ ] Resource hot-reload: detect file changes and auto-restart the resource via txAdmin
- [ ] Error log streaming: tail server console for Lua/JS/C# errors related to the active resource
- [ ] Bridge resource: a FiveM resource that connects to the MCP server for bidirectional debugging
- [ ] Player state inspection: read player data (position, health, vehicle) from a running server

### Server configuration

- [ ] server.cfg editor skill with convar reference
- [ ] Dependency resolver: check if required resources are present and started

---

## Milestone 4 - Polish

Harden the plugin for public release and community adoption.

### Linting and validation

- [ ] Static analysis rules for common Lua mistakes (missing Wait in loops, uncaptured source, etc.)
- [ ] fxmanifest.lua validator that checks for missing fields, invalid paths, deprecated directives
- [ ] Detect deprecated patterns: `Citizen.CreateThread`, `__resource.lua`, `lua54 'yes'` (now a no-op)
- [ ] Detect dangerous patterns: string concatenation in SQL, unsanitized ExecuteCommand

### Testing

- [ ] Mock environment for unit testing CFX resources outside a running server
- [ ] Sample test harness for common patterns (event handlers, commands, exports)
- [ ] CI-friendly test runner that validates resource structure

### RedM expansion

- [ ] Expand RDR3 native database to full coverage
- [ ] Add RedM-specific templates (VORP, RSG framework support)
- [ ] Add RedM-specific snippets (prompts, scenarios, RDR3 peds)
- [ ] RedM-specific coding conventions rule

### Community and marketplace

- [ ] Plugin logo and branding assets
- [ ] Submission to the Cursor Marketplace (requires public Git repo, valid manifest, manual review)
- [ ] Community template contribution workflow (PR template, validation script)
- [ ] Plugin versioning and update strategy

### Documentation

- [ ] Video walkthrough or GIF demos for Getting Started
- [ ] Expanded architecture docs with MCP tool flow diagrams
- [ ] FAQ and troubleshooting guide
- [ ] Example resources built entirely with the plugin (showcase)
