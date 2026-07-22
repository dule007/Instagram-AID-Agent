#!/usr/bin/env python3
"""Offline tests for credential-source isolation and expiry reporting."""

from __future__ import annotations

import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

import credentials


class CredentialTests(unittest.TestCase):
    def clean_environment(self) -> dict[str, str]:
        return {
            key: value
            for key, value in os.environ.items()
            if key not in (*credentials.ENV_CREDENTIAL_KEYS, "IG_API_HOST")
        }

    def session(self, expires_at: str | None = None) -> dict:
        return {
            "provider": "instagram_login",
            "graph_version": "v25.0",
            "ig_user_id": "42",
            "access_token": "session-secret",
            "api_host": "graph.instagram.com",
            "username": "autoinsightdata",
            "expected_username": "autoinsightdata",
            "account_type": "BUSINESS",
            "scopes": sorted(credentials.REQUIRED_INSTAGRAM_SCOPES),
            "token_kind": "long_lived",
            "expires_at": expires_at or (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        }

    @mock.patch.object(credentials, "read_session")
    def test_partial_environment_never_mixes_with_session(self, read_session: mock.Mock) -> None:
        read_session.return_value = self.session()
        environment = {**self.clean_environment(), "META_ACCESS_TOKEN": "environment-secret"}
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(credentials.CredentialError):
                credentials.api_credentials()

    @mock.patch.object(credentials, "read_session")
    def test_complete_session_is_selected_as_one_source(self, read_session: mock.Mock) -> None:
        read_session.return_value = self.session()
        with mock.patch.dict(os.environ, self.clean_environment(), clear=True):
            selected = credentials.api_credentials()
        self.assertEqual(selected["source"], "oauth_session")
        self.assertEqual(selected["ig_user_id"], "42")
        self.assertEqual(selected["access_token"], "session-secret")

    @mock.patch.object(credentials, "read_session")
    def test_graph_version_alone_does_not_override_oauth_session(self, read_session: mock.Mock) -> None:
        read_session.return_value = self.session()
        environment = {**self.clean_environment(), "META_GRAPH_VERSION": "v25.0"}
        with mock.patch.dict(os.environ, environment, clear=True):
            selected = credentials.api_credentials()
            status = credentials.connection_status()
        self.assertEqual(selected["source"], "oauth_session")
        self.assertEqual(selected["access_token"], "session-secret")
        self.assertEqual(status["status"], "connected")

    @mock.patch.object(credentials, "read_session")
    def test_instagram_alias_pair_is_selected_without_exposing_values(self, read_session: mock.Mock) -> None:
        read_session.return_value = self.session()
        environment = {
            **self.clean_environment(),
            "META_GRAPH_VERSION": "v25.0",
            "INSTAGRAM_IG_USER_ID": "42",
            "INSTAGRAM_ACCESS_TOKEN": "alias-secret",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            selected = credentials.api_credentials()
            status = credentials.connection_status()
        self.assertEqual(selected["source"], "environment")
        self.assertEqual(selected["ig_user_id"], "42")
        self.assertEqual(selected["access_token"], "alias-secret")
        self.assertEqual(status["status"], "configured")

    def test_conflicting_aliases_are_blocked_without_values_in_error(self) -> None:
        environment = {
            **self.clean_environment(),
            "META_GRAPH_VERSION": "v25.0",
            "IG_USER_ID": "42",
            "INSTAGRAM_IG_USER_ID": "99",
            "META_ACCESS_TOKEN": "first-secret",
            "INSTAGRAM_ACCESS_TOKEN": "second-secret",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(credentials.CredentialError) as raised:
                credentials.api_credentials()
        message = str(raised.exception)
        self.assertNotIn("first-secret", message)
        self.assertNotIn("second-secret", message)

    @mock.patch.object(credentials, "read_session")
    def test_expired_session_is_not_reported_as_connected(self, read_session: mock.Mock) -> None:
        expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        read_session.return_value = self.session(expired)
        with mock.patch.dict(os.environ, self.clean_environment(), clear=True):
            status = credentials.connection_status()
        self.assertEqual(status["status"], "expired")


if __name__ == "__main__":
    unittest.main()
