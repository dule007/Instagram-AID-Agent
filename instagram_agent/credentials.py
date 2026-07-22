#!/usr/bin/env python3
"""Local secret-session helpers shared by Instagram adapters."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parent
OAUTH_ROOT = AGENT_ROOT / "state" / "oauth"
SESSION_PATH = OAUTH_ROOT / "session.json"
ALLOWED_API_HOSTS = {"graph.instagram.com", "graph.facebook.com"}
ENV_CREDENTIAL_KEYS = (
    "META_GRAPH_VERSION",
    "IG_USER_ID",
    "META_ACCESS_TOKEN",
    "INSTAGRAM_IG_USER_ID",
    "INSTAGRAM_ACCESS_TOKEN",
)
ENV_ACCOUNT_KEYS = ("IG_USER_ID", "META_ACCESS_TOKEN", "INSTAGRAM_IG_USER_ID", "INSTAGRAM_ACCESS_TOKEN")
ENV_CREDENTIAL_ALIASES = {
    "META_GRAPH_VERSION": ("META_GRAPH_VERSION",),
    "IG_USER_ID": ("IG_USER_ID", "INSTAGRAM_IG_USER_ID"),
    "META_ACCESS_TOKEN": ("META_ACCESS_TOKEN", "INSTAGRAM_ACCESS_TOKEN"),
}
CANONICAL_INSTAGRAM_USERNAME = "autoinsightdata"
REQUIRED_INSTAGRAM_SCOPES = frozenset(
    {
        "instagram_business_basic",
        "instagram_business_content_publish",
        "instagram_business_manage_insights",
    }
)


ENV_FILE = AGENT_ROOT / ".env"


class CredentialError(RuntimeError):
    pass


def load_env_file(path: Path | None = None) -> list[str]:
    """Load the single local `.env` so every entry point shares one key file.

    Existing environment values win, pa vanjski launcher i dalje ima prednost.
    Vrijednosti se nikada ne ispisuju; vraćaju se samo imena učitanih ključeva.
    """
    source = path or ENV_FILE
    if not source.is_file():
        return []
    if source.stat().st_mode & 0o077:
        raise CredentialError(f"{source.name} mora imati dozvolu 0600.")
    loaded: list[str] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        name, _, value = entry.partition("=")
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if not name or not value or os.environ.get(name, "").strip():
            continue
        os.environ[name] = value
        loaded.append(name)
    return loaded


def environment_credentials() -> dict[str, str]:
    """Resolve supported environment aliases without ever exposing values."""
    resolved: dict[str, str] = {}
    for canonical, names in ENV_CREDENTIAL_ALIASES.items():
        present = [(name, os.environ.get(name, "").strip()) for name in names]
        present = [(name, value) for name, value in present if value]
        if len({value for _, value in present}) > 1:
            raise CredentialError("Konfliktne environment vrijednosti za: " + ", ".join(names) + ".")
        resolved[canonical] = present[0][1] if present else ""
    return resolved


def read_session() -> dict | None:
    if not SESSION_PATH.is_file():
        return None
    if SESSION_PATH.stat().st_mode & 0o077:
        raise CredentialError("OAuth session.json mora imati dozvolu 0600.")
    try:
        data = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CredentialError(f"OAuth sesija se ne može učitati: {exc}") from exc
    if data.get("schema_version") != 1:
        raise CredentialError("OAuth sesija ima nepodržanu schema_version.")
    required = (
        "provider",
        "api_host",
        "graph_version",
        "ig_user_id",
        "access_token",
        "username",
        "expected_username",
        "account_type",
        "scopes",
        "token_kind",
        "expires_at",
    )
    missing = [name for name in required if not data.get(name)]
    if missing:
        raise CredentialError("OAuth sesija je nepotpuna; nedostaje: " + ", ".join(missing) + ".")
    if str(data["username"]).casefold() != CANONICAL_INSTAGRAM_USERNAME.casefold():
        raise CredentialError("OAuth sesija nije vezana uz kanonski @autoinsightdata račun.")
    if str(data["expected_username"]).casefold() != CANONICAL_INSTAGRAM_USERNAME.casefold():
        raise CredentialError("OAuth sesija ima pogrešan expected_username.")
    if str(data["account_type"]).upper() not in {"BUSINESS", "MEDIA_CREATOR", "CREATOR"}:
        raise CredentialError("OAuth sesija nema valjan profesionalni account_type.")
    if data["token_kind"] != "long_lived":
        raise CredentialError("OAuth sesija mora sadržavati long-lived token.")
    if not isinstance(data["scopes"], list) or not REQUIRED_INSTAGRAM_SCOPES.issubset(data["scopes"]):
        raise CredentialError("OAuth sesija nema sve obavezne Instagram scopeove.")
    return data


def write_session(data: dict) -> None:
    OAUTH_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(OAUTH_ROOT, 0o700)
    payload = {**data, "schema_version": 1}
    descriptor, temporary = tempfile.mkstemp(prefix="session-", suffix=".tmp", dir=OAUTH_ROOT)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, SESSION_PATH)
        os.chmod(SESSION_PATH, 0o600)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            Path(temporary).unlink()
        except OSError:
            pass
        raise


def delete_session() -> bool:
    if not SESSION_PATH.exists():
        return False
    SESSION_PATH.unlink()
    return True


def api_credentials() -> dict:
    """Resolve one complete credential source without mixing accounts."""
    environment_values = environment_credentials()
    environment_present = bool(environment_values["IG_USER_ID"] or environment_values["META_ACCESS_TOKEN"])
    if environment_present:
        missing_environment = [name for name, value in environment_values.items() if not value]
        if missing_environment:
            raise CredentialError(
                "Djelomična Meta environment konfiguracija nije dopuštena; nedostaje: "
                + ", ".join(missing_environment)
                + "."
            )
        session: dict = {}
    else:
        session = read_session() or {}
    if session and session.get("expires_at"):
        try:
            expires_at = datetime.fromisoformat(str(session["expires_at"]))
        except ValueError as exc:
            raise CredentialError("OAuth sesija ima nevaljan expires_at.") from exc
        if expires_at.tzinfo is None or expires_at <= datetime.now(timezone.utc):
            raise CredentialError("Instagram OAuth token je istekao; ponovno povežite ili osvježite račun.")
    values = {
        "api_host": os.environ.get("IG_API_HOST") or session.get("api_host") or "graph.instagram.com",
        "graph_version": environment_values["META_GRAPH_VERSION"] or session.get("graph_version") or "",
        "ig_user_id": environment_values["IG_USER_ID"] or session.get("ig_user_id") or "",
        "access_token": environment_values["META_ACCESS_TOKEN"] or session.get("access_token") or "",
        "username": session.get("username", ""),
        "account_type": session.get("account_type", ""),
        "connected_at": session.get("connected_at", ""),
        "source": "environment" if environment_present else ("oauth_session" if session else "missing"),
    }
    if values["api_host"] not in ALLOWED_API_HOSTS:
        raise CredentialError(f"IG_API_HOST mora biti jedan od: {', '.join(sorted(ALLOWED_API_HOSTS))}.")
    missing = [
        name
        for name, key in (
            ("META_GRAPH_VERSION", "graph_version"),
            ("IG_USER_ID", "ig_user_id"),
            ("META_ACCESS_TOKEN", "access_token"),
        )
        if not values[key]
    ]
    if missing:
        raise CredentialError(f"Nedostaju službene Meta vrijednosti: {', '.join(missing)}.")
    if not str(values["graph_version"]).startswith("v"):
        raise CredentialError("META_GRAPH_VERSION mora imati oblik vXX.X.")
    return values


def connection_status() -> dict:
    environment_values = environment_credentials()
    environment_present = bool(environment_values["IG_USER_ID"] or environment_values["META_ACCESS_TOKEN"])
    environment_ready = all(environment_values.values())
    if environment_ready:
        return {
            "status": "configured",
            "source": "environment",
            "username": "",
            "account_type": "",
            "connected_at": "",
            "api_host": os.environ.get("IG_API_HOST", "graph.instagram.com"),
            "token_kind": "environment",
            "expires_at": "",
        }
    if environment_present:
        missing = [name for name, value in environment_values.items() if not value]
        return {
            "status": "error",
            "source": "incomplete_environment",
            "username": "",
            "account_type": "",
            "connected_at": "",
            "api_host": os.environ.get("IG_API_HOST", "graph.instagram.com"),
            "token_kind": "environment",
            "expires_at": "",
            "message": "Nedostaje: " + ", ".join(missing) + ".",
        }
    session = read_session()
    if session:
        expires_at_value = str(session.get("expires_at", ""))
        if expires_at_value:
            try:
                expires_at = datetime.fromisoformat(expires_at_value)
            except ValueError as exc:
                raise CredentialError("OAuth sesija ima nevaljan expires_at.") from exc
            if expires_at.tzinfo is None or expires_at <= datetime.now(timezone.utc):
                return {
                    "status": "expired",
                    "source": "oauth_session",
                    "username": session.get("username", ""),
                    "account_type": session.get("account_type", ""),
                    "connected_at": session.get("connected_at", ""),
                    "api_host": session.get("api_host", ""),
                    "token_kind": session.get("token_kind", ""),
                    "expires_at": expires_at_value,
                    "message": "Instagram OAuth token je istekao.",
                }
        return {
            "status": "connected",
            "source": "oauth_session",
            "username": session.get("username", ""),
            "account_type": session.get("account_type", ""),
            "connected_at": session.get("connected_at", ""),
            "api_host": session.get("api_host", ""),
            "token_kind": session.get("token_kind", ""),
            "expires_at": session.get("expires_at", ""),
        }
    return {
        "status": "disconnected",
        "source": "missing",
        "username": "",
        "account_type": "",
        "connected_at": "",
        "api_host": "",
        "token_kind": "",
        "expires_at": "",
    }
