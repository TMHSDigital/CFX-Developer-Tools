<!-- standards-version: 1.10.0 -->

# CLAUDE.md

Project documentation for Claude Code and AI assistants working on this repository.

## Project Overview

CFX Developer Tools is a Cursor IDE plugin for FiveM and RedM (CFX) resource development. It includes 10 skills, 6 rules, 24 code snippets, 11 starter templates, and a companion Python MCP server with 10 tools for resource scaffolding, native lookup, manifest generation, framework detection, live doc and event search, and txAdmin server control.

**Works with:** Cursor (plugin), Claude Code (terminal and in-editor), and any MCP-compatible client.

This is a monorepo. Skills, rules, snippets, templates, and the companion MCP server live in the same repository because CFX resource development crosses all of those layers in a single workflow.

**Version:** 0.11.2
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
  templates/                 # Resource starter templates (blank per-framework skeletons)
  examples/                  # Complete, runnable reference resources
  mcp-server/
    server.py                # MCP server entry point (Python, FastMCP)
    tools/                   # One module per tool
    data/                    # Native databases, doc index, events
    requirements.txt
  docs/                      # MkDocs Material site
  .github/
    workflows/               # CI / release / native-update / docs-index automation
```

## Skills (10)

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
| `txadmin-integration` | Control a running server, manage resources, search players, and kick players through the txAdmin API |

## Rules (6)

| Rule | Scope | Description |
|------|-------|-------------|
| `cfx-lua-conventions.mdc` | `**/*.lua` | Flag CFX-specific Lua antipatterns (string concat in tight loops, missing `local`, deprecated natives) |
| `cfx-javascript-conventions.mdc` | `**/*.js`, `**/*.ts` | Flag JS/TS antipatterns in CFX context (NUI message routing, async event handlers) |
| `cfx-csharp-conventions.mdc` | `**/*.cs` | Flag C# patterns specific to FiveM (BaseScript, Tick handlers, async exports) |
| `fxmanifest-standards.mdc` | `**/fxmanifest.lua` | Flag missing `fx_version`, `games`, `'cerulean'` declarations and deprecated directives like `lua54 'yes'` |
| `security-best-practices.mdc` | Global | Flag hardcoded API keys, server-trust violations, unsafe NUI callbacks, missing input validation |
| `performance-rules.mdc` | CFX resource files | Flag thread blockers, unbounded loops, missing `Wait()` in `CreateThread`, expensive natives in tight loops |

## MCP Server (10 tools)

The companion MCP server is Python-based (FastMCP). It exposes CFX-aware tools that read from local data files (`mcp-server/data/`) and the working tree. The txAdmin tools additionally talk to a running txAdmin panel over HTTP, using credentials from the `TXADMIN_URL` / `TXADMIN_USERNAME` / `TXADMIN_PASSWORD` environment variables.

| Tool | Description |
|------|-------------|
| `scaffold_resource_tool` | Generate a complete CFX resource (fxmanifest, client/server entries, optional NUI) from a name and framework selection |
| `lookup_native_tool` | Search GTA5, RDR3, and CFX-platform natives by name, hash, or namespace; returns parameters, return type, and usage notes |
| `generate_manifest_tool` | Author or update an `fxmanifest.lua` with required keys, dependencies, and NUI declarations |
| `search_events_tool` | Search the indexed CFX events database for canonical net-event and exports usage patterns |
| `detect_framework_tool` | Detect ESX / QBCore / Qbox / ox_core / VORP / RSG / standalone from a workspace path |
| `search_docs_tool` | Search the indexed `docs.fivem.net` snapshot for parameters, gotchas, and code samples |
| `txadmin_server_control_tool` | Start, stop, or restart the FXServer through a running txAdmin panel |
| `txadmin_resource_control_tool` | Start, stop, restart, or ensure a single resource through txAdmin |
| `txadmin_player_search_tool` | Search players known to the server by name, notes, or identifier through txAdmin |
| `txadmin_kick_player_tool` | Kick an online player by netid through txAdmin |

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
- **`rdr3` is the RedM identifier, not a game.** Cfx.re uses `rdr3` for the RedM platform, which targets Red Dead Redemption 2. There is no "Red Dead Redemption 3." Keep `rdr3` verbatim in manifests (`game 'rdr3'`), native database filenames/URLs, the MCP `game` enum, and framework detection. Do not rename it to `rdr2`; doing so breaks resource loading and the native data references.

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

# context-mode - MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional - they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands - do NOT attempt these

### curl / wget - BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP - BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox - only stdout enters context

### WebFetch - BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools - use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` - run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` - run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` - Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` - Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` - Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` - Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` - Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES - never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
