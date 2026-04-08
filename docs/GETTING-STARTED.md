# Getting Started

This guide takes you from zero to building FiveM/RedM resources with AI assistance. No prior experience with Cursor, Git, or Python is assumed -- every step is explained.

**Table of contents**

1. [What is this?](#1-what-is-this)
2. [Install the prerequisites](#2-install-the-prerequisites)
3. [Download the plugin](#3-download-the-plugin)
4. [Open the plugin in Cursor](#4-open-the-plugin-in-cursor)
5. [Set up the MCP server](#5-set-up-the-mcp-server)
6. [Verify everything works](#6-verify-everything-works)
7. [Build your first resource](#7-build-your-first-resource)
8. [What to try next](#8-what-to-try-next)
9. [Troubleshooting](#9-troubleshooting)
10. [Useful links](#useful-links)

---

## 1. What is this?

**CFX Developer Tools** is a plugin for the [Cursor](https://www.cursor.com/) code editor that teaches its built-in AI assistant how to build FiveM and RedM resources. Once installed, you can ask the AI to:

- Scaffold a complete resource in Lua, JavaScript, or C#
- Look up GTA5 or RDR3 native functions by name or description
- Generate a correct `fxmanifest.lua` with all the right directives
- Write code that follows FiveM/RedM best practices automatically

The plugin includes **9 skills**, **6 rules**, **20 code snippets**, **7 starter templates**, and **4 MCP tools** (including a searchable database of 12,000+ native functions).

<details>
<summary><strong>What is Cursor?</strong></summary>

&nbsp;

[Cursor](https://www.cursor.com/) is a code editor with a built-in AI assistant. It looks and works like VS Code, but adds an AI chat panel where you can ask questions about your code, request changes, and have the AI write entire files for you. If you have used VS Code before, Cursor will feel familiar. If you haven't, don't worry -- this guide covers what you need.

</details>

<details>
<summary><strong>What is FiveM / RedM?</strong></summary>

&nbsp;

[FiveM](https://docs.fivem.net/docs/) is a modification framework for GTA V that lets you run custom multiplayer servers. [RedM](https://redm.net/) is the equivalent for Red Dead Redemption 2. Both use "resources" -- packages of scripts and assets that add features to your server. This plugin helps you build those resources.

</details>

---

## 2. Install the prerequisites

You need three things installed before you can use the plugin. All steps below are for **Windows**.

<details>
<summary><strong>2a. Install Git</strong></summary>

&nbsp;

Git is a tool for downloading and managing code. You need it to download the plugin.

1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Click the download link for the 64-bit installer -- it should start automatically
3. Run the installer. **Use all the default settings** -- just click Next through each screen and then Install
4. When it finishes, close the installer

**Verify it works:** Open PowerShell (press the Windows key, type `powershell`, and press Enter) and run:

```
git --version
```

You should see something like `git version 2.53.0.windows.2`. If you see an error like `'git' is not recognized`, close PowerShell and reopen it -- the installer updated your system PATH and PowerShell needs to reload it.

</details>

<details>
<summary><strong>2b. Install Python 3.10 or newer</strong></summary>

&nbsp;

Python runs the plugin's MCP server, which gives the AI access to tools like native function lookup.

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python 3.x.x" button
3. Run the installer
4. **IMPORTANT: Check the box that says "Add python.exe to PATH"** at the bottom of the first screen. This is easy to miss and will cause problems later if you skip it.
5. Click "Install Now"
6. When it finishes, close the installer

**Verify it works:** Open a **new** PowerShell window and run:

```
python --version
```

You should see something like `Python 3.13.2`. Then verify pip (Python's package installer):

```
pip --version
```

You should see something like `pip 24.3.1 from ...`. If either command gives a "not recognized" error, see the [Troubleshooting](#python-or-pip-not-recognized) section below.

</details>

<details>
<summary><strong>2c. Install Cursor</strong></summary>

&nbsp;

Cursor is the code editor where you will use this plugin.

1. Go to [cursor.com/downloads](https://www.cursor.com/downloads)
2. Download the Windows installer
3. Run the installer and follow the prompts
4. When Cursor opens for the first time, it will ask you to create an account or sign in -- follow the on-screen instructions
5. Cursor may offer to import settings from VS Code. Accept or skip as you prefer.

Once Cursor is open, you will see:

- **Sidebar** (left) -- file explorer, search, extensions
- **Editor area** (center) -- where you edit files
- **AI chat panel** (right, or press `Ctrl+L`) -- where you talk to the AI assistant
- **Terminal** (bottom, or press `` Ctrl+` ``) -- where you run commands

If this is your first time using a code editor, spend a minute clicking around to get oriented. The [Cursor documentation](https://docs.cursor.com) has more details.

</details>

<details>
<summary><strong>2d. Optional -- set up a FiveM or RedM server</strong></summary>

&nbsp;

You need a running server to **test** resources, but you do not need one to **build** them. You can use the plugin to generate code and learn even without a server.

When you are ready to test, follow the official guide: [Setting up a server](https://docs.fivem.net/docs/server-manual/setting-up-a-server/) (covers both FiveM and RedM).

</details>

---

## 3. Download the plugin

There are two ways to get the plugin files onto your computer.

<details>
<summary><strong>Method A -- Git clone (recommended)</strong></summary>

&nbsp;

This method is preferred because it makes updating easier later.

1. Open PowerShell
2. Navigate to where you want the plugin folder to live. For example, to put it on your Desktop:

```
cd ~/Desktop
```

3. Clone (download) the repository:

```
git clone https://github.com/TMHSDigital/CFX-Developer-Tools.git
```

4. Git will create a `CFX-Developer-Tools` folder containing all the plugin files.

</details>

<details>
<summary><strong>Method B -- ZIP download</strong></summary>

&nbsp;

If you don't want to use Git:

1. Go to [github.com/TMHSDigital/CFX-Developer-Tools](https://github.com/TMHSDigital/CFX-Developer-Tools)
2. Click the green **Code** button near the top right
3. Click **Download ZIP**
4. Extract the ZIP file somewhere convenient (right-click > "Extract All")
5. The extracted folder may be named `CFX-Developer-Tools-main` -- you can rename it to `CFX-Developer-Tools` if you like

</details>

---

## 4. Open the plugin in Cursor

1. Open Cursor
2. Go to **File > Open Folder** (or press `Ctrl+K` then `Ctrl+O`)
3. Navigate to the `CFX-Developer-Tools` folder you just downloaded
4. Click **Select Folder**

You may see a prompt asking you to **trust the workspace**. Click **Yes, I trust the authors** -- this is needed for the plugin and terminal to work.

<details>
<summary><strong>What happens automatically</strong></summary>

&nbsp;

When you open the folder, Cursor:

- Reads `.cursor-plugin/plugin.json` and registers the plugin
- Makes the 9 skills available to the AI assistant
- Activates the 6 coding rules based on file types you open
- Loads the MCP server configuration from `.cursor/mcp.json`

You don't need to do anything to trigger these -- they happen on folder open.

</details>

---

## 5. Set up the MCP server

The MCP (Model Context Protocol) server is a small Python program that gives the AI access to tools like native function lookup and resource scaffolding. You need to install its dependencies once.

<details>
<summary><strong>What is a terminal?</strong></summary>

&nbsp;

A terminal is a text-based way to run commands on your computer. You type a command, press Enter, and it runs. Cursor has one built in so you don't have to open a separate window.

To open it: click **Terminal > New Terminal** in the menu bar, or press `` Ctrl+` `` (the backtick key, usually to the left of the 1 key).

</details>

### Install dependencies

Open the terminal and type these commands one at a time, pressing Enter after each:

```
cd mcp-server
```

```
pip install -r requirements.txt
```

The first command moves into the `mcp-server` folder. The second installs three Python packages the server needs. You will see some download progress and then a success message.

You do **not** need to manually start the MCP server. Cursor starts it automatically the first time the AI calls one of its tools. The configuration lives in `.cursor/mcp.json`.

---

## 6. Verify everything works

Let's confirm the plugin is active and the MCP tools are responding.

Open the AI chat by clicking the chat icon in the right sidebar, or pressing `Ctrl+L`.

<details>
<summary><strong>Test 1 -- ask about a native function</strong></summary>

&nbsp;

Type this prompt and press Enter:

> What native function gets a player's current position?

The AI should respond with information about `GetEntityCoords`, including its parameters and return type. This confirms that the **native functions skill** is active. If the AI also mentions searching the native database, the **MCP tools** are working too.

</details>

<details>
<summary><strong>Test 2 -- scaffold a resource</strong></summary>

&nbsp;

Type this prompt:

> Scaffold a new standalone resource called test-resource in Lua, targeting both FiveM and RedM

The AI should create a `test-resource/` directory containing:

- `fxmanifest.lua` -- the resource manifest
- `client/main.lua` -- client-side script
- `server/main.lua` -- server-side script
- `config.lua` -- configuration file

</details>

If both tests worked, you are ready to go. If something went wrong, check the [Troubleshooting](#9-troubleshooting) section.

---

## 7. Build your first resource

Let's build something real -- a simple resource that displays a welcome message when a player joins the server.

<details>
<summary><strong>Step 1 -- ask the AI to build it</strong></summary>

&nbsp;

In the AI chat, type:

> Create a new standalone resource called welcome-message in Lua, targeting both FiveM and RedM. When a player joins, show them a notification that says "Welcome to the server!" and print their name in the server console.

The AI will use its skills and tools to generate the complete resource.

</details>

<details>
<summary><strong>Step 2 -- understand what was generated</strong></summary>

&nbsp;

Look at the files in the `welcome-message/` folder:

| File | Purpose |
|:-----|:--------|
| `fxmanifest.lua` | Tells FiveM/RedM what scripts to load, the game target, and metadata. Every resource needs one. See the [resource docs](https://docs.fivem.net/docs/scripting-manual/introduction/introduction-to-resources/) for details. |
| `client/main.lua` | Runs on each player's game. Handles things the player sees and interacts with. |
| `server/main.lua` | Runs on the server. Handles authoritative logic, database queries, and player management. |
| `config.lua` | Shared settings that both client and server scripts can read. |

</details>

<details>
<summary><strong>Step 3 -- deploy to your server</strong></summary>

&nbsp;

If you have a FiveM or RedM server set up:

1. Copy the entire `welcome-message/` folder into your server's `resources/` directory
2. Open your server's `server.cfg` file and add this line:

```
ensure welcome-message
```

3. Restart your server (or run `ensure welcome-message` in the server console)
4. Join the server -- you should see the welcome notification

</details>

<details>
<summary><strong>Step 4 -- iterate</strong></summary>

&nbsp;

Now ask the AI to modify it:

> Add a config option for the welcome message text so server owners can change it without editing the script

The AI will update `config.lua` and the scripts to read from it. This is the core workflow: describe what you want, let the AI build it, test it, refine it.

</details>

---

## 8. What to try next

Here are example prompts to explore the plugin's capabilities. Paste them into the AI chat.

<details>
<summary><strong>Resource scaffolding prompts</strong></summary>

&nbsp;

- "Create a new QBCore resource called qb-shops in Lua with database support"
- "Scaffold a JavaScript resource called my-hud with NUI support for FiveM and RedM"
- "Generate a C# resource for RedM called rdr-horses"

</details>

<details>
<summary><strong>Native function lookup prompts</strong></summary>

&nbsp;

- "What native function sets a vehicle's speed?"
- "List all VEHICLE category natives"
- "How do I teleport a player to specific coordinates?"

</details>

<details>
<summary><strong>Manifest generation prompts</strong></summary>

&nbsp;

- "Generate an fxmanifest.lua for an ESX resource with NUI, targeting both FiveM and RedM"
- "What directives should I use for a resource that targets both FiveM and RedM?"

</details>

<details>
<summary><strong>NUI (in-game web UI) prompts</strong></summary>

&nbsp;

- "Create a simple NUI menu for my resource using the NUI Vite template"
- "How do I send data from a Lua client script to a NUI panel?"

</details>

<details>
<summary><strong>Database prompts</strong></summary>

&nbsp;

- "Show me how to create and query a MySQL table using oxmysql"
- "What's the best pattern for upsert queries in FiveM/RedM?"

</details>

<details>
<summary><strong>State Bags prompts</strong></summary>

&nbsp;

- "How do I sync vehicle fuel across all clients using State Bags?"
- "Show me a player state bag pattern for syncing job data"

</details>

<details>
<summary><strong>Learning more</strong></summary>

&nbsp;

- Browse the skills in `skills/` to see the full reference material the AI uses
- Read the [Architecture](ARCHITECTURE.md) doc to understand how all the pieces fit together
- Read the [CFX scripting introduction](https://docs.fivem.net/docs/scripting-manual/introduction/) for the official scripting guide
- Check the [GTA5 native reference](https://docs.fivem.net/natives/) and [RDR3 native reference](https://rdr3natives.com/) for game functions
- Visit the [Cfx.re forums](https://forum.cfx.re/) for community help and examples
- See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to help improve this plugin

</details>

---

## 9. Troubleshooting

<details>
<summary><strong>Python or pip not recognized</strong></summary>

&nbsp;

**Symptom:** Running `python --version` or `pip --version` in PowerShell gives `'python' is not recognized as an internal or external command`.

**Cause:** Python was installed without adding it to the system PATH.

**Fix:**

1. Open the Python installer again (re-download it from [python.org/downloads](https://www.python.org/downloads/) if needed)
2. Click **Modify**
3. Click **Next** on the first screen
4. On the "Advanced Options" screen, check **"Add Python to environment variables"**
5. Click **Install**
6. Close and reopen PowerShell, then try again

Alternatively, you can use the full path. The default Python install location on Windows is:

```
C:\Users\<YourName>\AppData\Local\Programs\Python\Python3xx\python.exe
```

</details>

<details>
<summary><strong>pip install fails with a permission error</strong></summary>

&nbsp;

**Symptom:** `pip install -r requirements.txt` fails with `Permission denied` or `Access is denied`.

**Fix:** Try adding the `--user` flag:

```
pip install --user -r requirements.txt
```

</details>

<details>
<summary><strong>MCP tools not responding</strong></summary>

&nbsp;

**Symptom:** The AI answers general questions but doesn't seem to use the native lookup or scaffolding tools.

**Checks:**

1. Make sure you opened the `CFX-Developer-Tools` folder itself in Cursor (not a parent folder)
2. Verify that `.cursor/mcp.json` exists in the project
3. Check that the Python dependencies installed successfully:

```
cd mcp-server
pip install -r requirements.txt
```

4. Restart Cursor completely (close and reopen)

</details>

<details>
<summary><strong>Cursor doesn't know about FiveM/RedM</strong></summary>

&nbsp;

**Symptom:** The AI gives generic coding answers without FiveM/RedM-specific knowledge.

**Cause:** The plugin is not loaded. This usually means you opened the wrong folder.

**Fix:** Make sure you opened the exact `CFX-Developer-Tools` folder in Cursor -- the folder that contains `.cursor-plugin/plugin.json` at its root. You can verify by checking if the file explorer sidebar shows `skills/`, `rules/`, `templates/`, etc. at the top level.

</details>

<details>
<summary><strong>Resource won't start on the server</strong></summary>

&nbsp;

**Symptom:** You copied the resource to your server but it doesn't load, or you get errors in the server console.

**Checks:**

1. Verify the resource folder is directly inside your server's `resources/` directory
2. Make sure you added `ensure resource-name` to your `server.cfg`
3. Check that `fxmanifest.lua` exists in the resource root and contains `fx_version 'cerulean'`
4. Look at the server console for error messages -- they usually tell you exactly what's wrong
5. If using a framework (ESX, QBCore), make sure the framework resource is started first

</details>

<details>
<summary><strong>Git clone fails</strong></summary>

&nbsp;

**Symptom:** `git clone` gives a network error or permission error.

**Checks:**

1. Make sure you have an internet connection
2. Try the URL in your browser to confirm the repo is accessible: [github.com/TMHSDigital/CFX-Developer-Tools](https://github.com/TMHSDigital/CFX-Developer-Tools)
3. If you're behind a corporate firewall or VPN, try the [ZIP download method](#method-b----zip-download) instead

</details>

---

## Useful links

| Resource | URL |
|:---------|:----|
| Cursor homepage | [cursor.com](https://www.cursor.com/) |
| Cursor downloads | [cursor.com/downloads](https://www.cursor.com/downloads) |
| Cursor documentation | [docs.cursor.com](https://docs.cursor.com) |
| Git for Windows | [git-scm.com/download/win](https://git-scm.com/download/win) |
| Python downloads | [python.org/downloads](https://www.python.org/downloads/) |
| FiveM/RedM documentation | [docs.fivem.net](https://docs.fivem.net/docs/) |
| Server setup guide | [docs.fivem.net/server-manual](https://docs.fivem.net/docs/server-manual/setting-up-a-server/) |
| Scripting introduction | [docs.fivem.net/scripting-manual](https://docs.fivem.net/docs/scripting-manual/introduction/) |
| GTA5 native reference | [docs.fivem.net/natives](https://docs.fivem.net/natives/) |
| RDR3 native reference | [rdr3natives.com](https://rdr3natives.com/) |
| Cfx.re forums | [forum.cfx.re](https://forum.cfx.re/) |
| Plugin GitHub repo | [github.com/TMHSDigital/CFX-Developer-Tools](https://github.com/TMHSDigital/CFX-Developer-Tools) |
