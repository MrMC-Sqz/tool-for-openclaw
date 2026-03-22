#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://openclaw:openclaw@localhost:5432/openclaw_skill_explorer}"
export DB_POOL_PRE_PING="${DB_POOL_PRE_PING:-true}"

cd "$PROJECT_ROOT/apps/api"
exec uvicorn app.main:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}" --reload
