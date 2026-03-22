#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <backup_file> [target_db_path]" >&2
  exit 1
fi

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
API_DIR="$PROJECT_ROOT/apps/api"
DEFAULT_TARGET_DB="$API_DIR/openclaw_skill_explorer.db"

BACKUP_FILE="$1"
TARGET_DB_PATH="${2:-$DEFAULT_TARGET_DB}"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_DB_PATH")"
cp "$BACKUP_FILE" "$TARGET_DB_PATH"

echo "database_restored=$TARGET_DB_PATH"
