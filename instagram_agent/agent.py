#!/usr/bin/env python3
"""Approval-gated Instagram publisher for AID campaign manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from credentials import CANONICAL_INSTAGRAM_USERNAME, CredentialError, api_credentials
from research_gate import ResearchGateError, validate_research_gate


AGENT_ROOT = Path(__file__).resolve().parent
STATE_ROOT = AGENT_ROOT / "state"
MAX_IMAGE_BYTES = 8 * 1024 * 1024
CONTAINER_POLL_ATTEMPTS = 30
CONTAINER_POLL_INTERVAL_SECONDS = 2.0
JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


class AgentError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentError(f"Manifest se ne može učitati: {exc}") from exc
    if data.get("schema_version") != 1 or not isinstance(data.get("items"), list):
        raise AgentError("Manifest mora imati schema_version=1 i items listu.")
    return data


def save_manifest(path: Path, manifest: dict) -> None:
    """Atomically persist a manifest edited from the control dashboard."""
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("items"), list):
        raise AgentError("Odbijen je upis manifesta bez schema_version=1 i items liste.")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def update_item(manifest_path: Path, content_id: str, changes: dict) -> dict:
    """Apply a whitelisted manifest change and return the updated item.

    Svaka izmjena ovdje mijenja fingerprint, pa postojeće odobrenje automatski
    prestaje vrijediti. To je namjerno i u skladu s pravilom da izmjena nakon
    odobrenja poništava odobrenje.
    """
    allowed = {"scheduled_at", "media_url", "status"}
    unknown = set(changes) - allowed
    if unknown:
        raise AgentError(f"Nedopuštena izmjena manifesta: {sorted(unknown)}.")
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, content_id)
    if "scheduled_at" in changes:
        scheduled = datetime.fromisoformat(str(changes["scheduled_at"]))
        if scheduled.tzinfo is None:
            raise AgentError("Novi termin mora sadržavati vremensku zonu.")
    if "media_url" in changes:
        media_url = str(changes["media_url"])
        if media_url and not media_url.startswith("https://"):
            raise AgentError("media_url mora biti javni HTTPS URL.")
    item.update(changes)
    save_manifest(manifest_path, manifest)
    return item


def resolve(manifest_path: Path, value: str) -> Path:
    return (manifest_path.parent / value).resolve()


def caption_text(manifest_path: Path, item: dict) -> str:
    caption_path = item.get("caption_path")
    if not caption_path:
        return ""
    text = resolve(manifest_path, caption_path).read_text(encoding="utf-8")
    marker = "## Caption\n"
    if marker not in text:
        raise AgentError(f"{item['id']}: caption datoteka nema odjeljak '## Caption'.")
    caption = text.split(marker, 1)[1].split("\n## ", 1)[0].strip()
    if not caption:
        raise AgentError(f"{item['id']}: caption je prazan.")
    return caption


def brief_text(manifest_path: Path, item: dict) -> str:
    brief_path = item.get("brief_path")
    if not brief_path:
        raise AgentError(f"{item.get('id', 'nepoznat sadržaj')}: brief_path nije postavljen.")
    text = resolve(manifest_path, brief_path).read_text(encoding="utf-8").strip()
    if not text:
        raise AgentError(f"{item['id']}: content brief je prazan.")
    return text


def story_instruction_text(manifest_path: Path, item: dict) -> str:
    text = brief_text(manifest_path, item)
    marker = "## Uputa\n"
    if marker not in text:
        raise AgentError(f"{item['id']}: Story brief nema odjeljak '## Uputa'.")
    return text.split(marker, 1)[1].strip()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AgentError(f"Nije valjan PNG: {path}")
    return struct.unpack(">II", header[16:24])


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise AgentError(f"Nije valjan JPEG: {path}")
    offset = 2
    while offset + 3 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0x01, 0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            break
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            break
        if marker in JPEG_SOF_MARKERS:
            if segment_length < 7:
                break
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            if width and height:
                return width, height
            break
        offset += segment_length
    raise AgentError(f"JPEG nema čitljive dimenzije: {path}")


def image_size(path: Path) -> tuple[int, int]:
    if path.suffix.casefold() == ".png":
        return png_size(path)
    if path.suffix.casefold() in {".jpg", ".jpeg"}:
        return jpeg_size(path)
    raise AgentError(f"Nepodržan slikovni format: {path}")


def publish_media_path(manifest_path: Path, item: dict) -> Path:
    return resolve(manifest_path, item.get("publish_media_path") or item["media_path"])


def fingerprint(manifest_path: Path, item: dict) -> str:
    media_path = resolve(manifest_path, item["media_path"])
    media_hash = hashlib.sha256(media_path.read_bytes()).hexdigest()
    api_media_path = publish_media_path(manifest_path, item)
    api_media_hash = hashlib.sha256(api_media_path.read_bytes()).hexdigest()
    brief_hash = hashlib.sha256(brief_text(manifest_path, item).encode("utf-8")).hexdigest()
    manifest = load_manifest(manifest_path)
    research_path = resolve(manifest_path, manifest["research_gate_path"])
    research_gate = json.loads(research_path.read_text(encoding="utf-8"))
    research_locked = {
        "researched_at": research_gate.get("researched_at"),
        "expires_at": research_gate.get("expires_at"),
        "benchmark_file": research_gate.get("benchmark_file"),
        "sources": research_gate.get("sources"),
        "record": research_gate.get("items", {}).get(item["id"]),
    }
    research_hash = hashlib.sha256(
        json.dumps(research_locked, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    locked = {
        "id": item["id"],
        "scheduled_at": item["scheduled_at"],
        "channel": item["channel"],
        "media_type": item["media_type"],
        "media_url": item.get("media_url", ""),
        "caption": caption_text(manifest_path, item),
        "media_sha256": media_hash,
        "brief_sha256": brief_hash,
        "research_sha256": research_hash,
        "native_sticker": item.get("native_sticker", ""),
    }
    if item.get("publish_media_path"):
        locked["publish_media_sha256"] = api_media_hash
    raw = json.dumps(locked, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def find_item(manifest: dict, content_id: str) -> dict:
    for item in manifest["items"]:
        if item.get("id") == content_id:
            return item
    raise AgentError(f"Sadržaj ne postoji u manifestu: {content_id}")


def validate_item(manifest_path: Path, item: dict, publishing: bool = False) -> list[str]:
    required = ("id", "scheduled_at", "channel", "media_type", "media_path", "brief_path", "claims_status")
    missing = [key for key in required if not item.get(key)]
    if missing:
        raise AgentError(f"Stavka nema obavezna polja {missing}: {item}")
    if item["claims_status"] != "verified":
        raise AgentError(f"{item['id']}: claims_status nije verified.")
    scheduled = datetime.fromisoformat(item["scheduled_at"])
    if scheduled.tzinfo is None:
        raise AgentError(f"{item['id']}: scheduled_at mora sadržavati vremensku zonu.")
    media = resolve(manifest_path, item["media_path"])
    if not media.is_file():
        raise AgentError(f"{item['id']}: nedostaje media datoteka {media}")
    expected = (1080, 1350) if item["channel"] == "FEED" else (1080, 1920)
    actual = image_size(media)
    if actual != expected:
        raise AgentError(f"{item['id']}: dimenzije {actual}, očekivano {expected}.")
    api_media = publish_media_path(manifest_path, item)
    if not api_media.is_file():
        raise AgentError(f"{item['id']}: nedostaje publish media datoteka {api_media}")
    api_actual = image_size(api_media)
    if api_actual != expected:
        raise AgentError(f"{item['id']}: publish media dimenzije {api_actual}, očekivano {expected}.")
    brief_text(manifest_path, item)
    caption_text(manifest_path, item)
    warnings: list[str] = []
    media_url = item.get("media_url", "")
    if not media_url:
        if not item.get("manual_only"):
            warnings.append(f"{item['id']}: media_url nije postavljen; objava je blokirana do javnog HTTPS URL-a.")
    elif not media_url.startswith("https://"):
        raise AgentError(f"{item['id']}: media_url mora biti javni HTTPS URL.")
    if item["channel"] == "STORY" and item.get("native_sticker"):
        warnings.append(f"{item['id']}: native sticker '{item['native_sticker']}' mora se dodati ručno u Instagramu.")
        if publishing:
            raise AgentError(f"{item['id']}: Story s native stickerom označen je manual_only.")
    if publishing and not item.get("manual_only") and item["media_type"] in {"IMAGE", "STORIES"}:
        if api_media.suffix.casefold() not in {".jpg", ".jpeg"}:
            raise AgentError(f"{item['id']}: Meta image publish zahtijeva zaključani JPEG asset.")
        if api_media.stat().st_size > MAX_IMAGE_BYTES:
            raise AgentError(f"{item['id']}: JPEG prelazi ograničenje od 8 MB.")
    return warnings


def approval_path(content_id: str) -> Path:
    return STATE_ROOT / "approvals" / f"{content_id}.json"


def published_path(content_id: str) -> Path:
    return STATE_ROOT / "published" / f"{content_id}.json"


def pending_path(content_id: str) -> Path:
    return STATE_ROOT / "pending" / f"{content_id}.json"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_approval(manifest_path: Path, item: dict) -> dict:
    path = approval_path(item["id"])
    if not path.is_file():
        raise AgentError(f"{item['id']}: nema ručnog approval zapisa.")
    approval = json.loads(path.read_text(encoding="utf-8"))
    current = fingerprint(manifest_path, item)
    if approval.get("fingerprint") != current:
        raise AgentError(f"{item['id']}: sadržaj je izmijenjen nakon odobrenja; potrebno je novo odobrenje.")
    return approval


def graph_post(endpoint: str, values: dict[str, str], token: str) -> dict:
    request = urllib.request.Request(
        endpoint,
        data=urllib.parse.urlencode(values).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        detail = detail.replace(token, "[REDACTED]")
        raise AgentError(f"Meta API greška {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise AgentError(f"Meta API nije dostupan: {exc}") from exc


def graph_get(endpoint: str, token: str) -> dict:
    request = urllib.request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").replace(token, "[REDACTED]")
        raise AgentError(f"Meta provjera ciljnog računa nije uspjela ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise AgentError(f"Meta API nije dostupan: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise AgentError(f"Meta nije vratio valjan profilni JSON: {exc}") from exc


def wait_for_container(base: str, creation_id: str, token: str) -> dict:
    endpoint = f"{base.rsplit('/', 1)[0]}/{creation_id}?fields=status_code,status"
    for attempt in range(CONTAINER_POLL_ATTEMPTS):
        payload = graph_get(endpoint, token)
        status_code = str(payload.get("status_code") or "").upper()
        if status_code == "FINISHED":
            return payload
        if status_code in {"ERROR", "EXPIRED", "PUBLISHED"}:
            detail = str(payload.get("status") or status_code)
            raise AgentError(f"Meta media container nije spreman za publish: {detail}.")
        if status_code != "IN_PROGRESS":
            raise AgentError(f"Meta je vratio nepoznat container status: {status_code or 'prazno'}.")
        if attempt + 1 < CONTAINER_POLL_ATTEMPTS:
            time.sleep(CONTAINER_POLL_INTERVAL_SECONDS)
    raise AgentError("Meta media container nije dovršen unutar 60 sekundi.")


def validate_target_profile(profile: dict, expected_id: str) -> None:
    profile_id = str(profile.get("user_id") or profile.get("id") or "")
    username = str(profile.get("username") or "").lstrip("@")
    account_type = str(profile.get("account_type") or "").upper()
    if profile_id != expected_id:
        raise AgentError("Meta profil ne odgovara konfiguriranom IG User ID-u; objava je blokirana.")
    if username.casefold() != CANONICAL_INSTAGRAM_USERNAME.casefold():
        raise AgentError(
            f"Token pripada @{username or 'nepoznat'}, a dopušten je samo @{CANONICAL_INSTAGRAM_USERNAME}."
        )
    if account_type not in {"BUSINESS", "MEDIA_CREATOR", "CREATOR"}:
        raise AgentError("Ciljni Instagram račun nije potvrđen kao Business/Creator.")


def publish_item(manifest_path: Path, item: dict, ignore_schedule: bool = False) -> dict:
    manifest = load_manifest(manifest_path)
    validate_research_gate(manifest_path, manifest, [item["id"]])
    validate_item(manifest_path, item, publishing=True)
    approval = require_approval(manifest_path, item)
    published = published_path(item["id"])
    if published.is_file():
        raise AgentError(f"{item['id']}: već postoji published zapis; duplikat je blokiran.")
    pending = pending_path(item["id"])
    if pending.is_file():
        raise AgentError(f"{item['id']}: postoji nerazriješen publish pokušaj; automatski retry je blokiran.")
    scheduled = datetime.fromisoformat(item["scheduled_at"])
    if not ignore_schedule and utc_now() < scheduled.astimezone(timezone.utc):
        raise AgentError(f"{item['id']}: termin još nije nastupio ({item['scheduled_at']}).")

    try:
        credentials = api_credentials()
    except CredentialError as exc:
        raise AgentError(str(exc)) from exc
    ig_user_id = str(credentials["ig_user_id"])
    access_token = str(credentials["access_token"])
    graph_version = str(credentials["graph_version"])
    base = f"https://{credentials['api_host']}/{graph_version}/{ig_user_id}"
    profile_query = urllib.parse.urlencode({"fields": "id,username,account_type"})
    profile = graph_get(f"{base}?{profile_query}", access_token)
    validate_target_profile(profile, ig_user_id)
    create_values = {"image_url": item["media_url"]}
    caption = caption_text(manifest_path, item)
    if caption:
        create_values["caption"] = caption
    if item["media_type"] == "STORIES":
        create_values["media_type"] = "STORIES"
    container = graph_post(f"{base}/media", create_values, access_token)
    creation_id = container.get("id")
    if not creation_id:
        raise AgentError(f"Meta API nije vratio creation_id: {container}")
    attempt = {
        "id": item["id"],
        "fingerprint": approval["fingerprint"],
        "creation_id": creation_id,
        "phase": "container_created",
        "started_at": utc_now().isoformat(),
    }
    write_json(pending, attempt)
    wait_for_container(base, str(creation_id), access_token)
    attempt["phase"] = "media_publish_requested"
    attempt["publish_requested_at"] = utc_now().isoformat()
    write_json(pending, attempt)
    result = graph_post(f"{base}/media_publish", {"creation_id": str(creation_id)}, access_token)
    external_id = result.get("id")
    if not external_id:
        raise AgentError(f"Meta API nije vratio publish id: {result}")
    audit = {
        "id": item["id"],
        "fingerprint": approval["fingerprint"],
        "approved_by": approval["approved_by"],
        "external_id": external_id,
        "container_id": creation_id,
        "published_at": utc_now().isoformat(),
        "credential_source": credentials["source"],
    }
    write_json(published, audit)
    attempt["phase"] = "published"
    attempt["external_id"] = external_id
    attempt["completed_at"] = audit["published_at"]
    write_json(pending, attempt)
    return audit


def command_validate(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    research = validate_research_gate(manifest_path, manifest)
    print(f"RESEARCH GATE OK: {len(research['scores'])} sadržaja; vrijedi do {research['expires_at']}.")
    ids: set[str] = set()
    warning_count = 0
    for item in manifest["items"]:
        if item.get("id") in ids:
            raise AgentError(f"Duplikat ID-a: {item.get('id')}")
        ids.add(item["id"])
        for warning in validate_item(manifest_path, item):
            warning_count += 1
            print(f"UPOZORENJE: {warning}")
        print(f"OK {item['id']} {fingerprint(manifest_path, item)[:12]}")
    print(f"Validirano: {len(ids)} stavki; upozorenja: {warning_count}.")


def command_approve(args: argparse.Namespace) -> None:
    if args.confirm != args.id:
        raise AgentError("Za odobrenje --confirm mora točno odgovarati --id.")
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, args.id)
    research = validate_research_gate(manifest_path, manifest, [args.id])
    print(f"RESEARCH GATE OK: {args.id} {research['scores'][args.id]}/100.")
    warnings = validate_item(manifest_path, item)
    for warning in warnings:
        print(f"UPOZORENJE: {warning}")
    approval = {
        "id": item["id"],
        "fingerprint": fingerprint(manifest_path, item),
        "approved_by": args.approved_by,
        "approved_at": utc_now().isoformat(),
        "scheduled_at": item["scheduled_at"],
    }
    write_json(approval_path(item["id"]), approval)
    print(f"Odobrena je zaključana verzija {item['id']} ({approval['fingerprint'][:12]}).")


def command_request_approval(args: argparse.Namespace) -> None:
    """Print the exact human-review package and stop without writing state."""
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, args.id)
    research = validate_research_gate(manifest_path, manifest, [args.id])
    warnings = validate_item(manifest_path, item)
    gate = json.loads(Path(research["path"]).read_text(encoding="utf-8"))
    record = gate["items"][args.id]
    approval = None
    approval_file = approval_path(args.id)
    if approval_file.is_file():
        approval = json.loads(approval_file.read_text(encoding="utf-8"))
    current_fingerprint = fingerprint(manifest_path, item)
    if not approval:
        approval_status = "NIJE ODOBRENO"
    elif approval.get("fingerprint") == current_fingerprint:
        approval_status = f"VAŽEĆE — {approval.get('approved_by', 'nepoznata osoba')}"
    else:
        approval_status = "PONIŠTENO — sadržaj je izmijenjen nakon odobrenja"

    caption = caption_text(manifest_path, item)
    review_text = caption if caption else story_instruction_text(manifest_path, item)
    print("=" * 72)
    print("ZAHTJEV ZA RUČNO ODOBRENJE — NIŠTA NIJE OBJAVLJENO")
    print("=" * 72)
    print(f"ID:               {item['id']}")
    print(f"Kanal / format:   {item['channel']} / {item['media_type']}")
    print(f"Planirani termin: {item['scheduled_at']}")
    print(f"Finalni vizual:   {resolve(manifest_path, item['media_path'])}")
    print(f"API publish asset:{publish_media_path(manifest_path, item)}")
    print(f"Claims status:    {item['claims_status']}")
    print(f"Research gate:    PASS {research['scores'][args.id]}/100; vrijedi do {research['expires_at']}")
    print(f"Odabrani obrasci: {', '.join(record['patterns'])}")
    print(f"Odbijena izvedba: {record['rejected']}")
    print(f"Očekivani signal: {record['expected_signal']}")
    if item.get("manual_only"):
        media_url_status = "NIJE POTREBAN — Story se dovršava ručno zbog native stickera"
    else:
        media_url_status = item.get("media_url") or "NEDOSTAJE — stvarna objava je blokirana"
    print(f"Media URL:        {media_url_status}")
    print(f"Approval status:  {approval_status}")
    print(f"Zaključani hash:  {current_fingerprint}")
    if item.get("native_sticker"):
        print(f"Native sticker:   {item['native_sticker']} — dodaje se ručno u Instagramu")
    print("\nFINALNI CAPTION / STORY UPUTA")
    print("-" * 72)
    print(review_text)
    if warnings:
        print("\nUPOZORENJA")
        print("-" * 72)
        for warning in warnings:
            print(f"- {warning}")
    print("\nODLUKA POTREBNA")
    print("-" * 72)
    print("Agent ovdje staje. Odgovorna osoba mora pregledati točan vizual, tekst,")
    print("termin i upozorenja te zatim izričito odobriti ovu zaključanu verziju.")
    print("\nNakon ljudske potvrde lokalni approval zapis izrađuje se naredbom:")
    print("python3 instagram_agent/agent.py approve \\")
    print(f"  --manifest {json.dumps(str(manifest_path), ensure_ascii=False)} \\")
    print(f"  --id {item['id']} \\")
    print('  --approved-by "IME ODGOVORNE OSOBE" ' + "\\")
    print(f"  --confirm {item['id']}")


def command_fingerprint(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    item = find_item(load_manifest(manifest_path), args.id)
    print(fingerprint(manifest_path, item))


def command_publish(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, args.id)
    if args.dry_run:
        validate_research_gate(manifest_path, manifest, [args.id])
        warnings = validate_item(manifest_path, item, publishing=True)
        require_approval(manifest_path, item)
        for warning in warnings:
            print(f"UPOZORENJE: {warning}")
        print(f"DRY RUN OK: {item['id']} ima važeće odobrenje; mrežni poziv nije izvršen.")
        return
    audit = publish_item(manifest_path, item, ignore_schedule=args.ignore_schedule)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


def command_run_due(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    due = published = waiting = 0
    now = utc_now()
    for item in manifest["items"]:
        scheduled = datetime.fromisoformat(item["scheduled_at"]).astimezone(timezone.utc)
        if scheduled > now or published_path(item["id"]).is_file():
            continue
        due += 1
        if item.get("manual_only"):
            waiting += 1
            print(f"RUČNO {item['id']}: native Story sticker zahtijeva Instagram aplikaciju.")
            continue
        if not item.get("media_url") or not approval_path(item["id"]).is_file():
            waiting += 1
            print(
                f"ČEKA {item['id']}: potreban je javni media_url i važeće ručno odobrenje; "
                "pokrenite request-approval za puni paket pregleda."
            )
            continue
        if args.dry_run:
            validate_research_gate(manifest_path, manifest, [item["id"]])
            validate_item(manifest_path, item, publishing=True)
            require_approval(manifest_path, item)
            print(f"DUE {item['id']}: spremno za objavu; dry-run ne šalje mrežni poziv.")
            continue
        audit = publish_item(manifest_path, item)
        published += 1
        print(f"OBJAVLJENO {item['id']}: {audit['external_id']}")
    print(f"Dospjelo: {due}; objavljeno: {published}; čeka/ručno: {waiting}.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="AID approval-gated Instagram agent")
    sub = result.add_subparsers(dest="command", required=True)
    for name in ("validate", "request-approval", "fingerprint", "approve", "publish", "run-due"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--manifest", type=Path, required=True)
        if name not in ("validate", "run-due"):
            cmd.add_argument("--id", required=True)
        if name == "approve":
            cmd.add_argument("--approved-by", required=True)
            cmd.add_argument("--confirm", required=True)
        if name == "publish":
            cmd.add_argument("--dry-run", action="store_true")
            cmd.add_argument("--ignore-schedule", action="store_true")
        if name == "run-due":
            cmd.add_argument("--dry-run", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    commands = {
        "validate": command_validate,
        "request-approval": command_request_approval,
        "fingerprint": command_fingerprint,
        "approve": command_approve,
        "publish": command_publish,
        "run-due": command_run_due,
    }
    try:
        commands[args.command](args)
    except (AgentError, ResearchGateError, OSError, ValueError, KeyError) as exc:
        print(f"BLOKIRANO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
