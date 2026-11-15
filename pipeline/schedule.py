import json
from datetime import datetime, timedelta, timezone

from . import PROFILES
from .analytics import equal_window_table, median_or_none

MIN_SAMPLES = 3
IST = timezone(timedelta(hours=5, minutes=30))


def language_profile(lang):
    path = PROFILES / "languages" / f"{lang}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def recommend(lang, not_before_hours=3, now=None):
    prof = language_profile(lang)
    slots = prof.get("publishing", {}).get("candidate_slots_ist", ["12:30", "18:30", "20:30"])
    rows = [r for r in equal_window_table("48h") if r["language"] == lang]
    stats = {s: [r for r in rows if r["slot"] == s] for s in slots}
    under = sorted((len(v), s) for s, v in stats.items() if len(v) < MIN_SAMPLES)
    if under:
        slot = under[0][1]
        why = (f"Exploring: slot {slot} IST has {under[0][0]} of {MIN_SAMPLES} required 48h samples for '{lang}'. "
               "Candidate slots are hypotheses from the language profile until channel data ranks them.")
    else:
        ranked = sorted(slots, key=lambda s: -(median_or_none([r["views"] for r in stats[s]]) or 0))
        slot = ranked[0]
        why = "Exploiting: best median 48h views — " + ", ".join(f"{s}: {median_or_none([r['views'] for r in stats[s]])}" for s in ranked)
    now = (now or datetime.now(timezone.utc)).astimezone(IST)
    hh, mm = map(int, slot.split(":"))
    t = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    while t < now + timedelta(hours=not_before_hours):
        t += timedelta(days=1)
    return {"language": lang, "slot": slot, "publish_at": t.isoformat(), "reason": why,
            "samples": {s: len(v) for s, v in stats.items()},
            "note": "YouTube's API has no hour-of-day audience data; check YouTube Studio > Analytics > Audience > 'When your viewers are on YouTube' and update candidate_slots_ist in the profile."}
