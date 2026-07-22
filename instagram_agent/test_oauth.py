#!/usr/bin/env python3
"""Offline tests for OAuth URL, multipart payload and token handling."""

from __future__ import annotations

import unittest
import urllib.parse
from unittest import mock

import oauth


class OAuthTests(unittest.TestCase):
    def settings(self) -> dict:
        return {
            "app_id": "123456",
            "app_secret": "secret-value",
            "redirect_uri": "http://127.0.0.1:7012/callback",
            "graph_version": "v25.0",
            "expected_username": "autoinsightdata",
            "expected_user_id": "",
            "scopes": oauth.DEFAULT_SCOPES,
        }

    def test_authorization_url_uses_current_business_scopes_and_state(self) -> None:
        url = urllib.parse.urlparse(oauth.authorization_url(self.settings(), "csrf-state"))
        query = urllib.parse.parse_qs(url.query)
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.netloc, "www.instagram.com")
        self.assertEqual(query["client_id"], ["123456"])
        self.assertEqual(query["state"], ["csrf-state"])
        self.assertEqual(query["enable_fb_login"], ["false"])
        self.assertEqual(query["force_reauth"], ["true"])
        self.assertIn("instagram_business_content_publish", query["scope"][0])
        self.assertNotIn("force_authentication", query)

    def test_non_numeric_instagram_app_id_is_rejected(self) -> None:
        settings = self.settings()
        settings["app_id"] = "not-an-instagram-app-id"
        self.assertIn(
            "INSTAGRAM_APP_ID (mora biti numerički Instagram App ID)",
            oauth.missing_config(settings),
        )

    def test_multipart_token_exchange_does_not_use_query_string(self) -> None:
        body, content_type = oauth.multipart_form({"client_id": "123", "code": "one-time-code"})
        self.assertTrue(content_type.startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="client_id"', body)
        self.assertIn(b"one-time-code", body)

    @mock.patch.object(oauth, "write_session")
    @mock.patch.object(oauth, "profile_request")
    @mock.patch.object(oauth, "exchange_long_lived")
    @mock.patch.object(oauth, "exchange_code")
    def test_connect_returns_no_access_token(
        self,
        exchange_code: mock.Mock,
        exchange_long_lived: mock.Mock,
        profile_request: mock.Mock,
        write_session: mock.Mock,
    ) -> None:
        exchange_code.return_value = {
            "access_token": "short-secret",
            "user_id": "42",
            "permissions": list(oauth.DEFAULT_SCOPES),
        }
        exchange_long_lived.return_value = {"access_token": "long-secret", "expires_in": 5_184_000}
        profile_request.return_value = {"user_id": "42", "username": "autoinsightdata", "account_type": "BUSINESS"}
        visible = oauth.connect(self.settings(), "one-time-code")
        self.assertNotIn("access_token", visible)
        self.assertEqual(visible["username"], "autoinsightdata")
        stored = write_session.call_args.args[0]
        self.assertEqual(stored["access_token"], "long-secret")
        self.assertEqual(stored["token_kind"], "long_lived")

    @mock.patch.object(oauth, "write_session")
    @mock.patch.object(oauth, "profile_request")
    @mock.patch.object(oauth, "exchange_long_lived")
    @mock.patch.object(oauth, "exchange_code")
    def test_long_lived_exchange_failure_does_not_write_session(
        self,
        exchange_code: mock.Mock,
        exchange_long_lived: mock.Mock,
        profile_request: mock.Mock,
        write_session: mock.Mock,
    ) -> None:
        exchange_code.return_value = {
            "access_token": "short-secret",
            "user_id": "42",
            "permissions": list(oauth.DEFAULT_SCOPES),
        }
        exchange_long_lived.side_effect = oauth.OAuthError("exchange unavailable")
        with self.assertRaises(oauth.OAuthError):
            oauth.connect(self.settings(), "one-time-code")
        write_session.assert_not_called()

    @mock.patch.object(oauth, "write_session")
    @mock.patch.object(oauth, "exchange_long_lived")
    @mock.patch.object(oauth, "exchange_code")
    def test_missing_scope_blocks_connection(
        self,
        exchange_code: mock.Mock,
        exchange_long_lived: mock.Mock,
        write_session: mock.Mock,
    ) -> None:
        exchange_code.return_value = {
            "access_token": "short-secret",
            "user_id": "42",
            "permissions": ["instagram_business_basic"],
        }
        with self.assertRaises(oauth.OAuthError):
            oauth.connect(self.settings(), "one-time-code")
        exchange_long_lived.assert_not_called()
        write_session.assert_not_called()

    @mock.patch.object(oauth, "write_session")
    @mock.patch.object(oauth, "profile_request")
    @mock.patch.object(oauth, "exchange_long_lived")
    @mock.patch.object(oauth, "exchange_code")
    def test_wrong_username_blocks_connection(
        self,
        exchange_code: mock.Mock,
        exchange_long_lived: mock.Mock,
        profile_request: mock.Mock,
        write_session: mock.Mock,
    ) -> None:
        exchange_code.return_value = {
            "access_token": "short-secret",
            "user_id": "42",
            "permissions": list(oauth.DEFAULT_SCOPES),
        }
        exchange_long_lived.return_value = {"access_token": "long-secret", "expires_in": 5_184_000}
        profile_request.return_value = {"user_id": "42", "username": "another_account", "account_type": "BUSINESS"}
        with self.assertRaises(oauth.OAuthError):
            oauth.connect(self.settings(), "one-time-code")
        write_session.assert_not_called()

    def test_request_log_never_contains_callback_code_or_state(self) -> None:
        line = oauth.safe_request_log("GET", "/callback?code=secret-code&state=secret-state", 200)
        self.assertEqual(line, "[oauth] GET /callback -> 200\n")
        self.assertNotIn("secret-code", line)
        self.assertNotIn("secret-state", line)


if __name__ == "__main__":
    unittest.main()
