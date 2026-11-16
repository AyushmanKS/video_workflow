import json
import re
import sqlite3
import time
from contextlib import contextmanager

from . import DATA

DB_PATH = DATA / "studio.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS contents (
    id TEXT PRIMARY KEY,
    series TEXT,
    episode INTEGER,
    topic TEXT NOT NULL,
    category TEXT,
    style TEXT,
    status TEXT NOT NULL DEFAULT 'idea',
    folder TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS variants (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES contents(id),
    language TEXT NOT NULL,
    voice TEXT,
    script_path TEXT,
    video_path TEXT,
    thumbnail_path TEXT,
    duration_s REAL,
    status TEXT NOT NULL DEFAULT 'planned',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT,
    query TEXT,
    source TEXT NOT NULL,
    payload TEXT NOT NULL,
    captured_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id TEXT NOT NULL,
    text TEXT NOT NULL,
    scores TEXT,
    selected INTEGER NOT NULL DEFAULT 0,
    reasoning TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT,
    variant_id TEXT,
    stage TEXT NOT NULL,
    decision TEXT NOT NULL,
    reasoning TEXT,
    decided_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT,
    variant_id TEXT,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    seconds REAL,
    detail TEXT
);
CREATE TABLE IF NOT EXISTS qa_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    verdict TEXT NOT NULL,
    report TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    url TEXT,
    privacy TEXT,
    scheduled_for TEXT,
    published_at TEXT,
    slot TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(platform, platform_id)
);
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_id INTEGER NOT NULL REFERENCES publications(id),
    label TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    metrics TEXT NOT NULL,
    UNIQUE(publication_id, label)
);
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT NOT NULL,
    finding TEXT NOT NULL,
    evidence TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    confidence TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS waivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id TEXT NOT NULL,
    check_name TEXT NOT NULL,
    mp4_sha256 TEXT,
    note TEXT NOT NULL,
    actor TEXT NOT NULL,
    channel TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS publish_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT NOT NULL,
    lang TEXT NOT NULL,
    platform TEXT NOT NULL,
    publish_at TEXT,
    priority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,
    next_try_at TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(content_id, lang, platform)
);
CREATE TABLE IF NOT EXISTS features (
    variant_id TEXT PRIMARY KEY,
    content_id TEXT,
    language TEXT,
    episode INTEGER,
    cohort TEXT,
    duration_s REAL,
    duration_source TEXT,
    scenes INTEGER,
    words INTEGER,
    wps REAL,
    hook_type TEXT,
    hook_words INTEGER,
    hook_seconds REAL,
    first_frame TEXT,
    voice TEXT,
    slot_ist TEXT,
    weekday TEXT,
    title_pattern TEXT,
    has_verse INTEGER,
    stage TEXT,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis TEXT NOT NULL,
    variable TEXT NOT NULL,
    arms TEXT NOT NULL,
    assignment_rule TEXT NOT NULL,
    metric TEXT NOT NULL,
    min_n_per_arm INTEGER NOT NULL DEFAULT 6,
    start TEXT,
    stop_rule TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    objective TEXT,
    languages TEXT,
    config TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    t REAL NOT NULL,
    project_id TEXT,
    content_id TEXT,
    variant_id TEXT,
    platform TEXT,
    stage TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT,
    progress REAL,
    message TEXT,
    detail TEXT,
    error_code TEXT,
    error_raw TEXT,
    retry_safe INTEGER,
    log_ref TEXT,
    run_id INTEGER
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS events_t ON events(t);
CREATE INDEX IF NOT EXISTS events_variant ON events(variant_id);
CREATE TABLE IF NOT EXISTS task_state (
    task_key TEXT PRIMARY KEY,
    project_id TEXT,
    content_id TEXT,
    variant_id TEXT,
    stage TEXT NOT NULL,
    platform TEXT,
    stage_order INTEGER,
    status TEXT NOT NULL,
    kind TEXT,
    progress REAL,
    message TEXT,
    error_code TEXT,
    last_event_id TEXT,
    started_at TEXT,
    updated_at TEXT NOT NULL,
    t REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedupe_key TEXT NOT NULL UNIQUE,
    severity TEXT NOT NULL,
    project_id TEXT,
    content_id TEXT,
    variant_id TEXT,
    platform TEXT,
    stage TEXT,
    error_code TEXT,
    last_kind TEXT,
    title TEXT NOT NULL,
    explanation TEXT,
    technical TEXT,
    suggestion TEXT,
    retry_safe INTEGER,
    log_ref TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    last_t REAL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'open',
    resolved_at TEXT,
    resolution TEXT,
    last_event_id TEXT
);
CREATE INDEX IF NOT EXISTS issues_status ON issues(status);
CREATE TABLE IF NOT EXISTS outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    issue_id INTEGER,
    channel TEXT NOT NULL DEFAULT 'telegram',
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    next_try_at TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL,
    sent_at TEXT
);
CREATE INDEX IF NOT EXISTS outbox_status ON outbox(status);
"""

COLUMNS = {
    "decisions": {"actor": "TEXT", "channel": "TEXT", "artifact_sha256": "TEXT"},
    "qa_reports": {"mp4_sha256": "TEXT", "scores": "TEXT"},
    "variants": {"cohort": "TEXT"},
    "hooks": {"source_sha256": "TEXT"},
    "analytics_snapshots": {"age_h": "REAL", "platform": "TEXT", "published_ref": "TEXT"},
    "features": {"engine_version": "INTEGER"},
    "experiments": {"name": "TEXT", "design": "TEXT", "notes": "TEXT"},
    "contents": {"project_id": "TEXT"},
}

PROJECT_SLUGS = {"RAMAYANA — The Epic in Chalk": "ramayana"}


def migrate(con):
    for table, cols in COLUMNS.items():
        have = {r[1] for r in con.execute(f"PRAGMA table_info({table})")}
        for col, typ in cols.items():
            if col not in have:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    con.execute("UPDATE variants SET cohort='unreviewed-language' WHERE language IN ('gu','te') AND cohort IS NULL")
    backfill_projects(con)


def slugify(name):
    head = re.split(r"\s+[—–-]\s+", name.strip())[0]
    return re.sub(r"[^a-z0-9]+", "-", head.lower()).strip("-") or "project"


def backfill_projects(con):
    rows = con.execute("SELECT series, GROUP_CONCAT(DISTINCT v.language) AS langs FROM contents c LEFT JOIN variants v ON v.content_id=c.id "
                       "WHERE c.project_id IS NULL AND c.series IS NOT NULL AND c.series != '' GROUP BY series").fetchall()
    for r in rows:
        slug = PROJECT_SLUGS.get(r["series"]) or slugify(r["series"])
        if not con.execute("SELECT 1 FROM projects WHERE id=?", (slug,)).fetchone():
            langs = sorted(set((r["langs"] or "").split(",")) - {""})
            con.execute("INSERT INTO projects (id, name, description, objective, languages, config, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                        (slug, r["series"], None, None, json.dumps(langs), json.dumps({}), "active", now(), now()))
        con.execute("UPDATE contents SET project_id=? WHERE project_id IS NULL AND series=?", (slug, r["series"]))


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


@contextmanager
def connect():
    DATA.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA + EVENT_SCHEMA)
    migrate(con)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def as_json(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def upsert(con, table, row, key="id"):
    cols = list(row)
    sets = ", ".join(f"{c}=excluded.{c}" for c in cols if c != key)
    con.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)}) "
        f"ON CONFLICT({key}) DO UPDATE SET {sets}",
        [row[c] for c in cols],
    )


def next_content_id(con):
    row = con.execute("SELECT id FROM contents WHERE id LIKE 'C%' ORDER BY id DESC LIMIT 1").fetchone()
    n = int(row["id"][1:5]) + 1 if row else 1
    return f"C{n:04d}"


def log_decision(con, stage, decision, reasoning, decided_by, content_id=None, variant_id=None, actor=None, channel=None, artifact_sha256=None):
    con.execute(
        "INSERT INTO decisions (content_id, variant_id, stage, decision, reasoning, decided_by, created_at, actor, channel, artifact_sha256) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (content_id, variant_id, stage, decision, reasoning, decided_by, now(), actor, channel, as_json(artifact_sha256) if artifact_sha256 is not None else None),
    )


def cohort_for(language):
    return "unreviewed-language" if language in ("gu", "te") else None


def _emit(**kw):
    try:
        from . import events

        return events.emit(**kw)
    except Exception:
        return None


class Run:
    def __init__(self, stage, content_id=None, variant_id=None, emit_done=True):
        self.stage, self.content_id, self.variant_id, self.emit_done = stage, content_id, variant_id, emit_done

    def __enter__(self):
        self.t0 = time.time()
        with connect() as con:
            cur = con.execute(
                "INSERT INTO runs (content_id, variant_id, stage, status, started_at) VALUES (?,?,?,?,?)",
                (self.content_id, self.variant_id, self.stage, "running", now()),
            )
            self.id = cur.lastrowid
        _emit(kind="started", stage=self.stage, content_id=self.content_id, variant_id=self.variant_id, run_id=self.id, message=f"{self.stage} started")
        return self

    def __exit__(self, exc_type, exc, tb):
        secs = round(time.time() - self.t0, 1)
        with connect() as con:
            con.execute(
                "UPDATE runs SET status=?, finished_at=?, seconds=?, detail=? WHERE id=?",
                ("failed" if exc else "ok", now(), secs, repr(exc)[:500] if exc else None, self.id),
            )
        if exc is not None:
            cancelled = isinstance(exc, KeyboardInterrupt)
            _emit(kind="failed", stage=self.stage, content_id=self.content_id, variant_id=self.variant_id, run_id=self.id, status="Cancelled" if cancelled else None,
                  message=f"{self.stage} {'stopped' if cancelled else 'failed'} after {secs:.0f} s", error=f"{type(exc).__name__}: {exc!r}", detail={"seconds": secs})
        else:
            _emit(kind="completed" if self.emit_done else "info", stage=self.stage, content_id=self.content_id, variant_id=self.variant_id, run_id=self.id,
                  status=None if self.emit_done else "Running", message=f"{self.stage} finished in {secs:.0f} s", detail={"seconds": secs})
        return False
