# Roadmap

## Milestone 1 - Foundation (v0.1.x--v0.2.0, complete)

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
- [x] MCP server with 4 tool definitions (scaffold, native lookup, manifest gen, event search)
- [x] Native function database stubs (GTA5: 50 natives, RDR3: 10 natives)
- [x] Common events reference database (20 events)
- [x] Documentation: Getting Started, Architecture, Contributing, Roadmap, Changelog
- [x] CI/CD: PR validation, auto release, weekly native updates, stale cleanup
- [x] AGENTS.md and .cursorrules for AI agent guidance
- [x] Plugin logo and branding assets

---

## Milestone 2 - Intelligence (v0.3.0--v0.4.x, complete)

Expanded the data layer and added new skills and content for real development workflows.

### Native function database

- [x] Expand GTA5 native database to 6300+ real natives from runtime.fivem.net
- [x] Expand RDR3 native database to 5800+ real natives from runtime.fivem.net
- [x] Full parameter type annotations and usage examples
- [x] Deprecation flags and replacement recommendations
- [x] Namespace/category browsing (44 GTA5 categories, 84 RDR3 categories)
- [x] Native hash field in output schema
- [x] Merge 942 CFX platform natives with accurate apiset-based side classification
- [x] Update weekly CI workflow to fetch from runtime.fivem.net (GTA5, RDR3, CFX sources)

### Content expansion

- [x] State Bags skill covering Entity/Player/Global state, change handlers, replication, and security
- [x] State Bags snippets for Lua and JavaScript (entity, player, change handler)
- [x] CfxLua vector/quaternion type documentation in Lua conventions rule and client-server patterns skill
- [x] NUI Vite + React template with postMessage bridge and HMR dev workflow
- [x] Balanced FiveM/RedM representation across all documentation, skills, templates, and snippets
- [x] Comprehensive Getting Started guide for complete beginners with collapsible sections

---

## Milestone 3 - Expansion (v0.5.0, complete)

Expanded event coverage, added documentation search and framework detection MCP tools, and improved code generation intelligence.

### Documentation search

- [x] Implement `search_docs_tool` MCP tool that queries a local index of FiveM/RedM documentation
- [x] Pre-built local index (~80 pages) from docs.fivem.net, updated monthly by CI
- [x] Support searching by topic, function name, keyword, or section filter
- [x] CI workflow (`update-docs-index.yml`) for automated monthly index rebuilds

### Event reference

- [x] Expand events.json from 20 to 82 events (base game, CFX, and popular framework events)
- [x] Add ESX-specific events (15 events: esx:playerLoaded, esx:setJob, etc.)
- [x] Add QBCore-specific events (15 events: QBCore:Client:OnPlayerLoaded, etc.)
- [x] Add ox_core events (8 events: ox:playerLoaded, ox:setGroup, etc.)
- [x] Add chat resource events (7 events)
- [x] Add `game` and `framework` fields to event schema with filter support

### Framework auto-detection

- [x] Implement workspace scanning MCP tool (`detect_framework_tool`)
- [x] Auto-detect framework from fxmanifest.lua dependencies and script imports
- [x] Scan code patterns (`exports['es_extended']`, `QBCore = exports`, `require '@ox_core'`)
- [x] Return framework name, confidence level, and evidence

### Code generation improvements

- [x] Context-aware scaffolding that reads existing workspace for author/description
- [x] Smarter manifest generation that scans existing files for script paths and NUI
- [x] Template variable substitution utility (`substitute_variables`)
- [x] Workspace-aware `scaffold_resource_tool` and `generate_manifest_tool`

---

## Milestone 3.5 - Research Alignment (v0.6.0, complete)

Aligned the toolkit with 2026 platform realities based on comprehensive research audit. Added missing frameworks, modern patterns, and expanded content.

### New framework support

- [x] Qbox framework: detection, template, events (10), scaffold init, manifest_common
- [x] VORP framework (RedM): detection, template, events (4), scaffold init
- [x] RSG framework (RedM): detection, template, events (5), scaffold init
- [x] All 7 frameworks in detect_framework.py, manifest_common.py, scaffold.py, server.py

### Modern patterns and content

- [x] NUI Svelte 5 template with Vite and Runes ($state, $derived, $effect)
- [x] `node_version '22'` in JS template, manifest_gen, and scaffold output
- [x] Compile-time backtick hashing snippet and rule enhancement
- [x] Routing bucket (instancing) snippet and skill content
- [x] Lua 5.4 `<const>` and `<close>` variable attributes snippet and rule content
- [x] ACE permissions snippet
- [x] `setImmediate()` thread affinity warning in JS conventions and client-server skill
- [x] mysql-async/ghmattimysql explicit deprecation in database skill
- [x] `repository`, `version`, and `escrow_ignore` manifest directives in fxmanifest skill
- [x] `Citizen.` prefix explicitly deprecated across all rules and skills
- [x] NUI skill updated to recommend Svelte 5 as the community favorite

### Counts after M3.5

- 9 skills, 6 rules, 24 snippets, 11 templates, 6 MCP tools, 101 events

---

## Milestone 4 - Integration (planned)

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
- [ ] Bridge resource: a FiveM/RedM resource that connects to the MCP server for bidirectional debugging
- [ ] Player state inspection: read player data (position, health, vehicle) from a running server

### Server configuration

- [ ] server.cfg editor skill with convar reference
- [ ] Dependency resolver: check if required resources are present and started

---

## Milestone 5 - Polish (planned)

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

- [x] Expand RDR3 native database to full coverage (done in M2: 5800+ natives)
- [x] Add RedM-specific templates (VORP, RSG framework support) (done in M3.5)
- [ ] Add RedM-specific snippets (prompts, scenarios, RDR3 peds)
- [ ] RedM-specific coding conventions rule

### Community and marketplace

- [x] Plugin logo and branding assets
- [ ] Submission to the Cursor Marketplace (requires public Git repo, valid manifest, manual review)
- [ ] Community template contribution workflow (PR template, validation script)
- [ ] Plugin versioning and update strategy

### Documentation

- [ ] Video walkthrough or GIF demos for Getting Started
- [ ] Expanded architecture docs with MCP tool flow diagrams
- [ ] FAQ and troubleshooting guide
- [ ] Example resources built entirely with the plugin (showcase)
