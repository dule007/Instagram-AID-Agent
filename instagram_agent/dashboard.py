#!/usr/bin/env python3
"""Operational control dashboard for AID Instagram publishing.

Sučelje izvršava stvarne radnje: objavljuje finalni asset na javni media host,
evidentira ručno odobrenje zaključane verzije, objavljuje na Instagram i vodi
autopilot koji u zadanom terminu pušta samo prethodno odobrene stavke.

Sigurnosni okvir ostaje nepromijenjen: svaka objava traži izričito ljudsko
odobrenje točne verzije, izmjena nakon odobrenja poništava odobrenje, a token
se nikada ne prikazuje u sučelju, statusu ni auditu.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import secrets
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import media_host
from agent import (
    STATE_ROOT,
    AgentError,
    approval_path,
    caption_text,
    find_item,
    fingerprint,
    graph_get,
    load_manifest,
    pending_path,
    publish_item,
    publish_media_path,
    published_path,
    resolve,
    story_instruction_text,
    update_item,
    utc_now,
    validate_item,
    validate_target_profile,
    write_json,
)
from credentials import CredentialError, api_credentials, connection_status, load_env_file
from media_host import MediaHostError
from research_gate import ResearchGateError, validate_research_gate

AUTOPILOT_PATH = STATE_ROOT / "autopilot.json"
ACTION_LOG_PATH = STATE_ROOT / "action_log.json"
ACTION_LOG_LIMIT = 200
MIN_AUTOPILOT_INTERVAL_MINUTES = 1
MAX_AUTOPILOT_INTERVAL_MINUTES = 720
MAX_REQUEST_BYTES = 64 * 1024

PUBLISH_LOCK = threading.RLock()
CSRF_TOKEN = secrets.token_urlsafe(32)


class ActionError(RuntimeError):
    pass


def read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def autopilot_state() -> dict:
    stored = read_json(AUTOPILOT_PATH) or {}
    return {
        "enabled": bool(stored.get("enabled")),
        "interval_minutes": int(stored.get("interval_minutes") or 5),
        "changed_at": stored.get("changed_at", ""),
        "changed_by": stored.get("changed_by", ""),
        "last_run_at": stored.get("last_run_at", ""),
        "last_result": stored.get("last_result", ""),
    }


def save_autopilot(state: dict) -> None:
    write_json(AUTOPILOT_PATH, state)


def log_action(action: str, content_id: str, outcome: str, detail: str = "") -> None:
    entries = read_json(ACTION_LOG_PATH) or {"entries": []}
    entries["entries"] = ([
        {
            "at": utc_now().isoformat(),
            "action": action,
            "id": content_id,
            "outcome": outcome,
            "detail": detail,
        }
    ] + entries.get("entries", []))[:ACTION_LOG_LIMIT]
    write_json(ACTION_LOG_PATH, entries)


def action_log() -> list[dict]:
    return (read_json(ACTION_LOG_PATH) or {}).get("entries", [])


def item_state(
    manifest_path: Path,
    item: dict,
    now: datetime,
    research_score: int | None,
    research_gate_ok: bool,
) -> dict:
    approval = read_json(approval_path(item["id"]))
    published = read_json(published_path(item["id"]))
    pending = read_json(pending_path(item["id"]))
    current_fingerprint = fingerprint(manifest_path, item)
    approval_valid = bool(approval and approval.get("fingerprint") == current_fingerprint)
    scheduled = datetime.fromisoformat(item["scheduled_at"])
    due = scheduled.astimezone(timezone.utc) <= now
    manual_only = bool(item.get("manual_only"))
    media_ready = bool(item.get("media_url"))
    unresolved_pending = bool(pending and not published and pending.get("phase") != "published")

    if published:
        status, label = "published", "Objavljeno"
    elif unresolved_pending:
        status, label = "invalid", "Nerazriješen pokušaj objave"
    elif not research_gate_ok:
        status, label = "blocked", "Research gate blokiran"
    elif approval and not approval_valid:
        status, label = "invalid", "Izmijenjeno nakon odobrenja"
    elif manual_only and not approval_valid:
        status, label = "waiting_approval", "Ručni Story / čeka odobrenje"
    elif manual_only:
        status, label = "manual", "Ručni Story / odobren"
    elif not media_ready:
        status, label = ("blocked" if due else "waiting_url"), ("Dospjelo / nema media URL" if due else "Čeka media URL")
    elif not approval_valid:
        status, label = ("blocked" if due else "waiting_approval"), ("Dospjelo / nema odobrenje" if due else "Čeka odobrenje")
    elif due:
        status, label = "ready", "Spremno za objavu"
    else:
        status, label = "scheduled", "Zakazano"

    return {
        "id": item["id"],
        "channel": item["channel"],
        "scheduled_at": item["scheduled_at"],
        "scheduled_display": scheduled.strftime("%d.%m.%Y. · %H:%M"),
        "scheduled_input": scheduled.strftime("%Y-%m-%dT%H:%M"),
        "status": status,
        "status_label": label,
        "approval_valid": approval_valid,
        "approved_by": approval.get("approved_by", "") if approval else "",
        "approved_at": approval.get("approved_at", "") if approval else "",
        "external_id": published.get("external_id", "") if published else "",
        "published_at": published.get("published_at", "") if published else "",
        "native_sticker": item.get("native_sticker", ""),
        "media_ready": media_ready,
        "media_url": item.get("media_url", ""),
        "manual_only": manual_only,
        "unresolved_pending": unresolved_pending,
        "due": due,
        "publishable": bool(
            research_gate_ok
            and approval_valid
            and media_ready
            and not manual_only
            and not published
            and not unresolved_pending
        ),
        "fingerprint": current_fingerprint[:12],
        "caption": caption_text(manifest_path, item),
        "research_score": research_score,
        "research_gate_ok": research_gate_ok,
    }


def snapshot(manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    now = utc_now()
    try:
        instagram_connection = connection_status()
    except CredentialError as exc:
        instagram_connection = {
            "status": "error",
            "source": "invalid_local_session",
            "username": "",
            "message": str(exc),
        }
    try:
        research = validate_research_gate(manifest_path, manifest)
        research_gate = {
            "status": "pass",
            "message": f"Benchmark vrijedi do {research['expires_at']}.",
            "researched_at": research["researched_at"],
            "expires_at": research["expires_at"],
        }
        scores = research["scores"]
    except ResearchGateError as exc:
        research_gate = {"status": "blocked", "message": str(exc), "researched_at": "", "expires_at": ""}
        scores = {}
    states = [
        item_state(manifest_path, item, now, scores.get(item["id"]), research_gate["status"] == "pass")
        for item in manifest["items"]
    ]
    counts: dict[str, int] = {}
    for state in states:
        counts[state["status"]] = counts.get(state["status"], 0) + 1
    upcoming = sorted(
        (state for state in states if state["publishable"] and not state["due"]),
        key=lambda state: state["scheduled_at"],
    )
    return {
        "campaign": manifest.get("campaign", ""),
        "generated_at": now.isoformat(),
        "counts": counts,
        "research_gate": research_gate,
        "instagram_connection": instagram_connection,
        "autopilot": autopilot_state(),
        "next_publish": upcoming[0]["scheduled_at"] if upcoming else "",
        "items": states,
        "log": action_log()[:25],
    }


def review_package(manifest_path: Path, content_id: str) -> dict:
    """Return the exact package a human must see before approving a version."""
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, content_id)
    research = validate_research_gate(manifest_path, manifest, [content_id])
    warnings = validate_item(manifest_path, item)
    gate = json.loads(Path(research["path"]).read_text(encoding="utf-8"))
    record = gate["items"][content_id]
    caption = caption_text(manifest_path, item)
    approval = read_json(approval_path(content_id))
    current_fingerprint = fingerprint(manifest_path, item)
    return {
        "id": item["id"],
        "channel": item["channel"],
        "media_type": item["media_type"],
        "scheduled_at": item["scheduled_at"],
        "media_path": str(resolve(manifest_path, item["media_path"])),
        "publish_media_path": str(publish_media_path(manifest_path, item)),
        "claims_status": item["claims_status"],
        "research_score": research["scores"][content_id],
        "research_expires_at": research["expires_at"],
        "patterns": record["patterns"],
        "rejected": record["rejected"],
        "expected_signal": record["expected_signal"],
        "media_url": item.get("media_url", ""),
        "native_sticker": item.get("native_sticker", ""),
        "manual_only": bool(item.get("manual_only")),
        "review_text": caption or story_instruction_text(manifest_path, item),
        "fingerprint": current_fingerprint,
        "warnings": warnings,
        "revokes_approval": bool(approval and approval.get("fingerprint") != current_fingerprint),
    }


def action_host_media(manifest_path: Path, payload: dict) -> dict:
    content_id = str(payload.get("id", ""))
    item = find_item(load_manifest(manifest_path), content_id)
    if item.get("manual_only"):
        raise ActionError(f"{content_id}: ručni Story se dovršava u aplikaciji i ne treba javni media URL.")
    asset = publish_media_path(manifest_path, item)
    result = media_host.upload(content_id, asset)
    media_host.verify(result["url"])
    had_approval = approval_path(content_id).is_file()
    update_item(manifest_path, content_id, {"media_url": result["url"]})
    note = "Odobrenje je poništeno jer se media URL mijenja." if had_approval else ""
    log_action("host_media", content_id, "ok", result["url"])
    return {"message": f"{result['message']} {note}".strip(), "url": result["url"]}


def action_approve(manifest_path: Path, payload: dict) -> dict:
    content_id = str(payload.get("id", ""))
    approved_by = str(payload.get("approved_by", "")).strip()
    if str(payload.get("confirm", "")) != content_id:
        raise ActionError("Potvrda mora točno odgovarati ID-u sadržaja.")
    if len(approved_by) < 3:
        raise ActionError("Upišite ime odgovorne osobe koja odobrava ovu verziju.")
    manifest = load_manifest(manifest_path)
    item = find_item(manifest, content_id)
    validate_research_gate(manifest_path, manifest, [content_id])
    warnings = validate_item(manifest_path, item)
    approval = {
        "id": content_id,
        "fingerprint": fingerprint(manifest_path, item),
        "approved_by": approved_by,
        "approved_at": utc_now().isoformat(),
        "scheduled_at": item["scheduled_at"],
        "approved_via": "control_dashboard",
    }
    write_json(approval_path(content_id), approval)
    log_action("approve", content_id, "ok", f"{approved_by} · {approval['fingerprint'][:12]}")
    return {
        "message": f"Odobrena je zaključana verzija {content_id} ({approval['fingerprint'][:12]}).",
        "warnings": warnings,
    }


def action_revoke(manifest_path: Path, payload: dict) -> dict:
    content_id = str(payload.get("id", ""))
    path = approval_path(content_id)
    if not path.is_file():
        raise ActionError(f"{content_id}: nema approval zapisa za povlačenje.")
    path.unlink()
    log_action("revoke", content_id, "ok", "")
    return {"message": f"Odobrenje za {content_id} je povučeno; autopilot ga više neće objaviti."}


def campaign_timezone(manifest_path: Path) -> ZoneInfo:
    name = load_manifest(manifest_path).get("timezone") or "Europe/Zagreb"
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ActionError(f"Kampanja ima nepoznatu vremensku zonu '{name}'.") from exc


def action_reschedule(manifest_path: Path, payload: dict) -> dict:
    content_id = str(payload.get("id", ""))
    scheduled_at = str(payload.get("scheduled_at", "")).strip()
    if not scheduled_at:
        raise ActionError("Novi termin nije upisan.")
    try:
        parsed = datetime.fromisoformat(scheduled_at)
    except ValueError as exc:
        raise ActionError(f"Termin nije u ispravnom obliku: {scheduled_at}") from exc
    if parsed.tzinfo is None:
        # Sučelje šalje lokalno vrijeme kampanje; ljetni i zimski pomak računa
        # se iz baze vremenskih zona, a ne iz fiksnog offseta.
        parsed = parsed.replace(tzinfo=campaign_timezone(manifest_path))
    scheduled_at = parsed.isoformat()
    had_approval = approval_path(content_id).is_file()
    item = update_item(manifest_path, content_id, {"scheduled_at": scheduled_at})
    note = " Odobrenje je poništeno jer se termin mijenja." if had_approval else ""
    log_action("reschedule", content_id, "ok", scheduled_at)
    return {"message": f"{content_id} je pomaknut na {item['scheduled_at']}.{note}"}


def action_publish(manifest_path: Path, payload: dict) -> dict:
    content_id = str(payload.get("id", ""))
    if str(payload.get("confirm", "")) != content_id:
        raise ActionError("Za stvarnu objavu potvrda mora točno odgovarati ID-u sadržaja.")
    with PUBLISH_LOCK:
        manifest = load_manifest(manifest_path)
        item = find_item(manifest, content_id)
        try:
            audit = publish_item(manifest_path, item, ignore_schedule=True)
        except (AgentError, ResearchGateError) as exc:
            log_action("publish", content_id, "blocked", str(exc))
            raise ActionError(str(exc)) from exc
    log_action("publish", content_id, "published", audit["external_id"])
    return {"message": f"{content_id} je objavljen. Meta ID: {audit['external_id']}.", "audit": audit}


def action_resolve_pending(manifest_path: Path, payload: dict) -> dict:
    """Clear a stalled attempt only after a human confirmed Instagram state."""
    content_id = str(payload.get("id", ""))
    outcome = str(payload.get("outcome", ""))
    if str(payload.get("confirm", "")) != content_id:
        raise ActionError("Potvrda mora točno odgovarati ID-u sadržaja.")
    pending = pending_path(content_id)
    if not pending.is_file():
        raise ActionError(f"{content_id}: nema nerazriješenog pokušaja.")
    if outcome not in {"not_published", "published"}:
        raise ActionError("Odaberite je li objava stvarno vidljiva na Instagramu.")
    if outcome == "published":
        external_id = str(payload.get("external_id", "")).strip()
        if not external_id:
            raise ActionError("Za već objavljen sadržaj upišite Meta ID iz Instagrama.")
        record = read_json(pending) or {}
        write_json(
            published_path(content_id),
            {
                "id": content_id,
                "fingerprint": record.get("fingerprint", ""),
                "approved_by": record.get("approved_by", ""),
                "external_id": external_id,
                "container_id": record.get("creation_id", ""),
                "published_at": utc_now().isoformat(),
                "credential_source": "manual_reconciliation",
                "note": "Ručno potvrđeno prema stvarnom stanju na Instagramu.",
            },
        )
        pending.unlink()
        log_action("resolve_pending", content_id, "published", external_id)
        return {"message": f"{content_id} je evidentiran kao objavljen ({external_id})."}
    pending.unlink()
    log_action("resolve_pending", content_id, "cleared", "operater potvrdio da objava nije vidljiva")
    return {"message": f"{content_id}: pokušaj je poništen; objava se može ponoviti."}


def action_autopilot(manifest_path: Path, payload: dict) -> dict:
    enabled = bool(payload.get("enabled"))
    # Nedostajuća vrijednost dobiva razuman default, ali izričita nula mora
    # pasti na provjeri raspona umjesto da tiho postane default.
    raw_interval = payload.get("interval_minutes")
    if raw_interval is None or (isinstance(raw_interval, str) and not raw_interval.strip()):
        raw_interval = 5
    try:
        interval = int(raw_interval)
    except (TypeError, ValueError) as exc:
        raise ActionError("Interval mora biti cijeli broj minuta.") from exc
    if not MIN_AUTOPILOT_INTERVAL_MINUTES <= interval <= MAX_AUTOPILOT_INTERVAL_MINUTES:
        raise ActionError(
            f"Interval mora biti između {MIN_AUTOPILOT_INTERVAL_MINUTES} i {MAX_AUTOPILOT_INTERVAL_MINUTES} minuta."
        )
    changed_by = str(payload.get("changed_by", "")).strip() or "operater"
    if enabled:
        try:
            api_credentials()
        except CredentialError as exc:
            raise ActionError(f"Autopilot se ne može uključiti bez valjanog Meta credentiala: {exc}") from exc
    state = autopilot_state()
    state.update(
        {
            "enabled": enabled,
            "interval_minutes": interval,
            "changed_at": utc_now().isoformat(),
            "changed_by": changed_by,
        }
    )
    save_autopilot(state)
    log_action("autopilot", "", "on" if enabled else "off", f"{interval} min · {changed_by}")
    return {
        "message": (
            f"Autopilot je UKLJUČEN; provjera svakih {interval} min. Objavljuje isključivo prethodno odobrene stavke."
            if enabled
            else "Autopilot je isključen."
        )
    }


def action_check_connection(manifest_path: Path, payload: dict) -> dict:
    """Read-only Meta probe of the configured account; never prints the token."""
    try:
        credentials = api_credentials()
    except CredentialError as exc:
        raise ActionError(str(exc)) from exc
    base = f"https://{credentials['api_host']}/{credentials['graph_version']}/{credentials['ig_user_id']}"
    try:
        profile = graph_get(f"{base}?fields=id,username,account_type", credentials["access_token"])
        validate_target_profile(profile, str(credentials["ig_user_id"]))
    except AgentError as exc:
        log_action("check_connection", "", "failed", str(exc))
        raise ActionError(str(exc)) from exc
    log_action("check_connection", "", "ok", f"@{profile.get('username', '')}")
    return {
        "message": (
            f"Token je valjan za @{profile.get('username', '')} "
            f"({profile.get('account_type', '')}); izvor: {credentials['source']}."
        )
    }


def action_media_host_status(manifest_path: Path, payload: dict) -> dict:
    state = media_host.repo_status()
    if state["status"] != "ready":
        raise ActionError(state["message"])
    return {"message": state["message"]}


ACTIONS = {
    "host_media": action_host_media,
    "approve": action_approve,
    "revoke": action_revoke,
    "reschedule": action_reschedule,
    "publish": action_publish,
    "resolve_pending": action_resolve_pending,
    "autopilot": action_autopilot,
    "check_connection": action_check_connection,
    "media_host_status": action_media_host_status,
}


def autopilot_cycle(manifest_path: Path) -> dict:
    """Publish every due item that already carries a valid human approval."""
    published: list[str] = []
    skipped: list[str] = []
    with PUBLISH_LOCK:
        manifest = load_manifest(manifest_path)
        now = utc_now()
        for item in manifest["items"]:
            content_id = item["id"]
            if published_path(content_id).is_file() or item.get("manual_only"):
                continue
            if datetime.fromisoformat(item["scheduled_at"]).astimezone(timezone.utc) > now:
                continue
            if pending_path(content_id).is_file():
                skipped.append(f"{content_id}: nerazriješen prethodni pokušaj")
                continue
            if not item.get("media_url"):
                skipped.append(f"{content_id}: nema javni media URL")
                continue
            approval = read_json(approval_path(content_id))
            if not approval or approval.get("fingerprint") != fingerprint(manifest_path, item):
                skipped.append(f"{content_id}: nema važeće ručno odobrenje")
                continue
            try:
                audit = publish_item(manifest_path, item)
            except (AgentError, ResearchGateError, OSError) as exc:
                skipped.append(f"{content_id}: {exc}")
                log_action("autopilot_publish", content_id, "blocked", str(exc))
                continue
            published.append(content_id)
            log_action("autopilot_publish", content_id, "published", audit["external_id"])
    return {"published": published, "skipped": skipped}


def autopilot_loop(manifest_path: Path, stop: threading.Event) -> None:
    while not stop.is_set():
        state = autopilot_state()
        interval = max(MIN_AUTOPILOT_INTERVAL_MINUTES, state["interval_minutes"])
        if state["enabled"]:
            try:
                result = autopilot_cycle(manifest_path)
                summary = f"objavljeno {len(result['published'])}, preskočeno {len(result['skipped'])}"
            except Exception as exc:  # noqa: BLE001 - autopilot must never die silently
                summary = f"greška: {exc}"
                log_action("autopilot_cycle", "", "error", str(exc))
            state = autopilot_state()
            state.update({"last_run_at": utc_now().isoformat(), "last_result": summary})
            save_autopilot(state)
            stop.wait(interval * 60)
        else:
            stop.wait(20)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


PAGE_STYLE = """
:root{--navy:#0d1b2a;--navy2:#13243a;--line:#283c58;--amber:#f5a623;--blue:#3b9dd6;--ink:#e8edf4;--mut:#94a6be;--red:#ef6b73;--green:#46c98b}
*{box-sizing:border-box} body{margin:0;background:#08131f;color:var(--ink);font:15px/1.5 system-ui,-apple-system,sans-serif}
.bar{height:6px;background:linear-gradient(90deg,var(--amber) 0 62%,var(--blue) 62%)} main{max-width:1500px;margin:auto;padding:34px}
header{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:28px} h1{margin:0;font-size:clamp(28px,4vw,48px)} .muted,.schedule{color:var(--mut)}
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:12px;margin:24px 0} .stat{background:var(--navy2);border:1px solid var(--line);border-radius:14px;padding:18px}
.stat strong{display:block;font-size:28px;color:var(--amber)} .stat span{color:var(--mut)}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin:22px 0}
.panel{background:var(--navy2);border:1px solid var(--line);border-radius:16px;padding:18px} .panel h3{margin:0 0 10px;font-size:14px;letter-spacing:1.4px;color:var(--blue);text-transform:uppercase}
.panel p{margin:6px 0;font-size:13px;color:var(--mut)} .panel .value{color:var(--ink)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}
button{border:1px solid var(--line);background:var(--navy2);color:var(--ink);padding:9px 14px;border-radius:999px;cursor:pointer;font:inherit}
button:hover:not(:disabled){border-color:var(--amber)} button:disabled{opacity:.38;cursor:not-allowed} button.active{border-color:var(--amber);color:var(--amber)}
button.go{background:var(--amber);color:#08131f;border-color:var(--amber);font-weight:700} button.danger{border-color:var(--red);color:var(--red)}
input,select{background:#08131f;border:1px solid var(--line);color:var(--ink);border-radius:9px;padding:8px 10px;font:inherit;width:100%}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px} .card{background:var(--navy);border:1px solid var(--line);border-radius:18px;overflow:hidden;display:flex;flex-direction:column} .card.hidden{display:none}
.preview-wrap{aspect-ratio:4/3;background:#050d15;overflow:hidden;display:flex;justify-content:center} .preview-wrap img{height:100%;width:100%;object-fit:contain}
.body{padding:17px;display:flex;flex-direction:column;flex:1} .topline{display:flex;justify-content:space-between;gap:8px;align-items:center} .channel{font-size:12px;letter-spacing:1.5px;color:var(--blue);font-weight:800}
.pill{font-size:11px;font-weight:800;padding:5px 8px;border-radius:999px;background:var(--line)} .pill.published{color:var(--green)} .pill.ready{color:var(--green)} .pill.manual{color:var(--blue)} .pill.invalid,.pill.blocked{color:var(--red)} .pill.scheduled{color:var(--amber)}
h2{font-size:18px;margin:14px 0 2px} details{border-top:1px solid var(--line);margin-top:14px;padding-top:12px} summary{cursor:pointer;color:var(--amber)}
.caption{white-space:pre-wrap;color:#cbd6e6;font-size:13px;max-height:260px;overflow:auto} ul{padding-left:18px;color:var(--mut);font-size:12px}
.actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px;padding-top:13px;border-top:1px solid var(--line)} .actions button{padding:7px 12px;font-size:13px}
.notice{border-left:4px solid var(--amber);background:var(--navy2);padding:12px 16px;border-radius:10px;color:var(--mut)}
.control{display:flex;flex-wrap:wrap;gap:12px;align-items:center;background:var(--navy2);border:1px solid var(--line);border-radius:16px;padding:16px;margin:22px 0}
.control .lamp{width:12px;height:12px;border-radius:50%;background:var(--red)} .control.on .lamp{background:var(--green);box-shadow:0 0 10px var(--green)}
.control label{font-size:13px;color:var(--mut)} .control input{width:90px}
.logbox{max-height:230px;overflow:auto;font-size:12px;color:var(--mut)} .logbox div{padding:4px 0;border-bottom:1px solid var(--line)}
.modal{position:fixed;inset:0;background:rgba(4,10,17,.86);display:none;align-items:center;justify-content:center;padding:24px;z-index:50} .modal.open{display:flex}
.modal-inner{background:var(--navy);border:1px solid var(--line);border-radius:18px;max-width:720px;width:100%;max-height:88vh;overflow:auto;padding:26px}
.modal-inner h2{margin-top:0} .modal-inner dl{display:grid;grid-template-columns:190px 1fr;gap:6px 14px;font-size:13px;margin:16px 0} .modal-inner dt{color:var(--mut)} .modal-inner dd{margin:0;word-break:break-word}
.modal-inner .field{margin:12px 0} .modal-inner .field label{display:block;font-size:12px;color:var(--mut);margin-bottom:5px}
.warn{border-left:3px solid var(--red);padding:8px 12px;background:rgba(239,107,115,.1);border-radius:8px;font-size:13px;margin:10px 0}
.toast{position:fixed;right:20px;bottom:20px;max-width:460px;background:var(--navy2);border:1px solid var(--amber);border-radius:12px;padding:14px 18px;display:none;z-index:60;font-size:14px}
.toast.err{border-color:var(--red)} .toast.open{display:block}
@media(max-width:760px){main{padding:20px} header{display:block} .summary{grid-template-columns:repeat(2,1fr)} .modal-inner dl{grid-template-columns:1fr}}
"""


def render_card(item: dict) -> str:
    caption = item["caption"] or "Story bez captiona — interaktivni element dodaje se ručno."
    meta = []
    if item["approval_valid"]:
        meta.append(f"Odobrio/la: {esc(item['approved_by'])}")
    if item["external_id"]:
        meta.append(f"Meta ID: {esc(item['external_id'])}")
    if item["native_sticker"]:
        meta.append(f"Sticker: {esc(item['native_sticker'])}")
    if item["research_score"] is not None:
        meta.append(f"Research score: {esc(item['research_score'])}/100")
    if item["media_url"]:
        meta.append(f"Media URL: {esc(item['media_url'])}")
    meta.append(f"Hash: {esc(item['fingerprint'])}")

    identifier = esc(item["id"])
    buttons: list[str] = []
    if item["status"] == "published":
        buttons.append('<span class="muted">Objavljeno — daljnje akcije su zaključane.</span>')
    elif item["unresolved_pending"]:
        buttons.append(f'<button class="danger" data-act="pending" data-id="{identifier}">Razriješi pokušaj</button>')
    else:
        if not item["manual_only"]:
            label = "Osvježi media URL" if item["media_ready"] else "Objavi asset na host"
            buttons.append(f'<button data-act="host" data-id="{identifier}">{label}</button>')
        if item["approval_valid"]:
            buttons.append(f'<button class="danger" data-act="revoke" data-id="{identifier}">Povuci odobrenje</button>')
        else:
            buttons.append(f'<button data-act="approve" data-id="{identifier}">Odobri</button>')
        buttons.append(f'<button data-act="schedule" data-id="{identifier}" data-when="{esc(item["scheduled_input"])}">Termin</button>')
        if item["manual_only"]:
            buttons.append('<span class="muted">Ručni Story — objavljuje se u Instagram aplikaciji.</span>')
        else:
            disabled = "" if item["publishable"] else " disabled"
            buttons.append(f'<button class="go" data-act="publish" data-id="{identifier}"{disabled}>Objavi sad</button>')

    return f"""
        <article class="card" data-channel="{esc(item['channel'])}" data-status="{esc(item['status'])}">
          <div class="preview-wrap"><img loading="lazy" src="/media/{identifier}" alt="{identifier} preview"></div>
          <div class="body">
            <div class="topline"><span class="channel">{esc(item['channel'])}</span><span class="pill {esc(item['status'])}">{esc(item['status_label'])}</span></div>
            <h2>{identifier}</h2>
            <p class="schedule">{esc(item['scheduled_display'])} · Europe/Zagreb</p>
            <details><summary>Caption i detalji</summary><p class="caption">{esc(caption)}</p><ul>{''.join(f'<li>{entry}</li>' for entry in meta)}</ul></details>
            <div class="actions">{''.join(buttons)}</div>
          </div>
        </article>"""


def render_page(manifest_path: Path) -> bytes:
    data = snapshot(manifest_path)
    cards = "".join(render_card(item) for item in data["items"])
    counts = data["counts"]
    summary = [
        ("Ukupno", len(data["items"])),
        ("Objavljeno", counts.get("published", 0)),
        ("Zakazano", counts.get("scheduled", 0)),
        ("Spremno", counts.get("ready", 0)),
        ("Čeka", sum(counts.get(key, 0) for key in ("waiting_url", "waiting_approval", "blocked", "invalid"))),
        ("Ručni Story", counts.get("manual", 0)),
        ("Research", "PASS" if data["research_gate"]["status"] == "pass" else "BLOKIRAN"),
        ("Instagram", "POVEZAN" if data["instagram_connection"]["status"] in ("connected", "configured") else "NIJE POVEZAN"),
    ]
    summary_html = "".join(
        f'<div class="stat"><strong>{esc(value)}</strong><span>{esc(label)}</span></div>' for label, value in summary
    )
    research_notice = (
        f"Research gate PASS. {esc(data['research_gate']['message'])}"
        if data["research_gate"]["status"] == "pass"
        else f"Research gate BLOKIRAN: {esc(data['research_gate']['message'])}"
    )
    connection = data["instagram_connection"]
    if connection["status"] in ("connected", "configured"):
        account = f"@{connection.get('username')}" if connection.get("username") else "profesionalni račun"
        connection_notice = f"Instagram povezan ({esc(account)}, izvor: {esc(connection.get('source', ''))})."
    else:
        connection_notice = "Instagram nije povezan; otvorite OAuth konektor na portu 7012."

    autopilot = data["autopilot"]
    next_publish = data["next_publish"] or "nema zakazane odobrene stavke"
    log_html = "".join(
        f'<div>{esc(entry["at"][:19].replace("T", " "))} · {esc(entry["action"])} '
        f'{esc(entry["id"])} · <strong>{esc(entry["outcome"])}</strong> {esc(entry["detail"][:120])}</div>'
        for entry in data["log"]
    ) or '<div class="muted">Još nema zabilježenih akcija.</div>'

    boot = json.dumps({"csrf": CSRF_TOKEN, "autopilot": autopilot}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="hr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AID Instagram Control</title><style>{PAGE_STYLE}</style></head><body><div class="bar"></div><main>
<header>
  <div><div class="channel">AUTOINSIGHT DATA</div><h1>Instagram Control Agent</h1>
  <p class="muted">Kampanja {esc(data['campaign'])} · osvježavanje svakih 30 sekundi</p></div>
  <div class="muted">Operativna kontrola</div>
</header>
<p class="notice">{research_notice} {connection_notice} Objava i odobrenje izvršavaju se iz ovog sučelja.
Svaka objava i dalje traži izričito ljudsko odobrenje točne verzije, a izmjena sadržaja, termina ili media URL-a
poništava odobrenje. Autopilot objavljuje isključivo stavke koje su prethodno odobrene. Bez Insights podataka ovaj
ekran ne prikazuje reach, saves, shares ni lead performance.</p>

<div class="control{' on' if autopilot['enabled'] else ''}" id="autopilot-bar">
  <span class="lamp"></span>
  <strong>Autopilot {'UKLJUČEN' if autopilot['enabled'] else 'isključen'}</strong>
  <label>Interval (min) <input type="number" id="ap-interval" min="{MIN_AUTOPILOT_INTERVAL_MINUTES}"
    max="{MAX_AUTOPILOT_INTERVAL_MINUTES}" value="{esc(autopilot['interval_minutes'])}"></label>
  <button class="{'danger' if autopilot['enabled'] else 'go'}" id="ap-toggle">{'Isključi' if autopilot['enabled'] else 'Uključi'}</button>
  <span class="muted">Sljedeća odobrena objava: {esc(next_publish)}</span>
  <span class="muted">Zadnji ciklus: {esc(autopilot['last_run_at'][:19].replace('T', ' ') or '—')} {esc(autopilot['last_result'])}</span>
</div>

<section class="summary">{summary_html}</section>

<section class="panels">
  <div class="panel"><h3>Veza i ključevi</h3>
    <p>Status: <span class="value">{esc(connection['status'])}</span></p>
    <p>Izvor: <span class="value">{esc(connection.get('source', ''))}</span></p>
    <p>Istek tokena: <span class="value">{esc(connection.get('expires_at') or 'nije poznat')}</span></p>
    <p>Svi ključevi žive u jednom fileu: <span class="value">instagram_agent/.env</span> (dozvola 0600).
    Nakon izmjene tokena restartajte dashboard. Vrijednosti se nikada ne prikazuju ovdje.</p>
    <div class="actions"><button data-act="check">Provjeri token</button><button data-act="hoststatus">Provjeri media host</button></div>
  </div>
  <div class="panel"><h3>Zadnje akcije</h3><div class="logbox">{log_html}</div></div>
</section>

<nav class="filters"><button class="active" data-filter="all">Sve</button><button data-filter="FEED">Feed</button>
<button data-filter="STORY">Story</button><button data-filter="published">Objavljeno</button>
<button data-filter="ready">Spremno</button><button data-filter="manual">Ručno</button></nav>
<section class="grid">{cards}</section>
</main>
<div class="modal" id="modal"><div class="modal-inner" id="modal-inner"></div></div>
<div class="toast" id="toast"></div>
<script>const BOOT={boot};{PAGE_SCRIPT}</script></body></html>""".encode("utf-8")


PAGE_SCRIPT = r"""
const modal = document.getElementById('modal');
const inner = document.getElementById('modal-inner');
const toast = document.getElementById('toast');
let busy = false;

function notify(message, isError) {
  toast.textContent = message;
  toast.className = 'toast open' + (isError ? ' err' : '');
  setTimeout(() => { toast.className = 'toast'; }, isError ? 12000 : 6000);
}
function closeModal() { modal.className = 'modal'; inner.innerHTML = ''; }
function openModal(html) { inner.innerHTML = html; modal.className = 'modal open'; }
function esc(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function call(action, payload) {
  if (busy) return null;
  busy = true;
  try {
    const response = await fetch('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': BOOT.csrf },
      body: JSON.stringify(Object.assign({ action }, payload || {}))
    });
    const data = await response.json();
    if (!response.ok) { notify(data.error || 'Akcija je blokirana.', true); return null; }
    notify(data.message || 'Gotovo.');
    return data;
  } catch (error) {
    notify('Mrežna greška: ' + error, true);
    return null;
  } finally { busy = false; }
}

async function run(action, payload, reload) {
  const result = await call(action, payload);
  if (result && reload !== false) { closeModal(); setTimeout(() => location.reload(), 1200); }
  return result;
}

async function approveDialog(id) {
  const response = await fetch('/api/package/' + encodeURIComponent(id));
  const pkg = await response.json();
  if (!response.ok) { notify(pkg.error || 'Paket se ne može učitati.', true); return; }
  const warnings = (pkg.warnings || []).map(w => '<div class="warn">' + esc(w) + '</div>').join('');
  const revoked = pkg.revokes_approval
    ? '<div class="warn">Postojeće odobrenje više ne vrijedi jer je sadržaj izmijenjen. Ovime odobravate novu verziju.</div>' : '';
  const missingUrl = (!pkg.manual_only && !pkg.media_url)
    ? '<div class="warn">Nema javni media URL. Odobrenje je moguće, ali objava ostaje blokirana dok asset ne ode na host.</div>' : '';
  openModal(
    '<h2>Odobrenje zaključane verzije</h2>' +
    '<p class="muted">Pregledajte točno ovu verziju. Odobrenje vrijedi samo za prikazani hash.</p>' + revoked + missingUrl +
    '<img src="/media/' + encodeURIComponent(id) + '" alt="" style="max-width:100%;border-radius:12px;margin:12px 0">' +
    '<dl>' +
    '<dt>ID</dt><dd>' + esc(pkg.id) + '</dd>' +
    '<dt>Kanal / format</dt><dd>' + esc(pkg.channel) + ' / ' + esc(pkg.media_type) + '</dd>' +
    '<dt>Termin</dt><dd>' + esc(pkg.scheduled_at) + '</dd>' +
    '<dt>Claims status</dt><dd>' + esc(pkg.claims_status) + '</dd>' +
    '<dt>Research score</dt><dd>' + esc(pkg.research_score) + '/100 · vrijedi do ' + esc(pkg.research_expires_at) + '</dd>' +
    '<dt>Obrasci</dt><dd>' + esc((pkg.patterns || []).join(', ')) + '</dd>' +
    '<dt>Odbijena izvedba</dt><dd>' + esc(pkg.rejected) + '</dd>' +
    '<dt>Očekivani signal</dt><dd>' + esc(pkg.expected_signal) + '</dd>' +
    '<dt>Media URL</dt><dd>' + esc(pkg.media_url || 'nedostaje') + '</dd>' +
    (pkg.native_sticker ? '<dt>Native sticker</dt><dd>' + esc(pkg.native_sticker) + ' — dodaje se ručno</dd>' : '') +
    '<dt>Zaključani hash</dt><dd>' + esc(pkg.fingerprint) + '</dd>' +
    '</dl>' + warnings +
    '<div class="field"><label>Finalni caption / Story uputa</label>' +
    '<p class="caption">' + esc(pkg.review_text) + '</p></div>' +
    '<div class="field"><label>Ime odgovorne osobe koja odobrava</label><input id="ap-by"></div>' +
    '<div class="field"><label>Za potvrdu upišite točan ID: ' + esc(pkg.id) + '</label><input id="ap-confirm"></div>' +
    '<div class="actions"><button onclick="closeModal()">Odustani</button>' +
    '<button class="go" onclick="submitApprove(\'' + esc(pkg.id) + '\')">Odobri ovu verziju</button></div>'
  );
}

function submitApprove(id) {
  run('approve', {
    id,
    approved_by: document.getElementById('ap-by').value,
    confirm: document.getElementById('ap-confirm').value
  });
}

function publishDialog(id) {
  openModal(
    '<h2>Stvarna objava na Instagram</h2>' +
    '<div class="warn">Ovo odmah objavljuje sadržaj na @autoinsightdata. Radnja se ne može poništiti iz ovog sučelja.</div>' +
    '<p class="muted">Agent prije poziva ponovno provjerava research gate, odobrenje, ciljni račun i media URL.</p>' +
    '<div class="field"><label>Za potvrdu upišite točan ID: ' + esc(id) + '</label><input id="pub-confirm"></div>' +
    '<div class="actions"><button onclick="closeModal()">Odustani</button>' +
    '<button class="go" onclick="submitPublish(\'' + esc(id) + '\')">Objavi sada</button></div>'
  );
}

function submitPublish(id) {
  run('publish', { id, confirm: document.getElementById('pub-confirm').value });
}

function scheduleDialog(id, when) {
  openModal(
    '<h2>Novi termin objave</h2>' +
    '<div class="warn">Izmjena termina poništava postojeće odobrenje; verziju treba ponovno odobriti.</div>' +
    '<div class="field"><label>Termin (lokalno vrijeme kampanje)</label><input type="datetime-local" id="sc-when" value="' + esc(when) + '"></div>' +
    '<div class="actions"><button onclick="closeModal()">Odustani</button>' +
    '<button class="go" onclick="submitSchedule(\'' + esc(id) + '\')">Spremi termin</button></div>'
  );
}

function submitSchedule(id) {
  const value = document.getElementById('sc-when').value;
  if (!value) { notify('Termin nije upisan.', true); return; }
  run('reschedule', { id, scheduled_at: value + ':00' });
}

function pendingDialog(id) {
  openModal(
    '<h2>Nerazriješen pokušaj objave</h2>' +
    '<div class="warn">Prethodni pokušaj nije jasno završio. Otvorite Instagram i provjerite je li objava stvarno vidljiva ' +
    'prije nego što ovo razriješite, inače možete stvoriti duplikat.</div>' +
    '<div class="field"><label>Stvarno stanje na Instagramu</label><select id="pd-outcome">' +
    '<option value="not_published">Objava NIJE vidljiva — poništi pokušaj</option>' +
    '<option value="published">Objava JEST vidljiva — evidentiraj kao objavljeno</option></select></div>' +
    '<div class="field"><label>Meta ID (samo ako je objava vidljiva)</label><input id="pd-external"></div>' +
    '<div class="field"><label>Za potvrdu upišite točan ID: ' + esc(id) + '</label><input id="pd-confirm"></div>' +
    '<div class="actions"><button onclick="closeModal()">Odustani</button>' +
    '<button class="go" onclick="submitPending(\'' + esc(id) + '\')">Razriješi</button></div>'
  );
}

function submitPending(id) {
  run('resolve_pending', {
    id,
    outcome: document.getElementById('pd-outcome').value,
    external_id: document.getElementById('pd-external').value,
    confirm: document.getElementById('pd-confirm').value
  });
}

document.addEventListener('click', event => {
  const target = event.target.closest('[data-act]');
  if (!target) return;
  const id = target.dataset.id;
  switch (target.dataset.act) {
    case 'host': run('host_media', { id }); break;
    case 'approve': approveDialog(id); break;
    case 'revoke': run('revoke', { id }); break;
    case 'schedule': scheduleDialog(id, target.dataset.when); break;
    case 'publish': publishDialog(id); break;
    case 'pending': pendingDialog(id); break;
    case 'check': call('check_connection', {}); break;
    case 'hoststatus': call('media_host_status', {}); break;
  }
});

document.getElementById('ap-toggle').addEventListener('click', () => {
  run('autopilot', {
    enabled: !BOOT.autopilot.enabled,
    interval_minutes: parseInt(document.getElementById('ap-interval').value, 10) || 5,
    changed_by: 'dashboard'
  });
});

document.querySelectorAll('button[data-filter]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('button[data-filter]').forEach(other => other.classList.remove('active'));
  button.classList.add('active');
  const filter = button.dataset.filter;
  document.querySelectorAll('.card').forEach(card => card.classList.toggle(
    'hidden', filter !== 'all' && card.dataset.channel !== filter && card.dataset.status !== filter));
}));

modal.addEventListener('click', event => { if (event.target === modal) closeModal(); });
setInterval(() => { if (!busy && !modal.classList.contains('open')) location.reload(); }, 30000);
"""


class DashboardHandler(BaseHTTPRequestHandler):
    manifest_path: Path

    def send_bytes(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: dict) -> None:
        self.send_bytes(status, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def authorised(self) -> str:
        """Fail closed on anything that is not a same-origin loopback request."""
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            return "Dopušten je samo lokalni pristup."
        if self.headers.get("X-CSRF-Token", "") != CSRF_TOKEN:
            return "Neispravan CSRF token; osvježite stranicu."
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).hostname not in ("127.0.0.1", "::1", "localhost"):
            return "Zahtjev nije s lokalnog podrijetla."
        return ""

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/":
                self.send_bytes(200, "text/html; charset=utf-8", render_page(self.manifest_path))
                return
            if path == "/api/status":
                body = json.dumps(snapshot(self.manifest_path), ensure_ascii=False, indent=2).encode("utf-8")
                self.send_bytes(200, "application/json; charset=utf-8", body)
                return
            if path.startswith("/api/package/"):
                content_id = unquote(path.removeprefix("/api/package/"))
                self.send_json(200, review_package(self.manifest_path, content_id))
                return
            if path.startswith("/media/"):
                content_id = unquote(path.removeprefix("/media/"))
                manifest = load_manifest(self.manifest_path)
                item = next((entry for entry in manifest["items"] if entry["id"] == content_id), None)
                if not item:
                    self.send_bytes(404, "text/plain; charset=utf-8", b"Not found")
                    return
                media = resolve(self.manifest_path, item["media_path"])
                self.send_bytes(200, mimetypes.guess_type(media.name)[0] or "application/octet-stream", media.read_bytes())
                return
            self.send_bytes(404, "text/plain; charset=utf-8", b"Not found")
        except (AgentError, ResearchGateError, OSError, ValueError, KeyError) as exc:
            if path.startswith("/api/"):
                self.send_json(500, {"error": str(exc)})
            else:
                self.send_bytes(500, "text/plain; charset=utf-8", f"Dashboard error: {exc}".encode("utf-8"))

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/action":
            self.send_json(404, {"error": "Nepoznat endpoint."})
            return
        denial = self.authorised()
        if denial:
            self.send_json(403, {"error": denial})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            self.send_json(400, {"error": "Neispravan Content-Length."})
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self.send_json(400, {"error": "Neispravna veličina zahtjeva."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self.send_json(400, {"error": f"Neispravan JSON: {exc}"})
            return
        if not isinstance(payload, dict):
            self.send_json(400, {"error": "Tijelo zahtjeva mora biti JSON objekt."})
            return
        handler = ACTIONS.get(str(payload.get("action", "")))
        if not handler:
            self.send_json(400, {"error": f"Nepoznata akcija: {payload.get('action')}"})
            return
        try:
            self.send_json(200, handler(self.manifest_path, payload))
        except (ActionError, AgentError, ResearchGateError, MediaHostError, CredentialError) as exc:
            self.send_json(400, {"error": str(exc)})
        except (OSError, ValueError, KeyError) as exc:
            self.send_json(500, {"error": f"Neočekivana greška: {exc}"})

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("[dashboard] " + format % args + "\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="AID Instagram operational control dashboard")
    result.add_argument("--manifest", type=Path, required=True)
    result.add_argument("--host", default="127.0.0.1")
    result.add_argument("--port", type=int, default=7010)
    result.add_argument("--no-autopilot", action="store_true", help="Ne pokreći pozadinski scheduler.")
    return result


def main() -> int:
    args = parser().parse_args()
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        print("Dashboard izvršava stvarne objave i smije slušati samo na loopbacku.", file=sys.stderr)
        return 1
    load_env_file()
    manifest_path = args.manifest.resolve()
    load_manifest(manifest_path)
    DashboardHandler.manifest_path = manifest_path

    stop = threading.Event()
    if not args.no_autopilot:
        threading.Thread(target=autopilot_loop, args=(manifest_path, stop), daemon=True).start()

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    state = autopilot_state()
    print(f"AID Instagram Control: http://{args.host}:{args.port}")
    print(f"Autopilot: {'UKLJUČEN' if state['enabled'] else 'isključen'} · interval {state['interval_minutes']} min")
    print("Operativni dashboard. Ctrl+C za zaustavljanje.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
