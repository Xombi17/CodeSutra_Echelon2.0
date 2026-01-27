#!/usr/bin/env bash
set -euo pipefail

# Simple entrypoint to run migrations (if any) and start the server
# Use environment variables for configuration

echo "[entrypoint] Starting SilverSentinel..."

# Ensure DB directory exists for SQLite path if using file path
if [[ "$DATABASE_URL" == sqlite:* ]] || [[ -n "${DATABASE_FILE:-}" ]]; then
  DBFILE="${DATABASE_FILE:-/tmp/silversentinel.db}"
  mkdir -p "$(dirname "$DBFILE")"
fi

# Run the main module
exec python main.py
