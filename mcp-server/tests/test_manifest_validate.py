import json
import os

import pytest

from conftest import write_files
from tools.manifest_validate import main, parse_manifest, validate_manifest, validate_manifest_report

GOOD = """fx_version 'cerulean'
games { 'gta5' }
-- dependency 'vorp_core'   (commented out)
shared_scripts {
    'config.lua',
    '@ox_lib/init.lua'
}
client_script 'client/main.lua'
server_scripts { "server/*.lua" }
ui_page 'html/index.html'
files { 'html/**' }
"""


def test_parse_forms():
    d = parse_manifest(GOOD)
    assert d["shared_scripts"] == ["config.lua", "@ox_lib/init.lua"]
    assert d["client_script"] == ["client/main.lua"]
    assert d["server_scripts"] == ["server/*.lua"]
    assert "dependency" not in d


def test_good_manifest(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": GOOD, "config.lua": "", "client/main.lua": "",
                           "server/a.lua": "", "html/index.html": ""})
    r = validate_manifest(str(tmp_path))
    assert r["errors"] == [] and r["warnings"] == []


@pytest.mark.parametrize("manifest,expected", [
    ("games { 'gta5' }\n", "missing fx_version"),
    ("fx_version 'bodacious'\ngames { 'gta5' }\n", "use 'cerulean'"),
    ("fx_version 'cerulean'\ngames { 'rdr2' }\n", "invalid game 'rdr2'"),
    ("fx_version 'cerulean'\n", "missing games"),
    ("fx_version 'cerulean'\ngames { 'gta5' }\nlua54 true\n", "lua54"),
    ("fx_version 'cerulean'\ngames { 'gta5' }\nclient_script 'client/missing.lua'\n", "does not match any file"),
    ("fx_version 'cerulean'\ngames { 'gta5' }\nui_page 'html/index.html'\n", "not covered by a files entry"),
    ("fx_version 'cerulean'\ngames { 'gta5' }\ndependency 'vorp_core'\n", "does not run on gta5"),
])
def test_bad_manifests(tmp_path, manifest, expected):
    write_files(tmp_path, {"fxmanifest.lua": manifest, "html/index.html": ""})
    errors = validate_manifest(str(tmp_path))["errors"]
    assert any(expected in e for e in errors), errors


def test_build_output_is_a_warning(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "fx_version 'cerulean'\ngames { 'gta5' }\n"
                                             "client_scripts { 'dist/x.Client.net.dll' }\n"})
    r = validate_manifest(str(tmp_path))
    assert r["errors"] == [] and len(r["warnings"]) == 1


def test_resource_lua_and_missing(tmp_path):
    write_files(tmp_path, {"__resource.lua": ""})
    assert "__resource.lua" in validate_manifest(str(tmp_path))["errors"][0]
    assert "not found" in validate_manifest(str(tmp_path / "nope"))["errors"][0]


def test_json_format(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "games { 'gta5' }\n"})
    data = json.loads(validate_manifest_report(str(tmp_path), format="json"))
    assert data["errors"]


def test_repo_templates_and_examples_pass(repo_dir):
    assert main([os.path.join(repo_dir, "templates"), os.path.join(repo_dir, "examples")]) == 0
