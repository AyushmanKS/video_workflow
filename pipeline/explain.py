import re

SEVERITIES = ("info", "warning", "recoverable", "critical")

REDACTIONS = [
    (re.compile(r"(access_token=)[^&\s'\"<>]+"), r"\1<redacted>"),
    (re.compile(r"(['\"]?access_token['\"]?\s*[:=]\s*['\"])[^'\"]+"), r"\1<redacted>"),
    (re.compile(r"(['\"]?(?:refresh_token|client_secret|app_secret)['\"]?\s*[:=]\s*['\"]?)[^'\"\s,}]+"), r"\1<redacted>"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9_\-.~+/=%]+"), r"\1<redacted>"),
    (re.compile(r"\bEAA[A-Za-z0-9]+"), "EAA<redacted>"),
    (re.compile(r"\bya29[.][A-Za-z0-9_\-.]+"), "<redacted-google-token>"),
    (re.compile(r"\b1//[A-Za-z0-9_\-]{20,}"), "1//<redacted>"),
    (re.compile(r"\bIGQ[A-Za-z0-9_\-]{20,}"), "IGQ<redacted>"),
]


def redact(text):
    if text is None:
        return None
    s = str(text)
    for rx, rep in REDACTIONS:
        s = rx.sub(rep, s)
    return s


CATALOGUE = [
    {
        "code": "youtube_upload_limit",
        "patterns": [r"uploadLimitExceeded", r"exceeded the number of videos they may upload"],
        "title": "YouTube daily upload limit reached",
        "explanation": "YouTube caps how many videos a channel can upload per day. This upload was refused, nothing was published.",
        "suggestion": "Nothing to do. The publish queue retries automatically with backoff (1 h, 2 h, 4 h, 6 h) and keeps the approved times.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "youtube_quota",
        "patterns": [r"quotaExceeded", r"exceeded your\s+<a[^>]*>quota", r"exceeded your quota"],
        "title": "YouTube API quota used up",
        "explanation": "The Google Cloud project used its daily YouTube Data API quota (10,000 units; one upload costs about 1,600).",
        "suggestion": "Nothing to do. The queue retries after Pacific midnight, when the quota resets.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "google_token_expired",
        "patterns": [r"invalid_grant", r"Token has been expired or revoked", r"RefreshError"],
        "title": "Google sign-in expired",
        "explanation": "The saved YouTube OAuth token was rejected. Tokens of an app in Testing mode expire after about 7 days.",
        "suggestion": "On the Mac, run any YouTube command (e.g. python -m pipeline analytics --platform youtube) and sign in again in the browser.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "youtube_forbidden",
        "patterns": [r"insufficientPermissions", r"HttpError 403", r"forbidden", r"youtubeSignupRequired", r"accessNotConfigured"],
        "title": "YouTube refused the request (403)",
        "explanation": "The signed-in Google account lacks permission for this action, the API is not enabled, or the token was issued for another channel.",
        "suggestion": "Check that the OAuth token belongs to the channel and has the youtube.upload scope; enable the API in the GCP project if the message says so, then re-authorise on the Mac.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "ig_api_blocked",
        "patterns": [r"API access blocked", r"5258005"],
        "title": "Instagram API access blocked by Meta",
        "explanation": "Meta put the app or account behind a security checkpoint (OAuthException code 200, subcode 5258005). Every API call fails until it is cleared.",
        "suggestion": "Open Meta Business Suite / the developer dashboard and the Instagram app on the phone and confirm the login or security check. Do not keep retrying; repeated calls can prolong the block. Missed slots need a new Instagram G3.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "ig_permission",
        "patterns": [r"\(#10\)", r"'code':\s*10\b", r"\"code\":\s*10\b", r"does not have permission", r"permission\(s\) must be granted"],
        "title": "Instagram permission missing",
        "explanation": "The token lacks a permission needed for this call (Graph API error #10).",
        "suggestion": "Add the permission to the system user / app in Meta Business settings, generate a new token and run python instagram.py setup in the Mac terminal.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "ig_token_invalid",
        "patterns": [r"'code':\s*190\b", r"\"code\":\s*190\b", r"Error validating access token", r"Session has expired", r"Missing .*instagram\.json"],
        "title": "Instagram token invalid",
        "explanation": "Meta rejected the saved access token (expired, revoked or rotated).",
        "suggestion": "Generate a new token in Meta Business settings and run python instagram.py setup in the Mac terminal.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "ig_container_error",
        "patterns": [r"Instagram processing failed", r"'status_code':\s*'(?:ERROR|EXPIRED)'"],
        "title": "Instagram could not process the video",
        "explanation": "Instagram fetched the file but its processing ended in ERROR or EXPIRED, so nothing was posted.",
        "suggestion": "Check the video format (H.264/AAC, 9:16, 3 s to 15 min, under 300 MB) and retry; a new container is created on retry.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "ig_processing_timeout",
        "patterns": [r"Instagram processing timed out"],
        "title": "Instagram processing took too long",
        "explanation": "Instagram did not finish processing within 20 minutes; the post was not published.",
        "suggestion": "Retry later; the old container is never published.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "tunnel_failed",
        "patterns": [r"tunnel never became reachable", r"cloudflared gave no URL", r"Could not start the temporary tunnel", r"cloudflared is not installed", r"\bexit(?: code)? 75\b", r"tunnel failed"],
        "title": "Temporary upload link failed",
        "explanation": "The cloudflared quick tunnel that lets Instagram fetch the video did not come up (exit 75).",
        "suggestion": "Usually a network blip: the scheduled job retries 4 times, 2 minutes apart. If it keeps failing, check the Mac's internet connection and that cloudflared is installed.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "ig_job_late",
        "patterns": [r"more than 24 h ago; not posting"],
        "title": "Scheduled Instagram post skipped (over 24 h late)",
        "explanation": "The Mac was off or asleep at post time and woke more than 24 hours later, so the job refused to post.",
        "suggestion": "Pick a new time and record a new Instagram G3 approval.",
        "retry_safe": False,
        "severity": "warning",
    },
    {
        "code": "disk_low",
        "patterns": [r"No space left on device", r"ENOSPC", r"disk (?:is )?(?:low|full)", r"free disk below"],
        "title": "Disk space low",
        "explanation": "The Mac is running out of disk space, so files could not be written.",
        "suggestion": "Run python -m pipeline cleanup (preview) and then --apply to free reproducible intermediates.",
        "retry_safe": True,
        "severity": "critical",
    },
    {
        "code": "qa_fail",
        "patterns": [r"QA verdict fail"],
        "title": "QA failed",
        "explanation": "Automated QA found auto-reject problems in this variant.",
        "suggestion": "Fix the failing checks listed and run python -m pipeline qa again. Only auto-warn checks can be waived by the owner.",
        "retry_safe": False,
        "severity": "recoverable",
    },
    {
        "code": "gate_refused",
        "patterns": [r"^Refused", r"Blocked:", r"approval record does not match", r"differs from the \w+ G3 approval", r"is not approved for", r"changed after G\d", r"needs a new owner approval"],
        "title": "Blocked by an approval gate",
        "explanation": "The action needs an owner approval that is missing, or the files changed after they were approved.",
        "suggestion": "Review the files and record a fresh approval in chat (G1 script, G2 video, G3 publish with time).",
        "retry_safe": False,
        "severity": "warning",
    },
    {
        "code": "gate_rejected",
        "patterns": [],
        "title": "Owner rejected this step",
        "explanation": "The owner rejected the script, video or publish plan at an approval gate.",
        "suggestion": "Apply the owner's note, then ask for approval again.",
        "retry_safe": False,
        "severity": "warning",
    },
    {
        "code": "missing_output",
        "patterns": [r"FileNotFoundError", r"No such file or directory", r"^Missing ", r"Unknown content id"],
        "title": "Expected file missing",
        "explanation": "A step expected a file (script, audio, image or video) that is not on disk.",
        "suggestion": "Re-run the stage that produces the file (see python -m pipeline status <ID>).",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "render_failed",
        "patterns": [r"CalledProcessError.*studio\.py", r"studio\.py.*returned non-zero", r"ffmpeg.*(?:error|failed)"],
        "title": "Production step crashed",
        "explanation": "studio.py (voice, images or render) exited with an error.",
        "suggestion": "Open the run log, fix the cause and re-run the same produce step; cached scenes are reused.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "ig_container_orphaned",
        "context": "container_created",
        "patterns": [r"ConnectTimeout", r"ReadTimeout", r"timed out", r"Network unreachable", r"network error", r"ConnectionError", r"NameResolutionError", r"ENOTFOUND", r"nodename nor servname"],
        "kind": "unknown_outcome",
        "title": "Instagram post outcome unknown",
        "explanation": "Instagram accepted the upload (a media container was created), then the network dropped before the Mac could confirm what happened next.",
        "suggestion": "Open the Instagram account and check whether the Reel is there before retrying. If it is not, a retry is fine; the unconfirmed container expires on its own.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "network_unknown_outcome",
        "patterns": [r"may have reached Instagram", r"may have reached the server", r"request may have reached"],
        "kind": "unknown_outcome",
        "title": "Request outcome unknown",
        "explanation": "The connection failed after a write request (POST) was sent, so the server may have acted on it.",
        "suggestion": "Check the account for the post before retrying; a blind retry could create a duplicate.",
        "retry_safe": False,
        "severity": "critical",
    },
    {
        "code": "network_timeout",
        "patterns": [r"ConnectTimeout", r"ReadTimeout", r"timed out", r"Network unreachable", r"NameResolutionError", r"ENOTFOUND", r"nodename nor servname", r"Temporary failure in name resolution", r"ConnectionError", r"Connection reset"],
        "title": "Network problem",
        "explanation": "The Mac could not reach the service (timeout or DNS failure). Read-only requests are retried automatically.",
        "suggestion": "Check the Mac's internet connection. Safe to retry read-only steps; for posts, check the account first.",
        "retry_safe": True,
        "severity": "recoverable",
    },
    {
        "code": "cancelled",
        "patterns": [r"KeyboardInterrupt"],
        "title": "Stopped by hand",
        "explanation": "The step was interrupted (Ctrl-C or the process was stopped).",
        "suggestion": "Re-run the same step when ready.",
        "retry_safe": True,
        "severity": "info",
    },
]

UNKNOWN = {
    "code": "unknown_error",
    "title": "Unrecognised error",
    "explanation": "This error is not in the catalogue yet; the raw text is kept below.",
    "suggestion": "Read the technical detail and the log; add the case to pipeline/explain.py once understood.",
    "retry_safe": None,
    "severity": "recoverable",
}

_COMPILED = [(e, [re.compile(p, re.I | re.M) for p in e["patterns"]]) for e in CATALOGUE]


def explain(raw, context=None):
    text = redact(raw) or ""
    ctx = set(context or ())
    for entry, rxs in _COMPILED:
        need = entry.get("context")
        if need and need not in ctx:
            continue
        if any(rx.search(text) for rx in rxs):
            out = {k: v for k, v in entry.items() if k not in ("patterns", "context")}
            break
    else:
        out = dict(UNKNOWN)
    out.setdefault("kind", None)
    out["raw"] = text
    return out


def by_code(code):
    for e in CATALOGUE:
        if e["code"] == code:
            return {k: v for k, v in e.items() if k not in ("patterns", "context")}
    return dict(UNKNOWN, code=code)


def qa_failure_text(report):
    checks = report.get("checks", []) if isinstance(report, dict) else []
    bad = [c["name"] for c in checks if not c.get("ok") and not c.get("skipped") and c.get("class") == "reject"]
    warn = [c["name"] for c in checks if not c.get("ok") and not c.get("skipped") and c.get("class") != "reject"]
    s = f"QA verdict fail: {', '.join(bad) or 'see report'}"
    if warn:
        s += f" (also warnings: {', '.join(warn)})"
    return s
