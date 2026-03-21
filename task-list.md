# OpenClaw Skill Explorer + Risk Scanner - Task List

## Phase 0 - Project Setup

### Task 0.1
Create monorepo/project structure:
- apps/web
- apps/api
- packages/shared
- scripts
- docs

Output:
- folder structure committed

### Task 0.2
Initialize frontend with Next.js + TypeScript + Tailwind

Output:
- frontend app boots locally

### Task 0.3
Initialize backend with FastAPI

Output:
- backend app boots locally
- /health endpoint returns 200

### Task 0.4
Set up shared environment config
- .env.example
- frontend API base URL
- backend DB URL
- optional GitHub token

Output:
- example env files committed

---

## Phase 1 - Database and Models

### Task 1.1
Create SQLite database setup

Output:
- DB connection utility
- migration/init script

### Task 1.2
Create core tables/models:
- sources
- skills
- skill_tags
- risk_reports
- scan_jobs

Output:
- ORM models or SQL schema
- local DB initializes successfully

### Task 1.3
Add seed script for categories and one sample source

Output:
- seed script runnable from CLI

---

## Phase 2 - Source Ingestion

### Task 2.1
Implement source fetcher for curated skill list

Input:
- source URL

Output:
- raw source items list

### Task 2.2
Parse curated source into normalized skill candidates

Normalize:
- name
- source URL
- repo URL
- category
- tags
- short description

Output:
- normalized objects

### Task 2.3
Implement repository metadata fetcher

Fields:
- repo name
- owner
- stars
- updated_at
- default branch
- description

Output:
- metadata fetch utility

### Task 2.4
Implement README fetcher

Output:
- raw README content stored or cached

### Task 2.5
Persist skills into database with upsert logic

Output:
- rerunnable sync without duplicates

### Task 2.6
Create sync CLI command

Command:
- python scripts/sync_sources.py

Output:
- database populated with skill data

---

## Phase 3 - Risk Engine v1

### Task 3.1
Create capability keyword dictionary

Include:
- file read/write
- network access
- shell/exec
- secrets/env vars
- email/calendar/contacts
- browser/session/user data

Output:
- structured keyword config file

### Task 3.2
Implement metadata text aggregation pipeline

Combine:
- description
- tags
- README
- install instructions

Output:
- single text blob for analysis

### Task 3.3
Implement rule-based detector

Detect:
- file_read
- file_write
- network_access
- shell_exec
- secrets_access
- external_download
- unclear_docs

Output:
- structured findings JSON

### Task 3.4
Implement risk score calculator

Output:
- numeric score
- risk level enum

### Task 3.5
Implement recommendation generator

Examples:
- review before install
- avoid granting secrets unnecessarily
- isolate environment for high-risk skills

Output:
- recommendation list

### Task 3.6
Persist risk reports

Output:
- one risk report per skill
- rescans create updated report

---

## Phase 4 - Backend APIs

### Task 4.1
Implement GET /api/skills
Supports:
- q
- category
- risk_level
- sort
- page
- page_size

Output:
- paginated JSON response

### Task 4.2
Implement GET /api/skills/{slug}

Output:
- full detail payload
- latest risk report included

### Task 4.3
Implement GET /api/categories and GET /api/tags

Output:
- filter options for UI

### Task 4.4
Implement POST /api/scan/readme

Input:
- raw text

Output:
- structured risk result

### Task 4.5
Implement POST /api/scan/url

Input:
- repository URL or source URL

Output:
- fetched content + scan result

### Task 4.6
Implement POST /api/config/generate

Input:
- skill_id or raw metadata

Output:
- config snippet
- setup notes
- minimal permission guidance

### Task 4.7
Implement POST /api/admin/sync

Output:
- sync summary
- inserted/updated counts

---

## Phase 5 - Frontend UI

### Task 5.1
Create app layout and navigation

Pages:
- /
- /skills
- /skills/[slug]
- /scan

Output:
- basic navigation working

### Task 5.2
Create home page

Sections:
- hero search
- featured categories
- recent updates
- high-risk note

Output:
- home page complete

### Task 5.3
Create skills catalog page

Features:
- search bar
- category filter
- risk filter
- sort select
- result list

Output:
- catalog page working against API

### Task 5.4
Create skill card component

Must show:
- name
- short description
- tags
- updated date
- risk badge
- capability badges

Output:
- reusable component

### Task 5.5
Create skill detail page

Sections:
- summary
- source metadata
- README summary
- risk report
- recommendations
- config snippet

Output:
- detail page working against API

### Task 5.6
Create risk score card component

Must show:
- risk level
- score
- top reasons
- detected capabilities

Output:
- reusable component

### Task 5.7
Create manual scan page

Inputs:
- URL
- README text
- manifest text

Output:
- scan results rendered in UI

---

## Phase 6 - Config Generator

### Task 6.1
Design config output format

Output:
- deterministic text format
- copy-friendly UI block

### Task 6.2
Implement backend config template builder

Output:
- generated config text

### Task 6.3
Add “minimal permissions” section

Output:
- concise security guidance

---

## Phase 7 - Quality and Testing

### Task 7.1
Add backend unit tests for risk engine

Output:
- tests for low/medium/high/critical cases

### Task 7.2
Add backend API tests

Output:
- skills list/detail/scan endpoints covered

### Task 7.3
Add frontend smoke tests

Output:
- critical pages render successfully

### Task 7.4
Add sample fixture data

Output:
- local demo works without remote sync

---

## Phase 8 - Demo Readiness

### Task 8.1
Add loading, empty, and error states

Output:
- usable UX for all pages

### Task 8.2
Add README with local setup instructions

Output:
- repo is runnable by others

### Task 8.3
Prepare demo data snapshot

Output:
- stable demo dataset committed or exportable

### Task 8.4
Deploy MVP

Suggested:
- frontend on Vercel
- backend on Render/Railway/Fly.io

Output:
- public demo URL

---

## Recommended Build Order

1. Task 0.x
2. Task 1.x
3. Task 2.1 - 2.6
4. Task 3.1 - 3.6
5. Task 4.1 - 4.5
6. Task 5.3 - 5.7
7. Task 6.x
8. Task 7.x
9. Task 8.x

---

## Codex Execution Rule

For each coding request:
- do one task at a time
- provide exact file targets
- provide acceptance criteria
- do not ask Codex to build the whole project in one go

Example request format:

Task:
Implement GET /api/skills with pagination and filters

Files:
- apps/api/app/routes/skills.py
- apps/api/app/services/skill_service.py
- apps/api/app/schemas/skill.py

Requirements:
- support q, category, risk_level, sort, page, page_size
- return latest risk_level for each skill
- use SQLite-compatible SQL
- include total count

Output:
- complete code only