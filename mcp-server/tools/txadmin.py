"""
txAdmin integration tools (txadmin.py).

Thin, agent-friendly wrappers over the txAdmin web API that return formatted
markdown. All network and auth handling lives in txadmin_client.py; these
functions translate tool arguments into API calls and shape the response.

Credentials are never passed as arguments. They are read from the
TXADMIN_USERNAME / TXADMIN_PASSWORD / TXADMIN_URL environment variables by
TxAdminConfig. See the txadmin-integration skill for setup.
"""

from __future__ import annotations

from tools.txadmin_client import TxAdminClient, TxAdminConfig, TxAdminError


SERVER_ACTIONS = {"start", "stop", "restart"}

# Maps a friendly resource action to the txAdmin /fxserver/commands action.
RESOURCE_ACTIONS = {
    "start": "start_res",
    "stop": "stop_res",
    "restart": "restart_res",
    "ensure": "ensure_res",
}


def _render_toast(result: dict, fallback: str) -> str:
    """Render an ApiToastResp ({type, msg}) as markdown."""
    toast_type = (result.get("type") or "info").lower()
    msg = result.get("msg") or result.get("error") or fallback
    icon = {"success": "OK", "warning": "WARN", "error": "ERROR"}.get(
        toast_type, "INFO"
    )
    return f"**[{icon}]** {msg}"


def txadmin_server_control(action: str) -> str:
    """Start, stop, or restart the FXServer via txAdmin.

    Args:
        action: One of start, stop, restart.
    """
    action = (action or "").strip().lower()
    if action not in SERVER_ACTIONS:
        return (
            f"Error: invalid action '{action}'. "
            f"Valid actions: {', '.join(sorted(SERVER_ACTIONS))}."
        )

    try:
        client = TxAdminClient()
        result = client.request(
            "POST", "/fxserver/controls", body={"action": action}
        )
    except TxAdminError as exc:
        return f"Error: {exc}"

    return _render_toast(result, f"Server {action} request sent.")


def txadmin_resource_control(action: str, resource: str) -> str:
    """Start, stop, restart, or ensure a single resource via txAdmin.

    Args:
        action: One of start, stop, restart, ensure.
        resource: The resource name (folder name) to act on.
    """
    action = (action or "").strip().lower()
    resource = (resource or "").strip()
    if action not in RESOURCE_ACTIONS:
        return (
            f"Error: invalid action '{action}'. "
            f"Valid actions: {', '.join(sorted(RESOURCE_ACTIONS))}."
        )
    if not resource:
        return "Error: a resource name is required."

    try:
        client = TxAdminClient()
        result = client.request(
            "POST",
            "/fxserver/commands",
            body={"action": RESOURCE_ACTIONS[action], "parameter": resource},
        )
    except TxAdminError as exc:
        return f"Error: {exc}"

    return _render_toast(result, f"Resource '{resource}' {action} command sent.")


def txadmin_player_search(
    search_value: str = "",
    search_type: str = "playerName",
    filters: str | None = None,
    limit: int = 25,
) -> str:
    """Search players known to the server (online and in the database).

    Args:
        search_value: Text to search for (name, or identifier when search_type is set accordingly).
        search_type: Search mode - playerName, playerNotes, or playerIds.
        filters: Comma-separated simple filters - isAdmin, isOnline, isWhitelisted, hasNote.
        limit: Maximum number of players to display (server caps at 100).
    """
    query = {
        "searchValue": search_value or None,
        "searchType": search_type or None,
        "filters": filters,
        # sortingKey is required by the endpoint.
        "sortingKey": "tsLastConnection",
        "sortingDesc": "true",
    }

    try:
        client = TxAdminClient()
        result = client.request("GET", "/player/search", query=query)
    except TxAdminError as exc:
        return f"Error: {exc}"

    if result.get("error"):
        return f"Error: {result['error']}"

    players = result.get("players") or result.get("data") or []
    if not players:
        return "No players matched the search."

    lines = [f"Found {len(players)} player(s):", ""]
    for player in players[: max(1, limit)]:
        name = player.get("displayName") or player.get("name") or "unknown"
        license_id = player.get("license") or "no license"
        details = []
        if player.get("isOnline"):
            details.append("online")
        if player.get("isAdmin"):
            details.append("admin")
        if player.get("playTime") is not None:
            details.append(f"{player['playTime']} min played")
        suffix = f" ({', '.join(details)})" if details else ""
        lines.append(f"- **{name}** - `{license_id}`{suffix}")

    if len(players) > limit:
        lines.append("")
        lines.append(f"... and {len(players) - limit} more (raise `limit` to see them).")

    return "\n".join(lines)


def txadmin_kick_player(netid: int, reason: str = "", mutex: str = "current") -> str:
    """Kick an online player by their server network id (netid).

    Args:
        netid: The player's server id (netid) as shown in the player list.
        reason: Optional kick reason shown to the player.
        mutex: Server instance mutex; 'current' (default) targets the running server.
    """
    try:
        netid_int = int(netid)
    except (TypeError, ValueError):
        return f"Error: netid must be a number, got '{netid}'."

    reason = (reason or "").strip()

    try:
        client = TxAdminClient()
        result = client.request(
            "POST",
            "/player/kick",
            body={"reason": reason},
            query={"netid": netid_int, "mutex": mutex},
        )
    except TxAdminError as exc:
        return f"Error: {exc}"

    if result.get("error"):
        return f"Error: {result['error']}"
    if result.get("success"):
        detail = f" Reason: {reason}" if reason else ""
        return f"**[OK]** Kicked player netid {netid_int}.{detail}"
    return f"Unexpected response: {result}"
