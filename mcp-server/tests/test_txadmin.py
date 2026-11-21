"""txAdmin tools against a local fake panel (no real network)."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

from tools import txadmin as t


class FakePanel:
    def __init__(self):
        self.requests: list[dict] = []
        self.routes: dict[str, tuple[int, object]] = {
            "/auth/password": (200, {"csrfToken": "tok123"}),
            "/fxserver/controls": (200, {"type": "success", "msg": "Restarting"}),
            "/fxserver/commands": (200, {"type": "success", "msg": "ok"}),
            "/player/kick": (200, {"success": True}),
            "/player/search": (200, {"players": [{"displayName": f"p{i}", "license": "l"} for i in range(30)]}),
        }
        panel = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _handle(self):
                url = urlparse(self.path)
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode() if length else ""
                panel.requests.append({
                    "method": self.command, "path": url.path, "query": parse_qs(url.query),
                    "body": json.loads(body) if body else None,
                    "csrf": self.headers.get("x-txadmin-csrftoken"),
                })
                code, payload = panel.routes.get(url.path, (404, {"error": "not found"}))
                data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)

            do_GET = _handle
            do_POST = _handle

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def paths(self):
        return [r["path"] for r in self.requests]


@pytest.fixture
def panel(monkeypatch):
    p = FakePanel()
    monkeypatch.setenv("TXADMIN_URL", p.url)
    monkeypatch.setenv("TXADMIN_USERNAME", "admin")
    monkeypatch.setenv("TXADMIN_PASSWORD", "pw")
    yield p
    p.server.shutdown()


def test_missing_credentials(monkeypatch, panel):
    monkeypatch.delenv("TXADMIN_PASSWORD")
    out = t.txadmin_server_control("restart")
    assert out.startswith("Error") and "TXADMIN_PASSWORD" in out
    assert panel.requests == []


def test_login_csrf_propagates(panel):
    assert t.txadmin_server_control("  RESTART ") == "**[OK]** Restarting"
    assert panel.paths() == ["/auth/password", "/fxserver/controls"]
    assert panel.requests[1]["csrf"] == "tok123"


@pytest.mark.parametrize("payload", [{"error": "bad password"}, {"csrfToken": "not_set"}])
def test_login_failures(panel, payload):
    panel.routes["/auth/password"] = (200, payload)
    assert t.txadmin_server_control("restart").startswith("Error")
    assert panel.paths() == ["/auth/password"]


def test_invalid_action_sends_nothing(panel):
    assert t.txadmin_server_control("explode").startswith("Error: invalid action")
    assert panel.requests == []


def test_resource_ensure_body(panel):
    t.txadmin_resource_control("ensure", "my-res")
    assert panel.requests[-1]["body"] == {"action": "ensure_res", "parameter": "my-res"}


@pytest.mark.parametrize("route", [(401, {"logout": True}), (500, b"<html>boom</html>"), (200, {"logout": True}), (200, {})])
def test_failures_never_report_sent(panel, route):
    panel.routes["/fxserver/controls"] = route
    out = t.txadmin_server_control("stop")
    assert "request sent" not in out
    assert "Error" in out or "ERROR" in out


def test_connection_refused(monkeypatch):
    monkeypatch.setenv("TXADMIN_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("TXADMIN_USERNAME", "a")
    monkeypatch.setenv("TXADMIN_PASSWORD", "b")
    assert t.txadmin_server_control("restart").startswith("Error: Could not reach txAdmin")


def test_player_search_query_and_more(panel):
    out = t.txadmin_player_search("bob", limit=25)
    query = panel.requests[-1]["query"]
    assert "filters" not in query
    assert query["searchValue"] == ["bob"]
    assert out.splitlines()[-1].startswith("... and 5 more")


def test_player_search_limit_zero(panel):
    assert t.txadmin_player_search("", limit=0).splitlines()[-1].startswith("... and 29 more")


def test_kick(panel):
    assert t.txadmin_kick_player(5, "afk") == "**[OK]** Kicked player netid 5. Reason: afk"
    panel.routes["/player/kick"] = (200, {})
    assert t.txadmin_kick_player(5).startswith("Unexpected response")


@pytest.mark.parametrize("netid", ["abc", True, -1, 0])
def test_kick_rejects_bad_netid(panel, netid):
    assert t.txadmin_kick_player(netid).startswith("Error")
    assert panel.requests == []


def test_session_is_reused_across_calls(panel):
    t.txadmin_server_control("restart")
    t.txadmin_resource_control("restart", "x")
    assert panel.paths().count("/auth/password") == 1


def test_expired_session_logs_in_again(panel):
    t.txadmin_server_control("restart")
    panel.routes["/fxserver/commands"] = (401, {"logout": True})
    t.txadmin_resource_control("restart", "x")  # 401 on the reused session
    assert panel.paths().count("/auth/password") == 2


def test_refuses_plain_http_to_remote_host(monkeypatch, panel):
    monkeypatch.setenv("TXADMIN_URL", "http://203.0.113.10:40120")
    out = t.txadmin_server_control("restart")
    assert out.startswith("Error") and "plain HTTP" in out
    assert panel.requests == []
    from tools.txadmin_client import TxAdminConfig
    monkeypatch.setenv("TXADMIN_ALLOW_INSECURE", "1")
    assert TxAdminConfig().insecure_transport_error() is None
    monkeypatch.setenv("TXADMIN_URL", "https://panel.example.com")
    monkeypatch.delenv("TXADMIN_ALLOW_INSECURE")
    assert TxAdminConfig().insecure_transport_error() is None
