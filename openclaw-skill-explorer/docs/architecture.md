# OpenClaw Skill Explorer + Risk Scanner - Architecture Deep Dive

## System Design

### High-Level Components

1. **Ingestion Layer (`scripts/`)**
   - Reads curated seed data and source definitions
   - Pulls repository metadata and README content
   - Normalizes raw records into a consistent schema
   - Upserts results into SQLite through service methods

2. **API Layer (`apps/api/app/routes`)**
   - Exposes endpoints for:
     - health/readiness
     - skill catalog listing/detail
     - similarity recommendations
     - scan operations
   - Keeps HTTP concerns isolated from core domain logic

3. **Domain Services (`apps/api/app/services`)**
   - `skill_service`: search/filter/ranking and readme summary support
   - `risk_service`: orchestration for creating and reading risk reports
   - `risk_engine`: deterministic keyword/capability analysis and scoring
   - `recommendation_service`: similarity scoring across skills
   - Optional LLM enhancement services for improved summaries/explanations

4. **Persistence Layer (`apps/api/app/models`, `db`)**
   - SQLAlchemy ORM models map to SQLite tables
   - Core entities: skills, tags, risk reports, sources, scan jobs

5. **Frontend Layer (`apps/web`)**
   - Next.js pages for home, skills list, skill detail, and manual scan
   - API client wrapper in `lib/api.ts`
   - UI components for cards, filters, and risk visualization
   - Demo fallback data for resilient demos

### Data Flow

```text
seed/source input
  -> ingestion + normalization
  -> SQLite (skills/tags/reports)
  -> risk engine evaluation
  -> FastAPI responses
  -> Next.js UI rendering
```

### Service Separation Rationale

- **Routes** remain thin and testable.
- **Services** encapsulate business rules and transformations.
- **Models/DB** remain storage-focused.
- **Frontend** remains API-driven, with graceful fallback for demo reliability.

## Risk Engine Design

### Detection Strategy

The risk engine uses deterministic rule matching over structured and unstructured text:

- manifest snippets
- README text
- normalized metadata fields

It detects capability signals such as:

- file read/write
- network access
- shell execution
- secrets access
- external download
- app access
- unclear documentation markers

### Scoring System

Each detected capability contributes weighted risk points.  
The aggregate score maps to risk tiers:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

This keeps classification:

- explainable
- reproducible
- easy to calibrate over time

### Explainability

Risk reports persist:

- active capability flags
- matched keyword context
- reason list
- recommendations

LLM refinement is additive, not authoritative: deterministic output stays the source of truth.

## Trade-offs

### Why Rule-Based First (vs LLM-Only)

**Chosen:** deterministic rule engine core, optional LLM augmentation.

Benefits:

- reproducible outputs
- low cost and latency
- straightforward debugging
- easier security/compliance review

Cost:

- less semantic nuance than model-only reasoning

### Why SQLite for MVP

**Chosen:** SQLite as embedded storage.

Benefits:

- zero external infra
- fast local iteration
- minimal operational setup

Cost:

- limited write concurrency and horizontal scalability

### Why No Vector DB Initially

**Chosen:** lexical matching + weighted relevance on SQLite.

Benefits:

- lower complexity
- no extra infrastructure
- easier onboarding for contributors

Cost:

- weaker semantic retrieval for ambiguous queries

## Evolution Path

When scaling beyond MVP:

1. Move persistence to Postgres and add indexed search fields.
2. Introduce background jobs for ingestion and report generation.
3. Add caching and query optimization for high-traffic lists.
4. Add semantic retrieval (hybrid lexical + vector) where justified by usage data.
