#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

exec python3 "$SCRIPT_DIR/dashboard.py" \
  --manifest "$PROJECT_DIR/content/campaigns/2026-08-relaunch/publishing-manifest.json" \
  --host 127.0.0.1 \
  --port 7010
