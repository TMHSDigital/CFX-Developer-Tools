import json

import pytest

from tools.docs_search import search_docs
from tools.event_search import search_events

EVENTS = [
    {"name": "playerDropped", "side": "server", "framework": "cfx", "game": "shared", "description": "Player left."},
    {"name": "onClientResourceStart", "side": "client", "framework": "cfx", "game": "shared", "description": ""},
    {"name": "onResourceStart", "side": "shared", "framework": "cfx", "game": "shared", "description": ""},
    {"name": "esx:playerLoaded", "side": "server", "framework": "esx", "game": "gta5", "description": ""},
    {"name": "vorp:SelectedCharacter", "side": "server", "framework": "vorp", "game": "rdr3", "description": ""},
]
DOCS = [
    {"title": "State Bags", "url": "https://docs.fivem.net/docs/scripting-manual/networking/state-bags/",
     "section": "scripting-manual", "snippet": "Values can be replicated to clients."},
    {"title": "Prerequisites", "url": "https://docs.fivem.net/docs/getting-started/prerequisites/",
     "section": "getting-started", "snippet": "What you need."},
]


@pytest.fixture
def data(tmp_path):
    (tmp_path / "events.json").write_text(json.dumps(EVENTS), encoding="utf-8")
    (tmp_path / "docs_index.json").write_text(json.dumps(DOCS), encoding="utf-8")
    return str(tmp_path)


def test_events_summary(data):
    assert search_events(data_path=data).startswith("Event reference database (5 events)")


def test_events_server_side_includes_shared(data):
    out = search_events(side="server", data_path=data)
    assert "onResourceStart" in out and "playerDropped" in out
    assert "onClientResourceStart" not in out


def test_events_rdr3_excludes_gta5_only(data):
    out = search_events(game="rdr3", data_path=data)
    assert "vorp:SelectedCharacter" in out
    assert "esx:playerLoaded" not in out


def test_docs_summary_and_query(data):
    assert "2" in search_docs(data_path=data).splitlines()[0]
    assert "State Bags" in search_docs("replicated", data_path=data)


def test_docs_invalid_section(data):
    assert search_docs("x", section="nope", data_path=data).startswith("Error: invalid section")


@pytest.mark.parametrize("fn", [lambda p: search_events("x", data_path=p), lambda p: search_docs("x", data_path=p)])
def test_missing_and_malformed_files(tmp_path, fn):
    assert fn(str(tmp_path)).startswith("Error")
    (tmp_path / "events.json").write_text("{bad", encoding="utf-8")
    (tmp_path / "docs_index.json").write_text("{bad", encoding="utf-8")
    assert fn(str(tmp_path)).startswith("Error: could not read")


def test_real_docs_index_has_content(data_dir):
    assert "State Bags" in search_docs("replicated", data_path=data_dir)
