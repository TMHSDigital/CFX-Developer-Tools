import re

from conftest import write_files
from tools.manifest_gen import generate_manifest

GOLDEN_LUA = """fx_version 'cerulean'
games { 'gta5' }

author 'YourName'
description 'r'
version '1.0.0'

shared_scripts {
    'config.lua'
}

client_scripts {
    'client/*.lua'
}

server_scripts {
    'server/*.lua'
}
"""


def blocks(manifest: str) -> dict[str, list[str]]:
    """Parse `name { 'a', 'b' }` blocks and assert entries are comma-separated."""
    out = {}
    for name, body in re.findall(r"(\w+) \{\n(.*?)\n\}", manifest, re.S):
        lines = [line.strip() for line in body.splitlines()]
        for line in lines[:-1]:
            assert line.endswith(","), f"missing comma in {name}: {line!r}"
        assert not lines[-1].endswith(","), f"trailing comma in {name}"
        out[name] = [line.rstrip(",").strip("'") for line in lines]
    return out


def test_default_matches_golden():
    assert generate_manifest("r", "gta5", "lua", "standalone") == GOLDEN_LUA


def test_multiple_scripts_are_comma_separated_and_classified():
    m = generate_manifest("r", "gta5", "lua", "standalone",
                          scripts=["client/a.lua", "client/b.lua", "server/c.lua", "sv_d.lua",
                                   "shared/config.lua", "utils.lua"])
    b = blocks(m)
    assert b["client_scripts"] == ["client/a.lua", "client/b.lua"]
    assert b["server_scripts"] == ["server/c.lua", "sv_d.lua"]
    assert b["shared_scripts"] == ["shared/config.lua", "utils.lua"]


def test_dependencies_ordered_and_deduped():
    m = generate_manifest("r", "gta5", "lua", "esx", dependencies=["ox_lib", "es_extended"])
    assert re.findall(r"dependency '([^']+)'", m) == ["es_extended", "ox_lib"]


def test_values_are_escaped():
    m = generate_manifest("o'brien\\x", "gta5", "lua", "standalone", dependencies=["we'ird"])
    assert "description 'o\\'brien\\\\x'" in m
    assert "dependency 'we\\'ird'" in m


def test_workspace_scan_shared_and_vite_nui(tmp_path):
    write_files(tmp_path, {
        "shared/utils.lua": "", "client/main.lua": "", "server/main.lua": "",
        "sh_x.lua": "", "README.md": "", "web/dist/index.html": "", "web/index.html": "",
    })
    b = blocks(generate_manifest("x", "gta5", "lua", "standalone", workspace_path=str(tmp_path)))
    assert b["shared_scripts"] == ["sh_x.lua", "shared/utils.lua"]
    assert b["client_scripts"] == ["client/main.lua"]
    assert b["files"] == ["web/dist/**"]
    m = generate_manifest("x", "gta5", "lua", "standalone", workspace_path=str(tmp_path))
    assert "ui_page 'web/dist/index.html'" in m
    assert "config.lua" not in m  # only listed when it exists


def test_workspace_html_nui(tmp_path):
    write_files(tmp_path, {"client/main.lua": "", "html/index.html": ""})
    m = generate_manifest("x", "gta5", "lua", "standalone", workspace_path=str(tmp_path))
    assert "ui_page 'html/index.html'" in m


def test_csharp_entries():
    b = blocks(generate_manifest("cres", "gta5", "csharp", "standalone"))
    assert b["client_scripts"] == ["dist/cres.Client.net.dll"]
    assert b["server_scripts"] == ["dist/cres.Server.net.dll"]


def test_invalid_input_returns_error():
    assert generate_manifest("x", "gta5", "lua", "nope").startswith("Error")


def test_exports_blocks():
    b = blocks(generate_manifest("r", "gta5", "lua", "standalone", exports=["GetA"], server_exports=["GetB", "GetC"]))
    assert b["exports"] == ["GetA"]
    assert b["server_exports"] == ["GetB", "GetC"]


EXISTING = """-- my resource
fx_version 'cerulean'
games { 'gta5' }

client_scripts {
    'client/main.lua' -- entry
}
dependency 'oxmysql'
custom_data 'keep me'
"""


def test_update_mode_preserves_lines_and_returns_diff(tmp_path):
    (tmp_path / "fxmanifest.lua").write_text(EXISTING, encoding="utf-8")
    out = generate_manifest("r", "gta5", "lua", "standalone", mode="update", workspace_path=str(tmp_path),
                            scripts=["client/extra.lua", "client/main.lua"], dependencies=["ox_lib", "oxmysql"],
                            server_exports=["GetThing"])
    assert "+client_script 'client/extra.lua'" in out
    assert "+dependency 'ox_lib'" in out
    assert "+server_export 'GetThing'" in out
    assert "+client_script 'client/main.lua'" not in out
    assert "+dependency 'oxmysql'" not in out
    full = out.split("```lua\n", 1)[1].rsplit("```", 1)[0]
    assert full.startswith(EXISTING)
    assert (tmp_path / "fxmanifest.lua").read_text(encoding="utf-8") == EXISTING  # not written


def test_update_mode_errors_and_no_change(tmp_path):
    assert generate_manifest("r", "gta5", "lua", "standalone", mode="update").startswith("Error")
    assert generate_manifest("r", "gta5", "lua", "standalone", mode="update",
                             workspace_path=str(tmp_path)).startswith("Error: fxmanifest.lua not found")
    (tmp_path / "fxmanifest.lua").write_text(EXISTING, encoding="utf-8")
    assert generate_manifest("r", "gta5", "lua", "standalone", mode="update", workspace_path=str(tmp_path),
                             dependencies=["oxmysql"]).startswith("No changes")
