#!/usr/bin/env python3
"""Loopback-only server for one locked Instagram publish asset."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class AssetError(RuntimeError):
    pass


class AssetHandler(BaseHTTPRequestHandler):
    asset_path: str
    asset_bytes: bytes
    asset_sha256: str

    def send_asset(self, include_body: bool) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != self.asset_path or parsed.query or parsed.fragment:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(self.asset_bytes)))
        self.send_header("ETag", f'"{self.asset_sha256}"')
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if include_body:
            self.wfile.write(self.asset_bytes)

    def do_GET(self) -> None:  # noqa: N802
        self.send_asset(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self.send_asset(include_body=False)

    def do_POST(self) -> None:  # noqa: N802
        self.send_error(405)

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        del size
        sys.stderr.write(f"[asset] {self.command} -> {code}\n")

    def log_message(self, format: str, *args: object) -> None:
        del format, args


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Serve exactly one locked JPEG on loopback")
    result.add_argument("--file", type=Path, required=True)
    result.add_argument("--path-token", required=True)
    result.add_argument("--host", default="127.0.0.1")
    result.add_argument("--port", type=int, default=7013)
    return result


def main() -> int:
    args = parser().parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        raise AssetError("Asset server smije slušati samo na loopback adresi.")
    if len(args.path_token) < 32 or not all(character in "0123456789abcdef" for character in args.path_token):
        raise AssetError("Path token mora biti najmanje 128-bitni lowercase hex.")
    asset = args.file.resolve()
    data = asset.read_bytes()
    if asset.suffix.casefold() not in {".jpg", ".jpeg"} or not data.startswith(b"\xff\xd8"):
        raise AssetError("Objavljivi asset mora biti stvarni JPEG.")
    AssetHandler.asset_path = f"/{args.path_token}.jpg"
    AssetHandler.asset_bytes = data
    AssetHandler.asset_sha256 = hashlib.sha256(data).hexdigest()
    server = ThreadingHTTPServer((args.host, args.port), AssetHandler)
    print(f"AID one-file media server: http://{args.host}:{args.port}{AssetHandler.asset_path}")
    print(f"SHA-256: {AssetHandler.asset_sha256}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
