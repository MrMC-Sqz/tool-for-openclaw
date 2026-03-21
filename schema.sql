PRAGMA foreign_keys = ON;

-- =========================
-- sources
-- =========================
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,                   -- curated_list, registry, github_repo, manual
    base_url TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    sync_status TEXT NOT NULL DEFAULT 'idle', -- idle, running, success, failed
    last_synced_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- skills
-- =========================
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    source_url TEXT,
    repo_url TEXT,
    repo_owner TEXT,
    repo_name TEXT,
    author TEXT,
    description TEXT,
    readme_summary TEXT,
    category TEXT,
    stars INTEGER NOT NULL DEFAULT 0,
    last_repo_updated_at TEXT,
    install_method TEXT,
    raw_manifest TEXT,
    raw_readme TEXT,
    normalized_text TEXT,
    is_featured INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_slug ON skills(slug);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_stars ON skills(stars);
CREATE INDEX IF NOT EXISTS idx_skills_last_repo_updated_at ON skills(last_repo_updated_at);

-- =========================
-- tags
-- =========================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_tags (
    skill_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_tags_skill_id ON skill_tags(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_tags_tag_id ON skill_tags(tag_id);

-- =========================
-- risk_reports
-- =========================
CREATE TABLE IF NOT EXISTS risk_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER,
    input_type TEXT NOT NULL,            -- skill, url, readme, manifest
    risk_level TEXT NOT NULL,            -- LOW, MEDIUM, HIGH, CRITICAL
    risk_score INTEGER NOT NULL DEFAULT 0,

    file_read INTEGER NOT NULL DEFAULT 0,
    file_write INTEGER NOT NULL DEFAULT 0,
    network_access INTEGER NOT NULL DEFAULT 0,
    shell_exec INTEGER NOT NULL DEFAULT 0,
    secrets_access INTEGER NOT NULL DEFAULT 0,
    external_download INTEGER NOT NULL DEFAULT 0,
    app_access INTEGER NOT NULL DEFAULT 0,
    unclear_docs INTEGER NOT NULL DEFAULT 0,

    permissions_detected TEXT,           -- JSON string
    sensitive_scopes TEXT,               -- JSON string
    findings_json TEXT,                  -- JSON string
    explanation TEXT,
    recommendations TEXT,                -- JSON string

    scanned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_risk_reports_skill_id ON risk_reports(skill_id);
CREATE INDEX IF NOT EXISTS idx_risk_reports_risk_level ON risk_reports(risk_level);
CREATE INDEX IF NOT EXISTS idx_risk_reports_scanned_at ON risk_reports(scanned_at);

-- =========================
-- scan_jobs
-- =========================
CREATE TABLE IF NOT EXISTS scan_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',   -- pending, running, success, failed
    input_type TEXT NOT NULL,                 -- skill, url, readme, manifest
    input_value TEXT,
    error_message TEXT,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scan_jobs_skill_id ON scan_jobs(skill_id);
CREATE INDEX IF NOT EXISTS idx_scan_jobs_status ON scan_jobs(status);

-- =========================
-- config_generations
-- =========================
CREATE TABLE IF NOT EXISTS config_generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER,
    generated_config TEXT NOT NULL,
    setup_notes TEXT,
    minimal_permissions TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_config_generations_skill_id ON config_generations(skill_id);

-- =========================
-- optional helpful view
-- =========================
CREATE VIEW IF NOT EXISTS latest_skill_risk AS
SELECT rr.*
FROM risk_reports rr
JOIN (
    SELECT skill_id, MAX(scanned_at) AS max_scanned_at
    FROM risk_reports
    WHERE skill_id IS NOT NULL
    GROUP BY skill_id
) latest
ON rr.skill_id = latest.skill_id
AND rr.scanned_at = latest.max_scanned_at;