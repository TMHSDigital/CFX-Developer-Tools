import json
import os
import time

from tools import data
from tools.natives import lookup_native


def test_parsed_once_until_file_changes(tmp_path, monkeypatch):
    path = tmp_path / "x.json"
    path.write_text(json.dumps([1, 2]), encoding="utf-8")
    calls = []
    real_load = json.load
    monkeypatch.setattr(data.json, "load", lambda f: calls.append(1) or real_load(f))
    data._load.cache_clear()

    assert data.load_dataset(str(path), "x") == [1, 2]
    assert data.load_dataset(str(path), "x") == [1, 2]
    assert len(calls) == 1

    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    st = os.stat(path)
    os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    assert data.load_dataset(str(path), "x") == [1, 2, 3]
    assert len(calls) == 2


def test_errors_are_strings(tmp_path):
    assert data.load_dataset(str(tmp_path / "nope.json"), "thing").startswith("Error: thing not found")
    bad = tmp_path / "bad.json"
    bad.write_text("{oops", encoding="utf-8")
    assert data.load_dataset(str(bad), "thing").startswith("Error: could not read thing")
    obj = tmp_path / "obj.json"
    obj.write_text("{}", encoding="utf-8")
    assert "expected a JSON array" in data.load_dataset(str(obj), "thing")


def test_repeated_lookup_is_fast(data_dir):
    lookup_native("GetPlayerPed", "gta5", None, data_dir)
    start = time.perf_counter()
    for _ in range(5):
        lookup_native("GetPlayerPed", "gta5", None, data_dir)
    assert (time.perf_counter() - start) / 5 < 0.5
