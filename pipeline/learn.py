import json
import random
import statistics

from . import db
from .analytics import equal_window_table

MIN_N = 6
ROLLING = 10
MIN_PEERS = 3
BOOT = 2000
CONTENT_VARIABLES = ("duration", "frame0", "first_frame", "hook_type", "hook", "pacing", "reveal", "voice", "title", "thumbnail", "cover")
EXP1 = {
    "name": "exp1-duration",
    "hypothesis": "35-55 s engine-v2 episodes earn a higher within-language outlier ratio than the legacy 82-111 s episodes.",
    "variable": "duration",
    "arms": ["legacy", "v2_35_55"],
    "assignment_rule": {"type": "episode_range", "arms": {"legacy": [1, 5], "v2_35_55": [6, None]}},
    "design": "observational before/after: owner decision O1 made every new episode 35-55 s, so arms are not randomised or alternated; legacy C0001-C0005 is the baseline arm. Confounded with series position, channel age and engine v2 visual changes; any result is evidence of association, not causation.",
    "metric": "7d views / language rolling median (leave-one-out, up to 10 nearest episodes, same platform); secondary 48h ratio and averageViewPercentage",
    "min_n_per_arm": MIN_N,
    "stop_rule": "Pre-registered: the legacy arm is fixed at episodes 1-5 (at most 5 variants per language), below the 6-per-arm rule, so this experiment can only ever report 'anecdote' and never a claim. Evaluate descriptively once each language has >= 6 v2_35_55 variants with 7d data; close at 12 v2_35_55 episodes. Never stop or act on a single spike. A causal duration test would need a parity-assigned experiment, which O1 rules out.",
}


def rolling_ratios(rows, window=ROLLING, min_peers=MIN_PEERS):
    out = []
    by = {}
    for r in rows:
        by.setdefault((r["language"], r.get("platform", "youtube")), []).append(r)
    for key, rs in by.items():
        for r in rs:
            peers = [p for p in rs if p is not r and p.get("views") is not None]
            if r.get("episode") is not None:
                peers.sort(key=lambda p: (abs((p.get("episode") or 0) - r["episode"]), p.get("episode") or 0))
            peers = peers[:window]
            med = statistics.median(p["views"] for p in peers) if len(peers) >= min_peers else None
            ratio = (r["views"] / med) if med else None
            out.append({**r, "peers": len(peers), "language_median": med, "ratio": round(ratio, 3) if ratio is not None else None})
    return out


def arm_of(exp, episode):
    rule = exp["assignment_rule"] if isinstance(exp["assignment_rule"], dict) else json.loads(exp["assignment_rule"])
    if episode is None:
        return None
    if rule["type"] == "parity":
        return rule["odd"] if episode % 2 else rule["even"]
    for arm, (lo, hi) in rule["arms"].items():
        if episode >= lo and (hi is None or episode <= hi):
            return arm
    return None


def bootstrap_ratio(a, b, n=BOOT, seed=7, level=0.95):
    if not a or not b:
        return None
    rng = random.Random(seed)
    stats = []
    for _ in range(n):
        ma = statistics.median(rng.choice(a) for _ in a)
        mb = statistics.median(rng.choice(b) for _ in b)
        if ma > 0:
            stats.append(mb / ma)
    if not stats:
        return None
    stats.sort()
    lo, hi = stats[int((1 - level) / 2 * len(stats))], stats[min(len(stats) - 1, int((1 + level) / 2 * len(stats)))]
    point = statistics.median(b) / statistics.median(a) if statistics.median(a) > 0 else None
    return {"effect": round(point, 3) if point else None, "lo": round(lo, 3), "hi": round(hi, 3), "level": level, "resamples": n}


def evaluate(exp, rows, min_n=None):
    min_n = min_n or exp.get("min_n_per_arm") or MIN_N
    arms = exp["arms"] if isinstance(exp["arms"], list) else json.loads(exp["arms"])
    ratios = [r for r in rolling_ratios(rows) if r["ratio"] is not None]
    per_lang = {}
    for r in ratios:
        arm = arm_of(exp, r.get("episode"))
        if arm in arms:
            per_lang.setdefault(r["language"], {a: [] for a in arms})[arm].append(r["ratio"])
    langs = {}
    for lang, by_arm in sorted(per_lang.items()):
        n = {a: len(v) for a, v in by_arm.items()}
        enough = all(x >= min_n for x in n.values())
        res = {"n": n, "median_ratio": {a: round(statistics.median(v), 3) if v else None for a, v in by_arm.items()}}
        if enough and len(arms) == 2:
            res["interval"] = bootstrap_ratio(by_arm[arms[0]], by_arm[arms[1]])
            iv = res["interval"]
            res["tier"] = "claim" if iv and (iv["lo"] > 1 or iv["hi"] < 1) else "no detectable difference"
        else:
            res["tier"] = "anecdote"
            res["why"] = f"needs >= {min_n} variants per arm in this language with ratio data (has {n})"
        langs[lang] = res
    claims = [l for l, r in langs.items() if r["tier"] == "claim"]
    return {"languages": langs, "overall": "anecdote" if not langs or all(r["tier"] == "anecdote" for r in langs.values()) else ("claim in " + ", ".join(claims) if claims else "no detectable difference"), "min_n": min_n}


def metric_window(exp):
    m = exp["metric"] if isinstance(exp, dict) else exp
    for w in ("30d", "14d", "7d", "48h", "24h"):
        if m.strip().startswith(w):
            return w
    return "7d"


def rows_for(window, platform="youtube"):
    return equal_window_table(window, platform)


def add(con, spec, start=False):
    if start and active(con):
        raise ValueError(f"experiment #{active(con)['id']} is already active; close it first (one experiment at a time)")
    cur = con.execute("INSERT INTO experiments (hypothesis, variable, arms, assignment_rule, metric, min_n_per_arm, start, stop_rule, status, result, created_at, updated_at, name, design, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (spec["hypothesis"], spec["variable"], json.dumps(spec["arms"]), json.dumps(spec["assignment_rule"]), spec["metric"], spec.get("min_n_per_arm", MIN_N),
                       db.now() if start else None, spec["stop_rule"], "active" if start else "planned", None, db.now(), db.now(), spec.get("name"), spec.get("design"), spec.get("notes")))
    return cur.lastrowid


def active(con):
    return con.execute("SELECT * FROM experiments WHERE status='active' ORDER BY id LIMIT 1").fetchone()


def start(con, exp_id):
    a = active(con)
    if a and a["id"] != exp_id:
        raise ValueError(f"experiment #{a['id']} is already active; close it first (one experiment at a time)")
    con.execute("UPDATE experiments SET status='active', start=COALESCE(start, ?), updated_at=? WHERE id=?", (db.now(), db.now(), exp_id))


def close(con, exp_id, result):
    con.execute("UPDATE experiments SET status='closed', result=?, updated_at=? WHERE id=?", (result, db.now(), exp_id))


def all_experiments(con):
    return con.execute("SELECT * FROM experiments ORDER BY id").fetchall()


def as_dict(row):
    d = dict(row)
    for k in ("arms", "assignment_rule"):
        try:
            d[k] = json.loads(d[k])
        except (TypeError, ValueError):
            pass
    return d


def content_experiment_active(con):
    a = active(con)
    return as_dict(a) if a and a["variable"] in CONTENT_VARIABLES else None


def ensure_exp1(con):
    row = con.execute("SELECT id FROM experiments WHERE name=?", (EXP1["name"],)).fetchone()
    return row["id"] if row else add(con, EXP1)
