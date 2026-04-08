# Changelog

## 0.5.0 - 2026-04-08

### Added

- Documentation search MCP tool (`search_docs_tool`) with local index of ~80 FiveM/RedM docs pages
- Framework auto-detection MCP tool (`detect_framework_tool`) scanning fxmanifest deps and code patterns
- CI workflow (`update-docs-index.yml`) for monthly docs index rebuilds
- `build_docs_index.py` CI script to crawl and index docs.fivem.net pages
- Event `game` and `framework` fields for filtering by GTA5/RDR3 and framework origin
- 62 new events: ESX (15), QBCore (15), ox_core (8), chat (7), and additional CFX platform events
- Framework and game filters to `search_events_tool`
- Workspace scanning utilities (`read_workspace_context`, `scan_script_files`, `detect_nui_presence`) in manifest_common.py
- Template variable substitution (`substitute_variables`) in manifest_common.py

### Changed

- Event reference expanded from 20 to 82 events with framework/game metadata
- `scaffold_resource_tool` now accepts `workspace_path` to inherit author from existing manifests
- `generate_manifest_tool` now accepts `workspace_path` to auto-detect scripts, author, and NUI presence
- MCP server tool count increased from 4 to 6
- docs_index.json validation added to validate.yml
- detect_framework.py added to py_compile checks in validate.yml

## 0.4.1 - 2026-04-08

### Fixed

- Balanced FiveM/RedM representation across all documentation, skills, templates, and snippets
- Updated template `fxmanifest.lua` files to include `rdr3` where appropriate with comments
- Fixed FiveM-only language in database integration, fxmanifest, NUI, and native function skills

## 0.4.0 - 2026-04-08

### Added

- State Bags skill covering Entity/Player/Global state, change handlers, replication, and security
- State Bags snippets for Lua (entity, player, handler) and JavaScript (entity, handler)
- NUI Vite + React template with postMessage bridge, TypeScript, and HMR dev workflow
- CfxLua vector/quaternion type documentation in Lua conventions rule and client-server patterns skill

### Changed

- Updated README with prominent Getting Started guide links, large badge, and callout
- Rewrote Getting Started guide for complete beginners with collapsible sections

## 0.3.0 - 2026-04-08

### Added

- Expanded GTA5 native database from 50 stubs to 6300+ real natives from runtime.fivem.net
- Expanded RDR3 native database from 10 stubs to 5800+ real natives from runtime.fivem.net
- Merged 942 CFX platform natives with accurate apiset-based side classification
- Native hash field in output schema
- Deprecation flags for deprecated natives
- Usage examples extracted from upstream documentation
- Namespace/category browsing in `lookup_native_tool` (44 GTA5 categories, 84 RDR3 categories)
- Category listing mode when query is empty
- Hash-based native lookup

### Changed

- Native data source updated from citizenfx/natives (MDX, non-existent JSON) to runtime.fivem.net/doc/ (compiled JSON)
- Weekly update workflow now fetches GTA5, RDR3, and CFX natives separately
- Schema validation in CI now checks for hash, deprecated, and examples fields
- Side classification uses upstream apiset field for CFX natives instead of regex heuristics

## 0.2.0 - 2026-04-08

### Added

- AGENTS.md for AI agent guidance and repository conventions
- .cursorrules file for Cursor-specific context

## 0.1.2 - 2026-04-08

### Fixed

- Updated README version badge to match release tags
- Enhanced release workflow to automatically update README badge on version bump

## 0.1.1 - 2026-04-08

### Fixed

- Updated README with logo, badges, collapsible sections, and Mermaid architecture diagram
- Updated RedM native reference links to working URL (rdr3natives.com)

## 0.1.0 - 2026-04-08

### Added

- Initial repository structure and Cursor plugin manifest
- 8 AI skills: resource scaffolding, native functions, fxmanifest, client-server patterns, framework detection, performance optimization, NUI development, database integration
- 6 coding rules: Lua conventions, JavaScript conventions, C# conventions, fxmanifest standards, security best practices, performance rules
- 15 code snippets across Lua (7), JavaScript (5), and C# (3)
- 6 resource templates: standalone, ESX, QBCore, ox_core, JavaScript, C#
- MCP server with 4 tools: scaffold_resource, lookup_native, generate_manifest, search_events
- Native function databases for GTA5 (50 natives) and RDR3 (10 natives)
- Common events reference database (20 events)
- Documentation: Getting Started, Architecture, Contributing, Roadmap
- GitHub Actions CI/CD:
  - PR validation (JSON lint, manifest checks, em dash detection, template validation, Python syntax)
  - Auto version bump, tag, and GitHub Release on merge to main (conventional commits)
  - Scheduled weekly native database update from runtime.fivem.net (auto-transform, auto-merge)
  - Stale issue/PR cleanup

### Fixed

- Removed deprecated `lua54 'yes'` directive from all templates and code generation (Lua 5.4 is now the only runtime)
