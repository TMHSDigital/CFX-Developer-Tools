import json

import pytest

from tools.natives import lookup_native

FIXTURE = [
    {"name": "GetPlayerPed", "hash": "0x6E31E993", "params": [{"type": "char*", "name": "playerSrc"}],
     "return_type": "Entity", "description": "Server ped lookup.", "side": "server", "category": "CFX",
     "deprecated": False, "examples": None},
    {"name": "GetEntityCoords", "hash": "0x3FEF770D40960D5A", "params": [{"type": "Entity", "name": "entity"}],
     "return_type": "Vector3", "description": "Coords.", "side": "shared", "category": "ENTITY",
     "deprecated": False, "examples": None},
    {"name": "SetVehicleColours", "hash": "0x4F1D4BE3A7F24601", "params": [{"name": "vehicle"}],
     "return_type": "void", "description": None, "side": "client", "category": "VEHICLE",
     "deprecated": True, "examples": None},
    {"name": "LongDesc", "hash": "0x1", "params": [], "return_type": "void",
     "description": "x" * 400, "side": "client", "category": "VEHICLE", "deprecated": False, "examples": None},
]


@pytest.fixture
def fixture_dir(tmp_path):
    (tmp_path / "natives_gta5.json").write_text(json.dumps(FIXTURE), encoding="utf-8")
    many = [dict(FIXTURE[1], name=f"Native{i}", hash=f"0x{i:X}") for i in range(30)]
    (tmp_path / "natives_rdr3.json").write_text(json.dumps(many), encoding="utf-8")
    return str(tmp_path)


@pytest.mark.parametrize("query", ["GET_PLAYER_PED", "GetPlayerPed", "getplayerped"])
def test_name_forms(fixture_dir, query):
    assert "GetPlayerPed" in lookup_native(query, "gta5", None, fixture_dir)


@pytest.mark.parametrize("query", ["0x6E31E993", "6e31e993", "0X6E31E993"])
def test_hash_forms(fixture_dir, query):
    assert lookup_native(query, "gta5", None, fixture_dir).startswith("Found 1 native")


def test_invalid_game(fixture_dir):
    out = lookup_native("x", "rdr2", None, fixture_dir)
    assert out.startswith("Error: invalid game")
    assert fixture_dir not in out


def test_malformed_entries_do_not_raise(fixture_dir):
    out = lookup_native("SetVehicleColours", "gta5", None, fixture_dir)
    assert "[DEPRECATED]" in out
    assert "Parameters: (vehicle)" in out


def test_side_filter_includes_shared(fixture_dir):
    out = lookup_native("", "gta5", "server", fixture_dir, category="ENTITY")
    assert "GetEntityCoords" in out
    assert "SetVehicleColours" not in lookup_native("Set", "gta5", "server", fixture_dir)


def test_category_case_insensitive(fixture_dir):
    assert "SetVehicleColours" in lookup_native("", "gta5", None, fixture_dir, category="vehicle")


def test_category_summary_counts(fixture_dir):
    out = lookup_native("", "gta5", None, fixture_dir)
    assert f"({len(FIXTURE)} total natives)" in out


def test_result_limit_and_truncation(fixture_dir):
    out = lookup_native("Native", "rdr3", None, fixture_dir)
    assert "... and 5 more" in out
    long = lookup_native("LongDesc", "gta5", None, fixture_dir)
    assert "x" * 297 + "..." in long and "x" * 301 not in long


def test_missing_and_malformed_database(tmp_path):
    assert lookup_native("x", "gta5", None, str(tmp_path)).startswith("Error: native database not found")
    (tmp_path / "natives_gta5.json").write_text("{not json", encoding="utf-8")
    assert lookup_native("x", "gta5", None, str(tmp_path)).startswith("Error: could not read")


def test_real_data_smoke(data_dir):
    out = lookup_native("GET_PLAYER_PED", "gta5", None, data_dir)
    assert "GetPlayerPed" in out
