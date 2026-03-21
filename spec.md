# OpenClaw Skill Explorer + Risk Scanner

## 1. Project Overview

OpenClaw Skill Explorer + Risk Scanner is a web application for discovering, browsing, evaluating, and configuring OpenClaw skills.

The product solves two user problems:

1. Skill discovery:
   Users do not know which OpenClaw skills exist, what they do, or which ones are relevant.

2. Pre-install safety review:
   Users want to understand what a skill might access or do before adopting it.

This product does NOT execute or install skills automatically in MVP.
It focuses on discovery, metadata aggregation, risk analysis, and config generation.

---

## 2. Goals

### Primary Goals
- Provide a searchable catalog of OpenClaw skills
- Show normalized metadata for each skill
- Generate a structured risk report for each skill
- Generate installation/config guidance
- Make it easy to compare skills by category, recency, and risk

### Non-Goals (MVP)
- No one-click skill installation
- No sandbox execution
- No live runtime monitoring
- No user accounts
- No private registry support
- No browser extension
- No direct integration into the OpenClaw runtime

---

## 3. Users

### User Type A: New OpenClaw users
Needs:
- Understand what skills exist
- Find beginner-friendly skills
- Avoid risky skills by default

### User Type B: Intermediate OpenClaw users
Needs:
- Compare similar skills
- Review install/setup steps
- Understand dependencies and scope

### User Type C: Security-conscious users
Needs:
- Review file/network/exec/data risks
- Understand why a skill is classified as risky
- See minimal-permission recommendations

---

## 4. Core User Stories

### Discovery
- As a user, I want to search for skills by keyword
- As a user, I want to filter skills by category
- As a user, I want to filter by risk level
- As a user, I want to sort by updated date or popularity

### Evaluation
- As a user, I want to open a skill detail page
- As a user, I want to see a short summary of what the skill does
- As a user, I want to see a risk report before using the skill
- As a user, I want to know whether the skill may read files, write files, access secrets, or call external services

### Configuration
- As a user, I want a generated configuration snippet
- As a user, I want dependency/setup notes
- As a user, I want minimal-permission guidance

### Manual Scan
- As a user, I want to paste a README, manifest, or repository URL
- As a user, I want the system to generate a risk report for that input

---

## 5. MVP Features

### Feature 1: Skill Catalog
A list page that shows:
- skill name
- short description
- category
- tags
- source/repo link
- updated time
- risk level
- quick badges (network, file-write, exec, secrets)

### Feature 2: Skill Detail Page
A detail page that shows:
- name
- source URL
- repo URL
- author
- categories/tags
- README summary
- install/config notes
- normalized metadata
- risk report
- recommendations

### Feature 3: Risk Scanner
Inputs:
- repository URL
- raw README text
- raw manifest text

Outputs:
- risk level
- risk score
- detected capabilities
- detected sensitive scopes
- explanation
- recommendations

### Feature 4: Config Generator
Input:
- skill metadata + install hints

Output:
- generated config snippet
- setup instructions
- minimal-permission guidance

### Feature 5: Sync Pipeline
A backend sync process that:
- pulls skill source data
- normalizes metadata
- fetches README
- stores/updates database
- generates/refreshes risk reports

---

## 6. Functional Requirements

### 6.1 Catalog
- Support keyword search
- Support category filter
- Support risk filter
- Support source filter
- Support sorting by:
  - updated_desc
  - stars_desc
  - risk_desc
  - name_asc

### 6.2 Detail Page
- Must render risk summary above the fold
- Must show exact reasons for risk classification
- Must show source provenance
- Must show raw links to source material

### 6.3 Risk Scanner
- Must use rule-based classification for baseline scoring
- May use LLM-generated explanation text
- Must preserve structured machine-readable findings
- Must support rescanning

### 6.4 Sync
- Must be idempotent
- Must avoid duplicate skill entries
- Must preserve historical scan timestamps
- Must support partial updates

### 6.5 Config Generator
- Must produce a deterministic output format
- Must include setup notes
- Must include “review before use” messaging for high-risk skills

---

## 7. Risk Model

### 7.1 Risk Levels
- LOW
- MEDIUM
- HIGH
- CRITICAL

### 7.2 Risk Dimensions

#### A. Data Access Risk
- reads local files
- writes local files
- accesses secrets/env vars
- accesses email/calendar/contacts
- accesses browser/session/user content

#### B. External Communication Risk
- network access
- arbitrary external API calls
- webhook/callback support
- downloads remote content/code

#### C. Execution Risk
- shell/terminal execution
- process spawning
- system command execution
- package installation
- script execution

#### D. Trust/Transparency Risk
- missing documentation
- vague permissions
- unclear ownership/source
- excessive dependency surface
- suspicious install/setup instructions

### 7.3 Example Classification Rules
- Read-only info retrieval + no write/exec -> LOW
- Access to sensitive apps or services, read-only -> MEDIUM
- File write or message sending or system modification -> HIGH
- Shell execution + network + secrets/data access -> CRITICAL

### 7.4 Scoring Strategy
Use a weighted rule engine:
- file_read = +10
- file_write = +25
- secrets_access = +30
- network_access = +15
- shell_exec = +35
- external_download = +20
- unclear_docs = +10

Suggested thresholds:
- 0-19 = LOW
- 20-39 = MEDIUM
- 40-69 = HIGH
- 70+ = CRITICAL

---

## 8. Architecture

### Frontend
- Next.js
- TypeScript
- Tailwind
- shadcn/ui

### Backend
- FastAPI
- SQLAlchemy or sqlmodel
- SQLite for MVP

### Data Flow
1. Source sync job fetches skill source list
2. Fetch README / metadata
3. Normalize into database
4. Run risk engine
5. Save risk report
6. Frontend reads catalog and detail data

---

## 9. API Endpoints

### Public Read APIs
- GET /api/skills
- GET /api/skills/{slug}
- GET /api/categories
- GET /api/tags
- GET /api/search?q=...

### Scan APIs
- POST /api/scan/url
- POST /api/scan/readme
- POST /api/scan/manifest

### Config API
- POST /api/config/generate

### Admin APIs
- POST /api/admin/sync
- POST /api/admin/rescan/{skill_id}
- GET /api/admin/sources

---

## 10. Pages

### Page: Home
- hero search
- featured categories
- recent updates
- high-risk warning note

### Page: Skills Catalog
- search input
- category filter
- risk filter
- sort select
- result cards/table

### Page: Skill Detail
- header summary
- risk card
- metadata
- README summary
- install/config section
- recommendations

### Page: Manual Scan
- input selector (URL / README / manifest)
- textarea/input
- scan result panel

---

## 11. Data Sources

MVP will use a public skill index/repository list as the initial source of truth, then enrich each skill with repository metadata and README content.

Source ingestion strategy:
1. ingest curated skill list
2. extract skill source URLs
3. fetch repository metadata
4. fetch README / metadata files
5. normalize and store

---

## 12. Success Criteria

The MVP is successful if:
- Users can browse and search skills
- Each skill has a basic metadata profile
- Each skill can display a structured risk report
- Users can manually scan input text/URL
- A demo can show clear differentiation between low-risk and high-risk skills

---

## 13. Future Enhancements

- Multi-source registry ingestion
- Similar skill recommendation
- User-saved comparisons
- Risk diff across updates
- Supply-chain dependency analysis
- Optional LLM-generated summaries
- Export risk reports as JSON/PDF