#!/usr/bin/env python3
"""Build the relaunch publishing manifest from the campaign schedule."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO = Path(__file__).resolve().parents[1]
CAMPAIGN = REPO / "content" / "campaigns" / "2026-08-relaunch"


def story_sticker(brief_path: Path) -> str:
    prefix = "- Interaktivni element: `"
    for line in brief_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line.removeprefix(prefix).removesuffix("`")
    raise ValueError(f"Story brief nema interaktivni element: {brief_path}")


def main() -> None:
    manifest_path = CAMPAIGN / "publishing-manifest.json"
    existing_by_id: dict[str, dict] = {}
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing_by_id = {item["id"]: item for item in existing.get("items", [])}
    items = []
    with (CAMPAIGN / "schedule.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            local = datetime.fromisoformat(f"{row['date']}T{row['time']}").replace(tzinfo=ZoneInfo(row["timezone"]))
            is_feed = row["channel"] == "feed"
            media = Path(row["asset"])
            brief = media.with_suffix(".md")
            existing_item = existing_by_id.get(row["id"], {})
            item = {
                "id": row["id"],
                "scheduled_at": local.isoformat(),
                "channel": "FEED" if is_feed else "STORY",
                "media_type": "IMAGE" if is_feed else "STORIES",
                "media_path": media.as_posix(),
                "brief_path": brief.as_posix(),
                "caption_path": brief.as_posix() if is_feed else "",
                "media_url": existing_item.get("media_url", ""),
                "claims_status": "verified",
                "status": row["status"],
            }
            publish_media = media.with_suffix(".jpg")
            if is_feed and (CAMPAIGN / publish_media).is_file():
                item["publish_media_path"] = publish_media.as_posix()
            if not is_feed:
                item["native_sticker"] = story_sticker(CAMPAIGN / brief)
                item["manual_only"] = True
            items.append(item)
    manifest = {
        "schema_version": 1,
        "campaign": "2026-08-relaunch",
        "timezone": "Europe/Zagreb",
        "approval_required": True,
        "research_gate_path": "research-gate.json",
        "items": items,
    }
    (CAMPAIGN / "publishing-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
