# Contributing

Thank you for your interest in contributing to CFX Developer Tools.

## How to contribute

### Reporting issues

Open a GitHub issue with:
- A clear description of the problem
- Steps to reproduce (if applicable)
- Expected vs actual behavior
- Your environment (OS, Cursor version, Python version)

### Suggesting features

Open a GitHub issue with the "feature request" label. Describe:
- What you want the plugin to do
- Why it would be useful
- Any examples or references

### Submitting changes

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Test your changes in Cursor
5. Submit a pull request

## What to contribute

### Templates

Add new resource templates for additional frameworks or use cases:
- Place them in `templates/your-template-name/`
- Include a complete `fxmanifest.lua`
- Include working client and server scripts
- Follow existing template conventions

### Snippets

Add code patterns for common tasks:
- Place them in the correct language folder under `snippets/`
- Include a header comment explaining what the snippet does and when to use it
- Keep snippets focused on a single pattern

### Native data

The native databases (`mcp-server/data/natives_gta5.json`, `natives_rdr3.json`) are **auto-generated** by a weekly CI workflow that fetches from `runtime.fivem.net/doc/`. Do not edit them manually.

To improve the native transformation logic:
- Edit `.github/scripts/transform_natives.py`
- Changes to side classification, description parsing, or schema mapping go there
- You can trigger a manual update via `gh workflow run update-natives.yml`

### Events data

Help expand the event reference database:
- `mcp-server/data/events.json`
- Follow the existing JSON structure: `name`, `side`, `description`, `params`, `game`
- Include accurate side (client/server/shared) and parameter lists

### Documentation

Improve or expand documentation:
- Fix typos or unclear explanations
- Add examples
- Update outdated information

Documentation changes auto-deploy to the [docs site](https://tmhsdigital.github.io/CFX-Developer-Tools/) when merged to main.

## Code style

- No em dashes anywhere - use hyphens or rewrite the sentence
- No hardcoded credentials, tokens, or passwords
- Follow existing file naming conventions
- Keep fxmanifest.lua syntax consistent with the fxmanifest-standards rule

## License

By contributing, you agree that your contributions will be licensed under the project's CC-BY-NC-ND-4.0 license.
