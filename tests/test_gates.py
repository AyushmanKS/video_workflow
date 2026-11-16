import argparse
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import __main__ as cli
from pipeline import db, g3hook, gates, lint
from pipeline import queue as pqueue

CID = "C0009"


def scene(text, **kw):
    return {"narration": text, "keywords": [], "visual": f"v-{len(text)}", "pause": 0.18, **kw}


def good_script(lang="en"):
    words = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho".split()
    scenes = [scene("Rama hesitated before the forest.", pause=0.4)]
    for i in range(8):
        scenes.append(scene(" ".join(words[:12]) + f" scene{i}.", pause=0.4 if i in (3,) else 0.18))
    for i, sc in enumerate(scenes):
        sc["visual"] = f"visual {i}"
    return {"title": "t", "language": lang, "sources": ["1.1.1"], "edition": "Critical edition", "scenes": scenes}


@pytest.fixture
def studio(tmp_path, monkeypatch):
    content = tmp_path / "content"
    root = tmp_path
    for mod in (gates, lint, cli):
        monkeypatch.setattr(mod, "CONTENT", content)
    monkeypatch.setattr(gates, "ROOT", root)
    monkeypatch.setattr(cli, "ROOT", root)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(lint, "RATES_PATH", tmp_path / "lint_rates.json")
    monkeypatch.setattr(pqueue, "CONTENT", content)
    monkeypatch.setattr(pqueue, "LOG", tmp_path / "q.log")
    monkeypatch.delenv(gates.OWNER_ENV, raising=False)
    d = content / CID
    m = {"id": CID, "topic": "t", "style": "chalk", "languages": ["en", "hi"], "primary_language": "en", "stages": {}}
    for lang in ("en", "hi"):
        w = d / lang
        w.mkdir(parents=True)
        (w / "script.json").write_text(json.dumps(good_script(lang)))
        (w / f"{CID}-{lang}.mp4").write_bytes(b"video-" + lang.encode())
        (w / "publish.json").write_text(json.dumps({"youtube": {"title": "y"}, "instagram": {"caption": "c"}}))
    (d / "manifest.json").write_text(json.dumps(m))
    with db.connect():
        pass
    return d


def ns(**kw):
    base = {"note": "", "by": "owner", "channel": "chat", "nonce": None, "yes": True, "platform": None, "at": None, "langs": "en"}
    base.update(kw)
    return argparse.Namespace(**base)


def owner(monkeypatch):
    monkeypatch.setenv(gates.OWNER_ENV, CID)


def add_qa(variant, verdict, checks, sha):
    with db.connect() as con:
        con.execute("INSERT INTO qa_reports (variant_id, kind, verdict, report, created_at, mp4_sha256) VALUES (?,?,?,?,?,?)",
                    (variant, "automated", verdict, json.dumps({"checks": checks}), db.now(), sha))


def test_lint_good_script_passes(studio):
    r = lint.lint(CID, ["en"], write=False)["en"]
    assert r["verdict"] in ("pass", "warn"), r["findings"]
    assert r["estimate"]["total"] < 57


def test_lint_rules_fail():
    s = good_script("te")
    s["scenes"][0]["narration"] = "This hook goes on and on and on with far too many words for three seconds."
    s["scenes"][2]["narration"] = "He said 1000 things"
    s["scenes"][3]["narration"] = "Valmiki wrote “the forest was dreadful and dark” in the text."
    s["scenes"][4]["kind"] = "verse"
    s["scenes"][4]["source"] = "Ramayana"
    r = lint.lint_script(s, "te", primary=good_script("en"))
    rules = {f["rule"] for f in r["findings"] if f["level"] == "fail"}
    assert {"hook", "digits", "quote_src", "sources", "visual_parity"} <= rules
    long = good_script("en")
    long["scenes"] = long["scenes"] * 3
    assert any(f["rule"] == "duration" and f["level"] == "fail" for f in lint.lint_script(long, "en")["findings"])


def test_lint_reveal_cap_only_when_used():
    s = good_script("en")
    assert not any(f["rule"] == "reveal" for f in lint.lint_script(s, "en")["findings"])
    s["scenes"][0]["reveal"] = "instant"
    assert any(f["rule"] == "reveal" and f["level"] == "fail" for f in lint.lint_script(s, "en")["findings"])


def test_estimate_uses_letter_rate_when_calibrated():
    s = good_script("en")
    a = lint.estimate(s, "en", {"en": {"wps": 2.8, "lps": None}})
    b = lint.estimate(s, "en", {"en": {"wps": 2.8, "lps": 12.0}})
    assert a["basis"] == "words" and b["basis"] == "letters"


def test_approve_requires_owner_env_for_yes(studio, monkeypatch):
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="script", langs="en"))
    assert "STUDIO_OWNER_APPROVED" in str(e.value)


def test_approve_script_refused_on_lint_fail(studio, monkeypatch):
    owner(monkeypatch)
    s = good_script("en")
    s["scenes"] = s["scenes"] * 3
    (studio / "en" / "script.json").write_text(json.dumps(s))
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="script", langs="en"))
    assert "lint FAIL" in str(e.value)


def test_script_hash_binding(studio, monkeypatch):
    owner(monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="script", langs="en,hi"))
    m = gates.load(CID)
    assert gates.check_script(m, "en") == []
    s = json.loads((studio / "en" / "script.json").read_text())
    s["style_overrides"] = {"caption_size": 80}
    (studio / "en" / "script.json").write_text(json.dumps(s))
    assert gates.check_script(gates.load(CID), "en") == []
    s["scenes"][1]["narration"] += " extra"
    (studio / "en" / "script.json").write_text(json.dumps(s))
    assert gates.check_script(gates.load(CID), "en")


def test_final_requires_qa_pass_or_waivers(studio, monkeypatch):
    owner(monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="script", langs="en"))
    sha = gates.sha256(studio / "en" / f"{CID}-en.mp4")
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="final", langs="en"))
    assert "no QA report" in str(e.value)
    add_qa(f"{CID}-en", "warn", [{"name": "silence", "ok": False, "class": "warn", "issues": ["gap"]}], sha)
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="final", langs="en"))
    assert "unwaived" in str(e.value)
    cli.cmd_waive(argparse.Namespace(id=CID, lang="en", check="silence", note="intended pause", by="owner", channel="chat", yes=True))
    cli.cmd_approve(ns(id=CID, gate="final", langs="en"))
    assert gates.check_final(gates.load(CID), "en") == []
    add_qa(f"{CID}-en", "fail", [{"name": "duration", "ok": False, "class": "reject", "issues": ["long"]}], sha)
    with pytest.raises(SystemExit):
        cli.cmd_approve(ns(id=CID, gate="final", langs="en"))


def test_reject_check_cannot_be_waived(studio, monkeypatch):
    owner(monkeypatch)
    sha = gates.sha256(studio / "en" / f"{CID}-en.mp4")
    add_qa(f"{CID}-en", "fail", [{"name": "duration", "ok": False, "class": "reject", "issues": ["long"]}], sha)
    with pytest.raises(SystemExit) as e:
        cli.cmd_waive(argparse.Namespace(id=CID, lang="en", check="duration", note="x", by="owner", channel="chat", yes=True))
    assert "cannot be waived" in str(e.value)


def test_qa_on_other_file_refused(studio, monkeypatch):
    owner(monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="script", langs="en"))
    add_qa(f"{CID}-en", "pass", [], "0" * 64)
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="final", langs="en"))
    assert "different file" in str(e.value)


def approve_through_final(studio, monkeypatch, langs=("en",)):
    owner(monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="script", langs=",".join(langs)))
    for lang in langs:
        add_qa(f"{CID}-{lang}", "pass", [], gates.sha256(studio / lang / f"{CID}-{lang}.mp4"))
    cli.cmd_approve(ns(id=CID, gate="final", langs=",".join(langs)))


def test_publish_gate_per_platform_time_and_hashes(studio, monkeypatch):
    approve_through_final(studio, monkeypatch)
    yt, ig = "2030-01-01T20:30:00+05:30", "2030-01-02T20:00:00+05:30"
    cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="en", at=yt))
    cli.cmd_approve(ns(id=CID, gate="publish", platform="instagram", langs="en", at=ig))
    m = gates.load(CID)
    assert gates.approved_time(m, "en", "youtube") == yt
    assert gates.approved_time(m, "en", "instagram") == ig
    assert gates.check_publish(m, "en", "youtube", yt) == []
    assert gates.check_publish(m, "en", "youtube", "2030-01-01T21:00:00+05:30")
    assert gates.check_publish(m, "en", "instagram", ig, immediate=True)
    when = datetime.fromisoformat(ig)
    assert gates.check_publish(m, "en", "instagram", ig, immediate=True, now=when) == []
    meta = json.loads((studio / "en" / "publish.json").read_text())
    meta["instagram"]["caption"] = "new caption"
    (studio / "en" / "publish.json").write_text(json.dumps(meta))
    m = gates.load(CID)
    assert gates.check_publish(m, "en", "youtube", yt) == []
    assert any("instagram" in p for p in gates.check_publish(m, "en", "instagram", ig, now=when))
    (studio / "en" / f"{CID}-en.mp4").write_bytes(b"re-rendered")
    probs = gates.check_publish(gates.load(CID), "en", "youtube", yt)
    assert any("changed after G2" in p for p in probs) and any("video differs" in p for p in probs)


def test_publish_now_record(studio, monkeypatch):
    approve_through_final(studio, monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="en", at="now"))
    m = gates.load(CID)
    later = (datetime.now(gates.IST) + timedelta(minutes=15)).isoformat()
    assert gates.check_publish(m, "en", "youtube", later) == []
    assert gates.check_publish(m, "en", "youtube", "2020-01-01T00:00:00+05:30")


def test_reject_blocks(studio, monkeypatch):
    approve_through_final(studio, monkeypatch)
    cli.cmd_reject(argparse.Namespace(id=CID, gate="final", platform=None, langs="en", note="bad frame", by="owner", channel="chat"))
    assert gates.check_final(gates.load(CID), "en")


def test_done_cannot_mark_qa(studio):
    for stage in ("video_qa", "voice_qa", "gate:final"):
        with pytest.raises(SystemExit):
            cli.cmd_done(argparse.Namespace(id=CID, stage=stage, lang="en", note=None))


def test_migration_uses_evidence_only(studio, monkeypatch):
    monkeypatch.setattr(gates, "ig_job_time", lambda v: None)
    m = gates.load(CID)
    m["stages"] = {
        "gate:script": {"status": "approved", "at": "2026-11-16T10:00:00+0530", "note": "ok", "langs": ["en", "hi"]},
        "gate:final": {"status": "approved", "at": "2026-11-16T11:00:00+0530", "note": "ok", "langs": ["en", "hi"]},
        "gate:publish": {"status": "approved", "at": "2026-11-16T12:00:00+0530", "note": "Instagram G3", "langs": ["en", "hi"]},
        "instagram_scheduled:en": {"status": "done", "at": "x", "note": "2026-11-17T20:30:00+05:30"},
    }
    gates.save(m)
    (studio / "en" / "published.json").write_text(json.dumps([{"platform": "youtube", "id": "abc", "scheduled_for": "2026-11-16T16:00:00Z"}]))
    with db.connect() as con:
        rep = gates.migrate(gates.load(CID), con)
    m = gates.load(CID)
    yt, ig = m["stages"]["gate:publish:youtube"]["entries"], m["stages"]["gate:publish:instagram"]["entries"]
    assert set(yt) == {"en"} and set(ig) == {"en"}
    assert yt["en"]["time"] == "2026-11-16T21:30:00+05:30" and ig["en"]["time"] == "2026-11-17T20:30:00+05:30"
    assert yt["en"]["migrated_from_legacy"] and yt["en"]["video_sha256"] == gates.sha256(studio / "en" / f"{CID}-en.mp4")
    assert m["stages"]["gate:publish"]["migrated"] and m["stages"]["gate:publish"]["langs"] == ["en", "hi"]
    assert "hi/youtube: no evidence" in rep["skipped"]
    assert m["stages"]["gate:final"]["entries"]["hi"]["sha256"] == gates.sha256(studio / "hi" / f"{CID}-hi.mp4")
    assert gates.check_publish(m, "en", "instagram", "2026-11-17T20:30:00+05:30", immediate=True, now=datetime.fromisoformat("2026-11-17T20:30:00+05:30")) == []
    with db.connect() as con:
        again = gates.migrate(gates.load(CID), con)
    assert not again["youtube"] and not again["instagram"]


def test_legacy_out_file_blocked_without_migration(studio, monkeypatch):
    approve_through_final(studio, monkeypatch)
    m = gates.load(CID)
    monkeypatch.setattr(gates, "variant_files", lambda m, lang: {**{"work": studio / lang, "video": studio / lang / f"{CID}-{lang}.mp4", "meta": studio / lang / "publish.json", "thumb": studio / lang / "t.png", "script": studio / lang / "script.json"}, "legacy": True})
    with pytest.raises(SystemExit) as e:
        cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="en", at="2030-01-01T20:30:00+05:30"))
    assert "legacy" in str(e.value)


def test_queue_respects_cap_and_time(studio, monkeypatch):
    approve_through_final(studio, monkeypatch, ("en", "hi"))
    cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="en", at="2030-01-01T20:30:00+05:30"))
    cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="hi", at="2020-01-01T20:30:00+05:30"))
    with db.connect() as con:
        pqueue.add(con, CID, ["en", "hi"])
        d = {f"{r['content_id']}-{r['lang']}": (a, when) for r, a, why, when in pqueue.plan(con, cap=5)}
        assert d[f"{CID}-en"] == ("upload", "2030-01-01T20:30:00+05:30")
        assert d[f"{CID}-hi"][0] == "blocked"
        assert {a for r, a, w, t in pqueue.plan(con, cap=0)} <= {"capped", "blocked"}


def test_hook_blocks_and_allows(studio, monkeypatch):
    env = {}
    assert g3hook.check_command("python -m pipeline approve C0009 final --langs en --yes", env)
    assert not g3hook.check_command("python -m pipeline approve C0009 final --langs en --yes", {gates.OWNER_ENV: CID})
    assert g3hook.check_command("python -m pipeline waive C0009 --lang en --check x --note y", env)
    assert g3hook.check_command("zsh data/upload_queue.sh", env)
    assert g3hook.check_command("python3 publish.py youtube a.mp4 --meta m.json", env)
    assert not g3hook.check_command("grep -n publish.py README.md", env)
    assert not g3hook.check_command("python -m pipeline status", env)
    assert g3hook.check_command("echo ok && python -m pipeline publish C0009 --lang en --yes", env)
    approve_through_final(studio, monkeypatch)
    cli.cmd_approve(ns(id=CID, gate="publish", platform="youtube", langs="en", at="2030-01-01T20:30:00+05:30"))
    assert not g3hook.check_command("python -m pipeline publish C0009 --lang en --yes", env)
    assert g3hook.check_command("python -m pipeline publish C0009 --lang en --at 2030-01-01T21:30:00+05:30 --yes", env)


def test_hook_main_fails_closed(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not json"))
    with pytest.raises(SystemExit) as e:
        g3hook.main()
    assert e.value.code == 2
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})))
    with pytest.raises(SystemExit) as e:
        g3hook.main()
    assert e.value.code == 0


def test_settings_hook_schema():
    s = json.loads((ROOT / ".claude" / "settings.json").read_text())
    if "hooks" not in s:
        pytest.skip("owner removed the approval hook on 2026-11-16 (approvals are recorded from chat)")
    h = s["hooks"]["PreToolUse"][0]
    assert h["matcher"] == "Bash"
    assert h["hooks"][0]["type"] == "command" and h["hooks"][0]["onFailure"] == "block"
    assert "pipeline.g3hook" in h["hooks"][0]["command"]


def test_qa_scoring_and_verdict():
    from pipeline import qa

    checks = [qa.chk("a", "final", "reject", True), qa.chk("b", "final", "warn", False, ["x"]), qa.chk("c", "audio", "reject", False, ["y"]), qa.chk("d", "visual", "warn", True, skipped=True)]
    fam = qa.score(checks)
    assert fam["final"]["score"] == 67 and not fam["final"]["pass"]
    assert fam["audio"]["rejects"] == ["c"] and "visual" not in fam
    assert qa.verdict_of(checks, fam) == "fail"
    assert qa.verdict_of(checks[:2], qa.score(checks[:2])) == "warn"
    assert qa.duration_checks(60.0)[0]["ok"] is False and qa.duration_checks(59.9)[0]["ok"] is True
    assert qa.duration_checks(45)[1]["ok"] and not qa.duration_checks(30)[1]["ok"]


def test_glyph_coverage_detects_missing():
    from pipeline import qa

    s = {"scenes": [{"narration": "hello रामायण"}], "style_overrides": {"caption_font": "/System/Library/Fonts/Supplemental/Chalkduster.ttf", "caption_font_index": 0}}
    c = qa.check_glyphs(s)
    assert not c["ok"] and "U+0930" in c["issues"][0]
