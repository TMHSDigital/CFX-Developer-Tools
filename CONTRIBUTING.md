# Contributing to CFX Developer Tools

Thanks for helping improve this plugin. This document describes how to set up locally, extend skills and rules, and submit changes.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/<your-username>/CFX-Developer-Tools.git
   cd CFX-Developer-Tools
   ```

3. **Create a branch** for your work:

   ```bash
   git checkout -b your-feature-name
   ```

## Local Development

Install the plugin from your working copy so Cursor loads your changes. Cursor loads local plugins from `~/.cursor/plugins/local/<name>` and skips symlinks that point outside that folder, so the simplest setup is to clone your fork straight into it:

**macOS / Linux:**

```bash
git clone https://github.com/<your-username>/CFX-Developer-Tools.git ~/.cursor/plugins/local/cfx-developer-tools
cd ~/.cursor/plugins/local/cfx-developer-tools
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/<your-username>/CFX-Developer-Tools.git "$env:USERPROFILE\.cursor\plugins\local\cfx-developer-tools"
Set-Location "$env:USERPROFILE\.cursor\plugins\local\cfx-developer-tools"
```

Restart Cursor after cloning so it picks up the plugin.

### Running the MCP server tests

The MCP server has a pytest suite in `mcp-server/tests/`. It needs no network access (txAdmin is tested against a local fake panel) and runs in CI on every pull request and push to `main`.

```bash
cd mcp-server
pip install -r requirements-dev.txt
python -m pytest
```

Add or update a test in `mcp-server/tests/` with every change to `mcp-server/tools/`.

## Plugin Structure

The repo is organized as a Cursor plugin with **10 skills** and **6 rules**, plus snippets, templates, and a companion MCP server.

```text
.cursor-plugin/
  plugin.json
skills/
  <skill-name-kebab>/
    SKILL.md
rules/
  <rule-name>.mdc
snippets/
templates/
mcp-server/
  server.py
  tools/
  data/
docs/
.github/
  workflows/
```

- **`plugin.json`** - manifest (name, version, paths to skills/rules).
- **`skills/`** - one directory per skill; each contains `SKILL.md`.
- **`rules/`** - Cursor rules as `.mdc` files with YAML frontmatter.
- **`snippets/`** - Lua / JS / C# code snippets for FiveM and RedM scripting patterns.
- **`templates/`** - resource starter templates (standalone, ESX, QBCore, Qbox, ox_core, VORP, RSG, JS, C#, NUI Vite, NUI Svelte).
- **`examples/`** - complete, runnable reference resources.
- **`mcp-server/`** - Python MCP server exposing CFX-aware tools (resource scaffolding, native lookup, manifest generation, framework detection, doc and event search, txAdmin server control), with tests in `mcp-server/tests/`.

## Adding a Skill

1. Add a **kebab-case** directory under `skills/`, e.g. `skills/cfx-example-flow/`.
2. Create **`SKILL.md`** with the same YAML frontmatter as the existing skills: `title`, `description`, `standards-version`, and `globs` when the skill applies to specific files. (The Developer-Tools-Directory skills standard specifies `name`, `description` and `triggers`; the existing skills have not been migrated to it yet, so match the existing files.)
3. Structure the body like the existing skills: an overview, then focused `##` sections with working code examples, common pitfalls, and links to related skills or rules.
4. Register the path in `.cursor-plugin/plugin.json` under `"skills"` and update the counts (CI checks them with `.github/scripts/counts.py`).

Match tone, formatting, and frontmatter style of existing skills in this repo.

## Adding a Rule

1. Add a **`.mdc`** file under `rules/`, e.g. `rules/cfx-example.mdc`.
2. Start with YAML **frontmatter**:
   - `title` - short human-readable name.
   - `description` - one-line summary for humans and tooling.
   - `standards-version` - copy the value used by the existing rules.
   - `alwaysApply` - `true` or `false` depending on whether the rule should apply globally.
   - `globs` - optional glob patterns (e.g. `**/*.lua`, `**/fxmanifest.lua`) when the rule is path-scoped.

3. Below the frontmatter, write the rule content in Markdown (constraints, patterns, anti-patterns).

Keep rules focused; prefer linking to a skill for long workflows.

## Adding a Snippet or Template

1. Snippets live under `snippets/` grouped by language (Lua, JS, C#). Each file should be self-contained, runnable in a CFX resource, and free of hardcoded credentials.
2. Templates live under `templates/`. A new template needs at least an `fxmanifest.lua` (with `fx_version`, `games`, and `'cerulean'`), the canonical client/server entry files, and any framework-specific config the template targets.
3. There is no separate validator script: `.github/workflows/validate.yml` checks `fxmanifest.lua` required keys, rejects any `lua54` directive, syntax-checks Lua (`luac -p`) and JS (`node --check`) in snippets, templates and examples, and verifies documented counts with `python .github/scripts/counts.py --require README.md --check README.md`.

## Pull Request Process

1. **Update docs** if you change behavior, skill lists, snippet counts, or versioning (`README.md`, `CLAUDE.md`, `CHANGELOG.md`, `docs/ROADMAP.md` as appropriate).
2. **Run checks** locally where possible: the MCP server tests (`cd mcp-server && python -m pytest`), the counts check above, and `node --check` / `luac -p` on changed snippets. CI also runs JSON schema checks, kebab-case enforcement, em/en dash detection, credential scans and deprecated-directive scans.
3. **Open a PR** against `main` with a clear title and summary of changes. Use a conventional commit prefix (`feat:`, `fix:`, `docs:`, `chore:`).
4. **Respond to review** feedback; CI must pass before merge.

## Developer Certificate of Origin and Inbound License Grant

This project uses CC-BY-NC-ND-4.0 as its outbound license, which forbids derivatives. Every pull request is a derivative. Contributions are accepted inbound under a broader grant via the Developer Certificate of Origin (DCO), which resolves the conflict so the project can accept and redistribute contributions.

### Required grant

By submitting a contribution to this repository, you certify that you have the right to do so under the Developer Certificate of Origin (DCO) 1.1, and you grant TMHSDigital a perpetual, worldwide, non-exclusive, royalty-free, irrevocable license to use, reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute your contribution under the project's current license (CC-BY-NC-ND-4.0) or any successor license chosen by the project.

### DCO sign-off

Every commit in a pull request must have a `Signed-off-by:` trailer matching the commit author:

```
Signed-off-by: Jane Developer <jane@example.com>
```

Signing is done at commit time:

```bash
git commit -s -m "feat: add new skill"
```

The GitHub DCO App enforces this on every PR.

For the full inbound/outbound model and rationale, see [`standards/licensing.md`](https://github.com/TMHSDigital/Developer-Tools-Directory/blob/main/standards/licensing.md) in the Developer-Tools-Directory meta-repo.

## Conduct

Be respectful and constructive in issues, pull requests and reviews.
