#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

exec python3 "$SCRIPT_DIR/oauth.py" serve \
  --host 127.0.0.1 \
  --port 7012 \
  --open-browser
