import json
import os
import re
import threading
import time

from . import DATA, db, events, monitor, notify
from .notify import esc

STATE = DATA / "bot_state.json"
LOG = DATA / "logs" / "bot.log"
OFFLINE_NOTICE_S = 600
DRAIN_S = 5
IDLE_S = 60
HELP = ("<b>shorts-studio bot</b> (read-only)\n/status — health and what is running\n/overview — workspace counts\n/issues — open problems\n"
        "/queue — videos in production\n/uploads — YouTube queue, Instagram jobs, recent posts\n/timeline [C0006-hi] — recent events\n"
        "/link — dashboard sign-in link\n/app — setup code for the phone app\n/ack &lt;issue id&gt; — acknowledge an issue\nApprovals stay in the Claude chat.")


def log(msg):
    print(f"{time.strftime('%m-%d %H:%M:%S')} {notify.scrub(msg)}", flush=True)


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st))
    os.replace(tmp, STATE)


def _con():
    from .dashboard import ro_connect

    return ro_connect()


def clip(text, n=4000):
    return text if len(text) <= n else text[:n - 20].rsplit("\n", 1)[0] + "\n…"


def cmd_overview(_args):
    con = _con()
    try:
        return f"<pre>{esc(monitor.fmt_overview(monitor.overview(con)))}</pre>"
    finally:
        con.close()


def cmd_status(_args):
    from . import dashboard

    con = _con()
    try:
        o = monitor.overview(con)
        running = con.execute("SELECT variant_id, content_id, stage, platform, progress, message, t FROM task_state WHERE status='Running' AND t >= ? ORDER BY t DESC LIMIT 8",
                              (time.time() - 6 * 3600,)).fetchall()
    finally:
        con.close()
    lines = ["🟢 <b>Mac online</b> · bot running"]
    info = dashboard.read_url()
    lines.append(f"Dashboard: {'up since ' + esc(dashboard.fmt_ts(info.get('since'))) + ', checked ' + esc(dashboard.fmt_ts(info.get('checked_at'))) if info.get('url') else 'no tunnel address yet'}")
    iss = o["open_issues"]
    lines.append(f"Open issues: {sum(iss.values())}" + (f" ({', '.join(f'{v} {k}' for k, v in iss.items())})" if iss else ""))
    lines.append(f"Waiting for approval: {o['waiting_approval']} · YouTube queue: {o['queued_uploads_youtube']} · Instagram jobs: {o['scheduled_instagram_jobs']}")
    if running:
        lines.append("<b>Running now</b>")
        for r in running:
            prog = f" {r['progress'] * 100:.0f}%" if r["progress"] is not None else ""
            lines.append(f"• {esc(r['variant_id'] or r['content_id'] or '-')} {esc(r['stage'])}{esc(prog)} — {esc(dashboard.scrub(r['message']))}")
    else:
        lines.append("Nothing running.")
    lines.append(f"Last live event: {esc(o['last_live_event'] or 'none')}")
    return "\n".join(lines)


def cmd_issues(_args):
    con = _con()
    try:
        rows = monitor.issues(con, only_open=True)
    finally:
        con.close()
    if not rows:
        return "✅ No open issues."
    icon = {"critical": "🔴", "recoverable": "🟠", "warning": "🟡", "info": "⚪"}
    out = [f"<b>{len(rows)} open issue(s)</b>"]
    for r in rows[:15]:
        who = r["variant_id"] or r["content_id"] or r["project_id"] or "workspace"
        out.append(f"{icon.get(r['severity'], '•')} #{r['id']} {esc(who)} {esc(r['platform'] or '')} — {esc(r['title'])} (×{r['occurrences']}){' · acked' if r['status'] == 'acknowledged' else ''}\n   {esc(r['suggestion'] or '')}")
    out.append("Acknowledge with /ack &lt;id&gt;.")
    return clip("\n".join(out))


def cmd_queue(_args):
    from . import dashboard

    con = _con()
    try:
        vs = dashboard.variants(con)
    finally:
        con.close()
    active = [v for v in vs if v["bucket"] != "completed"]
    if not active:
        return "Nothing in production."
    out = [f"<b>{len(active)} video(s) not yet complete</b> (of {len(vs)})"]
    for v in sorted(active, key=lambda v: -(v["t"] or 0))[:25]:
        out.append(f"• {esc(v['id'])} [{esc(v['bucket'])}] {esc(v['stage'])} — {esc(v['status'])}")
    return clip("\n".join(out))


def cmd_uploads(_args):
    from . import dashboard

    con = _con()
    try:
        q = con.execute("SELECT * FROM publish_queue WHERE status != 'done' ORDER BY priority DESC, id").fetchall()
        pubs = con.execute("SELECT variant_id, platform, scheduled_for, published_at FROM publications ORDER BY id DESC LIMIT 8").fetchall()
        posted = {(r[0], r[1]) for r in con.execute("SELECT variant_id, platform FROM publications")}
    finally:
        con.close()
    out = [f"<b>YouTube queue</b> ({len(q)})"]
    for r in q[:15]:
        out.append(f"• {esc(r['content_id'])}-{esc(r['lang'])} {esc(r['status'])} · at {esc(dashboard.fmt_ts(r['publish_at']))}" + (f" · {esc(dashboard.scrub(r['last_error'])[:80])}" if r["last_error"] else ""))
    jobs = [j for j in dashboard.ig_jobs() if (j["variant"], "instagram") not in posted]
    out.append(f"<b>Instagram jobs</b> ({len(jobs)})")
    for j in jobs[:15]:
        out.append(f"• {esc(j['variant'])} at {esc(j['when'])}{' (dry run)' if j['dry_run'] else ''}")
    out.append("<b>Recent publications</b>")
    for r in pubs:
        out.append(f"• {esc(r['variant_id'])} {esc(r['platform'])} {esc(dashboard.fmt_ts(r['scheduled_for'] or r['published_at']))}")
    return clip("\n".join(out))


def cmd_timeline(args):
    from . import dashboard

    video = args[0] if args else None
    if video and not re.fullmatch(r"C\d{4,}(-[a-z]{2,3})?", video):
        return "Usage: /timeline or /timeline C0006-hi"
    rows = dashboard.query_events(limit=15, video=video)
    if not rows:
        return "No events."
    out = [f"<b>{'History of ' + esc(video) if video else 'Latest events'}</b>"]
    for x in rows:
        prog = f" {x['progress'] * 100:.0f}%" if x["progress"] is not None else ""
        out.append(f"{esc(x['time'])} {esc(x['icon'])} {esc(x['who'])} {esc(x['stage'])}: {esc(x['message'][:140])}{esc(prog)}")
    return clip("\n".join(out))


def cmd_link(_args):
    from . import dashboard

    msg = dashboard.link_message("current address (sent on request)")
    if not msg:
        return "The dashboard tunnel is not up yet. On the Mac: python -m pipeline service status"
    info = dashboard.read_url()
    if info.get("checked_at") and (dashboard.ts_epoch(info["checked_at"]) or 0) < time.time() - 900:
        msg += "\n⚠️ Last successful check was over 15 min ago; the address may have changed."
    return msg


def cmd_app(_args):
    from . import dashboard, linkgist

    if not linkgist.configured():
        return "The phone app is not set up yet: the GitHub gist token is missing on the Mac (secrets/github_gist.json)."
    url = dashboard.read_url().get("url")
    if url and not linkgist.synced(url):
        linkgist.sync(url, log)
    code = linkgist.setup_code(dashboard.keys()["login_key"])
    if not code:
        return "The address gist has not been created yet (the tunnel is not up). Try again in a minute."
    return ("📱 <b>Chalk Dashboard app setup code</b>\nOpen the app once and paste this code. Do not forward it.\n\n"
            f"<code>{esc(code)}</code>")


def cmd_ack(args):
    if not args or not args[0].lstrip("#").isdigit():
        return "Usage: /ack 12"
    iid = int(args[0].lstrip("#"))
    con = events.connect()
    try:
        r = con.execute("SELECT * FROM issues WHERE id=?", (iid,)).fetchone()
        if not r:
            return f"No issue #{iid}."
        if r["status"] != "open":
            return f"Issue #{iid} is already {esc(r['status'])}."
        monitor.resolve_issue(con, iid, "acknowledged via Telegram", "acknowledged")
    finally:
        con.close()
    return f"👍 Issue #{iid} acknowledged: {esc(r['title'])}\nIt stays listed until a later success resolves it."


COMMANDS = {"/status": cmd_status, "/overview": cmd_overview, "/issues": cmd_issues, "/queue": cmd_queue, "/uploads": cmd_uploads, "/timeline": cmd_timeline,
            "/link": cmd_link, "/app": cmd_app, "/ack": cmd_ack}


def dispatch(text):
    parts = (text or "").strip().split()
    if not parts:
        return None
    cmd = parts[0].split("@", 1)[0].lower()
    if cmd in ("/start", "/help"):
        return HELP
    if cmd == "/pair":
        return "Already paired with this chat."
    fn = COMMANDS.get(cmd)
    if not fn:
        return "Unknown command. Send /help."
    try:
        return fn(parts[1:])
    except Exception as ex:
        log(f"{cmd} failed: {type(ex).__name__}: {ex}")
        return f"⚠️ {esc(cmd)} failed on the Mac ({esc(type(ex).__name__)}). See data/logs/bot.log."


def handle(update, cfg):
    if not notify.is_owner(update, cfg):
        msg = update.get("message") or update.get("edited_message") or {}
        log(f"ignored update {update.get('update_id')} from chat {(msg.get('chat') or {}).get('id')} ({(msg.get('chat') or {}).get('type')})")
        return None
    msg = update.get("message") or {}
    return dispatch(msg.get("text"))


class Bot:
    def __init__(self, cfg, api=None):
        self.cfg = cfg
        self.api = api or notify.Telegram(cfg["bot_token"])
        self.state = load_state()
        self.stop = threading.Event()
        self.poller = None
        self.unauthorized = False

    def skip_backlog(self):
        if self.state.get("offset") is not None:
            return
        try:
            last = self.api.call("getUpdates", offset=-1, timeout=0) or []
        except notify.TelegramError as ex:
            log(f"could not read the update backlog: {ex}")
            return
        if last:
            self.state["offset"] = last[-1]["update_id"] + 1
            self.api.call("getUpdates", offset=self.state["offset"], timeout=0)
            log(f"skipped Telegram messages sent before the first start (up to update {last[-1]['update_id']})")
        else:
            self.state["offset"] = 0
        save_state(self.state)

    def poll_loop(self):
        backoff = 5
        self.skip_backlog()
        while not self.stop.is_set():
            try:
                ups = notify.poll(self.api, self.state.get("offset") or None)
                backoff = 5
            except notify.TelegramError as ex:
                if ex.status in (401, 404):
                    log(f"token rejected by Telegram ({ex.status}); stopping poller")
                    self.unauthorized = True
                    self.stop.set()
                    return
                log(f"getUpdates failed: {ex}")
                self.stop.wait(ex.retry_after or backoff)
                backoff = min(backoff * 2, 300)
                continue
            for u in ups:
                self.state["offset"] = u["update_id"] + 1
                save_state(self.state)
                try:
                    reply = handle(u, self.cfg)
                    if reply:
                        self.api.send(self.cfg["owner_chat_id"], reply)
                except notify.TelegramError as ex:
                    log(f"reply failed: {ex}")
                except Exception as ex:
                    log(f"handler error: {type(ex).__name__}: {ex}")

    def announce_start(self):
        prev = self.state.get("beat_t")
        now = time.time()
        if prev is None or now - prev > OFFLINE_NOTICE_S:
            since = time.strftime("%b %d %I:%M %p", time.localtime(prev)) if prev else None
            text = f"💻 <b>Mac online</b> — bot started{'; offline since ' + since + f' ({int((now - prev) / 60)} min)' if since else ' for the first time'}."
            notify.enqueue_local("Mac online", text)
        self.state.update(started_t=now, pid=os.getpid())
        self.beat()

    def beat(self):
        self.state["beat_t"] = time.time()
        save_state(self.state)

    def run(self):
        self.announce_start()
        self.poller = threading.Thread(target=self.poll_loop, daemon=True)
        self.poller.start()
        while not self.stop.is_set():
            try:
                notify.drain(self.api, self.cfg["owner_chat_id"], log=log)
            except Exception as ex:
                log(f"drain error: {type(ex).__name__}: {ex}")
            self.beat()
            if notify.load_config().get("bot_token") != self.cfg.get("bot_token") or notify.load_config().get("owner_chat_id") != self.cfg.get("owner_chat_id"):
                log("telegram config changed; restarting bot loop")
                self.stop.set()
                break
            self.stop.wait(DRAIN_S)


def pair_loop(cfg, api, window):
    offset = None
    while notify.pair_window():
        try:
            ups = notify.poll(api, offset, wait=20)
        except notify.TelegramError as ex:
            log(f"pairing poll failed: {ex}")
            time.sleep(5)
            continue
        for u in ups:
            offset = u["update_id"] + 1
            if notify.try_pair(u, window, cfg):
                api.call("getUpdates", offset=offset, timeout=0)
                api.send(cfg["owner_chat_id"], "✅ Paired. This chat now receives shorts-studio notifications. Send /help for commands.")
                log(f"paired with chat {cfg['owner_chat_id']}")
                return True
    return False


def rotate_log():
    try:
        if LOG.exists() and LOG.stat().st_size > 5 * 1024 * 1024:
            os.replace(LOG, LOG.with_suffix(".log.1"))
    except OSError:
        pass


def run():
    rotate_log()
    log(f"bot starting (pid {os.getpid()})")
    said = None
    while True:
        try:
            cfg = notify.load_config()
            has_token, paired = notify.configured(cfg)
            if not has_token:
                if said != "no-token":
                    log("no Telegram token in secrets/telegram.json; idling (run: python -m pipeline telegram setup)")
                    said = "no-token"
                st = load_state()
                st["idle_t"] = time.time()
                save_state(st)
                time.sleep(IDLE_S)
                continue
            api = notify.Telegram(cfg["bot_token"])
            if not paired:
                w = notify.pair_window()
                if w:
                    log("pairing window open; waiting for /pair <code>")
                    pair_loop(cfg, api, w)
                    continue
                if said != "unpaired":
                    log("token set but not paired; idling (run: python -m pipeline telegram pair)")
                    said = "unpaired"
                time.sleep(15)
                continue
            said = None
            bot = Bot(cfg, api)
            bot.run()
            time.sleep(300 if bot.unauthorized else 5)
        except KeyboardInterrupt:
            log("stopped")
            return
        except Exception as ex:
            log(f"bot loop error: {type(ex).__name__}: {ex}")
            time.sleep(30)
