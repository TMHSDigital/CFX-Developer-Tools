<p align="center">
  <img src="assets/logo.png" alt="CFX Developer Tools" width="200">
</p>

<h1 align="center">CFX Developer Tools</h1>

<p align="center">
  <strong>AI-powered development toolkit for FiveM and RedM resource development in Cursor IDE.</strong>
</p>

<p align="center">
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/"><img src="https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg" alt="License: CC BY-NC-ND 4.0"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.8.4-blue.svg" alt="Version"></a>
  <a href="https://github.com/TMHSDigital/CFX-Developer-Tools/stargazers"><img src="https://img.shields.io/github/stars/TMHSDigital/CFX-Developer-Tools?style=flat" alt="GitHub stars"></a>
  <a href="https://tmhsdigital.github.io/CFX-Developer-Tools/"><img src="https://img.shields.io/badge/docs-online-blue?logo=materialformkdocs&logoColor=white" alt="Documentation"></a>
</p>

<p align="center">
  <a href="docs/GETTING-STARTED.md"><strong>Getting Started</strong></a> &bull;
  <a href="https://tmhsdigital.github.io/CFX-Developer-Tools/">Documentation</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#mcp-server">MCP Server</a> &bull;
  <a href="#skills-9">Skills</a> &bull;
  <a href="#rules-6">Rules</a> &bull;
  <a href="#roadmap">Roadmap</a>
</p>

---

<p align="center">
  9 skills &nbsp;&bull;&nbsp; 6 rules &nbsp;&bull;&nbsp; 6 MCP tools &nbsp;&bull;&nbsp; 12,000+ natives &nbsp;&bull;&nbsp; 101 events &nbsp;&bull;&nbsp; 24 snippets &nbsp;&bull;&nbsp; 11 templates
</p>

Scaffold complete FiveM/RedM resources, look up native functions, generate manifests, detect frameworks, search documentation, and write optimized scripts in Lua, JavaScript, and C# -- all from within Cursor's AI chat. Covers the full CFX development lifecycle from project setup to database integration.

<p align="center">
  <a href="docs/GETTING-STARTED.md"><img src="https://img.shields.io/badge/%F0%9F%93%96_Getting_Started_Guide-blue?style=for-the-badge" alt="Getting Started Guide"></a>
</p>

> **First time here?** The **[Getting Started guide](docs/GETTING-STARTED.md)** walks you through every step -- from installing Git, Python, and Cursor to building and deploying your first FiveM/RedM resource. No prior experience required.

## How It Works

```mermaid
flowchart LR
    A["You ask Cursor\na CFX question"] --> B["Cursor loads\na Skill"]
    B -->     C{"MCP server\navailable?"}
    C -- Yes --> D["CFX MCP Server\n(6 tools)"]
    C -- No --> E["Skill guidance\nonly"]
    D --> F["Scaffold, lookup,\ngenerate, search,\ndetect, docs"]
    E --> G["AI-assisted answer\nin Cursor chat"]
    F --> G
```

**Skills** teach Cursor how to handle CFX development prompts. **Rules** enforce FiveM/RedM best practices in your code. The **MCP server** provides programmatic tools so skills can scaffold resources, look up natives, and generate manifests directly.

## Quick Start

Already have Git, Python 3.10+, and Cursor installed? Here's the short version:

```bash
git clone https://github.com/TMHSDigital/CFX-Developer-Tools.git
# Open CFX-Developer-Tools folder in Cursor (File > Open Folder)
cd mcp-server && pip install -r requirements.txt
```

Then ask the AI agent to scaffold a resource, look up a native, or generate a manifest.

> **Need more detail?** The **[Getting Started guide](docs/GETTING-STARTED.md)** covers installing prerequisites, troubleshooting, and building your first resource step by step.

## Features

- **Resource scaffolding** -- Generate complete resources in Lua, JavaScript, or C# with proper `fxmanifest.lua`
- **Framework detection** -- Automatically detect and adapt to ESX, QBCore, Qbox, ox_core, VORP, RSG, or standalone
- **Native function lookup** -- Search GTA5/RDR3 native functions by name or description via MCP tools
- **Performance-aware coding rules** -- Catch common mistakes (`Wait(0)` in loops, runtime hashing, etc.)
- **Snippet library** -- 24 copy-paste-ready code patterns across all three runtimes
- **NUI development support** -- Skills and patterns for building in-game web UIs
- **Database integration** -- oxmysql query patterns, schema templates, and migration guidance
- **Event reference** -- Searchable database of 101 FiveM/RedM events across CFX, ESX, QBCore, Qbox, ox_core, VORP, and RSG
- **Documentation search** -- Query the FiveM/RedM docs index by keyword or section via MCP tools
- **Framework auto-detection** -- MCP tool that scans workspace files to detect ESX, QBCore, Qbox, ox_core, VORP, RSG, or standalone

<details>
<summary><strong>Supported Frameworks</strong></summary>

&nbsp;

| Framework | Game | Status |
|:----------|:-----|:-------|
| ESX | FiveM | Supported |
| QBCore | FiveM | Supported |
| Qbox | FiveM | Supported |
| ox_core | FiveM | Supported |
| VORP | RedM | Supported |
| RSG | RedM | Supported |
| Standalone | Both | Supported |

</details>

<details>
<summary><strong>Supported Languages</strong></summary>

&nbsp;

| Language | Client | Server |
|:---------|:-------|:-------|
| Lua | Yes | Yes |
| JavaScript | Yes | Yes |
| C# | Yes | Yes |

</details>

<details>
<summary><strong>Supported Games</strong></summary>

&nbsp;

| Game | Platform |
|:-----|:---------|
| GTA5 | FiveM |
| RDR3 | RedM |

</details>

## Skills (9)

| Skill | What it does |
|:------|:-------------|
| **Resource Scaffolding** | Generate complete resource boilerplate for any framework and language |
| **Native Functions** | Look up GTA5/RDR3 natives by name, hash, or description |
| **fxmanifest** | Author and validate `fxmanifest.lua` files with correct directives |
| **Client-Server Patterns** | Correct event communication, threading, and state sync patterns |
| **Framework Detection** | Auto-detect ESX, QBCore, Qbox, ox_core, VORP, RSG, or standalone and adapt code accordingly |
| **Performance Optimization** | Identify and fix CFX-specific performance pitfalls |
| **NUI Development** | Build in-game web UIs with proper message passing and devtools setup |
| **Database Integration** | oxmysql queries, schema design, migrations, and connection pooling |
| **State Bags** | Modern data sync with Entity/Player/Global state bags, change handlers, and security |

## Rules (6)

| Rule | What it does |
|:-----|:-------------|
| **Lua Conventions** | Enforces CFX Lua idioms -- locals, proper event handlers, vector types, variable attributes |
| **JavaScript Conventions** | Enforces CFX JavaScript patterns -- async/await, proper exports, event typing |
| **C# Conventions** | Enforces CitizenFX C# patterns -- `[FromSource]`, `BaseScript`, tick handlers |
| **fxmanifest Standards** | Validates manifest structure, version strings, dependency declarations |
| **Security Best Practices** | Flags server-side validation gaps, exposed endpoints, insecure patterns |
| **Performance Rules** | Catches `Wait(0)`, runtime hashing, unnecessary tick handlers, memory leaks |

## Snippets (24)

<details>
<summary><strong>Lua (14)</strong></summary>

&nbsp;

| Snippet | Description |
|:--------|:------------|
| `client-event.lua` | Client-side event handler template |
| `server-event.lua` | Server-side event handler with source validation |
| `register-command.lua` | Command registration with permission checks |
| `thread-loop.lua` | Thread with proper `Wait()` usage |
| `nui-callback.lua` | NUI callback handler for client-side |
| `export-function.lua` | Exported function pattern |
| `config-template.lua` | Shared config file structure |
| `state-bag-entity.lua` | Entity state bag set/read pattern |
| `state-bag-player.lua` | Player state bag set/read pattern |
| `state-bag-handler.lua` | State bag change handler |
| `backtick-hash.lua` | Compile-time hashing with backticks |
| `routing-bucket.lua` | Routing bucket (instance) management |
| `variable-attributes.lua` | Lua 5.4 `<const>` and `<close>` attributes |
| `ace-permissions.lua` | ACE permission checks and config |

</details>

<details>
<summary><strong>JavaScript (7)</strong></summary>

&nbsp;

| Snippet | Description |
|:--------|:------------|
| `client-event.js` | Client-side event handler |
| `server-event.js` | Server-side event handler |
| `register-command.js` | Command registration |
| `thread-loop.js` | Tick-based loop pattern |
| `nui-callback.js` | NUI callback registration |
| `state-bag-entity.js` | Entity state bag set/read pattern |
| `state-bag-handler.js` | State bag change handler |

</details>

<details>
<summary><strong>C# (3)</strong></summary>

&nbsp;

| Snippet | Description |
|:--------|:------------|
| `base-script.cs` | `BaseScript` class template |
| `tick-handler.cs` | Tick handler with async pattern |
| `register-command.cs` | Command registration with attributes |

</details>

## Templates (11)

| Template | Description |
|:---------|:------------|
| **Standalone** | Minimal Lua resource -- no framework dependency |
| **ESX** | ESX Legacy-ready resource with `es_extended` integration |
| **QBCore** | QBCore-ready resource with `qb-core` integration |
| **Qbox** | Qbox-ready resource with `qbx_core` integration |
| **ox_core** | ox_core-ready resource with `ox_lib` integration |
| **VORP** | VORP-ready RedM resource with `vorp_core` integration |
| **RSG** | RSG-ready RedM resource with `rsg-core` integration |
| **JavaScript** | Full JS resource with `node_version '22'`, client/server structure |
| **C#** | .NET resource with `.csproj`, compiled DLL pattern |
| **NUI Vite** | Modern NUI with Vite + React, postMessage bridge, and HMR |
| **NUI Svelte** | Modern NUI with Vite + Svelte 5, Runes, postMessage bridge |

## MCP Server

The companion MCP server provides programmatic tools that Cursor's AI agent can call directly. Configuration lives in `.cursor/mcp.json`.

**Prerequisites:** Python 3.10+

```bash
cd mcp-server
pip install -r requirements.txt
```

The server starts automatically when Cursor invokes an MCP tool.

<details>
<summary><strong>Available Tools (6)</strong></summary>

&nbsp;

| Tool | Description |
|:-----|:------------|
| `scaffold_resource_tool` | Create a new resource with boilerplate files for any framework/language combo. Inherits author from workspace. |
| `lookup_native_tool` | Search natives by name, hash, description, or category. Browse namespaces. |
| `generate_manifest_tool` | Generate a complete `fxmanifest.lua` with correct directives. Auto-detects scripts and NUI from workspace. |
| `search_events_tool` | Search 101 events by name, side, game, or framework (cfx, esx, qbcore, qbox, oxcore, vorp, rsg, baseevents, chat) |
| `detect_framework_tool` | Scan workspace files to detect ESX, QBCore, Qbox, ox_core, VORP, RSG, or standalone with confidence score |
| `search_docs_tool` | Search the FiveM/RedM documentation index by keyword or section |

</details>

<details>
<summary><strong>Usage Examples</strong></summary>

&nbsp;

**Scaffold a resource:**
```
Create a new QBCore resource called "qb-garage" with client and server scripts in Lua
```

**Look up a native:**
```
What native function gets a vehicle's current speed?
```

**Generate a manifest:**
```
Generate an fxmanifest.lua for an ESX resource with NUI, targeting both FiveM and RedM
```

**Search events:**
```
What events fire when a player connects to the server?
```

**Search documentation:**
```
How do I set up NUI callbacks?
```

**Detect framework:**
```
What framework does this resource use?
```

</details>

## Project Structure

```
CFX-Developer-Tools/
  .cursor-plugin/      Plugin manifest
  .cursor/             MCP server configuration
  skills/              AI skill files (9 skills)
  rules/               Coding convention rules (6 rules)
  snippets/            Code snippets -- Lua, JS, C# (24 files)
  templates/           Resource starter templates (11 sets)
  mcp-server/          Python MCP server (6 tools) and data files
  docs/                Architecture, roadmap, contributing guide, docs site landing page
  assets/              Logo and images
  .github/             CI/CD workflows (validate, release, update-natives, update-docs-index, stale, deploy-docs)
  mkdocs.yml           Documentation site configuration
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full project roadmap.

<details>
<summary><strong>Release Plan</strong></summary>

&nbsp;

| Version | Milestone | Status |
|:--------|:----------|:-------|
| **v0.1.x** | Foundation -- skills, rules, snippets, templates, MCP server, CI/CD | Done |
| **v0.2.0** | AGENTS.md and .cursorrules for AI agent guidance | Done |
| **v0.3.0** | Native DB expansion -- 6300+ GTA5, 5800+ RDR3, category browsing, deprecation flags | Done |
| **v0.4.x** | Content expansion -- State Bags skill, NUI Vite template, vector docs, FiveM/RedM balance | Done |
| **v0.5.0** | M3 Expansion -- docs search, 82 events, framework detection, smart code gen | Done |
| **v0.6.0** | M3.5 Research Alignment -- Qbox/VORP/RSG, Svelte NUI, 101 events, 24 snippets, 11 templates | Done |
| **v1.0.0** | Stable release -- marketplace listing, full documentation | Planned |

</details>

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on adding skills, rules, and improvements.

## Support

If this plugin is useful to you, consider [sponsoring the project](https://github.com/sponsors/TMHSDigital).

## License

CC BY-NC-ND 4.0 -- see [LICENSE](LICENSE) for details.

<details>
<summary><strong>CFX Reference Links</strong></summary>

&nbsp;

- [CFX Developer Tools Documentation](https://tmhsdigital.github.io/CFX-Developer-Tools/)
- [FiveM/RedM Documentation](https://docs.fivem.net/docs/)
- [GTA5 Native Reference](https://docs.fivem.net/natives/)
- [RDR3 Native Reference](https://rdr3natives.com/)
- [Cfx.re Forums](https://forum.cfx.re/)
- [Cfx.re Platform](https://cfx.re/)

</details>

---

<p align="center">
  <strong>Built by <a href="https://github.com/TMHSDigital">TMHSDigital</a></strong>
</p>
