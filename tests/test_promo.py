import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import db, gates, mediakit, promo

CID = "C0099"
LANGS = ("en", "hi", "gu", "te", "mr")
IG_URL = "https://www.instagram.com/aks.chalk.tales/"
EMAIL = "ayushman.k.singh@gmail.com"

SAMPLE = {
    "en": ("The weapons bowed to Rama.\n\n💬 Why did Rama ask how to call them back? Tell me in the comments.\n\nSource: VR 1.28\n\n#Ramayana #ShriRam #Shorts",
           "Shri Ram's weapons bowed\n\nStory line.\nSend this to someone. Save it.\n\n#ramayana #valmiki #shriram"),
    "hi": ("दिव्य अस्त्र झुके।\n\n💬 राम ने अस्त्र लौटाने की विद्या क्यों माँगी?\n\nDivya astra | Brahmastra\n\n#रामायण #श्रीराम #Shorts",
           "जब दिव्य अस्त्र झुके\n\nकथा।\nउन्हें भेजिए।\n\n#रामायण #वाल्मीकि #ramayan"),
    "gu": ("દિવ્ય અસ્ત્રો.\n\n💬 તમને શું લાગે છે?\n\n#રામાયણ #Shorts", "દિવ્ય અસ્ત્રો\n\nવાર્તા.\n\n#રામાયણ #ramayan"),
    "te": ("దివ్యాస్త్రాలు.\n\n💬 మీరేమనుకుంటున్నారు?\n\n#రామాయణం #Shorts", "దివ్యాస్త్రాలు\n\nకథ.\n\n#రామాయణం #ramayan"),
    "mr": ("दिव्य अस्त्रे.\n\n💬 तुम्हाला काय वाटते?\n\n#रामायण #Shorts", "दिव्य अस्त्रे\n\nगोष्ट.\n\n#रामायण #marathi"),
}


def meta(lang, pinned=None):
    d, c = SAMPLE[lang]
    yt = {"title": "t", "description": d, "language": lang, "synthetic": True}
    if pinned:
        yt["pinned_comment"] = pinned
    return {"youtube": yt, "instagram": {"caption": c, "is_ai_generated": True}}


@pytest.fixture
def brand():
    return promo.load("ramayana")


@pytest.fixture
def studio(tmp_path, monkeypatch):
    content = tmp_path / "content"
    for mod in (gates, promo):
        monkeypatch.setattr(mod, "CONTENT", content)
    monkeypatch.setattr(gates, "ROOT", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    d = content / CID
    for lang in LANGS:
        (d / lang).mkdir(parents=True)
        (d / lang / "publish.json").write_text(json.dumps(meta(lang), indent=2, ensure_ascii=False) + "\n")
    m = {"id": CID, "series": "RAMAYANA — The Epic in Chalk", "languages": list(LANGS), "primary_language": "en", "stages": {}}
    (d / "manifest.json").write_text(json.dumps(m))
    return d


@pytest.mark.parametrize("lang", LANGS)
def test_youtube_promo_per_language(brand, lang):
    new, problems = promo.plan(meta(lang), brand, lang)
    c = promo.cta(brand, lang)
    desc = new["youtube"]["description"].split("\n")
    assert not problems
    assert c["youtube_description_line"] in desc and c["collab_line"] in desc
    assert IG_URL in c["youtube_description_line"] and EMAIL in c["collab_line"]
    assert desc[-1].startswith("#")
    assert desc.index(c["collab_line"]) == desc.index(c["youtube_description_line"]) + 1
    assert "@aks.chalk.tales" in new["youtube"]["pinned_comment"]
    assert new["youtube"]["pinned_comment"].split("\n")[0] == promo.question_from(SAMPLE[lang][0])


@pytest.mark.parametrize("lang", LANGS)
def test_instagram_promo_per_language(brand, lang):
    new, problems = promo.plan(meta(lang), brand, lang)
    line = promo.cta(brand, lang)["instagram_caption_line"]
    lines = new["instagram"]["caption"].split("\n")
    assert not problems
    assert lines.count(line) == 1
    i = lines.index(line)
    assert lines[i + 1] == "" and lines[i + 2].startswith("#")
    assert "http" not in line and "YouTube" in line
    assert len(promo.hashtags(new["instagram"]["caption"])) == len(promo.hashtags(SAMPLE[lang][1]))


def test_cta_strings_short_and_marked(brand):
    for lang in LANGS:
        c = promo.cta(brand, lang)
        for k in ("youtube_description_line", "youtube_pinned_comment", "instagram_caption_line", "collab_line"):
            assert len(c[k]) <= 90, (lang, k)
        assert (c["review"] == "needs native review") == (lang in ("gu", "te", "mr"))
    assert brand["email"] == EMAIL
    assert brand["instagram"]["url"] == IG_URL
    assert brand["youtube"]["active_url"] == brand["youtube"]["current_url"] == "https://www.youtube.com/@knowledgepowerbank"


@pytest.mark.parametrize("lang", LANGS)
def test_idempotent(brand, lang):
    once, _ = promo.plan(meta(lang, pinned="Ep 7 next 👇"), brand, lang)
    twice, _ = promo.plan(once, brand, lang)
    assert once == twice
    assert once["youtube"]["description"].count(IG_URL) == 1
    assert once["youtube"]["description"].count(EMAIL) == 1
    assert once["youtube"]["pinned_comment"].count("@aks.chalk.tales") == 1
    assert once["youtube"]["pinned_comment"].startswith("Ep 7 next 👇")


def test_switching_language_replaces_not_duplicates(brand):
    en, _ = promo.plan(meta("en"), brand, "en")
    hi, _ = promo.plan(en, brand, "hi")
    assert hi["youtube"]["description"].count(IG_URL) == 1
    assert promo.cta(brand, "hi")["youtube_description_line"] in hi["youtube"]["description"]
    assert promo.cta(brand, "en")["instagram_caption_line"] not in hi["instagram"]["caption"]


def test_caption_without_hashtags_appends(brand):
    m = meta("en")
    m["instagram"]["caption"] = "Just a story."
    new, _ = promo.plan(m, brand, "en")
    assert new["instagram"]["caption"].endswith(promo.cta(brand, "en")["instagram_caption_line"])


def test_limits_respected(brand):
    m = meta("en")
    m["instagram"]["caption"] = "x" * 2180 + "\n\n#a #b #c #d #e #f"
    m["youtube"]["description"] = "y" * 4990
    _, problems = promo.plan(m, brand, "en")
    assert any("2200" in p for p in problems)
    assert any("hashtags" in p for p in problems)
    assert any("5000" in p for p in problems)


def test_apply_writes_and_is_idempotent(studio):
    res = promo.run(CID, ["en", "hi"], apply=True, out=lambda *_: None)
    assert all(r["written"] for r in res)
    first = (studio / "en" / "publish.json").read_text()
    res2 = promo.run(CID, ["en", "hi"], apply=True, out=lambda *_: None)
    assert not any(r["written"] or r["changed"] for r in res2)
    assert (studio / "en" / "publish.json").read_text() == first
    assert first.endswith("\n")


def test_dry_run_writes_nothing(studio):
    before = (studio / "gu" / "publish.json").read_text()
    res = promo.run(CID, ["gu"], apply=False, out=lambda *_: None)
    assert res[0]["changed"] == ["youtube", "instagram"]
    assert (studio / "gu" / "publish.json").read_text() == before


def approve_g3(studio, lang, platform):
    mp = studio / "manifest.json"
    m = json.loads(mp.read_text())
    m["stages"][gates.publish_key(platform)] = {"status": "approved", "entries": {lang: {"status": "approved", "time": "2026-11-30T20:00:00+05:30", "meta_sha256": "x"}}}
    mp.write_text(json.dumps(m))


def test_refuses_g3_approved_section(studio):
    approve_g3(studio, "en", "youtube")
    before = json.loads((studio / "en" / "publish.json").read_text())
    res = promo.run(CID, ["en"], apply=True, out=lambda *_: None)[0]
    after = json.loads((studio / "en" / "publish.json").read_text())
    assert any(r.startswith("youtube") for r in res["refused"])
    assert after["youtube"] == before["youtube"]
    assert after["instagram"] != before["instagram"]


def test_force_reapproval_needed(studio):
    approve_g3(studio, "hi", "instagram")
    lines = []
    res = promo.run(CID, ["hi"], platforms=("instagram",), apply=True, force=True, out=lines.append)[0]
    assert res["written"] and res["reapproval"] == ["instagram"]
    assert any("OWNER MUST RE-APPROVE G3" in l for l in lines)


def test_refuses_published_even_with_force(studio):
    (studio / "te" / "published.json").write_text(json.dumps([{"platform": "youtube", "id": "abc"}]))
    res = promo.run(CID, ["te"], platforms=("youtube",), apply=True, force=True, out=lambda *_: None)[0]
    assert not res["written"]
    assert "already uploaded" in res["refused"][0]


def test_missing_warns_until_applied(brand):
    m = meta("en")
    assert promo.missing(m, "youtube", "en", brand)
    assert promo.missing(m, "instagram", "en", brand)
    new, _ = promo.plan(m, brand, "en")
    assert promo.missing(new, "youtube", "en", brand) == []
    assert promo.missing(new, "instagram", "en", brand) == []


def test_project_override(tmp_path):
    raw = promo.raw_config()
    raw["projects"]["other"] = {"series": ["X"], "overrides": {"cta": {"en": {"collab_line": "Work with us: {email}"}}}}
    p = tmp_path / "brand.json"
    p.write_text(json.dumps(raw, ensure_ascii=False))
    assert promo.project_for({"series": "X"}, p) == "other"
    b = promo.load("other", p)
    assert promo.cta(b, "en")["collab_line"] == f"Work with us: {EMAIL}"
    assert promo.cta(b, "en")["instagram_caption_line"] == promo.cta(promo.load(), "en")["instagram_caption_line"]


def test_mediakit_empty_data_not_yet_available(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    with db.connect() as con:
        v = mediakit.build(con, live=False, today="2026-01-01")
    for k in ("ig_followers", "ig_avg_views", "ig_engagement", "yt_subscribers", "yt_avg_views", "yt_engagement", "best", "demographics", "yt_countries", "data_through"):
        assert v[k] == mediakit.NA, k
    path = mediakit.write(v, tmp_path)
    text = path.read_text()
    assert "{{" not in text and "not yet available" in text
    assert EMAIL in text


def test_mediakit_uses_only_real_snapshots(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    with db.connect() as con:
        con.execute("INSERT INTO publications (variant_id, platform, platform_id, url, published_at, created_at) VALUES ('C1-en','instagram','m1','u1','2026-01-01T00:00:00Z','x')")
        pid = con.execute("SELECT id FROM publications").fetchone()[0]
        con.execute("INSERT INTO analytics_snapshots (publication_id, label, captured_at, metrics, platform) VALUES (?,?,?,?,?)",
                    (pid, "24h", "2026-01-02T00:00:00+0530", json.dumps({"insights": {"views": 200, "reach": 150, "likes": 10, "comments": 2, "shares": 4, "saved": 4}}), "instagram"))
        v = mediakit.build(con, live=False, today="2026-01-03")
    assert v["ig_avg_views"] == "200"
    assert v["ig_engagement"] == "10.0%"
    assert v["yt_avg_views"] == mediakit.NA
    assert v["ig_followers"] == mediakit.NA
