import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from . import CONTENT, DATA, PROFILES, ROOT

LOG = DATA / "cleanup_log.jsonl"
WARN_GB = 20
CRITICAL_GB = 10
ALWAYS_MODELS = {"Systran/faster-whisper-small", "mobiuslabsgmbh/faster-whisper-large-v3-turbo", "speechbrain/spkrec-ecapa-voxceleb", "ZhengPeng7/BiRefNet", "depth-anything/Depth-Anything-V2-Small-hf"}
VOICE_MODELS = {
    "af_": {"mlx-community/Kokoro-82M-bf16"},
    "maya2:": {"maya-research/maya2-native", "kyutai/moshiko-pytorch-bf16", "mlx-community/snac_24khz", "hubertsiuzdak/snac_24khz"},
    "veena:": {"maya-research/Veena", "mlx-community/orpheus-3b-0.1-ft-bf16", "hubertsiuzdak/snac_24khz"},
    "svara:": {"mlx-community/svara-tts-v1-4bit", "mlx-community/snac_24khz"},
}
IMAGE_FULL = "Tongyi-MAI/Z-Image-Turbo"
IMAGE_LOCAL = ROOT / "models" / "z-image-turbo-4bit"
TOOL_CACHES = [
    ("uv cache", Path.home() / ".cache" / "uv", ["uv", "cache", "prune"]),
    ("pip cache", Path.home() / "Library" / "Caches" / "pip", ["python3", "-m", "pip", "cache", "purge"]),
    ("Homebrew cache", Path.home() / "Library" / "Caches" / "Homebrew", ["brew", "cleanup", "-s"]),
]


def free_gb():
    return shutil.disk_usage(ROOT).free / 1e9


def size(p):
    p = Path(p)
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file() and not f.is_symlink())


def active_models():
    keep = set(ALWAYS_MODELS)
    voices = json.loads((PROFILES / "voices.json").read_text())
    for lang, v in voices.items():
        if not isinstance(v, dict) or v.get("status") not in ("approved", "pilot"):
            continue
        name = str(v.get("voice") or "")
        for prefix, repos in VOICE_MODELS.items():
            if name.startswith(prefix):
                keep |= repos
    if not IMAGE_LOCAL.exists():
        keep.add(IMAGE_FULL)
    return keep


def finished(work):
    lang = work.name
    manifest = work.parent / "manifest.json"
    if not manifest.exists() or not (work / f"{work.parent.name}-{lang}.mp4").exists():
        return False
    stages = json.loads(manifest.read_text()).get("stages", {})
    g = stages.get("gate:final", {})
    return g.get("status") == "approved" and lang in g.get("langs", [lang])


def safe_items():
    items = []
    for work in sorted(CONTENT.glob("C*/*")):
        if not work.is_dir() or not finished(work):
            continue
        cid = f"{work.parent.name} --lang {work.name}"
        for f in [work / "mix.wav", *work.glob("*.qa.png")]:
            if f.exists():
                items.append({"tier": "safe", "path": str(f), "bytes": size(f), "restore": f"python -m pipeline {'produce ' + cid + ' --steps render' if f.name == 'mix.wav' else 'qa ' + cid}"})
    for pat in ("ig-share-*", "ig-cover-*"):
        for d in Path(tempfile.gettempdir()).glob(pat):
            items.append({"tier": "safe", "path": str(d), "bytes": size(d), "restore": "temporary upload folder, not needed"})
    for d in [*ROOT.glob("**/__pycache__"), ROOT / ".pytest_cache"]:
        if d.exists() and ".venv" not in d.parts:
            items.append({"tier": "safe", "path": str(d), "bytes": size(d), "restore": "recreated automatically by Python"})
    return items


def model_items():
    from huggingface_hub import scan_cache_dir

    keep = active_models()
    items = []
    for repo in scan_cache_dir().repos:
        if repo.repo_id in keep:
            continue
        known = any(repo.repo_id in r for r in VOICE_MODELS.values()) or repo.repo_id == IMAGE_FULL
        idle_days = (time.time() - repo.last_accessed) / 86400
        if not known and idle_days < 30:
            continue
        revs = sorted(r.commit_hash for r in repo.revisions)
        items.append({"tier": "models", "path": str(repo.repo_path), "repo": repo.repo_id, "revisions": revs, "bytes": repo.size_on_disk, "idle_days": round(idle_days, 1), "restore": f"hf download {repo.repo_id} --revision {revs[0] if revs else 'main'}"})
    return items


def tool_items():
    return [{"tier": "tools", "path": str(p), "bytes": size(p), "cmd": cmd, "restore": f"{name}: packages re-download on next install"} for name, p, cmd in TOOL_CACHES if p.exists() and shutil.which(cmd[0])]


def plan(tiers):
    out = []
    if "safe" in tiers:
        out += safe_items()
    if "models" in tiers:
        out += model_items()
    if "tools" in tiers:
        out += tool_items()
    return out


def apply(items):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    freed = 0
    with LOG.open("a") as log:
        for it in items:
            before = size(it["path"]) if Path(it["path"]).exists() else 0
            if it["tier"] == "tools":
                subprocess.run(it["cmd"], capture_output=True)
            else:
                p = Path(it["path"])
                shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
            after = size(it["path"]) if Path(it["path"]).exists() else 0
            freed += before - after
            log.write(json.dumps({**{k: v for k, v in it.items() if k != "cmd"}, "freed": before - after, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}) + "\n")
    return freed


def report(items):
    total = sum(i["bytes"] for i in items)
    for tier in ("safe", "models", "tools"):
        group = [i for i in items if i["tier"] == tier]
        if not group:
            continue
        print(f"\n[{tier}] {sum(i['bytes'] for i in group) / 1e9:.2f} GB")
        for i in sorted(group, key=lambda x: -x["bytes"])[:25 if tier == "safe" else 99]:
            label = i.get("repo") or (Path(i["path"]).relative_to(ROOT) if str(i["path"]).startswith(str(ROOT)) else i["path"])
            extra = f"  idle {i['idle_days']}d" if "idle_days" in i else ""
            print(f"  {i['bytes'] / 1e6:9.1f} MB  {label}{extra}\n               restore: {i['restore']}")
        if tier == "safe" and len(group) > 25:
            print(f"  … {len(group) - 25} more")
    return total


def guard():
    gb = free_gb()
    if gb >= WARN_GB:
        return
    if gb < CRITICAL_GB:
        print(f"Disk critical: {gb:.1f} GB free. Removing safe, reproducible intermediates.", flush=True)
        freed = apply(safe_items())
        print(f"  freed {freed / 1e9:.2f} GB; now {free_gb():.1f} GB free. For more: python -m pipeline cleanup --models --tools", flush=True)
    else:
        print(f"Disk low: {gb:.1f} GB free. Preview what can go: python -m pipeline cleanup --models --tools", flush=True)
