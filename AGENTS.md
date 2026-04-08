# AGENTS.md

This file tells AI coding agents how the CFX Developer Tools repo works and how to contribute correctly.

## Repository overview

This is a Cursor IDE plugin for FiveM/RedM (CFX) resource development. It contains:

- **`.cursor-plugin/plugin.json`** -- plugin manifest (version, skills, rules)
- **`skills/`** -- 9 SKILL.md files teaching the AI domain-specific CFX knowledge
- **`rules/`** -- 6 .mdc rule files enforcing coding conventions
- **`snippets/`** -- 20 code snippet files (Lua, JS, C#)
- **`templates/`** -- 7 resource starter templates (standalone, ESX, QBCore, ox_core, JS, C#, NUI Vite)
- **`mcp-server/`** -- Python MCP server with 4 tools and JSON data files
- **`docs/`** -- ARCHITECTURE.md, ROADMAP.md, CONTRIBUTING.md, GETTING-STARTED.md
- **`CHANGELOG.md`** -- manually maintained release history (not auto-generated)
- **`.github/workflows/`** -- CI/CD automation

## Branching and commit model

- **Single branch**: `main` only. No develop/release branches.
- **Conventional commits** are required. The release workflow parses them:
  - `feat:` or `feat(scope):` -- triggers a **minor** version bump
  - `feat!:` or `BREAKING CHANGE` -- triggers a **major** version bump
  - Everything else (`fix:`, `chore:`, `docs:`, `refactor:`, etc.) -- triggers a **patch** bump
- Commit messages should be concise and describe the "why", not the "what".

## CI/CD workflows

### `validate.yml` (runs on PR and push to main)

Checks:
- JSON validity for plugin.json, mcp.json, native databases, events
- Plugin manifest required fields, kebab-case name, skill/rule file existence
- Content counts in README match actual files on disk (skills, rules, snippets, templates)
- Em dash and en dash detection (use hyphens, not em/en dashes)
- Hardcoded credential patterns
- Deprecated `lua54 'yes'` directive in templates
- fxmanifest.lua templates have `fx_version`, `games`, `'cerulean'`
- Python syntax for all MCP server modules

### `release.yml` (runs on push to main, ignores docs/md/github changes)

Automatic flow:
1. Reads current version from `plugin.json`
2. Determines bump type from conventional commit messages since last tag
3. Computes new semver version
4. Updates `plugin.json` version and `README.md` version badge
5. Commits with `[skip ci]` to prevent re-triggering
6. Creates git tag `vX.Y.Z`
7. Creates GitHub Release with grouped release notes

Has a concurrency guard -- only one release can run at a time to prevent race conditions.

**Do not manually edit the version in plugin.json or the README badge.** The release workflow owns both.

**CHANGELOG.md is manually maintained.** Update it when making significant changes. The release workflow does not auto-update it.

### `update-natives.yml` (weekly on Monday 06:00 UTC, or manual dispatch)

1. Fetches compiled native JSON from `runtime.fivem.net/doc/` (GTA5, RDR3, and CFX platform natives)
2. Transforms via `.github/scripts/transform_natives.py` into the plugin's flat schema
3. Validates the output (checks required fields, types, counts)
4. If changed, commits and pushes directly to main with `chore:` prefix

### `stale.yml`

Marks issues/PRs as stale after inactivity and closes them after further inactivity.

## Version management

- The **source of truth** for the current version is `.cursor-plugin/plugin.json`.
- The release workflow auto-bumps it and the README badge on every qualifying push to main.
- Never manually change the version unless you know the release workflow won't run (e.g., docs-only changes).

## Code conventions

- **No em dashes or en dashes** -- use hyphens or rewrite. CI will reject them.
- **No `lua54 'yes'`** -- it is deprecated. Lua 5.4 is the only CFX runtime. CI will reject this in templates.
- **No hardcoded credentials** -- CI scans for password/token/api_key patterns.
- fxmanifest.lua must use `fx_version 'cerulean'` and include `games`.
- Python code in `mcp-server/` must pass `py_compile`.
- Snippets, templates, and skills should be accurate to the current FiveM/RedM APIs.

## Adding content

### New skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (title, description, globs)
2. Add the path to `plugin.json` under `"skills"`
3. Update counts in README.md stats line and skills table
4. Use `fix:` or `feat:` commit prefix depending on scope

### New rule

1. Create `rules/<rule-name>.mdc` with frontmatter (`description`, `globs`, `alwaysApply`)
2. Add the path to `plugin.json` under `"rules"`

### New snippet

1. Add the file to `snippets/<language>/` (lua, javascript, csharp)
2. Include a header comment explaining what the snippet does
3. Update counts in README.md stats line and relevant snippet tables
4. CI will fail if README counts don't match actual file counts

### New template

1. Create `templates/<template-name>/` with at minimum `fxmanifest.lua`
2. Include working client/server scripts
3. Do not include `lua54 'yes'`

### Updating native databases

Do not manually edit `mcp-server/data/natives_*.json`. The `update-natives.yml` workflow handles this automatically. If you need to change the transformation logic, edit `.github/scripts/transform_natives.py`.

## MCP server

- Entry point: `mcp-server/server.py`
- Tools: `mcp-server/tools/` (scaffold.py, natives.py, manifest_gen.py, event_search.py)
- Shared logic: `mcp-server/tools/manifest_common.py`
- Data: `mcp-server/data/` (natives_gta5.json, natives_rdr3.json, events.json)
- Dependencies: `mcp-server/requirements.txt` (pinned ranges)

The MCP server is configured in `.cursor/mcp.json` and starts automatically when Cursor invokes a tool.

## Key technical facts

- FiveM and RedM only support Lua 5.4 (5.3 removed). The `lua54 'yes'` directive is deprecated and ignored.
- C# resources compile to a single DLL referenced in both `client_scripts` and `server_scripts`.
- `Wait(0)` in Lua loops is a performance anti-pattern in most cases; use appropriate wait times.
- Server-side event handlers must validate `source` to prevent spoofing.
- The native databases use a flat JSON array schema with `name`, `hash`, `params`, `return_type`, `description`, `category`, `side`, `deprecated`, `examples`.
- Native data is sourced from `runtime.fivem.net/doc/` -- GTA5, RDR3, and CFX platform natives are merged per game file.
- The `lookup_native_tool` supports keyword search, hash lookup, category browsing, and side filtering.

## License

CC-BY-NC-ND-4.0. All contributions fall under this license.
