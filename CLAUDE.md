<!-- standards-version: 1.9.4 -->

# CLAUDE.md

Project documentation for Claude Code and AI assistants working on this repository.

## Project Overview

CFX Developer Tools is a Cursor IDE plugin for FiveM and RedM (CFX) resource development. It includes 9 skills, 6 rules, 24 code snippets, 11 starter templates, and a companion Python MCP server with 6 tools for resource scaffolding, native lookup, manifest generation, framework detection, and live doc and event search.

**Works with:** Cursor (plugin), Claude Code (terminal and in-editor), and any MCP-compatible client.

This is a monorepo. Skills, rules, snippets, templates, and the companion MCP server live in the same repository because CFX resource development crosses all of those layers in a single workflow.

**Version:** 0.8.4
**License:** CC-BY-NC-ND-4.0
**Author:** TMHSDigital

## Plugin Architecture

```
CFX-Developer-Tools/
  .cursor-plugin/
    plugin.json              # Plugin manifest (version, skills, rules)
  skills/
    <skill-name>/
      SKILL.md               # One skill per directory (kebab-case)
  rules/
    <rule-name>.mdc          # Cursor rule files
  snippets/                  # Lua, JS, C# code snippets
  templates/                 # Resource starter templates
  mcp-server/
    server.py                # MCP server entry point (Python, FastMCP)
    tools/                   # One module per tool
    data/                    # Native databases, doc index, events
    requirements.txt
  docs/                      # MkDocs Material site
  .github/
    workflows/               # CI / release / native-update / docs-index automation
```

## Skills (9)

| Skill | Description |
|-------|-------------|
| `resource-scaffolding` | Generate a complete CFX resource skeleton (fxmanifest, client/server entries, NUI scaffolding) |
| `native-functions` | Look up GTA5, RDR3, and CFX-platform native functions with parameter and return types |
| `fxmanifest` | Author and validate `fxmanifest.lua` (fx_version, games, dependencies, NUI files, exports) |
| `client-server-patterns` | Event routing, NetEvents vs Events, callback patterns, state synchronization |
| `framework-detection` | Detect ESX / QBCore / Qbox / ox_core / VORP / RSG / standalone from a workspace |
| `performance-optimization` | Threads, OneSync, native batching, NUI message rate, and resource memory budget |
| `nui-development` | NUI lifecycle, message routing, asset loading, callbacks, and Vite / Svelte integration |
| `database-integration` | oxmysql, ghmattimysql, MariaDB connection patterns, prepared statements, migration flow |
| `state-bags` | StateBag CRUD, replicated vs local, change handlers, and replacement of legacy SetX patterns |

## Rules (6)

| Rule | Scope | Description |
|------|-------|-------------|
| `cfx-lua-conventions.mdc` | `**/*.lua` | Flag CFX-specific Lua antipatterns (string concat in tight loops, missing `local`, deprecated natives) |
| `cfx-javascript-conventions.mdc` | `**/*.js`, `**/*.ts` | Flag JS/TS antipatterns in CFX context (NUI message routing, async event handlers) |
| `cfx-csharp-conventions.mdc` | `**/*.cs` | Flag C# patterns specific to FiveM (BaseScript, Tick handlers, async exports) |
| `fxmanifest-standards.mdc` | `**/fxmanifest.lua` | Flag missing `fx_version`, `games`, `'cerulean'` declarations and deprecated directives like `lua54 'yes'` |
| `security-best-practices.mdc` | Global | Flag hardcoded API keys, server-trust violations, unsafe NUI callbacks, missing input validation |
| `performance-rules.mdc` | CFX resource files | Flag thread blockers, unbounded loops, missing `Wait()` in `CreateThread`, expensive natives in tight loops |

## MCP Server (6 tools)

The companion MCP server is Python-based (FastMCP). It exposes CFX-aware tools that read from local data files (`mcp-server/data/`) and the working tree.

| Tool | Description |
|------|-------------|
| `scaffold_resource_tool` | Generate a complete CFX resource (fxmanifest, client/server entries, optional NUI) from a name and framework selection |
| `lookup_native_tool` | Search GTA5, RDR3, and CFX-platform natives by name, hash, or namespace; returns parameters, return type, and usage notes |
| `generate_manifest_tool` | Author or update an `fxmanifest.lua` with required keys, dependencies, and NUI declarations |
| `search_events_tool` | Search the indexed CFX events database for canonical net-event and exports usage patterns |
| `detect_framework_tool` | Detect ESX / QBCore / Qbox / ox_core / VORP / RSG / standalone from a workspace path |
| `search_docs_tool` | Search the indexed `docs.fivem.net` snapshot for parameters, gotchas, and code samples |

## Development Workflow

### Plugin development (symlink)

**macOS / Linux:**
```bash
ln -s "$(pwd)" ~/.cursor/plugins/cfx-developer-tools
```

**Windows (PowerShell as Admin):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.cursor\plugins\cfx-developer-tools" -Target (Get-Location)
```

### MCP server development

```bash
cd mcp-server
pip install -r requirements.txt
python server.py
```

### Running validation

```bash
# JSON schema and content-count checks (run by CI)
python .github/scripts/validate_plugin.py

# Native database refresh (manual; usually run by update-natives.yml)
python .github/scripts/transform_natives.py
```

## Release Workflow

Releases are automated. The `release.yml` workflow:

1. Reads conventional commits since the last tag.
2. Computes the next semver bump (PATCH for `fix:`, MINOR for `feat:`, MAJOR for `BREAKING CHANGE`).
3. Updates `plugin.json` `version` and the README version badge.
4. Creates the tag, the GitHub Release, and floating major / minor tags.
5. Invokes `release-doc-sync` to update `**Version:**` in this file and prepend a CHANGELOG entry.
6. Syncs the GitHub repo "About" section (description, homepage, topics) with live artifact counts.

Do not hand-edit `plugin.json` `version`, the README badge, or the `**Version:**` line above. The release pipeline owns them.

## Key Conventions

- **No em dashes.** Use regular dashes (`-`) or rewrite the sentence. CI flags em and en dashes in markdown.
- **No hardcoded credentials.** Use environment variables, server-side `convar`s, or secrets stores. CI flags suspicious patterns.
- **Skill frontmatter:** `name` (matching directory) and `description` only.
- **Rule frontmatter:** `description`, `alwaysApply`, and `globs` (when path-scoped).
- **Snippets:** must compile or load cleanly inside a CFX resource (Lua / JS / C#), no placeholder credentials.
- **Templates:** every `fxmanifest.lua` must declare `fx_version`, `games`, and `'cerulean'`. Avoid `lua54 'yes'` (deprecated; use `lua54 true`).
- **MCP tool naming:** snake_case Python functions decorated with `@mcp.tool()`, suffix `_tool` for clarity in agent prompts.

## CFX Native Reference Quick Links

| Resource | Use |
|----------|-----|
| `runtime.fivem.net/doc/natives.json` | GTA5 native database upstream |
| `runtime.fivem.net/doc/natives_rdr3.json` | RDR3 native database upstream |
| `docs.fivem.net` | Authoritative scripting reference, refreshed monthly via `update-docs-index.yml` |
| `mcp-server/data/natives_gta5.json` | Local GTA5 native lookup index |
| `mcp-server/data/natives_rdr3.json` | Local RDR3 native lookup index |
| `mcp-server/data/events.json` | Indexed canonical CFX event names and payloads |
| `mcp-server/data/docs_index.json` | Indexed `docs.fivem.net` snippets for offline search |
