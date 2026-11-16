import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import db, insights, report

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(report, "MANUAL", tmp_path / "e7_manual.json")
    monkeypatch.setattr(insights, "CONTENT", tmp_path / "content")
    monkeypatch.setattr(insights, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(insights, "LATEST", tmp_path / "reports" / "latest_insights.json")
    with db.connect():
        pass
    return tmp_path


def add(variant, platform, age_h, metrics, duration=None, episode=None):
    pub = NOW - timedelta(hours=age_h)
    cid, _, lang = variant.partition("-")
    with db.connect() as con:
        row = con.execute("SELECT id FROM publications WHERE variant_id=? AND platform=?", (variant, platform)).fetchone()
        if row:
            pid = row["id"]
        else:
            pid = con.execute("INSERT INTO publications (variant_id, platform, platform_id, published_at, created_at) VALUES (?,?,?,?,?)",
                              (variant, platform, f"{variant}-{platform}", pub.isoformat(), db.now())).lastrowid
        n = con.execute("SELECT COUNT(*) n FROM analytics_snapshots").fetchone()["n"]
        cap = (NOW - timedelta(minutes=10 * (100 - n))).isoformat()
        con.execute("INSERT INTO analytics_snapshots (publication_id, label, captured_at, metrics, age_h, platform) VALUES (?,?,?,?,?,?)",
                    (pid, f"l{n}", cap, json.dumps(metrics), age_h, platform))
        if duration:
            con.execute("INSERT OR REPLACE INTO features (variant_id, content_id, language, episode, duration_s, duration_source, engine_version, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                        (variant, cid, lang, episode or int(cid[1:]), duration, "rendered", 1, db.now()))


def ig(views, reach, likes, shares, saved, avg_ms, comments=0):
    return {"insights": {"views": views, "reach": reach, "likes": likes, "shares": shares, "saved": saved, "comments": comments,
                         "ig_reels_avg_watch_time": avg_ms, "ig_reels_video_view_total_time": avg_ms * views}}


def build():
    return insights.build(now=NOW, probe=None, today="2026-11-20")


@pytest.mark.parametrize("n,age,expected", [(4, 100, "anecdote"), (6, 30, "anecdote"), (6, 48, "directional"), (12, 200, "directional"), (2, 10, "anecdote")])
def test_tier_rules(n, age, expected):
    assert insights.tier(n, age) == expected


def test_confirmed_tier_overrides():
    assert insights.tier(1, 1, confirmed=True) == "confirmed"


def test_bucket():
    assert insights.bucket(3.9) == "<12h"
    assert insights.bucket(21) == "24h"
    assert insights.bucket(50) == "48h"
    assert insights.bucket(170) == "7d"
    assert insights.bucket(-1) is None


def test_ratio_math_instagram(tmpdb):
    add("C0001-en", "instagram", 4, ig(1496, 1231, 39, 2, 7, 20175), duration=74.8)
    d = build()
    r = d["variants"][0]
    assert r["avg_watch_s"] == pytest.approx(20.175, abs=0.01)
    assert r["watch_ratio"] == pytest.approx(20.175 / 74.8, abs=1e-3)
    assert r["ratios"]["shares_per_reach"] == pytest.approx(2 / 1231, abs=1e-4)
    assert r["ratios"]["saves_per_reach"] == pytest.approx(7 / 1231, abs=1e-4)
    assert r["ratios"]["likes_per_reach"] == pytest.approx(39 / 1231, abs=1e-4)
    assert r["snapshot_age_h"] >= 0


def test_youtube_totals_and_counters(tmpdb):
    add("C0001-hi", "youtube", 30, {"public_counters": {"viewCount": 73, "likeCount": 4, "commentCount": 0}, "totals_to_date": []}, duration=94.0)
    add("C0001-en", "youtube", 80, {"totals_to_date": [{"views": 200, "likes": 10, "shares": 4, "comments": 1, "averageViewDuration": 30, "averageViewPercentage": 40.0, "subscribersGained": 2}]}, duration=75.0)
    d = build()
    by = {r["variant"]: r for r in d["variants"]}
    assert by["C0001-hi"]["avg_watch_s"] is None and by["C0001-hi"]["watch_ratio"] is None
    assert by["C0001-hi"]["ratios"]["likes_per_view"] == pytest.approx(4 / 73, abs=1e-4)
    assert by["C0001-en"]["watch_ratio"] == pytest.approx(0.4, abs=1e-3)
    assert by["C0001-en"]["ratios"]["subscribers_gained_per_view"] == pytest.approx(0.01)
    assert by["C0001-en"]["ratios"]["shares_per_view"] == pytest.approx(0.02)
    assert any(f["kind"] == "insufficient" and "watch time" in f["text"] for f in d["findings"])


def test_insufficient_data_when_empty(tmpdb):
    d = build()
    assert d["variants"] == []
    assert d["actions"] == []
    assert any("Insufficient data" in f["text"] for f in d["findings"])
    assert "insufficient data" in d["learnings_for_g1"][0]
    assert "Insufficient data" in insights.markdown(d) or "insufficient data" in insights.markdown(d)


def test_permission_error_snapshots_are_skipped(tmpdb):
    add("C0001-en", "instagram", 3, {"insights": {}, "permission_error": "(#10)"}, duration=74.8)
    assert build()["variants"] == []


def test_four_variant_case_is_anecdote_with_actions(tmpdb):
    add("C0001-en", "instagram", 3.8, ig(1496, 1231, 39, 2, 7, 20175), duration=74.8)
    add("C0001-hi", "instagram", 3.9, ig(1144, 844, 39, 8, 6, 25183), duration=94.0)
    add("C0001-gu", "instagram", 3.9, ig(129, 116, 7, 0, 2, 4779), duration=101.6)
    add("C0001-te", "instagram", 4.0, ig(1322, 1055, 78, 2, 11, 13431), duration=111.2)
    d = build()
    assert {f["tier"] for f in d["findings"]} == {"anecdote"}
    assert 1 <= len(d["actions"]) <= insights.MAX_ACTIONS
    assert all("anecdote" in a["text"] for a in d["actions"])
    fids = {f["id"] for f in d["findings"]}
    assert all(a["finding"] in fids for a in d["actions"])
    assert any("C0001-gu" in f["variants"] and f["kind"] == "outlier" for f in d["findings"])
    assert any("35 s beat shape" in a["text"] for a in d["actions"])
    assert not any("longer than 55" in a["text"] or "60 s" in a["text"] for a in d["actions"])


def test_directional_with_six_mature_variants(tmpdb):
    for i, lang in enumerate(["en", "hi", "en", "hi", "en", "hi"]):
        add(f"C000{i + 1}-{lang}", "instagram", 60, ig(1000, 900, 30, 3, 9, 15000 + 1000 * i), duration=50 + i)
    d = build()
    w = next(f for f in d["findings"] if f["metric"] == "watch_ratio" and f["kind"] == "observation")
    assert w["tier"] == "directional" and w["n"] == 6


def test_no_cross_language_raw_comparison(tmpdb):
    add("C0001-en", "instagram", 4, ig(100000, 90000, 3000, 50, 100, 20000), duration=50)
    add("C0001-gu", "instagram", 4, ig(10, 9, 1, 0, 0, 20000), duration=50)
    d = build()
    for f in d["findings"]:
        if f["metric"] in insights.RAW:
            assert len(f["languages"]) <= 1, f
    for m in d["language_medians"]:
        assert m["median"] is None or m["peers"] >= 3
    for f in d["findings"] + d["actions"]:
        assert "100000" not in f["text"]


def test_language_median_uses_same_language_only(tmpdb):
    for ep in range(1, 6):
        add(f"C000{ep}-en", "instagram", 30, ig(100 * ep, 90 * ep, 3, 1, 1, 10000), duration=50, episode=ep)
    add("C0001-hi", "instagram", 30, ig(99999, 9000, 3, 1, 1, 10000), duration=50)
    d = build()
    en = [m for m in d["language_medians"] if m["language"] == "en" and m["metric"] == "views"]
    assert all(m["median"] is not None and m["median"] < 1000 for m in en)
    hi = [m for m in d["language_medians"] if m["language"] == "hi" and m["metric"] == "views"]
    assert hi and hi[0]["median"] is None


def test_unlike_windows_are_not_mixed(tmpdb):
    add("C0001-en", "instagram", 4, ig(100, 90, 3, 1, 1, 5000), duration=50)
    add("C0002-en", "instagram", 170, ig(5000, 4000, 30, 5, 9, 30000), duration=50)
    d = build()
    for f in d["findings"]:
        if f["bucket"]:
            assert len(f["variants"]) <= 1 or f["bucket"] in ("<12h", "7d")
    assert set(d["groups"]) == {"instagram|<12h", "instagram|7d"}


def test_positive_duration_signal_is_conflict_not_action(tmpdb):
    add("C0001-en", "instagram", 30, ig(100, 90, 3, 1, 1, 10000), duration=40)
    add("C0001-hi", "instagram", 30, ig(100, 90, 3, 1, 1, 20000), duration=50)
    add("C0001-gu", "instagram", 30, ig(100, 90, 3, 1, 1, 40000), duration=60)
    d = build()
    assert any("O1" in c["text"] for c in d["conflicts"])
    assert not any("lower half" in a["text"] for a in d["actions"])


def test_run_writes_files(tmpdb):
    add("C0001-en", "instagram", 4, ig(100, 90, 3, 1, 1, 5000), duration=50)
    path, text, d = insights.run(now=NOW, probe=None)
    assert path.exists() and insights.LATEST.exists()
    j = json.loads(insights.LATEST.read_text())
    assert j["findings"] and "learnings_for_g1" in j
    assert "## Carry-forward actions" in text
