import os
import plistlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import ROOT

AGENTS = Path.home() / "Library" / "LaunchAgents"
LOGS = ROOT / "data" / "logs"
PREFIX = "com.shortsstudio.ig."


def label(variant):
    return PREFIX + variant


def plist_path(variant):
    return AGENTS / f"{label(variant)}.plist"


def domain():
    return f"gui/{os.getuid()}"


def install(content_id, lang, when, dry_run=False):
    variant = f"{content_id}-{lang}"
    local = when.astimezone()
    LOGS.mkdir(parents=True, exist_ok=True)
    AGENTS.mkdir(parents=True, exist_ok=True)
    args = [sys.executable, "-m", "pipeline", "publish", content_id, "--lang", lang, "--platform", "instagram", "--now", "--yes", "--at", when.isoformat()]
    if dry_run:
        args.append("--dry-run")
    spec = {
        "Label": label(variant),
        "ProgramArguments": args,
        "WorkingDirectory": str(ROOT),
        "StartCalendarInterval": {"Month": local.month, "Day": local.day, "Hour": local.hour, "Minute": local.minute},
        "StandardOutPath": str(LOGS / f"ig-{variant}.log"),
        "StandardErrorPath": str(LOGS / f"ig-{variant}.log"),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", "PYTHONUNBUFFERED": "1"},
    }
    remove(variant)
    plist_path(variant).write_bytes(plistlib.dumps(spec))
    subprocess.run(["launchctl", "bootstrap", domain(), str(plist_path(variant))], check=True)
    return plist_path(variant), local


def remove(variant):
    p = plist_path(variant)
    subprocess.run(["launchctl", "bootout", f"{domain()}/{label(variant)}"], capture_output=True)
    if p.exists():
        p.unlink()
        return True
    return False


def jobs():
    out = []
    for p in sorted(AGENTS.glob(PREFIX + "*.plist")):
        spec = plistlib.loads(p.read_bytes())
        c = spec["StartCalendarInterval"]
        out.append({"variant": spec["Label"][len(PREFIX):], "when": f"{c['Month']:02d}-{c['Day']:02d} {c['Hour']:02d}:{c['Minute']:02d}", "dry_run": "--dry-run" in spec["ProgramArguments"], "log": spec["StandardOutPath"]})
    return out


def parse(when):
    return datetime.fromisoformat(when)
