import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import dashboard, dashui, db, episodes, events, notify


@pytest.fixture
def longdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(events, "_ready", set())
    monkeypatch.setattr(events, "_workflows", {})
    monkeypatch.setattr(dashboard, "KEYFILE", tmp_path / "secrets" / "dashboard.json")
    monkeypatch.setattr(dashboard, "URLFILE", tmp_path / "dashboard_url.json")
    monkeypatch.setattr(notify, "CONFIG", tmp_path / "secrets" / "telegram.json")
    content = tmp_path / "content"
    monkeypatch.setattr(episodes, "CONTENT", content)
    events.clear_context()
    with db.connect() as con:
        con.execute("INSERT INTO contents (id, series, episode, topic, category, style, status, folder, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    ("C0099", "RAMAYANA", None, "Bala Kanda Part 1: Valmiki to the divine weapons", "mythology", "chalk", "research", "content/C0099", db.now(), db.now()))
        for lang in ("en", "hi", "te"):
            con.execute("INSERT INTO variants (id, content_id, language, status, created_at, updated_at) VALUES (?,?,?,?,?,?)", (f"C0099-{lang}", "C0099", lang, "planned", db.now(), db.now()))
    m = {"id": "C0099", "languages": ["en", "hi", "te"], "primary_language": "en", "engine_version": 3, "format": "long", "kanda": "Bala Kanda", "part": 1,
         "stages": {"script:en": {"status": "done"}, "script:hi": {"status": "done"}, "script:te": {"status": "done"}}}
    (content / "C0099" / "en").mkdir(parents=True)
    (content / "C0099" / "manifest.json").write_text(json.dumps(m))
    (content / "C0099" / "en" / "script.json").write_text(json.dumps({"chapters": [{"title": "The sage's sorrow", "first_scene": 0}, {"title": "The prince is born", "first_scene": 9}], "scenes": [{"narration": "x"}]}))
    (content / "C0099" / "en" / "lint.json").write_text(json.dumps({"estimate": {"total": 610.0}}))
    (content / "C0099" / "rig.json").write_text(json.dumps({"shots": [{"scene": 1, "puppets": [{}]}, {"scene": 2, "elements": [{}]}, {"scene": 3, "elements": [{}]}]}))
    yield tmp_path
    events.clear_context()


def test_long_video_pages(longdb):
    with db.connect() as con:
        eps = episodes.load(con)
        ep = next(x for x in eps if x["id"] == "C0099")
        assert ep["format"] == "long" and episodes.label_of(ep) == "Bala Kanda · Part 1"
        assert "Puppets" in [s["name"] for s in episodes.combined_steps(ep["langs"])]
        page = dashui.render_long(con)
        assert "Bala Kanda" in page and "Part 1" in page and "Part 2" in page and "Not started" in page
        detail = dashui.render_episode(con, "C0099")
        assert "About this long video" in detail and "10:10" in detail and "The prince is born" in detail
        assert "1 scene with moving characters" in detail and "2 scenes with moving objects only" in detail
        home = dashui.render_home(con)
        assert "YouTube long videos" in home and "1 of 14 parts started" in home
        prog = dashui.render_progress(con, {})
        assert "/long" in prog


def test_shorts_have_no_puppet_step_before_engine_3(longdb):
    m = {"id": "C0098", "languages": ["en"], "engine_version": 2, "stages": {}}
    steps = [k for k, _ in episodes.steps_for(m)]
    assert "puppets" not in steps and "video" in steps
