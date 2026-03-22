#!/usr/bin/env sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
API_DIR="$PROJECT_ROOT/apps/api"
DEFAULT_DB_PATH="$API_DIR/openclaw_skill_explorer.db"
DB_PATH="${1:-$DEFAULT_DB_PATH}"
BACKUP_DIR="${2:-$PROJECT_ROOT/backups}"

if [ ! -f "$DB_PATH" ]; then
  echo "database file not found: $DB_PATH" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
BACKUP_PATH="$BACKUP_DIR/openclaw_skill_explorer_$TIMESTAMP.db"
cp "$DB_PATH" "$BACKUP_PATH"

echo "backup_created=$BACKUP_PATH"
