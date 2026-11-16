import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import analytics, db, learn, lint, report, schedule


@pytest.fixture
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(report, "MANUAL", tmp_path / "e7_manual.json")
    with db.connect():
        pass
    return tmp_path


@pytest.mark.parametrize("age,label", [
    (19.3, "24h"), (24, "24h"), (36, "24h"), (36.1, "48h"), (60, "48h"), (60.6, "age_61h"), (100, "age_100h"),
    (160, "7d"), (180, "7d"), (330, "14d"), (725, "30d"), (733, "age_733h"), (5, "age_5h"), (-2.75, "prepublish_3h"), (None, "unknown_age"),
])
def test_window_label(age, label):
    assert analytics.window_label(age) == label


def test_age_hours_uses_published_time():
    assert analytics.age_hours("2026-11-16T17:45:09+0530", "2026-11-15T16:55:51Z") == pytest.approx(19.32, abs=0.01)
    assert analytics.age_hours("2026-11-16T17:45:10+0530", "2026-11-16T15:00:00Z") < 0


def test_windows_from_by_day_needs_coverage():
    pub = date(2026, 11, 1)
    by_day = [{"day": (pub + timedelta(days=k)).isoformat(), "views": 10 * (k + 1), "estimatedMinutesWatched": 1.0, "averageViewPercentage": 50.0} for k in range(3)]
    w = analytics.windows_from_by_day(by_day, pub, age_h=70)
    assert w["24h"]["views"] == 10 and w["48h"]["views"] == 30
    assert "7d" not in w
    assert analytics.windows_from_by_day(by_day, pub, age_h=20)["24h"]["views"] == 10
    assert analytics.windows_from_by_day(by_day, pub, age_h=5) == {}


def add_pub(con, variant, platform="youtube", published="2026-11-01T10:00:00Z", pid=None, slot=None):
    cur = con.execute("INSERT INTO publications (variant_id, platform, platform_id, url, privacy, scheduled_for, published_at, slot, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (variant, platform, pid or variant + platform, None, "public", None, published, slot, None, db.now()))
    return cur.lastrowid


def add_snap(con, pub_id, label, captured, metrics):
    con.execute("INSERT INTO analytics_snapshots (publication_id, label, captured_at, metrics) VALUES (?,?,?,?)", (pub_id, label, captured, json.dumps(metrics)))


def test_relabel_fixes_wrong_24h_labels(tmpdb):
    with db.connect() as con:
        a = add_pub(con, "C0001-en", published="2026-11-15T16:55:51Z")
        b = add_pub(con, "C0002-en", published=None)
        con.execute("UPDATE publications SET scheduled_for='2026-11-16T16:00:00Z' WHERE id=?", (b,))
        add_snap(con, a, "initial", "2026-11-16T08:35:28+0530", {})
        add_snap(con, a, "24h", "2026-11-16T17:45:09+0530", {})
        add_snap(con, b, "24h", "2026-11-16T17:42:02+0530", {})
    changes = {(c["publication_id"], c["old"]): c["new"] for c in analytics.relabel()}
    assert changes[(a, "initial")] == "age_10h"
    assert changes[(a, "24h")] == "24h"
    assert changes[(b, "24h")].startswith("prepublish_")
    with db.connect() as con:
        rows = con.execute("SELECT label, age_h, metrics FROM analytics_snapshots ORDER BY id").fetchall()
    assert rows[0]["age_h"] == pytest.approx(10.16, abs=0.01)
    assert json.loads(rows[2]["metrics"])["label_history"][0]["label"] == "24h"


def test_due_labels_only_near_windows(tmpdb):
    now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc)
    with db.connect() as con:
        add_pub(con, "C0001-en", published=(now - timedelta(hours=30)).isoformat())
        add_pub(con, "C0002-en", published=(now - timedelta(hours=5)).isoformat())
        p3 = add_pub(con, "C0003-en", published=(now - timedelta(hours=100)).isoformat())
        con.execute("UPDATE analytics_snapshots SET label=label")
        todo = {p["variant_id"]: lab for p, lab, _ in analytics.due(con, now=now)}
    assert todo["C0001-en"] == "24h"
    assert "C0002-en" not in todo
    assert todo["C0003-en"] == "age_100h"


def rows(lang, values, start_ep=1, slot=None):
    return [{"variant": f"C{start_ep + k:04d}-{lang}", "language": lang, "platform": "youtube", "episode": start_ep + k, "views": v, "slot": slot, "source": "test"} for k, v in enumerate(values)]


def test_rolling_ratio_is_within_language():
    rs = learn.rolling_ratios(rows("en", [100, 100, 100, 200]) + rows("gu", [1, 1, 1, 2]))
    en = {r["variant"]: r["ratio"] for r in rs if r["language"] == "en"}
    gu = {r["variant"]: r["ratio"] for r in rs if r["language"] == "gu"}
    assert en["C0004-en"] == pytest.approx(2.0) and gu["C0004-gu"] == pytest.approx(2.0)


def test_rolling_ratio_needs_peers():
    rs = learn.rolling_ratios(rows("en", [100, 200, 300]))
    assert all(r["ratio"] is None for r in rs)


PARITY = {"id": 9, "arms": ["A", "B"], "assignment_rule": {"type": "parity", "odd": "A", "even": "B"}, "min_n_per_arm": 6, "variable": "frame0", "metric": "7d views"}


def test_experiment_n_rule_anecdote_below_six():
    vals = [100, 300] * 5
    ev = learn.evaluate(PARITY, rows("en", vals))
    assert ev["languages"]["en"]["n"] == {"A": 5, "B": 5}
    assert ev["languages"]["en"]["tier"] == "anecdote"
    assert "interval" not in ev["languages"]["en"]
    assert ev["overall"] == "anecdote"


def test_experiment_claim_with_six_per_arm_and_bootstrap():
    vals = [100, 300] * 6
    ev = learn.evaluate(PARITY, rows("en", vals))
    r = ev["languages"]["en"]
    assert r["n"] == {"A": 6, "B": 6}
    assert r["interval"]["lo"] > 1.0 and r["tier"] == "claim"
    assert r["interval"]["lo"] <= r["interval"]["effect"] <= r["interval"]["hi"]


def test_experiment_n_rule_is_per_language():
    ev = learn.evaluate(PARITY, rows("en", [100, 300] * 6) + rows("hi", [100, 300] * 3))
    assert ev["languages"]["en"]["tier"] == "claim"
    assert ev["languages"]["hi"]["tier"] == "anecdote"


def test_exp1_is_observational_and_cannot_claim():
    exp = {**learn.EXP1, "id": 1}
    data = rows("en", [100] * 5 + [300] * 8)
    ev = learn.evaluate(exp, data)
    assert ev["languages"]["en"]["n"]["legacy"] == 5
    assert ev["languages"]["en"]["tier"] == "anecdote"
    assert "observational" in learn.EXP1["design"]


def test_one_active_experiment(tmpdb):
    with db.connect() as con:
        a = learn.add(con, {**learn.EXP1, "name": "a"}, start=True)
        with pytest.raises(ValueError):
            learn.add(con, {**learn.EXP1, "name": "b"}, start=True)
        b = learn.add(con, {**learn.EXP1, "name": "b"})
        with pytest.raises(ValueError):
            learn.start(con, b)
        learn.close(con, a, "anecdote")
        learn.start(con, b)
        assert learn.active(con)["id"] == b


def test_schedule_ranks_on_ratio_and_freezes(tmpdb, monkeypatch):
    monkeypatch.setattr(schedule, "language_profile", lambda lang: {"publishing": {"candidate_slots_ist": ["12:30", "20:30"]}})
    data = rows("en", [100, 100, 100], 1, "12:30") + rows("en", [300, 300, 300], 4, "20:30") + rows("hi", [9000] * 6, 1, "12:30")
    rec = schedule.recommend("en", rows=data, experiment=False)
    assert rec["slot"] == "20:30" and "ratio" in rec["reason"]
    frozen = schedule.recommend("en", rows=data, experiment={"id": 1, "variable": "duration"})
    assert frozen["frozen"] and "Frozen" in frozen["reason"]


def empty_data():
    return {"windows": {"youtube": {l: [] for l, _ in analytics.WINDOWS}, "instagram": {l: [] for l, _ in analytics.WINDOWS}},
            "experiments": [{**learn.EXP1, "id": 1, "status": "planned"}], "inventory": {"youtube": {"publications": 0, "snapshots": {}, "last_capture": None}}, "features": 0, "manual": {}}


def test_weekly_report_insufficient_data():
    text = report.weekly_markdown(empty_data(), "2026-11-16")
    assert "insufficient data" in text.lower()
    for head in ("Per-language medians", "Top and bottom", "Experiments", "Cannibalisation", "Account split triggers"):
        assert head in text
    assert "anecdote" in text
    ranking = text.split("## Top and bottom")[1].split("## Experiments")[0]
    assert ranking.count("insufficient data") == 2 and "|" not in ranking


def test_weekly_report_with_data_and_cannibalisation():
    d = empty_data()
    yt = []
    for ep in range(1, 9):
        yt.append({"variant": f"C{ep:04d}-en", "language": "en", "platform": "youtube", "episode": ep, "views": 100, "slot": None, "source": "t"})
        yt.append({"variant": f"C{ep:04d}-gu", "language": "gu", "platform": "youtube", "episode": ep, "views": 100 if ep <= 4 else 10, "slot": None, "source": "t"})
    d["windows"]["youtube"]["7d"] = yt
    text = report.weekly_markdown(d, "2026-11-16")
    assert "C0001-en" in text
    c = report.cannibalisation(yt)
    assert c["status"] == "flag" and c["longest_run"] >= 3
    assert "gu" in text.split("Account split triggers")[1]


def test_lint_accepts_source_objects_and_strings():
    sc = {"narration": "Rama went to the forest today with joy.", "keywords": [], "visual": "v", "pause": 0.18}
    script = {"scenes": [dict(sc) for _ in range(9)], "sources": [{"ref": "VR 1.26.12", "edition": "vulgate"}, "VR 1.24.26 (vulgate)", "https://x.org"]}
    f = lint.lint_script(script, "en", rates={"en": 2.8})["findings"]
    assert not [x for x in f if x["rule"] in ("sources", "edition")]
    script["sources"] = [{"edition": "vulgate"}, "VR 1.2.3"]
    f = lint.lint_script(script, "en", rates={"en": 2.8})["findings"]
    assert any(x["rule"] == "sources" and x["level"] == "fail" for x in f)
    assert any(x["rule"] == "edition" for x in f)


def test_lint_engine_values():
    v = lint.engine_vocab()
    if "error" in v:
        pytest.skip(v["error"])
    sc = {"narration": "Rama went to the forest today with joy.", "keywords": [], "visual": "v", "pause": 0.18}
    script = {"scenes": [dict(sc) for _ in range(9)], "sources": ["VR 1.1.1 (vulgate)"]}
    script["scenes"][1].update(transition="wipe", shot="CU", move={"type": "spin"}, hit="impact", overlay=["embers", "snow"])
    script["scenes"][2].update(music={"leitmotif": "rama"}, sfx=[{"name": "river"}, {"name": "file:x"}, {"name": "dragon"}], image=99)
    msgs = [x["message"] for x in lint.lint_script(script, "en", rates={"en": 2.8})["findings"] if x["rule"] == "engine_values"]
    assert any("transition 'wipe'" in m for m in msgs)
    assert any("move 'spin'" in m for m in msgs)
    assert any("overlay 'snow'" in m for m in msgs)
    assert any("'dragon'" in m for m in msgs)
    assert any("out of range" in m for m in msgs)
    assert not any("'impact'" in m or "'CU'" in m or "'river'" in m or "file:x" in m or "rama" in m for m in msgs)


def test_title_pattern():
    assert lint.title_pattern("श्रीराम का जन्म कैसे हुआ | रामायण भाग 3") == "question"
    assert lint.title_pattern("श्रीराम के 16 गुण | रामायण भाग 2") == "number"
    assert lint.title_pattern("The Demoness Rama Didn't Want to Kill | Ramayana Ep 5") == "statement"


def test_scrub_never_leaks_token():
    msg = analytics.scrub("ConnectTimeout url /v27.0/1/insights?metric=views&access_token=EAAUjbfOvtUoBTMIYyZB Bearer EAAzzz.yy")
    assert "EAAUjbf" not in msg and "EAAzzz" not in msg and "<redacted>" in msg


def test_instagram_permission_error_is_graceful(monkeypatch):
    calls = []

    class IG:
        @staticmethod
        def graph(cfg):
            return "https://graph.facebook.com/v27.0"

    def fake_get(url, params, token, timeout=25):
        calls.append(url)
        if url.endswith("/insights"):
            return 400, {"error": {"code": 10, "message": "(#10) Application does not have permission for this action"}}
        return 200, {"like_count": 3}

    monkeypatch.setattr(analytics, "ig_get", fake_get)
    out = analytics.fetch_instagram("123", ctx=(IG, {"access_token": "EAAsecret"}))
    assert out["insights"] == {} and "permission_error" in out
    assert len(calls) == 2
    assert "EAAsecret" not in json.dumps(out)
    assert "plays" in out["deprecated_not_requested"] and "plays" not in analytics.IG_METRICS


def test_qa_timeline_windows(tmp_path):
    from pipeline import qa

    script = {"scenes": [{"narration": "a"}, {"narration": "b"}]}
    assert qa.narration_windows(tmp_path, script) is None
    tl = {"scenes": [{"narration_start": 0.15, "narration_end": 2.0}, {"narration_start": 2.4, "narration_end": 5.0}], "hook_end": 2.0, "first_word": 0.15}
    (tmp_path / "timeline.json").write_text(json.dumps(tl))
    assert qa.narration_windows(tmp_path, script) == [(0.15, 1.85), (2.4, pytest.approx(2.6))]
    assert qa.narration_windows(tmp_path, {"scenes": [{"narration": "a"}]}) is None


def test_qa_glyphs_follow_engine_fontset():
    from pipeline import qa
    import chalk

    script = {"engine_version": 2, "scenes": [{"narration": "Rama", "kind": "verse", "devanagari": ["राम"], "source": "VR 1.1.1"}], "thumbnail": {"devanagari": "राम"}}
    if not Path(chalk.OFL["devanagari_serif"]).exists():
        pytest.skip("OFL fonts not installed")
    assert qa.check_glyphs(script)["data"]["fontset"] == "mac"
    assert qa.check_glyphs({**script, "fonts": "ofl"})["data"]["fontset"] == "ofl"
    assert qa.check_glyphs({**script, "engine_version": 1})["data"]["fontset"] == "mac"


def test_heard_json_requires_matching_sha(tmp_path, monkeypatch):
    from pipeline import qa

    wav = tmp_path / "00.wav"
    wav.write_bytes(b"RIFFfake")
    (tmp_path / "00.heard.json").write_text(json.dumps({"wav_sha256": qa.file_sha256(wav), "text": "hello"}))
    assert qa.transcript(wav, "en") == ("hello", "render-time transcript (heard.json)")
    (tmp_path / "00.heard.json").write_text(json.dumps({"wav_sha256": "stale", "text": "old"}))
    monkeypatch.setattr(qa, "CACHE", tmp_path)
    (tmp_path / f"asr-{qa.file_sha256(wav)}-en.json").write_text(json.dumps({"text": "cached"}))
    assert qa.transcript(wav, "en") == ("cached", "QA cache (wav hash)")
