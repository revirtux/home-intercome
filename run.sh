#!/usr/bin/env bash
set -euo pipefail

# Start the mock ESP32 server for local development.
# Requires: uv (https://github.com/astral-sh/uv)
#
# Usage:
#   ./run.sh               # default port 8000
#   ./run.sh --port 9000   # custom port

cd "$(dirname "$0")"
exec uv run server/main.py "$@"
