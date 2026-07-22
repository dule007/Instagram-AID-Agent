#!/usr/bin/env python3
"""Loopback-only OAuth connector for Instagram Professional accounts."""

from __future__ import annotations

import argparse
import html
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from credentials import (
    CANONICAL_INSTAGRAM_USERNAME,
    CredentialError,
    REQUIRED_INSTAGRAM_SCOPES,
    connection_status,
    delete_session,
    read_session,
    write_session,
)


AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
TOKEN_URL = "https://api.instagram.com/oauth/access_token"
LONG_LIVED_TOKEN_URL = "https://graph.instagram.com/access_token"
REFRESH_TOKEN_URL = "https://graph.instagram.com/refresh_access_token"
API_HOST = "graph.instagram.com"
DEFAULT_SCOPES = tuple(sorted(REQUIRED_INSTAGRAM_SCOPES))
LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
STATE_TTL_SECONDS = 600


class OAuthError(RuntimeError):
    pass


def config() -> dict:
    scopes = tuple(
        value.strip()
        for value in os.environ.get("META_INSTAGRAM_SCOPES", ",".join(DEFAULT_SCOPES)).split(",")
        if value.strip()
    )
    result = {
        "app_id": (os.environ.get("INSTAGRAM_APP_ID") or os.environ.get("META_APP_ID", "")).strip(),
        "app_secret": (os.environ.get("INSTAGRAM_APP_SECRET") or os.environ.get("META_APP_SECRET", "")).strip(),
        "redirect_uri": (os.environ.get("INSTAGRAM_REDIRECT_URI") or os.environ.get("META_REDIRECT_URI", "")).strip(),
        "graph_version": os.environ.get("META_GRAPH_VERSION", "").strip(),
        "expected_username": os.environ.get(
            "EXPECTED_INSTAGRAM_USERNAME", CANONICAL_INSTAGRAM_USERNAME
        ).strip().lstrip("@"),
        "expected_user_id": os.environ.get("EXPECTED_IG_USER_ID", "").strip(),
        "scopes": scopes,
    }
    return result


def missing_config(settings: dict) -> list[str]:
    pairs = (
        ("INSTAGRAM_APP_ID", "app_id"),
        ("INSTAGRAM_APP_SECRET", "app_secret"),
        ("INSTAGRAM_REDIRECT_URI", "redirect_uri"),
        ("META_GRAPH_VERSION", "graph_version"),
        ("EXPECTED_INSTAGRAM_USERNAME", "expected_username"),
    )
    missing = [name for name, key in pairs if not settings[key]]
    if settings["app_id"] and not settings["app_id"].isdigit():
        missing.append("INSTAGRAM_APP_ID (mora biti numerički Instagram App ID)")
    if settings["graph_version"] and not settings["graph_version"].startswith("v"):
        missing.append("META_GRAPH_VERSION (očekivano vXX.X)")
    if settings["expected_username"].casefold() != CANONICAL_INSTAGRAM_USERNAME.casefold():
        missing.append(f"EXPECTED_INSTAGRAM_USERNAME (mora biti {CANONICAL_INSTAGRAM_USERNAME})")
    if not settings["scopes"]:
        missing.append("META_INSTAGRAM_SCOPES")
    else:
        absent_scopes = sorted(REQUIRED_INSTAGRAM_SCOPES - set(settings["scopes"]))
        if absent_scopes:
            missing.append("META_INSTAGRAM_SCOPES (nedostaje " + ", ".join(absent_scopes) + ")")
    return missing


def validate_redirect_uri(value: str, host: str, port: int) -> None:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK_HOSTS:
        raise OAuthError("Lokalni konektor zahtijeva http loopback META_REDIRECT_URI.")
    if parsed.hostname != host:
        raise OAuthError(f"Host redirect URI-ja mora točno odgovarati serveru: {host}.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise OAuthError("META_REDIRECT_URI ne smije sadržavati userinfo, query ni fragment.")
    if parsed.port != port or parsed.path != "/callback":
        raise OAuthError(f"META_REDIRECT_URI mora točno biti http://{host}:{port}/callback.")


def authorization_url(settings: dict, state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": settings["app_id"],
            "redirect_uri": settings["redirect_uri"],
            "response_type": "code",
            "scope": ",".join(settings["scopes"]),
            "state": state,
            "enable_fb_login": "false",
            "force_reauth": "true",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def redact(value: str, secrets_to_hide: list[str]) -> str:
    result = value
    for secret in secrets_to_hide:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result


def request_json(request: urllib.request.Request, secrets_to_hide: list[str]) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = redact(exc.read().decode("utf-8", errors="replace"), secrets_to_hide)
        raise OAuthError(f"Meta OAuth greška {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise OAuthError(f"Meta OAuth nije dostupan: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise OAuthError(f"Meta nije vratio valjan JSON: {exc}") from exc


def multipart_form(values: dict[str, str]) -> tuple[bytes, str]:
    boundary = "----aid-instagram-" + secrets.token_hex(16)
    parts: list[bytes] = []
    for name, value in values.items():
        parts.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def exchange_code(settings: dict, code: str) -> dict:
    form, content_type = multipart_form(
        {
            "client_id": settings["app_id"],
            "client_secret": settings["app_secret"],
            "grant_type": "authorization_code",
            "redirect_uri": settings["redirect_uri"],
            "code": code,
        }
    )
    request = urllib.request.Request(
        TOKEN_URL,
        data=form,
        headers={"Content-Type": content_type, "Accept": "application/json"},
        method="POST",
    )
    payload = request_json(request, [settings["app_secret"], code])
    if not payload.get("access_token") or not payload.get("user_id"):
        raise OAuthError("Meta token odgovor nema access_token ili user_id.")
    return payload


def exchange_long_lived(settings: dict, short_token: str) -> dict:
    query = urllib.parse.urlencode(
        {
            "grant_type": "ig_exchange_token",
            "client_secret": settings["app_secret"],
            "access_token": short_token,
        }
    )
    request = urllib.request.Request(
        f"{LONG_LIVED_TOKEN_URL}?{query}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    payload = request_json(request, [settings["app_secret"], short_token])
    if not payload.get("access_token"):
        raise OAuthError("Meta long-lived odgovor nema access_token.")
    return payload


def refresh_long_lived(token: str) -> dict:
    query = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token})
    request = urllib.request.Request(
        f"{REFRESH_TOKEN_URL}?{query}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    payload = request_json(request, [token])
    if not payload.get("access_token"):
        raise OAuthError("Meta refresh odgovor nema access_token.")
    return payload


def profile_request(settings: dict, token: str, user_id: str) -> dict:
    candidates = (
        ("me", "user_id,username,account_type,media_count"),
        (str(user_id), "id,username,account_type,media_count"),
    )
    last_error: OAuthError | None = None
    for object_id, fields in candidates:
        query = urllib.parse.urlencode({"fields": fields})
        url = f"https://{API_HOST}/{settings['graph_version']}/{object_id}?{query}"
        request = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            method="GET",
        )
        try:
            return request_json(request, [token])
        except OAuthError as exc:
            last_error = exc
    raise last_error or OAuthError("Nije moguće potvrditi Instagram profil.")


def connect(settings: dict, code: str) -> dict:
    short_payload = exchange_code(settings, code)
    user_id = str(short_payload["user_id"])
    permissions_value = short_payload.get("permissions")
    if isinstance(permissions_value, str):
        granted_scopes = {value.strip() for value in permissions_value.split(",") if value.strip()}
    elif isinstance(permissions_value, list):
        granted_scopes = {str(value).strip() for value in permissions_value if str(value).strip()}
    else:
        granted_scopes = set()
    missing_scopes = sorted(set(settings["scopes"]) - granted_scopes)
    if missing_scopes:
        raise OAuthError("Meta nije dodijelio sve obavezne scopeove: " + ", ".join(missing_scopes) + ".")

    token_payload = exchange_long_lived(settings, str(short_payload["access_token"]))
    token_kind = "long_lived"
    token = str(token_payload["access_token"])
    profile = profile_request(settings, token, user_id)
    profile_id = str(profile.get("user_id") or profile.get("id") or "")
    username = str(profile.get("username") or "").lstrip("@")
    account_type = str(profile.get("account_type") or "").upper()
    if not profile_id or profile_id != user_id:
        raise OAuthError("Meta profil ne odgovara user_id vrijednosti iz OAuth razmjene.")
    if settings.get("expected_user_id") and profile_id != settings["expected_user_id"]:
        raise OAuthError("Odabran je pogrešan Instagram račun (ID se ne podudara).")
    if username.casefold() != str(settings["expected_username"]).casefold():
        raise OAuthError(
            f"Odabran je @{username or 'nepoznat'}; dopušten je samo @{settings['expected_username']}."
        )
    if account_type not in {"BUSINESS", "MEDIA_CREATOR", "CREATOR"}:
        raise OAuthError("Povezani Instagram račun nije potvrđen kao Business/Creator.")
    connected_at = datetime.now(timezone.utc)
    expires_in = token_payload.get("expires_in")
    if not expires_in:
        raise OAuthError("Meta long-lived token odgovor nema expires_in.")
    expires_at = (
        (connected_at + timedelta(seconds=int(expires_in))).isoformat()
        if isinstance(expires_in, (int, str)) and str(expires_in).isdigit()
        else ""
    )
    session = {
        "provider": "instagram_login",
        "api_host": API_HOST,
        "graph_version": settings["graph_version"],
        "ig_user_id": profile_id,
        "access_token": token,
        "username": username,
        "expected_username": settings["expected_username"],
        "account_type": account_type,
        "media_count": profile.get("media_count"),
        "scopes": sorted(granted_scopes),
        "token_kind": token_kind,
        "expires_in": expires_in,
        "expires_at": expires_at,
        "connected_at": connected_at.isoformat(),
    }
    write_session(session)
    return {key: value for key, value in session.items() if key != "access_token"}


def status_payload() -> dict:
    status = connection_status()
    settings = config()
    return {
        **status,
        "missing_configuration": missing_config(settings),
        "redirect_uri": settings["redirect_uri"],
        "requested_scopes": list(settings["scopes"]),
        "expected_username": settings["expected_username"],
        "password_used": False,
    }


def safe_request_log(method: str, target: str, status: object) -> str:
    """Render a request log line without OAuth query parameters."""
    path = urllib.parse.urlparse(target).path or "/"
    return f"[oauth] {method} {path} -> {status}\n"


def refresh_session() -> dict:
    session = read_session()
    if not session or not session.get("access_token"):
        raise OAuthError("Nema lokalne OAuth sesije za osvježavanje.")
    if session.get("token_kind") != "long_lived":
        raise OAuthError("Samo long-lived Instagram token može se osvježiti ovim tokom.")
    payload = refresh_long_lived(str(session["access_token"]))
    now = datetime.now(timezone.utc)
    expires_in = payload.get("expires_in")
    session["access_token"] = str(payload["access_token"])
    session["expires_in"] = expires_in
    session["expires_at"] = (
        (now + timedelta(seconds=int(expires_in))).isoformat()
        if isinstance(expires_in, (int, str)) and str(expires_in).isdigit()
        else ""
    )
    session["refreshed_at"] = now.isoformat()
    write_session({key: value for key, value in session.items() if key != "schema_version"})
    return {key: value for key, value in session.items() if key not in ("schema_version", "access_token")}


def page(title: str, body: str) -> bytes:
    return f"""<!doctype html><html lang="hr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>body{{margin:0;background:#08131f;color:#e8edf4;font:16px/1.55 system-ui,sans-serif}}main{{max-width:760px;margin:70px auto;padding:32px;background:#0d1b2a;border:1px solid #283c58;border-radius:18px}}h1{{margin-top:0}}code{{color:#f5a623}}a,button{{display:inline-block;background:#f5a623;color:#0d1b2a;border:0;border-radius:999px;padding:11px 18px;font-weight:800;text-decoration:none;cursor:pointer}}.muted{{color:#94a6be}}.error{{color:#ef6b73}}li{{margin:7px 0}}</style></head>
<body><main><h1>{html.escape(title)}</h1>{body}</main></body></html>""".encode("utf-8")


class OAuthHandler(BaseHTTPRequestHandler):
    settings: dict
    host: str
    port: int
    pending_states: dict[str, float] = {}

    def send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, url: str) -> None:
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            payload = json.dumps(status_payload(), ensure_ascii=False, indent=2).encode("utf-8")
            self.send(200, "application/json; charset=utf-8", payload)
            return
        if parsed.path == "/start":
            missing = missing_config(self.settings)
            if missing:
                message = "<p class=\"error\">Nedostaje konfiguracija:</p><ul>" + "".join(
                    f"<li><code>{html.escape(name)}</code></li>" for name in missing
                ) + "</ul><p><a href=\"/\">Natrag</a></p>"
                self.send(400, "text/html; charset=utf-8", page("Povezivanje je blokirano", message))
                return
            try:
                validate_redirect_uri(self.settings["redirect_uri"], self.host, self.port)
            except OAuthError as exc:
                self.send(400, "text/html; charset=utf-8", page("Povezivanje je blokirano", f'<p class="error">{html.escape(str(exc))}</p>'))
                return
            state = secrets.token_urlsafe(32)
            self.pending_states[state] = time.time()
            self.redirect(authorization_url(self.settings, state))
            return
        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            if params.get("error"):
                message = params.get("error_description", params["error"])[0]
                self.send(400, "text/html; charset=utf-8", page("Meta autorizacija nije uspjela", f'<p class="error">{html.escape(message)}</p>'))
                return
            state = params.get("state", [""])[0]
            code = params.get("code", [""])[0]
            created = self.pending_states.pop(state, None)
            if not state or created is None or time.time() - created > STATE_TTL_SECONDS:
                self.send(400, "text/html; charset=utf-8", page("Nevažeći OAuth state", '<p class="error">Pokrenite povezivanje ponovno.</p>'))
                return
            if not code:
                self.send(400, "text/html; charset=utf-8", page("Nedostaje OAuth code", '<p class="error">Meta nije vratila authorization code.</p>'))
                return
            try:
                connected = connect(self.settings, code)
            except (OAuthError, CredentialError, OSError) as exc:
                self.send(502, "text/html; charset=utf-8", page("Povezivanje nije dovršeno", f'<p class="error">{html.escape(str(exc))}</p>'))
                return
            username = connected.get("username") or connected.get("ig_user_id")
            body = f'<p>Račun <strong>@{html.escape(str(username))}</strong> službeno je povezan.</p><p class="muted">Lozinka nije proslijeđena agentu. Možete zatvoriti ovaj prozor.</p>'
            self.send(200, "text/html; charset=utf-8", page("Instagram je povezan", body))
            return
        if parsed.path == "/":
            payload = status_payload()
            if payload["status"] in ("connected", "configured"):
                username = f"@{payload['username']}" if payload["username"] else "profesionalni račun"
                body = f'<p>Povezano: <strong>{html.escape(username)}</strong></p><p class="muted">Izvor: {html.escape(payload["source"])}</p>'
            else:
                missing = payload["missing_configuration"]
                setup = "" if not missing else "<p>Nedostaje:</p><ul>" + "".join(
                    f"<li><code>{html.escape(name)}</code></li>" for name in missing
                ) + "</ul>"
                body = setup + '<p><a href="/start">Poveži Instagram kroz Meta</a></p><p class="muted">Prijava se otvara na instagram.com. Agent ne vidi ni sprema lozinku.</p>'
            self.send(200, "text/html; charset=utf-8", page("AID Instagram OAuth", body))
            return
        self.send(404, "text/plain; charset=utf-8", b"Not found")

    def do_POST(self) -> None:  # noqa: N802
        self.send(405, "text/plain; charset=utf-8", b"Method not allowed; use the confirmed local CLI command.")

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        del size
        sys.stderr.write(safe_request_log(self.command, self.path, code))

    def log_message(self, format: str, *args: object) -> None:
        del format, args
        sys.stderr.write("[oauth] lokalni server event\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="AID Instagram OAuth connector")
    sub = result.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=7012)
    serve.add_argument("--open-browser", action="store_true")
    sub.add_parser("check")
    sub.add_parser("status")
    sub.add_parser("refresh")
    disconnect = sub.add_parser("disconnect")
    disconnect.add_argument("--confirm", required=True)
    return result


def command_serve(args: argparse.Namespace) -> int:
    if args.host not in LOOPBACK_HOSTS:
        raise OAuthError("OAuth server smije slušati samo na loopback adresi.")
    OAuthHandler.settings = config()
    OAuthHandler.host = args.host
    OAuthHandler.port = args.port
    server = ThreadingHTTPServer((args.host, args.port), OAuthHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"AID Instagram OAuth: {url}")
    print("Token se sprema lokalno s dozvolom 0600 i ne ulazi u Git.")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "serve":
            return command_serve(args)
        if args.command == "check":
            payload = status_payload()
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            ready = payload["status"] in ("connected", "configured") and not payload["missing_configuration"]
            return 0 if ready else 1
        if args.command == "status":
            print(json.dumps(status_payload(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "refresh":
            print(json.dumps(refresh_session(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "disconnect":
            if args.confirm != "DISCONNECT":
                raise OAuthError("Za odspajanje koristite --confirm DISCONNECT.")
            print("OAuth sesija uklonjena." if delete_session() else "OAuth sesija nije postojala.")
            return 0
    except (OAuthError, CredentialError, OSError, ValueError) as exc:
        print(f"OAUTH BLOKIRAN: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
