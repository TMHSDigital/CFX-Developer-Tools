<!-- standards-version: 1.10.0 -->

# AGENTS.md

This file tells AI coding agents how the CFX Developer Tools repo works and how to contribute correctly.

**Documentation site:** https://tmhsdigital.github.io/CFX-Developer-Tools/ (auto-deployed on push to main)

## Repository overview

This is a Cursor IDE plugin for FiveM/RedM (CFX) resource development. It contains:

- **`.cursor-plugin/plugin.json`** -- plugin manifest (version, skills, rules)
- **`skills/`** -- 10 SKILL.md files teaching the AI domain-specific CFX knowledge
- **`rules/`** -- 6 .mdc rule files enforcing coding conventions
- **`snippets/`** -- 25 code snippet files (Lua, JS, C#)
- **`templates/`** -- 11 resource starter templates (standalone, ESX, QBCore, Qbox, ox_core, VORP, RSG, JS, C#, NUI Vite, NUI Svelte)
- **`examples/`** -- 5 complete, runnable reference resources
- **`mcp-server/`** -- Python MCP server (FastMCP, stdio) with 10 tools, JSON data files and a pytest suite
- **`docs/`** -- ARCHITECTURE.md, ROADMAP.md, CONTRIBUTING.md, GETTING-STARTED.md, index.md (docs site landing page)
- **`CHANGELOG.md`** -- release history; the release workflow's `release-doc-sync` step prepends each release entry
- **`mkdocs.yml`** -- MkDocs Material configuration for the documentation site
- **`.github/workflows/`** -- CI/CD automation (validate, release, drift-check, update-natives, update-docs-index, deploy-docs, stale)

## Branching and commit model

- **Single branch**: `main` only. No develop/release branches.
- **Conventional commits** are required. The release workflow parses them:
  - `feat:` or `feat(scope):` -- triggers a **minor** version bump
  - Any `<type>!:` (for example `feat!:` or `fix!:`) or a `BREAKING CHANGE:` footer -- triggers a **major** version bump
  - `fix:` or `perf:` -- triggers a **patch** bump
  - Everything else (`chore:`, `docs:`, `ci:`, `test:`, `refactor:`, etc.) -- no release
- Commit messages should be concise and describe the "why", not the "what".

## CI/CD workflows

### `validate.yml` (runs on PR and push to main)

Checks:
- JSON validity for plugin.json, mcp.json, native databases, events
- Plugin manifest required fields, kebab-case name, skill/rule file existence
- Content counts in README match actual files on disk (skills, rules, snippets, templates)
- Em dash and en dash detection (use hyphens, not em/en dashes)
- Hardcoded credential patterns
- Any `lua54` directive in templates or examples
- fxmanifest.lua templates have `fx_version`, `games`, `'cerulean'`
- Python syntax for all MCP server modules

### `release.yml` (runs after `validate.yml` succeeds for a push to main)

Automatic flow (skipped entirely when Validate fails or there are no release-worthy commits):
1. Reads current version from `plugin.json`
2. Determines bump type from conventional commit messages since last tag
3. Computes new semver version
4. Updates `plugin.json` version and `README.md` version badge
5. Commits with `[skip ci]` to prevent re-triggering
6. Creates git tag `vX.Y.Z`
7. Creates GitHub Release with grouped release notes

Has a concurrency guard -- only one release can run at a time to prevent race conditions.

After a successful release, the workflow also syncs the GitHub repository "About" section (description, homepage URL, and topics) via `gh repo edit`. The description is generated from artifact counts computed from the tree (skills, rules, snippets, templates, events, MCP tools, natives).

**Do not manually edit the version in plugin.json or the README badge.** The release workflow owns both.

**Do not manually edit the GitHub repo About section** (description, homepage, topics). The release workflow syncs it automatically on every release.

**CHANGELOG.md release entries are written by the release workflow** (`release-doc-sync`). Do not hand-write version entries; edit the generated entry afterwards only to add detail.

### `update-natives.yml` (weekly on Monday 06:00 UTC, or manual dispatch)

1. Fetches compiled native JSON from `runtime.fivem.net/doc/` (GTA5, RDR3, and CFX platform natives)
2. Transforms via `.github/scripts/transform_natives.py` into the plugin's flat schema
3. Validates the output (checks required fields, types, counts)
4. If changed, commits and pushes directly to main with `chore:` prefix

### `update-docs-index.yml` (monthly on 1st at 06:00 UTC, or manual dispatch)

1. Runs `.github/scripts/build_docs_index.py` to crawl ~80 pages from docs.fivem.net
2. Writes result to `mcp-server/data/docs_index.json`
3. Validates structure (title, url, section, snippet required)
4. If changed, commits and pushes directly to main with `chore:` prefix

### `deploy-docs.yml` (runs on push to main and manual dispatch)

Builds the MkDocs Material documentation site from the repository's Markdown files and deploys it to GitHub Pages via `actions/deploy-pages`. The site URL is https://tmhsdigital.github.io/CFX-Developer-Tools/.

### `stale.yml`

Marks issues/PRs as stale after inactivity and closes them after further inactivity.

## Version management

- The **source of truth** for the current version is `.cursor-plugin/plugin.json`.
- The release workflow auto-bumps it and the README badge on every qualifying push to main.
- Never manually change the version unless you know the release workflow won't run (e.g., docs-only changes).

## Code conventions

- **No em dashes or en dashes** -- use hyphens or rewrite. CI will reject them.
- **No `lua54` directive** -- `lua54 'yes'` is deprecated and `lua54 true` is invalid Lua. Lua 5.4 is the only CFX runtime. CI rejects any `lua54` line in templates and examples.
- **No hardcoded credentials** -- CI scans for password/token/api_key patterns.
- fxmanifest.lua must use `fx_version 'cerulean'` and include `games`.
- Python code in `mcp-server/` must pass `py_compile`.
- Snippets, templates, and skills should be accurate to the current FiveM/RedM APIs.

## Adding content

### New skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (`title`, `description`, `standards-version`, and `globs` when file-scoped)
2. Add the path to `plugin.json` under `"skills"`
3. Update counts in README.md stats line and skills table
4. Use `fix:` or `feat:` commit prefix depending on scope

### New rule

1. Create `rules/<rule-name>.mdc` with frontmatter (`title`, `description`, `globs`, `alwaysApply`, `standards-version`)
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
- Tools: `mcp-server/tools/` (scaffold.py, natives.py, manifest_gen.py, event_search.py, docs_search.py, detect_framework.py, txadmin.py, txadmin_client.py)
- Tests: `mcp-server/tests/` (`python -m pytest` after `pip install -r requirements-dev.txt`)
- Shared logic: `mcp-server/tools/manifest_common.py`
- Data: `mcp-server/data/` (natives_gta5.json, natives_rdr3.json, events.json, docs_index.json)
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
- Events use `{ "name", "side", "description", "params", "game", "framework" }`. 101 events across cfx, baseevents, chat, esx, qbcore, qbox, oxcore, vorp, rsg frameworks.
- `docs_index.json` is a searchable index of ~80 FiveM/RedM docs pages, rebuilt monthly by CI. Schema: `{ "title", "url", "section", "snippet" }`.
- The `detect_framework_tool` scans fxmanifest.lua dependencies (highest weight) and code patterns (`exports['es_extended']`, `QBCore = exports`, `exports['qbx_core']`, `require '@ox_core'`, `exports.vorp_core`, `exports['rsg-core']`) to report framework, confidence, and evidence. Supports ESX, QBCore, Qbox, ox_core, VORP, RSG, and standalone.

## License

CC-BY-NC-ND-4.0. All contributions fall under this license.
