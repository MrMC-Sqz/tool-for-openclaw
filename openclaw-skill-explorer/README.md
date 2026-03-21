# OpenClaw Skill Explorer + Risk Scanner

OpenClaw Skill Explorer + Risk Scanner is a full-stack demo app built with:

- FastAPI + SQLAlchemy + SQLite (`apps/api`)
- Next.js + TypeScript (`apps/web`)

This repository is ready for:

- local development
- production-style local runs with Docker Compose
- future deployment to Vercel (web) + Render/Railway/Fly.io (api)

## Project Structure

- `apps/api`: FastAPI backend
- `apps/web`: Next.js frontend
- `scripts`: helper scripts for local developer workflows
- `docs`: product and task documents
- `docker-compose.yml`: local full-stack container orchestration

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- Docker Desktop (for Docker workflow)

## Environment Variables

Copy these templates before running:

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
Copy-Item apps/api/.env.example apps/api/.env
Copy-Item apps/web/.env.local.example apps/web/.env.local
```

### Root `.env.example`

Used mainly by Docker Compose defaults and shared local config examples.

### Backend `apps/api/.env.example`

Required/important:

- `APP_NAME`
- `APP_ENV`
- `APP_HOST`
- `APP_PORT`
- `DATABASE_URL`
- `CORS_ALLOW_ORIGINS`

Optional:

- `GITHUB_TOKEN`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `OPENAI_FALLBACK_MODEL`
- `OPENAI_TIMEOUT_SECONDS`

### Frontend `apps/web/.env.local.example`

Required:

- `NEXT_PUBLIC_API_BASE_URL` (for example: `http://localhost:8000`)

## Local Development

### 1) Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell activate:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Initialize database:

```bash
cd apps/api
python -m app.db.init_db
```

Run backend:

```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use helper script:

```bash
./scripts/run_api.sh
```

### 2) Seed / Sync Skill Data

```bash
python scripts/sync_sources.py
```

### 3) Frontend

```bash
cd apps/web
npm install
npm run dev
```

Or use helper script:

```bash
./scripts/run_web.sh
```

### 4) Local URLs

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`

## Docker Development

From repository root:

```bash
docker compose up --build
```

Services:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Stop containers:

```bash
docker compose down
```

Stop and remove volumes (reset SQLite data):

```bash
docker compose down -v
```

## Production-Style Notes

- Frontend can be deployed to Vercel.
- Backend can be deployed to Render, Railway, or Fly.io.
- Keep `NEXT_PUBLIC_API_BASE_URL` pointed to deployed backend URL.
- Keep `CORS_ALLOW_ORIGINS` aligned with deployed frontend origins.
- SQLite is acceptable for demos and small local setups, but not ideal for high scale or heavy concurrency.
