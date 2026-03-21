# OpenClaw Skill Explorer + Risk Scanner

**A tool for discovering, evaluating, and safely configuring OpenClaw skills.**

OpenClaw Skill Explorer + Risk Scanner is a full-stack system that helps developers review skill metadata, assess operational risk, and make safer configuration decisions before enabling skills in real environments.

## Why This Project Matters

AI-agent skills are powerful but often opaque. Teams need a practical way to answer:

- What does this skill actually do?
- What capabilities does it require?
- Is it safe to run in my environment?

This project addresses that gap with a deterministic risk engine, transparent scoring, and an interface built for quick human review.

## Demo

- Live demo: `https://your-demo-url-here.example.com` (placeholder)
- Local frontend: `http://localhost:3000`
- Local backend API docs: `http://localhost:8000/docs`

### Run Locally

1. Copy env files:

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local
```

2. Start backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Seed skills:

```bash
cd ../../
python scripts/sync_sources.py
```

4. Start frontend:

```bash
cd apps/web
npm install
npm run dev
```

### Run with Docker

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Stop:

```bash
docker compose down
```

Reset data volume:

```bash
docker compose down -v
```

## Screenshots

- Skills List: `docs/images/skills-list.png` (placeholder)
- Skill Detail: `docs/images/skill-detail.png` (placeholder)
- Risk Analysis Card: `docs/images/risk-analysis.png` (placeholder)
- Manual Scan Page: `docs/images/manual-scan.png` (placeholder)

## Features

### Skill Discovery

- Searchable skill catalog across name, description, summary, category, and tags
- Category and risk-level filtering with sorting and ranking
- Similar-skill recommendations based on shared metadata and keywords

### Risk Analysis

- Deterministic rule-based risk engine
- Capability detection for file access, network access, shell execution, secret access, and more
- Risk scoring and classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)

### AI Enhancements

- README summarization to improve quick comprehension
- Risk explanation refinement using LLM augmentation on top of deterministic results

### Developer Tooling

- Manual scan interface for README / manifest text
- Configuration guidance via surfaced recommendations
- Demo fallback data for resilient demos when API data is unavailable

## Tech Stack

### Frontend

- Next.js
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- SQLite
- SQLAlchemy

### AI

- OpenAI API

## Architecture Overview

The system is organized into clear layers:

1. **Ingestion Pipeline**  
   Pulls seed skills and repository metadata, fetches README content, normalizes records, and upserts to SQLite.

2. **Backend Services (FastAPI)**  
   Exposes APIs for skills listing/detail, search/filtering, similar recommendations, and scan workflows.

3. **Risk Engine**  
   Runs deterministic capability and keyword detection, computes risk score/level, and persists explainable reports.

4. **Frontend (Next.js)**  
   Displays searchable catalog, skill details, recommendation lists, and risk visualization cards.

5. **Data Flow**  
   `seed/source -> normalization -> DB -> risk analysis -> API -> UI`

For a deeper design write-up, see [docs/architecture.md](docs/architecture.md).

## How It Works

1. Ingest skills from curated seed data / sources.
2. Normalize repository metadata and textual fields.
3. Analyze risk via rule-based detection and scoring.
4. Store skills and risk reports in SQLite.
5. Display searchable, explainable results in the web UI.

## Project Structure

```text
openclaw-skill-explorer/
|- apps/
|  |- api/                 # FastAPI backend, ORM models, services, routes
|  `- web/                 # Next.js frontend pages and UI components
|- scripts/                # Ingestion and local helper scripts
|- docs/                   # Specs, architecture deep dive, interview prep
|- docker-compose.yml      # Local orchestration (api + web)
`- README.md
```
## Local Development

### Environment Setup

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local
```

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

### Health Endpoints

- `GET /health` -> `{ "status": "ok" }`
- `GET /ready` -> `{ "status": "ready" }`

## Docker Usage

```bash
docker compose up --build
```

Default URLs:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`

## Resume / Portfolio Description

- Built a full-stack platform for discovering and evaluating AI-agent skills with searchable metadata, similarity recommendations, and risk visualization.
- Designed a deterministic risk scoring engine that classifies capability exposure (file, network, shell, secrets, app access) into explainable risk levels.
- Implemented ranking-based search and filtering on SQLite without external search infrastructure or vector databases.
- Integrated LLM-assisted README summarization and explanation refinement while preserving deterministic core risk logic.
- Productionized local deployment with Docker Compose, environment-driven config, and health/readiness endpoints.

## Elevator Pitch

OpenClaw Skill Explorer + Risk Scanner helps teams safely adopt AI-agent skills by making capabilities and risks visible before execution. It combines searchable skill discovery with deterministic risk scoring and clear recommendations in a single workflow. Instead of relying on black-box judgments, it provides transparent, explainable analysis that developers can trust and act on quickly. The result is faster evaluation cycles with lower operational risk.

## Interview Talking Points

See [docs/interview.md](docs/interview.md) for:

- a 60-second project explanation
- design decisions and trade-offs
- scaling roadmap and architecture discussion points

## Future Improvements

- Semantic search and hybrid ranking
- Sandboxed skill execution for runtime validation
- Fine-grained permission isolation policies
- Multi-source skill registry federation
- Background job orchestration for ingestion/scan pipelines

## Deployment Notes

- Frontend target: Vercel
- Backend targets: Render / Railway / Fly.io
- SQLite is suitable for MVP/demo environments; migrate to Postgres for larger scale.
