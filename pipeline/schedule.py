import json
from datetime import datetime, timedelta, timezone

from . import PROFILES, db
from .analytics import equal_window_table, median_or_none

MIN_SAMPLES = 3
WINDOW = "48h"
IST = timezone(timedelta(hours=5, minutes=30))


def language_profile(lang):
    path = PROFILES / "languages" / f"{lang}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def last_slot(lang):
    with db.connect() as con:
        r = con.execute("""SELECT p.slot FROM publications p LEFT JOIN variants v ON v.id=p.variant_id
                           WHERE p.platform='youtube' AND COALESCE(v.language, substr(p.variant_id, 7))=? AND p.slot GLOB '[0-9][0-9]:[0-9][0-9]'
                           ORDER BY COALESCE(p.published_at, p.scheduled_for) DESC LIMIT 1""", (lang,)).fetchone()
    return r["slot"] if r else None


def frozen_by():
    from .learn import content_experiment_active

    with db.connect() as con:
        return content_experiment_active(con)


def slot_stats(lang, slots, rows=None):
    from .learn import rolling_ratios

    rows = equal_window_table(WINDOW) if rows is None else rows
    rated = [r for r in rolling_ratios(rows) if r["language"] == lang and r["ratio"] is not None]
    return {s: [r["ratio"] for r in rated if r["slot"] == s] for s in slots}


def next_time(slot, not_before_hours, now):
    now = (now or datetime.now(timezone.utc)).astimezone(IST)
    hh, mm = map(int, slot.split(":"))
    t = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    while t < now + timedelta(hours=not_before_hours):
        t += timedelta(days=1)
    return t


def recommend(lang, not_before_hours=3, now=None, rows=None, experiment=None):
    prof = language_profile(lang)
    slots = prof.get("publishing", {}).get("candidate_slots_ist", ["12:30", "18:30", "20:30"])
    exp = frozen_by() if experiment is None else (experiment or None)
    stats = slot_stats(lang, slots, rows)
    if exp:
        slot = last_slot(lang) or slots[0]
        why = (f"Frozen: content experiment #{exp['id']} ({exp['variable']}) is active, so the slot stays at the last used {slot} IST "
               "to avoid a second changing variable (D4).")
    else:
        under = sorted((len(v), s) for s, v in stats.items() if len(v) < MIN_SAMPLES)
        if under:
            slot = under[0][1]
            why = (f"Exploring: slot {slot} IST has {under[0][0]} of {MIN_SAMPLES} required {WINDOW} outlier-ratio samples for '{lang}'. "
                   "Candidate slots are hypotheses from the language profile until channel data ranks them.")
        else:
            ranked = sorted(slots, key=lambda s: -(median_or_none(stats[s]) or 0))
            slot = ranked[0]
            why = f"Exploiting: best median {WINDOW} outlier ratio (views / '{lang}' rolling median) — " + ", ".join(f"{s}: {median_or_none(stats[s]):.2f}" for s in ranked)
    t = next_time(slot, not_before_hours, now)
    return {"language": lang, "slot": slot, "publish_at": t.isoformat(), "reason": why, "frozen": bool(exp),
            "samples": {s: len(v) for s, v in stats.items()},
            "note": "Ranks on the per-language outlier ratio, never raw views across languages. YouTube's API has no hour-of-day audience data; check YouTube Studio > Analytics > Audience > 'When your viewers are on YouTube' and update candidate_slots_ist in the profile."}
