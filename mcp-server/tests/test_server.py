import asyncio

import server

EXPECTED_TOOLS = {
    "scaffold_resource_tool",
    "lookup_native_tool",
    "generate_manifest_tool",
    "validate_manifest_tool",
    "search_events_tool",
    "detect_framework_tool",
    "search_docs_tool",
    "txadmin_server_control_tool",
    "txadmin_resource_control_tool",
    "txadmin_player_search_tool",
    "txadmin_kick_player_tool",
}


def test_registers_documented_tools():
    tools = asyncio.run(server.mcp.list_tools())
    assert {tool.name for tool in tools} == EXPECTED_TOOLS


def test_data_path_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert "GetPlayerPed" in server.lookup_native_tool("GetPlayerPed")


def test_tool_annotations():
    tools = {tool.name: tool for tool in asyncio.run(server.mcp.list_tools())}
    for name in ("txadmin_server_control_tool", "txadmin_resource_control_tool", "txadmin_kick_player_tool"):
        assert tools[name].annotations.destructiveHint is True
    for name in ("lookup_native_tool", "search_docs_tool", "search_events_tool", "txadmin_player_search_tool"):
        assert tools[name].annotations.readOnlyHint is True
