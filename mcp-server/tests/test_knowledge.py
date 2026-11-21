import asyncio
import json
import os

from mcp.server.fastmcp import FastMCP

import server
from conftest import REPO_DIR, write_files
from tools import knowledge


def test_server_exposes_every_skill_and_rule():
    plugin = json.load(open(os.path.join(REPO_DIR, ".cursor-plugin", "plugin.json"), encoding="utf-8"))
    resources = {str(r.uri) for r in asyncio.run(server.mcp.list_resources())}
    prompts = {p.name for p in asyncio.run(server.mcp.list_prompts())}
    for skill in plugin["skills"]:
        name = skill.split("/")[1]
        assert f"cfx://skills/{name}" in resources
        assert f"cfx-{name}" in prompts
    for rule in plugin["rules"]:
        assert f"cfx://rules/{os.path.basename(rule)[:-4]}" in resources


def test_resource_returns_current_content(tmp_path):
    write_files(tmp_path, {"skills/demo/SKILL.md": "---\ntitle: Demo\ndescription: Demo skill\n---\nv1\n",
                           "rules/r.mdc": "---\ndescription: A rule\n---\nrule body\n"})
    mcp = FastMCP("t")
    knowledge.register(mcp, str(tmp_path))
    first = list(asyncio.run(mcp.read_resource("cfx://skills/demo")))[0].content
    assert first.endswith("v1\n")
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("---\ndescription: Demo skill\n---\nv2\n", encoding="utf-8")
    assert list(asyncio.run(mcp.read_resource("cfx://skills/demo")))[0].content.endswith("v2\n")
    prompts = asyncio.run(mcp.list_prompts())
    assert [(p.name, p.description) for p in prompts] == [("cfx-demo", "Demo skill")]
    assert "rule body" in list(asyncio.run(mcp.read_resource("cfx://rules/r")))[0].content
