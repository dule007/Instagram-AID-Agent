#!/usr/bin/env python3
"""Offline tests for the operational dashboard actions and the media host."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import dashboard
import media_host
from dashboard import ActionError
from media_host import MediaHostError


def write_manifest(directory: Path, scheduled_at: str, content_id: str = "TEST-01") -> Path:
    path = directory / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "campaign": "test",
                "timezone": "Europe/Zagreb",
                "research_gate_path": "research-gate.json",
                "items": [
                    {
                        "id": content_id,
                        "scheduled_at": scheduled_at,
                        "channel": "FEED",
                        "media_type": "IMAGE",
                        "media_path": "a.png",
                        "brief_path": "a.md",
                        "caption_path": "a.md",
                        "media_url": "",
                        "claims_status": "verified",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


class MediaHostConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {key: os.environ.get(key) for key in ("GITHUB_TOKEN", "GITHUB_MEDIA_REPO")}

    def tearDown(self) -> None:
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_missing_token_blocks_hosting(self) -> None:
        os.environ.pop("GITHUB_TOKEN", None)
        with self.assertRaises(MediaHostError):
            media_host.config()

    def test_malformed_repository_is_rejected(self) -> None:
        os.environ["GITHUB_TOKEN"] = "x"
        os.environ["GITHUB_MEDIA_REPO"] = "samo-ime-bez-vlasnika"
        with self.assertRaises(MediaHostError):
            media_host.config()

    def test_remote_name_is_content_addressed_and_safe(self) -> None:
        name = media_host.remote_name("AID/../2608 F01", Path("x.jpg"), "a" * 64)
        self.assertNotIn("/", name)
        self.assertNotIn(" ", name)
        self.assertTrue(name.endswith("-aaaaaaaaaaaa.jpg"))

    def test_redact_removes_token_from_errors(self) -> None:
        self.assertEqual(media_host.redact("greska tajna123 kraj", "tajna123"), "greska [REDACTED] kraj")


class ApprovalGuardTest(unittest.TestCase):
    def test_approve_requires_exact_confirmation(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_approve(Path("x.json"), {"id": "A", "approved_by": "Ime", "confirm": "B"})

    def test_approve_requires_named_person(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_approve(Path("x.json"), {"id": "A", "approved_by": "", "confirm": "A"})

    def test_publish_requires_exact_confirmation(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_publish(Path("x.json"), {"id": "A", "confirm": ""})

    def test_resolve_pending_requires_known_outcome(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_resolve_pending(Path("x.json"), {"id": "A", "confirm": "A", "outcome": "mozda"})


class AutopilotGuardTest(unittest.TestCase):
    def test_interval_above_limit_is_rejected(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_autopilot(Path("x.json"), {"enabled": False, "interval_minutes": 10_000})

    def test_interval_below_limit_is_rejected(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_autopilot(Path("x.json"), {"enabled": False, "interval_minutes": 0})

    def test_non_numeric_interval_is_rejected(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_autopilot(Path("x.json"), {"enabled": False, "interval_minutes": "brzo"})


class RescheduleTest(unittest.TestCase):
    def test_naive_summer_time_uses_daylight_offset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(Path(directory), "2026-07-22T10:15:00+02:00")
            dashboard.action_reschedule(path, {"id": "TEST-01", "scheduled_at": "2026-07-30T09:00:00"})
            stored = json.loads(path.read_text(encoding="utf-8"))["items"][0]["scheduled_at"]
            self.assertEqual(stored, "2026-07-30T09:00:00+02:00")

    def test_naive_winter_time_uses_standard_offset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(Path(directory), "2026-07-22T10:15:00+02:00")
            dashboard.action_reschedule(path, {"id": "TEST-01", "scheduled_at": "2026-12-15T09:00:00"})
            stored = json.loads(path.read_text(encoding="utf-8"))["items"][0]["scheduled_at"]
            self.assertEqual(stored, "2026-12-15T09:00:00+01:00")

    def test_unparseable_time_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(Path(directory), "2026-07-22T10:15:00+02:00")
            with self.assertRaises(ActionError):
                dashboard.action_reschedule(path, {"id": "TEST-01", "scheduled_at": "sutra"})

    def test_empty_time_is_rejected(self) -> None:
        with self.assertRaises(ActionError):
            dashboard.action_reschedule(Path("x.json"), {"id": "TEST-01", "scheduled_at": "  "})


class ManifestWriteGuardTest(unittest.TestCase):
    def test_only_whitelisted_fields_can_be_written(self) -> None:
        from agent import AgentError, update_item

        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(Path(directory), "2026-07-22T10:15:00+02:00")
            with self.assertRaises(AgentError):
                update_item(path, "TEST-01", {"claims_status": "verified"})

    def test_non_https_media_url_is_rejected(self) -> None:
        from agent import AgentError, update_item

        with tempfile.TemporaryDirectory() as directory:
            path = write_manifest(Path(directory), "2026-07-22T10:15:00+02:00")
            with self.assertRaises(AgentError):
                update_item(path, "TEST-01", {"media_url": "http://nesigurno.example/a.jpg"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
