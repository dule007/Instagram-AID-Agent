#!/usr/bin/env python3
"""Public GitHub media host for final Instagram publish assets.

Meta ne može povući sliku s lokalnog diska; publish container traži javni HTTPS
URL. Ovaj modul objavljuje samo zaključani finalni JPEG u zaseban javni GitHub
repozitorij i vraća stabilan `raw.githubusercontent.com` URL.

Naziv datoteke sadrži sažetak sadržaja, pa izmijenjeni asset uvijek dobiva novi
URL i Meta nikada ne povuče predmemoriranu staru verziju.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_ROOT = "https://api.github.com"
RAW_ROOT = "https://raw.githubusercontent.com"
DEFAULT_REPO = "dule007/Instagram-AID-Agent"
DEFAULT_BRANCH = "main"
DEFAULT_DIRECTORY = "media"
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
CONTENT_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


class MediaHostError(RuntimeError):
    pass


def config() -> dict[str, str]:
    """Resolve host configuration from the single local `.env` file."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise MediaHostError(
            "GITHUB_TOKEN nije postavljen u instagram_agent/.env; media hosting je blokiran."
        )
    repo = os.environ.get("GITHUB_MEDIA_REPO", "").strip() or DEFAULT_REPO
    if repo.count("/") != 1 or not all(part.strip() for part in repo.split("/")):
        raise MediaHostError("GITHUB_MEDIA_REPO mora imati oblik vlasnik/repozitorij.")
    return {
        "token": token,
        "repo": repo,
        "branch": os.environ.get("GITHUB_MEDIA_BRANCH", "").strip() or DEFAULT_BRANCH,
        "directory": (os.environ.get("GITHUB_MEDIA_DIR", "").strip() or DEFAULT_DIRECTORY).strip("/"),
    }


def redact(text: str, token: str) -> str:
    return text.replace(token, "[REDACTED]") if token else text


def request_json(method: str, url: str, token: str, payload: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "aid-instagram-agent",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return response.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as exc:
        detail = redact(exc.read().decode("utf-8", errors="replace"), token)
        if exc.code == 404:
            return 404, {}
        if exc.code == 401:
            raise MediaHostError("GitHub je odbio token (401); provjerite GITHUB_TOKEN u .env.") from exc
        if exc.code == 403:
            raise MediaHostError(f"GitHub je odbio zahtjev (403); token nema potrebne ovlasti: {detail}") from exc
        raise MediaHostError(f"GitHub API greška {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MediaHostError(f"GitHub API nije dostupan: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise MediaHostError(f"GitHub nije vratio valjan JSON: {exc}") from exc


def repo_status() -> dict:
    """Report whether the configured media repository can serve Meta."""
    try:
        settings = config()
    except MediaHostError as exc:
        return {"status": "unconfigured", "repo": "", "message": str(exc)}
    status, payload = request_json("GET", f"{API_ROOT}/repos/{settings['repo']}", settings["token"])
    if status == 404:
        return {
            "status": "error",
            "repo": settings["repo"],
            "message": "Repozitorij ne postoji ili token nema pristup.",
        }
    if payload.get("private"):
        return {
            "status": "private",
            "repo": settings["repo"],
            "message": "Repozitorij je privatan; Meta ne može povući sliku. Postavite ga na Public.",
        }
    return {
        "status": "ready",
        "repo": settings["repo"],
        "branch": settings["branch"],
        "directory": settings["directory"],
        "message": f"Javni media host spreman: {settings['repo']}.",
    }


def remote_name(content_id: str, source: Path, digest: str) -> str:
    safe_id = "".join(char if char.isalnum() or char in "-_" else "-" for char in content_id)
    return f"{safe_id}-{digest[:12]}{source.suffix.casefold()}"


def public_url(settings: dict[str, str], path: str) -> str:
    return f"{RAW_ROOT}/{settings['repo']}/{settings['branch']}/{urllib.parse.quote(path)}"


def upload(content_id: str, source: Path) -> dict:
    """Publish one final asset and return its stable public HTTPS URL."""
    if not source.is_file():
        raise MediaHostError(f"{content_id}: publish asset ne postoji: {source}")
    if source.suffix.casefold() not in ALLOWED_SUFFIXES:
        raise MediaHostError(f"{content_id}: dopušteni su samo {sorted(ALLOWED_SUFFIXES)} asseti.")
    data = source.read_bytes()
    if len(data) > MAX_UPLOAD_BYTES:
        raise MediaHostError(f"{content_id}: asset prelazi ograničenje od 8 MB.")

    settings = config()
    state = repo_status()
    if state["status"] != "ready":
        raise MediaHostError(state["message"])

    digest = hashlib.sha256(data).hexdigest()
    path = f"{settings['directory']}/{remote_name(content_id, source, digest)}" if settings["directory"] else remote_name(content_id, source, digest)
    endpoint = f"{API_ROOT}/repos/{settings['repo']}/contents/{urllib.parse.quote(path)}"

    existing_status, existing = request_json(
        "GET", f"{endpoint}?ref={urllib.parse.quote(settings['branch'])}", settings["token"]
    )
    if existing_status == 200 and existing.get("type") == "file":
        return {
            "url": public_url(settings, path),
            "path": path,
            "sha256": digest,
            "uploaded": False,
            "message": "Asset je već objavljen s istim sadržajem.",
        }

    _, result = request_json(
        "PUT",
        endpoint,
        settings["token"],
        {
            "message": f"media: {content_id} ({digest[:12]})",
            "content": base64.b64encode(data).decode("ascii"),
            "branch": settings["branch"],
        },
    )
    if not result.get("content", {}).get("path"):
        raise MediaHostError(f"{content_id}: GitHub nije potvrdio upload asseta.")
    return {
        "url": public_url(settings, path),
        "path": path,
        "sha256": digest,
        "uploaded": True,
        "message": "Asset je objavljen na javni media host.",
    }


def verify(url: str, attempts: int = 5, delay_seconds: float = 3.0) -> dict:
    """Confirm the public URL really serves an image before Meta is called.

    Svježe objavljen asset zna nekoliko sekundi kasniti na GitHub CDN-u, pa se
    provjera ponavlja umjesto da odmah proglasi URL neispravnim.
    """
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "aid-instagram-agent"})
    last_error = ""
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                content_type = response.headers.get("Content-Type", "")
                length = response.headers.get("Content-Length", "")
                response.read(512)
            if content_type.startswith("image/"):
                return {"content_type": content_type, "content_length": length}
            last_error = f"URL ne vraća sliku nego '{content_type or 'nepoznat tip'}'"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
        except urllib.error.URLError as exc:
            last_error = str(exc.reason)
        if attempt + 1 < attempts:
            time.sleep(delay_seconds)
    raise MediaHostError(f"Javni media URL nije upotrebljiv za Metu: {last_error}.")
