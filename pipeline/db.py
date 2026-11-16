import json
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

COLUMNS = {
    "decisions": {"actor": "TEXT", "channel": "TEXT", "artifact_sha256": "TEXT"},
    "qa_reports": {"mp4_sha256": "TEXT", "scores": "TEXT"},
    "variants": {"cohort": "TEXT"},
    "hooks": {"source_sha256": "TEXT"},
}


def migrate(con):
    for table, cols in COLUMNS.items():
        have = {r[1] for r in con.execute(f"PRAGMA table_info({table})")}
        for col, typ in cols.items():
            if col not in have:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    con.execute("UPDATE variants SET cohort='unreviewed-language' WHERE language IN ('gu','te') AND cohort IS NULL")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


@contextmanager
def connect():
    DATA.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
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


class Run:
    def __init__(self, stage, content_id=None, variant_id=None):
        self.stage, self.content_id, self.variant_id = stage, content_id, variant_id

    def __enter__(self):
        self.t0 = time.time()
        with connect() as con:
            cur = con.execute(
                "INSERT INTO runs (content_id, variant_id, stage, status, started_at) VALUES (?,?,?,?,?)",
                (self.content_id, self.variant_id, self.stage, "running", now()),
            )
            self.id = cur.lastrowid
        return self

    def __exit__(self, exc_type, exc, tb):
        with connect() as con:
            con.execute(
                "UPDATE runs SET status=?, finished_at=?, seconds=?, detail=? WHERE id=?",
                ("failed" if exc else "ok", now(), round(time.time() - self.t0, 1), repr(exc)[:500] if exc else None, self.id),
            )
        return False
