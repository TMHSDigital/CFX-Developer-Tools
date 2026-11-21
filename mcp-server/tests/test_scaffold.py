import json
import os

import pytest

from tools.manifest_common import FRAMEWORK_DEPS, VALID_FRAMEWORKS
from tools.scaffold import FRAMEWORK_INIT_CLIENT, scaffold_resource


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_default_lua_resource(tmp_path):
    out = scaffold_resource("shop", "gta5", "lua", "standalone", output_path=str(tmp_path))
    base = tmp_path / "shop"
    assert str(base) in out
    for rel in ("fxmanifest.lua", "config.lua", "client/main.lua", "server/main.lua"):
        assert (base / rel).is_file(), rel
    manifest = read(base / "fxmanifest.lua")
    assert "fx_version 'cerulean'" in manifest
    assert "games { 'gta5' }" in manifest
    assert "author 'YourName'" in manifest
    assert "dependency" not in manifest


@pytest.mark.parametrize("framework", sorted(VALID_FRAMEWORKS))
def test_each_framework_dependency_and_init(tmp_path, framework):
    game = "rdr3" if framework in ("vorp", "rsg") else "gta5"
    assert scaffold_resource("res", game, "lua", framework, output_path=str(tmp_path)).startswith("Scaffolded")
    manifest = read(tmp_path / "res" / "fxmanifest.lua")
    client = read(tmp_path / "res" / "client" / "main.lua")
    dep = FRAMEWORK_DEPS.get(framework)
    if dep:
        assert f"dependency '{dep}'" in manifest
    if FRAMEWORK_INIT_CLIENT[framework]:
        assert client.startswith(FRAMEWORK_INIT_CLIENT[framework])


def test_oxcore_loads_ox_lib(tmp_path):
    scaffold_resource("ox", "gta5", "lua", "oxcore", output_path=str(tmp_path))
    manifest = read(tmp_path / "ox" / "fxmanifest.lua")
    assert "dependency 'ox_lib'" in manifest
    assert "'@ox_lib/init.lua'," in manifest


def test_javascript_resource(tmp_path):
    scaffold_resource("jsres", "both", "javascript", "standalone", output_path=str(tmp_path))
    base = tmp_path / "jsres"
    pkg = json.loads(read(base / "package.json"))
    assert pkg["name"] == "jsres"
    manifest = read(base / "fxmanifest.lua")
    assert "node_version '22'" in manifest
    assert "games { 'gta5', 'rdr3' }" in manifest
    client = read(base / "client" / "main.js")
    assert "const Delay = " in client


def test_csharp_resource_layout(tmp_path):
    scaffold_resource("cres", "gta5", "csharp", "standalone", output_path=str(tmp_path))
    base = tmp_path / "cres"
    for rel in ("Client/cres.Client.csproj", "Client/ClientMain.cs",
                "Server/cres.Server.csproj", "Server/ServerMain.cs"):
        assert (base / rel).is_file(), rel
    manifest = read(base / "fxmanifest.lua")
    assert "'dist/cres.Client.net.dll'" in manifest
    assert "'dist/cres.Server.net.dll'" in manifest
    assert "<AssemblyName>cres.Client.net</AssemblyName>" in read(base / "Client/cres.Client.csproj")
    assert "using static CitizenFX.Core.Native.API;" in read(base / "Server/ServerMain.cs")


def test_game_normalisation(tmp_path):
    out = scaffold_resource("r", "RDR3 ", "lua", "standalone", output_path=str(tmp_path))
    assert out.startswith("Scaffolded")
    assert "games { 'rdr3' }" in read(tmp_path / "r" / "fxmanifest.lua")


@pytest.mark.parametrize("args", [
    ("r", "gta6", "lua", "standalone"),
    ("r", "gta5", "python", "standalone"),
    ("r", "gta5", "lua", "nope"),
])
def test_invalid_inputs_create_nothing(tmp_path, args):
    assert scaffold_resource(*args, output_path=str(tmp_path)).startswith("Error")
    assert not (tmp_path / "r").exists()


@pytest.mark.parametrize("name", ["", "../x", "a/b", "a\\b", "..", "/abs", "C:\\x", "x" * 65])
def test_rejects_unsafe_names(tmp_path, name):
    assert scaffold_resource(name, "gta5", "lua", "standalone", output_path=str(tmp_path)).startswith("Error")
    assert os.listdir(tmp_path) == []


def test_refuses_to_overwrite_and_allows_with_flag(tmp_path):
    scaffold_resource("shop", "gta5", "lua", "standalone", output_path=str(tmp_path))
    target = tmp_path / "shop" / "client" / "main.lua"
    target.write_text("ORIGINAL", encoding="utf-8")

    out = scaffold_resource("shop", "gta5", "lua", "standalone", output_path=str(tmp_path))
    assert out.startswith("Error")
    assert target.read_text(encoding="utf-8") == "ORIGINAL"

    out = scaffold_resource("shop", "gta5", "lua", "standalone", output_path=str(tmp_path), overwrite=True)
    assert out.startswith("Scaffolded")
    assert target.read_text(encoding="utf-8") != "ORIGINAL"


def test_defaults_to_cwd_and_reports_absolute_path(tmp_path, monkeypatch):
    monkeypatch.delenv("CFX_SCAFFOLD_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    out = scaffold_resource("here", "gta5", "lua", "standalone")
    assert (tmp_path / "here" / "fxmanifest.lua").is_file()
    assert os.path.realpath(str(tmp_path / "here")) in out


def test_workspace_author_pickup_and_escaping(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "fxmanifest.lua").write_text("author \"O'Brien\"\n", encoding="utf-8")
    scaffold_resource("new", "gta5", "lua", "standalone", workspace_path=str(ws))
    assert "author 'O\\'Brien'" in read(ws / "new" / "fxmanifest.lua")


def test_author_falls_back_to_placeholder(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    scaffold_resource("new", "gta5", "lua", "standalone", workspace_path=str(ws))
    assert "author 'YourName'" in read(ws / "new" / "fxmanifest.lua")
