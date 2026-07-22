#!/usr/bin/env python3
"""Read-only snapshot of an owned Instagram Professional account via Meta API."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from credentials import CANONICAL_INSTAGRAM_USERNAME, CredentialError, api_credentials


class ScoutError(RuntimeError):
    pass


def get_json(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        detail = detail.replace(token, "[REDACTED]")
        raise ScoutError(f"Meta API greška {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ScoutError(f"Meta API nije dostupan: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ScoutError(f"Meta API nije vratio valjan JSON: {exc}") from exc


def endpoint(host: str, version: str, object_id: str, fields: str, **params: str | int) -> str:
    query = {"fields": fields, **params}
    return f"https://{host}/{version}/{object_id}?{urllib.parse.urlencode(query)}"


def collect(limit: int) -> dict:
    try:
        credentials = api_credentials()
    except CredentialError as exc:
        raise ScoutError(str(exc)) from exc
    host = str(credentials["api_host"])
    version = str(credentials["graph_version"])
    account_id = str(credentials["ig_user_id"])
    token = str(credentials["access_token"])

    profile = get_json(
        endpoint(host, version, account_id, "id,username,account_type,media_count"),
        token,
    )
    profile_id = str(profile.get("user_id") or profile.get("id") or "")
    profile_username = str(profile.get("username") or "").lstrip("@")
    if profile_id != account_id or profile_username.casefold() != CANONICAL_INSTAGRAM_USERNAME.casefold():
        raise ScoutError("Autorizirani profil nije kanonski @autoinsightdata račun.")
    media_payload = get_json(
        endpoint(
            host,
            version,
            f"{account_id}/media",
            "id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count",
            limit=limit,
        ),
        token,
    )
    media = media_payload.get("data", [])
    if not isinstance(media, list):
        raise ScoutError("Meta API media odgovor nema očekivanu data listu.")
    format_counts = Counter(entry.get("media_product_type") or entry.get("media_type") or "UNKNOWN" for entry in media)
    public_likes = sum(int(entry.get("like_count", 0) or 0) for entry in media)
    public_comments = sum(int(entry.get("comments_count", 0) or 0) for entry in media)
    return {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": "official_meta_instagram_api",
        "mode": "read_only_owned_professional_account",
        "private_insights_included": False,
        "limitations": [
            "Ovaj snapshot nije privatni Insights izvještaj.",
            "Like i comment count nisu dovoljni za procjenu reacha, saves, shares, retentiona ili leadova.",
            "Dohvaćena je samo prva stranica medija do zadanog limita.",
        ],
        "profile": profile,
        "summary": {
            "sample_size": len(media),
            "formats": dict(sorted(format_counts.items())),
            "public_like_count_total": public_likes,
            "public_comment_count_total": public_comments,
        },
        "media": media,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Read-only AID Instagram account scout")
    result.add_argument("--limit", type=int, default=25, help="Broj zadnjih medija, 1-50.")
    result.add_argument("--output", type=Path, help="Opcionalna lokalna JSON datoteka; token se ne sprema.")
    return result


def main() -> int:
    args = parser().parse_args()
    if not 1 <= args.limit <= 50:
        print("SCOUT BLOKIRAN: --limit mora biti između 1 i 50.", file=sys.stderr)
        return 1
    try:
        snapshot = collect(args.limit)
        rendered = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = args.output.resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
            print(f"READ-ONLY SCOUT OK: snapshot spremljen u {output}")
        else:
            print(rendered, end="")
    except (ScoutError, OSError, ValueError) as exc:
        print(f"SCOUT BLOKIRAN: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
