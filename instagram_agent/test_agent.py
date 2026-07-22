#!/usr/bin/env python3
"""Offline tests for the fail-closed publish target lock."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import agent


class AgentTargetTests(unittest.TestCase):
    def test_autoinsightdata_business_profile_is_allowed(self) -> None:
        agent.validate_target_profile(
            {"id": "42", "username": "autoinsightdata", "account_type": "BUSINESS"},
            "42",
        )

    def test_other_username_is_blocked(self) -> None:
        with self.assertRaises(agent.AgentError):
            agent.validate_target_profile(
                {"id": "42", "username": "another_account", "account_type": "BUSINESS"},
                "42",
            )

    def test_other_profile_id_is_blocked(self) -> None:
        with self.assertRaises(agent.AgentError):
            agent.validate_target_profile(
                {"id": "99", "username": "autoinsightdata", "account_type": "BUSINESS"},
                "42",
            )

    def test_jpeg_dimensions_are_read_from_real_sof_marker(self) -> None:
        jpeg = (
            b"\xff\xd8\xff\xc0\x00\x11\x08"
            + (1350).to_bytes(2, "big")
            + (1080).to_bytes(2, "big")
            + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset.jpg"
            path.write_bytes(jpeg)
            self.assertEqual(agent.jpeg_size(path), (1080, 1350))

    def test_png_renamed_to_jpeg_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset.jpg"
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
            with self.assertRaises(agent.AgentError):
                agent.jpeg_size(path)

    @mock.patch.object(agent.time, "sleep")
    @mock.patch.object(agent, "graph_get")
    def test_container_must_finish_before_publish(self, graph_get: mock.Mock, sleep: mock.Mock) -> None:
        graph_get.side_effect = [
            {"status_code": "IN_PROGRESS"},
            {"status_code": "FINISHED"},
        ]
        result = agent.wait_for_container("https://graph.instagram.com/v25.0/42", "99", "secret")
        self.assertEqual(result["status_code"], "FINISHED")
        self.assertEqual(graph_get.call_count, 2)
        sleep.assert_called_once()

    @mock.patch.object(agent, "graph_get")
    def test_container_error_blocks_publish(self, graph_get: mock.Mock) -> None:
        graph_get.return_value = {"status_code": "ERROR", "status": "Bad media"}
        with self.assertRaises(agent.AgentError):
            agent.wait_for_container("https://graph.instagram.com/v25.0/42", "99", "secret")

    @mock.patch.object(agent.urllib.request, "urlopen")
    def test_graph_post_sends_token_only_as_bearer_header(self, urlopen: mock.Mock) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"id":"99"}'
        urlopen.return_value = response
        result = agent.graph_post("https://graph.instagram.com/v25.0/42/media", {"caption": "test"}, "secret")
        request = urlopen.call_args.args[0]
        self.assertEqual(result["id"], "99")
        self.assertNotIn(b"secret", request.data)
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")


if __name__ == "__main__":
    unittest.main()
