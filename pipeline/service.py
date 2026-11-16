import os
import plistlib
import subprocess
import sys
import time

from . import ROOT
from .igschedule import AGENTS, LOGS, domain

SERVICES = {
    "queue": {"label": "com.shortsstudio.queue", "args": ["publish-queue", "run"], "log": "queue.log", "throttle": 60},
    "bot": {"label": "com.shortsstudio.bot", "args": ["bot", "run"], "log": "bot.log", "throttle": 30},
    "dashboard": {"label": "com.shortsstudio.dashboard", "args": ["dashboard", "run"], "log": "dashboard.log", "throttle": 10},
    "tunnel": {"label": "com.shortsstudio.tunnel", "args": ["dashboard", "tunnel"], "log": "tunnel.log", "throttle": 30},
}
DEFAULT_INSTALL = ("bot", "dashboard", "tunnel")


def python():
    venv = ROOT / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def plist_path(name):
    return AGENTS / f"{SERVICES[name]['label']}.plist"


def spec(name):
    s = SERVICES[name]
    log = str(LOGS / s["log"])
    return {
        "Label": s["label"],
        "ProgramArguments": [python(), "-m", "pipeline"] + s["args"],
        "WorkingDirectory": str(ROOT),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", "PYTHONUNBUFFERED": "1"},
        "KeepAlive": True,
        "RunAtLoad": True,
        "ThrottleInterval": s["throttle"],
        "StandardOutPath": log,
        "StandardErrorPath": log,
    }


def state(name):
    label = SERVICES[name]["label"]
    r = subprocess.run(["launchctl", "print", f"{domain()}/{label}"], capture_output=True, text=True)
    out = {"name": name, "label": label, "plist": plist_path(name).exists(), "loaded": r.returncode == 0, "state": None, "pid": None, "last_exit": None,
           "log": str(LOGS / SERVICES[name]["log"])}
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("state = "):
                out["state"] = line.split("=", 1)[1].strip()
            elif line.startswith("pid = "):
                out["pid"] = int(line.split("=", 1)[1].strip())
            elif line.startswith("last exit code = "):
                out["last_exit"] = line.split("=", 1)[1].strip()
    return out


def bootout(name, wait_s=15):
    subprocess.run(["launchctl", "bootout", f"{domain()}/{SERVICES[name]['label']}"], capture_output=True)
    deadline = time.time() + wait_s
    while time.time() < deadline and state(name)["loaded"]:
        time.sleep(0.5)


def install(names=None, restart=False, log=print):
    names = list(names or DEFAULT_INSTALL)
    LOGS.mkdir(parents=True, exist_ok=True)
    AGENTS.mkdir(parents=True, exist_ok=True)
    for name in names:
        p = plist_path(name)
        st = state(name)
        want = plistlib.dumps(spec(name))
        same = p.exists() and p.read_bytes() == want
        if name == "queue" and st["loaded"] and not restart:
            log(f"{name}: already loaded (pid {st['pid']}); left untouched (pass --restart to rewrite and restart it)")
            continue
        if st["loaded"] and same and not restart:
            log(f"{name}: already installed and loaded (pid {st['pid']})")
            continue
        if st["loaded"]:
            bootout(name)
        if not (name == "queue" and p.exists() and not restart):
            p.write_bytes(want)
        r = subprocess.run(["launchctl", "bootstrap", domain(), str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"{name}: bootstrap failed: {r.stderr.strip()}")
            continue
        log(f"{name}: installed {p} (log {SERVICES[name]['log']})")


def restart(names, log=print):
    for name in names:
        st = state(name)
        if not st["loaded"]:
            log(f"{name}: not loaded; install it first")
            continue
        r = subprocess.run(["launchctl", "kickstart", "-k", f"{domain()}/{SERVICES[name]['label']}"], capture_output=True, text=True)
        log(f"{name}: {'restarted' if r.returncode == 0 else 'restart failed: ' + r.stderr.strip()}")


def remove(names, log=print):
    for name in names:
        p = plist_path(name)
        bootout(name)
        existed = p.exists()
        if existed:
            p.unlink()
        log(f"{name}: {'removed' if existed else 'was not installed'}")


def status(names=None):
    return [state(n) for n in (names or list(SERVICES))]


def fmt(st):
    if not st["plist"] and not st["loaded"]:
        return f"{st['name']:10s} not installed"
    run = f"running pid {st['pid']}" if st["pid"] else (st["state"] or "not loaded")
    return f"{st['name']:10s} {run:22s} last exit {st['last_exit'] or '-':6s} plist {'yes' if st['plist'] else 'MISSING'}  log {os.path.relpath(st['log'], ROOT)}"


def running(name):
    st = state(name)
    return bool(st["pid"])
