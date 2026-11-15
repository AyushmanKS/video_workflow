import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_caption_groups_hindi_punctuation_and_postpositions():
    import studio

    text = "ये कथा ख़ुद रामायण सुनाती है। वन के एक शांत आश्रम में रहते थे... महर्षि वाल्मीकि।"
    groups = studio.caption_groups(text, 0, 6, 4, None, 24)
    lines = [" ".join(g["words"]) for g in groups]
    assert all(not l.split()[0] in studio.POSTPOSITIONS for l in lines if len(l.split()) > 1)
    assert any(l.endswith("है।") for l in lines)
    assert all(len(l) <= 30 for l in lines)


def test_caption_tokens_attach_dash():
    import studio

    assert studio.caption_tokens("था — अयोध्या") == ["था —", "अयोध्या"]


def test_db_roundtrip(tmp_path, monkeypatch):
    from pipeline import db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    with db.connect() as con:
        cid = db.next_content_id(con)
        db.upsert(con, "contents", {"id": cid, "topic": "t", "status": "idea", "created_at": db.now(), "updated_at": db.now()})
        assert db.next_content_id(con) == "C0002"


def test_schedule_explores_without_data(monkeypatch):
    from pipeline import schedule

    monkeypatch.setattr(schedule, "equal_window_table", lambda label: [])
    rec = schedule.recommend("hi")
    assert rec["slot"] in rec["samples"] and rec["reason"].startswith("Exploring")
    assert "+05:30" in rec["publish_at"]


def test_qa_char_error():
    from pipeline import qa

    assert qa.char_error("नमस्ते दुनिया", "नमस्ते दुनिया")[0] == 0
    assert qa.char_error("hello world", "hello")[0] > 0.3


def test_font_for_all_scripts():
    import chalk

    for word in ["रामायण", "রামায়ণ", "ਰਾਮਾਇਣ", "રામાયણ", "இராமாயணம்", "రామాయణం", "ರಾಮಾಯಣ", "രാമായണം"]:
        assert chalk.font_for(word, 40).getname()[0] != "Chalkduster"


def test_profiles_valid():
    langs = json.loads((ROOT / "profiles" / "voices.json").read_text())
    for code in ["en", "hi", "mr", "bn", "te", "ta", "gu", "kn", "ml", "pa"]:
        p = json.loads((ROOT / "profiles" / "languages" / f"{code}.json").read_text())
        assert Path(p["style_overrides"]["caption_font"]).exists()
        assert code in langs
