# OpenClaw Skill Explorer + Risk Scanner - Interview Talking Points

## 1) Explain the Project in 60 Seconds

OpenClaw Skill Explorer + Risk Scanner is a full-stack platform for evaluating AI-agent skills before adoption. It ingests skill metadata and documentation, normalizes the data, and applies a deterministic risk engine that flags capabilities like file access, shell execution, network calls, and secrets exposure. The frontend provides searchable discovery, skill detail pages, and clear risk visualization so developers can make safer configuration decisions quickly. LLM features are used as augmentation for summaries and explanation clarity, while deterministic scoring remains the source of truth.

## 2) Key Technical Challenges

### Data Normalization Across Heterogeneous Sources

- **Challenge:** source records vary in completeness and formatting.
- **Approach:** central normalization service with strict field shaping and fallback logic.
- **Outcome:** consistent searchable catalog and predictable downstream analysis.

### Risk Detection Accuracy vs Simplicity

- **Challenge:** avoid under-detection while keeping logic explainable.
- **Approach:** capability-focused keyword/rule sets with weighted scoring and explicit flags.
- **Outcome:** deterministic, auditable risk reports suitable for demos and technical review.

### Balancing Determinism vs AI Assistance

- **Challenge:** LLM-only output can be inconsistent for security-related judgments.
- **Approach:** deterministic engine for classification + LLM only for summary/explanation polish.
- **Outcome:** reproducible core decisions with improved readability for end users.

## 3) Design Decisions

### Why Rule Engine First

- faster to implement and calibrate
- transparent scoring model for reviewers
- stable behavior across repeated runs

### Why LLM Augmentation Later

- improved UX for explanations and summaries
- retains deterministic core logic
- limits model dependency for critical scoring

### Why Simple Search Before Vector Search

- lower complexity and infra cost
- sufficient for curated MVP dataset size
- enabled fast shipping and easier debugging

## 4) Scaling Considerations

### Database Migration

- Move from SQLite to Postgres for concurrent writes, indexing flexibility, and managed backups.

### Background Jobs

- Offload ingestion and risk scans to async workers/queues for throughput and responsiveness.

### Caching

- Cache hot list/detail endpoints and expensive ranking/recommendation results.

### Indexing and Query Optimization

- Add targeted indexes (e.g., category, stars, updated_at, risk_level).
- Consider full-text search and hybrid semantic ranking when query complexity grows.

## 5) Practical Q&A Prompts

### "How did you keep this project interview-safe from a security perspective?"

- deterministic and explainable scoring
- explicit capability flags persisted with reasons
- no hidden model-only decisions for risk classification

### "What would you do first if this got production traffic?"

1. Migrate to Postgres.
2. Add background jobs for sync/scan.
3. Introduce caching and query instrumentation.
4. Add role-based access controls and audit logging.

### "What measurable impact would this have for a team?"

- lower manual review time per skill
- clearer go/no-go decisions for enablement
- better consistency in risk assessment across reviewers
