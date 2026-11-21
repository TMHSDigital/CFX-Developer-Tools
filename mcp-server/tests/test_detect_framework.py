import os

import pytest

from conftest import write_files
from tools.detect_framework import MAX_FILE_SIZE, detect_framework


@pytest.mark.parametrize("framework", ["esx", "qbcore", "qbox", "oxcore", "vorp", "rsg", "standalone"])
def test_templates_detect_their_framework(repo_dir, framework):
    lines = detect_framework(os.path.join(repo_dir, "templates", framework)).splitlines()
    assert lines[0] == f"Detected framework: {framework}"
    assert lines[1].startswith("Confidence: high")


def test_ox_lib_alone_is_standalone(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "shared_script '@ox_lib/init.lua'\n"})
    out = detect_framework(str(tmp_path))
    assert out.startswith("Detected framework: standalone")
    assert "Libraries: ox_lib" in out


def test_qbox_with_ox_lib(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "shared_scripts { '@ox_lib/init.lua', '@qbx_core/modules/lib.lua' }\n"})
    assert detect_framework(str(tmp_path)).startswith("Detected framework: qbox")


def test_tie_reports_bridge(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "dependencies { 'es_extended', 'qb-core' }\n"})
    assert "multiple frameworks / bridge (esx, qbcore)" in detect_framework(str(tmp_path)).splitlines()[0]


def test_unrelated_and_commented_names_ignored(tmp_path):
    write_files(tmp_path, {"fxmanifest.lua": "dependency 'qb-target'\n-- dependency 'es_extended'\n"})
    assert detect_framework(str(tmp_path)).startswith("Detected framework: standalone")


def test_empty_and_missing(tmp_path):
    assert "No framework signals detected" in detect_framework(str(tmp_path))
    assert detect_framework(str(tmp_path / "nope")).startswith("Error: directory not found")


def test_vendored_dirs_ignored(tmp_path):
    write_files(tmp_path, {
        "node_modules/x/fxmanifest.lua": "dependency 'es_extended'\n",
        ".git/fxmanifest.lua": "dependency 'qb-core'\n",
    })
    assert detect_framework(str(tmp_path)).startswith("Detected framework: standalone")


def test_large_files_read_up_to_limit(tmp_path):
    write_files(tmp_path, {"client/big.lua": " " * (MAX_FILE_SIZE + 10) + "ESX = exports"})
    assert detect_framework(str(tmp_path)).startswith("Detected framework: standalone")


def test_dot_github_and_git_substring_paths_are_scanned(tmp_path):
    ws = tmp_path / "my.github.io"
    write_files(ws, {".github/res/fxmanifest.lua": "dependency 'es_extended'\n"})
    assert detect_framework(str(ws)).startswith("Detected framework: esx")


def test_walks_tree_once_and_prunes(tmp_path, monkeypatch):
    import os as _os
    from tools import manifest_common

    write_files(tmp_path, {
        "fxmanifest.lua": "dependency 'qb-core'\n",
        "node_modules/a/b.lua": "", "dist/x.lua": "", "client/main.lua": "",
    })
    calls, visited = [], []
    real_walk = _os.walk

    def counting_walk(top, *a, **k):
        calls.append(top)
        for dirpath, dirs, files in real_walk(top, *a, **k):
            visited.append(_os.path.relpath(dirpath, tmp_path))
            yield dirpath, dirs, files

    monkeypatch.setattr(manifest_common.os, "walk", counting_walk)
    assert detect_framework(str(tmp_path)).startswith("Detected framework: qbcore")
    assert len(calls) == 1
    assert not any(v.startswith(("node_modules", "dist")) for v in visited)
