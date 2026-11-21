"""Tests for .github/scripts/counts.py (the single source of artifact counts)."""

import importlib.util
import os

from conftest import REPO_DIR

_spec = importlib.util.spec_from_file_location(
    "counts", os.path.join(REPO_DIR, ".github", "scripts", "counts.py")
)
counts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(counts)


def test_tool_count_matches_registered_tools():
    import asyncio
    import server

    c = counts.compute_counts()
    assert c["tools"] == len(asyncio.run(server.mcp.list_tools()))
    assert c["natives"] == c["natives_gta5"] + c["natives_rdr3"]


def test_description_uses_computed_counts():
    c = counts.compute_counts()
    desc = counts.description(c)
    assert f"{c['tools']} MCP tools" in desc
    assert f"{c['skills']} skills" in desc


def test_natives_floor():
    assert counts.natives_floor(11737) == "11,500+"
    assert counts.natives_floor(12000) == "12,000+"


def test_check_flags_mismatches(tmp_path, monkeypatch):
    c = {"skills": 10, "rules": 6, "snippets": 25, "templates": 11, "examples": 5,
         "tools": 10, "events": 101, "natives": 11737}
    doc = tmp_path / "doc.md"
    doc.write_text(
        "10 skills, 6 rules, 10 MCP tools, 11,500+ natives\n"
        "9 skills here\n"
        "12,000+ natives\n"
        "24 snippets <!-- counts:ignore -->\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(counts, "ROOT", str(tmp_path))
    errors = counts.check_files(["doc.md"], c)
    assert len(errors) == 2
    assert "doc.md:2" in errors[0] and "doc.md:3" in errors[1]


def test_repository_docs_are_consistent():
    c = counts.compute_counts()
    docs = ["README.md", "CLAUDE.md", "AGENTS.md", ".cursorrules", "CONTRIBUTING.md",
            "docs/index.md", "docs/GETTING-STARTED.md", "docs/ARCHITECTURE.md",
            "docs/CONTRIBUTING.md", "mcp-server/README.md"]
    assert counts.check_files(docs, c) == []
