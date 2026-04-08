# Changelog

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
