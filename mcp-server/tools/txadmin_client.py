"""
txAdmin HTTP client (txadmin_client.py).

A small, dependency-free client for the txAdmin web API that ships with
FXServer. It authenticates with the local admin account, stores the session
cookie and CSRF token, and exposes a helper for authenticated requests.

Configuration is read from environment variables so that credentials never
live in the repository or in tool arguments:

    TXADMIN_URL        Base URL of the txAdmin panel (default http://127.0.0.1:40120)
    TXADMIN_USERNAME   Admin username (the one used to log into the panel)
    TXADMIN_PASSWORD   Admin password

The txAdmin API is not a formally versioned public REST API. These routes
were verified against the current txAdmin source (core/routes and
core/modules/WebServer). Auth uses POST /auth/password, which returns a
session cookie plus a csrfToken that must be echoed back in the
x-txadmin-csrftoken header on every authenticated route.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


DEFAULT_URL = "http://127.0.0.1:40120"
CSRF_HEADER = "x-txadmin-csrftoken"
REQUEST_TIMEOUT = 15  # seconds


class TxAdminError(Exception):
    """Raised when a txAdmin request cannot be completed."""


class TxAdminConfig:
    """Connection settings sourced from environment variables."""

    def __init__(self) -> None:
        self.url = os.environ.get("TXADMIN_URL", DEFAULT_URL).rstrip("/")
        self.username = os.environ.get("TXADMIN_USERNAME", "")
        self.password = os.environ.get("TXADMIN_PASSWORD", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.username and self.password)

    def missing_message(self) -> str:
        missing = []
        if not self.username:
            missing.append("TXADMIN_USERNAME")
        if not self.password:
            missing.append("TXADMIN_PASSWORD")
        return (
            "txAdmin is not configured. Set the following environment "
            f"variable(s): {', '.join(missing)}. "
            "Optionally set TXADMIN_URL (defaults to "
            f"{DEFAULT_URL})."
        )


class TxAdminClient:
    """Authenticated session against a txAdmin panel."""

    def __init__(self, config: TxAdminConfig | None = None) -> None:
        self.config = config or TxAdminConfig()
        self._cookies = CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookies)
        )
        self.csrf_token: str | None = None

    # -- internal helpers ---------------------------------------------------

    def _send(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        query: dict | None = None,
        with_csrf: bool = True,
    ) -> dict:
        url = f"{self.config.url}{path}"
        if query:
            # Drop None values so callers can pass optional params freely.
            cleaned = {k: v for k, v in query.items() if v is not None}
            url = f"{url}?{urllib.parse.urlencode(cleaned)}"

        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if with_csrf and self.csrf_token:
            headers[CSRF_HEADER] = self.csrf_token

        request = urllib.request.Request(
            url, data=data, headers=headers, method=method
        )

        try:
            with self._opener.open(request, timeout=REQUEST_TIMEOUT) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            parsed = _safe_json(raw)
            if parsed is not None:
                return parsed
            raise TxAdminError(
                f"HTTP {exc.code} from {path}: {raw[:200] or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TxAdminError(
                f"Could not reach txAdmin at {self.config.url} "
                f"({exc.reason}). Is the panel running and TXADMIN_URL correct?"
            ) from exc

        parsed = _safe_json(raw)
        if parsed is None:
            raise TxAdminError(f"Non-JSON response from {path}: {raw[:200]}")
        return parsed

    # -- public API ---------------------------------------------------------

    def login(self) -> None:
        """Authenticate and capture the session cookie and CSRF token."""
        if not self.config.is_configured:
            raise TxAdminError(self.config.missing_message())

        result = self._send(
            "POST",
            "/auth/password",
            body={
                "username": self.config.username,
                "password": self.config.password,
            },
            with_csrf=False,
        )

        if isinstance(result, dict) and result.get("error"):
            raise TxAdminError(f"Login failed: {result['error']}")

        token = result.get("csrfToken") if isinstance(result, dict) else None
        if not token or token == "not_set":
            raise TxAdminError(
                "Login succeeded but no CSRF token was returned. "
                "Your txAdmin version may be incompatible."
            )
        self.csrf_token = token

    def request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        query: dict | None = None,
    ) -> dict:
        """Run an authenticated request, logging in first if needed."""
        if self.csrf_token is None:
            self.login()
        return self._send(method, path, body=body, query=query)


def _safe_json(raw: str) -> dict | None:
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else {"data": parsed}
