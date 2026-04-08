# Changelog

## 0.2.0 - 2026-04-08

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

## 0.1.1 - 2026-04-08

### Fixed

- Updated README with logo, badges, collapsible sections, and Mermaid architecture diagram

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
  - Scheduled weekly native database update from citizenfx/natives (auto-transform, auto-merge)
  - Stale issue/PR cleanup

### Fixed

- Removed deprecated `lua54 'yes'` directive from all templates and code generation (Lua 5.4 is now the only runtime)
