import pytest

from conftest import write_files
from tools.manifest_common import (
    VALID_FRAMEWORKS,
    find_nui_page,
    lua_string,
    read_workspace_context,
    scan_script_files,
    validate_inputs,
)


def test_scan_script_files_classification(tmp_path):
    write_files(tmp_path, {
        "cl_x.lua": "", "sv_x.lua": "", "sh_x.lua": "", "config.lua": "", "README.md": "",
        "client/a.lua": "", "server/b.js": "", "shared/c.lua": "",
    })
    s = scan_script_files(str(tmp_path))
    assert s["client"] == ["cl_x.lua", "client/a.lua"]
    assert s["server"] == ["server/b.js", "sv_x.lua"]
    assert s["shared"] == ["config.lua", "sh_x.lua", "shared/c.lua"]


def test_scan_script_files_missing_dir(tmp_path):
    assert scan_script_files(str(tmp_path / "nope")) == {"client": [], "server": [], "shared": []}


def test_read_workspace_context_skips_vendored_dirs(tmp_path):
    write_files(tmp_path, {
        "node_modules/pkg/fxmanifest.lua": "author 'Vendor'\n",
        "res/fxmanifest.lua": "author \"O'Brien\"\ndescription 'Desc'\n",
    })
    ctx = read_workspace_context(str(tmp_path))
    assert ctx == {"author": "O'Brien", "description": "Desc"}


@pytest.mark.parametrize("framework", sorted(VALID_FRAMEWORKS))
def test_validate_inputs_accepts_every_framework(framework):
    assert validate_inputs("gta5", "lua", framework) is None


def test_validate_inputs_rejects():
    assert validate_inputs("gta6", "lua", "esx").startswith("Error")


def test_lua_string_escapes():
    assert lua_string("a'b\\c\n") == "a\\'b\\\\c\\n"


def test_find_nui_page_prefers_dist(tmp_path):
    write_files(tmp_path, {"web/index.html": "", "web/dist/index.html": ""})
    assert find_nui_page(str(tmp_path)) == "web/dist/index.html"
    assert find_nui_page(str(tmp_path / "missing")) is None
