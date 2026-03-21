# OpenClaw Skill Explorer + Risk Scanner

Monorepo scaffold for the MVP web application.

## Structure

- `apps/web`: Next.js frontend (TypeScript + Tailwind)
- `apps/api`: FastAPI backend (Python 3.11+)
- `packages/shared`: Shared package placeholder for future cross-app assets
- `scripts`: Local setup and utility scripts
- `docs`: Project documents

## Prerequisites

- Node.js 20+
- npm 10+
- Python 3.11+

## Environment Setup

1. Copy root env template:
   - `cp .env.example .env` (or create manually)
2. Backend env:
   - `cp apps/api/.env.example apps/api/.env`
3. Frontend env:
   - `cp apps/web/.env.local.example apps/web/.env.local`

## Backend Setup (FastAPI)

1. `cd apps/api`
2. `python -m venv .venv`
3. Activate venv:
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. Optional SQLite init placeholder:
   - `python ..\..\scripts\init_db.py`
6. Run API server:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Health check:
- `GET http://localhost:8000/health` -> `{ "status": "ok" }`

## Frontend Setup (Next.js)

1. `cd apps/web`
2. `npm install`
3. `npm run dev`
4. Open `http://localhost:3000`

## Notes

- This round includes initialization only.
- Business logic, sync pipelines, risk engine logic, and full product pages are intentionally deferred.
