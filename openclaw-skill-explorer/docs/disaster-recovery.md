# Disaster Recovery Runbook

## Scope

This runbook covers backup/restore procedures for:

- SQLite deployments (default local/demo mode)
- Postgres deployments (production-style mode)

## Recovery Objectives

- RPO target: <= 24 hours (or tighter based on backup schedule)
- RTO target: <= 30 minutes for SQLite restore, <= 60 minutes for Postgres restore

## 1) SQLite Backup

Create a point-in-time file backup:

```bash
./scripts/backup_sqlite.sh
```

Custom source DB and backup directory:

```bash
./scripts/backup_sqlite.sh ./apps/api/openclaw_skill_explorer.db ./backups
```

## 2) SQLite Restore

Stop API first, then restore:

```bash
./scripts/restore_sqlite.sh ./backups/openclaw_skill_explorer_YYYYMMDDTHHMMSSZ.db
```

Custom target DB path:

```bash
./scripts/restore_sqlite.sh ./backups/your_backup.db ./apps/api/openclaw_skill_explorer.db
```

After restore:

1. Start API
2. Check `GET /health`
3. Check `GET /api/skills?page=1&page_size=5`

## 3) Postgres Backup (Operational Note)

When running on Postgres, use native tools:

```bash
pg_dump "$DATABASE_URL" > backup.sql
```

Restore:

```bash
psql "$DATABASE_URL" < backup.sql
```

## 4) Incident Procedure

1. Confirm failure scope (read-only degradation vs data corruption).
2. Stop write traffic (stop API or put into maintenance mode).
3. Restore latest known-good backup.
4. Verify health endpoints and key APIs.
5. Document root cause and restoration timeline.

## 5) Validation Checklist

- `/health` returns `200`
- `/ready` returns `200`
- `/api/skills` returns data
- Recent scan/review records are present as expected
- Frontend can load skills list and detail pages
