import json
import os
import re
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")"}
OWNER_ONLY = {"approve", "waive"}


def segments(command):
    lex = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=";&|()")
    lex.whitespace_split = True
    cur, out = [], []
    for tok in lex:
        if tok in SEPARATORS or set(tok) <= set(";&|()"):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        out.append(cur)
    return out


def opt(args, name):
    for i, t in enumerate(args):
        if t == name and i + 1 < len(args):
            return args[i + 1]
        if t.startswith(name + "="):
            return t.split("=", 1)[1]
    return None


def pipeline_call(seg):
    for i, t in enumerate(seg):
        if t == "-m" and i + 1 < len(seg) and seg[i + 1] == "pipeline":
            rest = seg[i + 2:]
            return rest[0] if rest else None, rest[1:]
        if t == "-m" and i + 1 < len(seg) and seg[i + 1].startswith("pipeline."):
            return "module:" + seg[i + 1], seg[i + 2:]
    return None, None


SHELLS = ("sh", "bash", "zsh", "source", ".", "exec", "nohup", "caffeinate")
WRAPPERS = ("env", "nohup", "caffeinate", "exec", "time", "-i", "-m", "-u")


def executes(seg, name, launchers):
    for i, t in enumerate(seg):
        if not t.endswith(name):
            continue
        before = [x for x in seg[:i] if "=" not in x or x.startswith("-")]
        if not before or all(os.path.basename(x) in WRAPPERS or x.startswith("-") for x in before):
            return True
        nonflag = [x for x in before if not x.startswith("-")]
        prev = os.path.basename(nonflag[-1]) if nonflag else ""
        if prev.startswith("python") or prev in launchers:
            return True
    return False


def check_command(command, env=None):
    from . import gates

    env = os.environ if env is None else env
    problems = []
    if re.search(r"\bsqlite3\b.*studio\.db", command) and re.search(r"(?i)\b(insert|update|delete|drop|alter)\b", command) and re.search(r"(?i)decisions|waivers|qa_reports|publish_queue", command):
        problems.append("direct writes to approval/QA tables in data/studio.db are blocked")
    for seg in segments(command):
        joined = " ".join(seg)
        if executes(seg, "upload_queue.sh", SHELLS):
            problems.append("data/upload_queue.sh is retired (it reads the legacy gate); use python -m pipeline publish-queue run")
            continue
        if executes(seg, "publish.py", ()) and "--dry-run" not in seg and "-h" not in seg and "--help" not in seg:
            problems.append("run uploads through python -m pipeline publish, not publish.py directly")
            continue
        sub, args = pipeline_call(seg)
        if not sub:
            if re.search(r"manifest\.json", joined) and re.search(r"(?i)gate:|\"approved\"", joined) and re.search(r"(?:>|tee|write_text|json\.dump|sed -i)", joined):
                problems.append("hand-editing gate records in manifest.json is blocked")
            continue
        if sub in OWNER_ONLY:
            cid = args[0] if args and not args[0].startswith("-") else None
            val = env.get(gates.OWNER_ENV)
            if not val or (cid and val != cid):
                problems.append(f"'pipeline {sub}' is owner-only: the owner must start the session with {gates.OWNER_ENV}={cid or '<ID>'} (or run it in their own terminal)")
            elif sub == "approve" and "publish" in args:
                problems += check_approve_publish(args)
            continue
        if sub == "publish":
            problems += check_publish(args)
        elif sub == "publish-queue" and args and args[0] == "run" and "--dry-run" not in args:
            problems += check_queue()
    return problems


def check_approve_publish(args):
    from . import gates

    cid = args[0]
    if not opt(args, "--platform") or not opt(args, "--langs"):
        return [f"approve {cid} publish needs explicit --platform and --langs"]
    try:
        m = gates.load(cid)
    except FileNotFoundError:
        return [f"unknown content id {cid}"]
    out = []
    for lang in opt(args, "--langs").split(","):
        out += gates.check_final(m, lang)
    return out


def check_publish(args):
    from . import gates

    if not args or args[0].startswith("-"):
        return ["pipeline publish needs a content id"]
    cid, lang = args[0], opt(args, "--lang")
    platform = opt(args, "--platform") or "youtube"
    if "--cancel" in args or "-h" in args or "--help" in args:
        return []
    if not lang:
        return ["pipeline publish needs --lang"]
    try:
        m = gates.load(cid)
    except FileNotFoundError:
        return [f"unknown content id {cid}"]
    at = opt(args, "--at")
    if not at and platform == "youtube":
        t = gates.approved_time(m, lang, platform)
        at = None if t == gates.NOW else t
    immediate = platform == "instagram" and "--now" in args
    if platform == "instagram" and not at:
        t = gates.approved_time(m, lang, platform)
        at = None if t in (None, gates.NOW) else t
    if "--check-gates-only" in args or "--dry-run" in args:
        immediate = False
    return gates.check_publish(m, lang, platform, at, immediate)


def check_queue():
    from . import db, gates

    out = []
    with db.connect() as con:
        rows = [dict(r) for r in con.execute("SELECT content_id, lang, platform, status FROM publish_queue WHERE status IN ('queued','waiting','backoff')")]
    for r in rows:
        m = gates.load(r["content_id"])
        at = gates.approved_time(m, r["lang"], r["platform"])
        if not at:
            continue
        out += gates.check_publish(m, r["lang"], r["platform"], None if at == gates.NOW else at, immediate=at == gates.NOW)
    return out


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if data.get("tool_name") != "Bash":
            sys.exit(0)
        command = (data.get("tool_input") or {}).get("command", "")
        if not re.search(r"pipeline|publish\.py|upload_queue|studio\.db|manifest\.json", command):
            sys.exit(0)
        problems = check_command(command)
    except SystemExit:
        raise
    except Exception as e:
        print(f"G3 hook could not verify this command ({type(e).__name__}: {e}); blocking (fail closed).", file=sys.stderr)
        sys.exit(2)
    if problems:
        print("Blocked by the shorts-studio approval hook:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
