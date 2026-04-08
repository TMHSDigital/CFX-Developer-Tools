# Getting Started

This guide walks you through setting up CFX Developer Tools in Cursor and creating your first FiveM/RedM resource.

## Prerequisites

- [Cursor IDE](https://cursor.com/) installed
- Python 3.10+ (for the MCP server)
- A FiveM or RedM server to test resources on

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/TMHSDigital/CFX-Developer-Tools.git
```

### 2. Open in Cursor

Open the cloned `CFX-Developer-Tools` folder in Cursor. The plugin auto-activates based on the `.cursor-plugin/plugin.json` manifest.

### 3. Set up the MCP server

```bash
cd mcp-server
pip install -r requirements.txt
```

The MCP server is configured in `.cursor/mcp.json` and will start automatically when Cursor needs it.

### 4. Verify the setup

Open Cursor's AI chat and try:

> "Scaffold a new FiveM resource called my-first-resource using Lua and standalone framework"

The agent should use the resource-scaffolding skill and MCP tools to create a complete resource.

## Your first resource

### Option A: Use the AI agent

Ask the agent in Cursor chat:

> "Create a new FiveM resource called my-garage that lets players store and retrieve vehicles. Use QBCore framework and Lua."

The agent will:
1. Detect you want QBCore
2. Generate the full directory structure
3. Create fxmanifest.lua with the correct dependencies
4. Write client and server scripts with QBCore boilerplate
5. Set up a config.lua with customizable settings

### Option B: Use a template

Copy one of the template directories from `templates/` into your server's `resources/` folder:

```bash
cp -r templates/standalone/ resources/my-resource/
```

Then edit the files to match your needs.

## Next steps

- Read the [Architecture](ARCHITECTURE.md) doc to understand how the plugin works
- Check the snippets in `snippets/` for common code patterns
- Browse the skills in `skills/` to see what the AI agent can help with
- Review the rules in `rules/` for coding conventions the agent follows
