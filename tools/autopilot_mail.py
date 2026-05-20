"""Shared mail helper for EQMOD autopilot.

Sends plain-text email to the user via Apple Mail (osascript) with /usr/bin/mail
as fallback. If both fail, persists the unsent mail to ~/.eqmod/autopilot/.

Used by:
    - tools/autopilot_watchdog.py (hourly heartbeat + daily summary + alerts)
    - tools/autopilot_postflight.py (per-session report at end of every run)
"""
from __future__ import annotations

import datetime as _dt
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCPT_PATH = REPO / ".eqmod/autopilot/scripts/send_mail.scpt"
STATE_DIR = Path.home() / ".eqmod/autopilot"
RECIPIENT = "michael@kupermann.com"


def send_mail(subject: str, body: str) -> bool:
    """Send via Apple Mail osascript. Persists to disk on any failure.

    Discovered 2026-05-20: the previous `/usr/bin/mail` fallback returned
    rc=0 because macOS Postfix is unconfigured for outbound delivery on
    this Mac; the mail was silently dropped while `mail` reported success.
    send_mail() therefore returned True for weeks even though nothing
    reached the user, who reports never receiving any mail.

    New behaviour: osascript is the only delivery path. /usr/bin/mail
    fallback removed entirely. If osascript fails (Mail.app not running,
    AppleEvent -1712 timeout, automation permission missing in System
    Settings → Privacy & Security → Automation), persist the mail with
    the precise failure reason to ~/.eqmod/autopilot/unsent_mail_*.txt
    and return False. The health-check tool surfaces the unsent backlog.
    """
    body_escaped = body.replace("\\", "\\\\").replace("\n", "\\n")
    failure_reason = "unknown"

    try:
        r = subprocess.run(
            ["/usr/bin/osascript", str(SCPT_PATH), RECIPIENT, subject, body_escaped],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and "OK" in r.stdout:
            return True
        failure_reason = (r.stderr or r.stdout or "no output").strip()[:500]
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        failure_reason = f"subprocess error: {exc!r}"
    except Exception as exc:
        failure_reason = f"unexpected: {exc!r}"

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    fallback = STATE_DIR / f"unsent_mail_{stamp}.txt"
    fallback.write_text(
        f"SUBJECT: {subject}\n"
        f"TIMESTAMP: {_dt.datetime.now().isoformat()}\n"
        f"OSASCRIPT_FAILURE: {failure_reason}\n\n"
        f"{body}\n\n"
        "----\n"
        "/usr/bin/mail fallback intentionally removed 2026-05-20 because\n"
        "macOS Postfix on this Mac drops outbound silently while reporting\n"
        "rc=0, which made the autopilot 'send' mails for weeks without any\n"
        "ever reaching the user. If you see this file, mail delivery via\n"
        "Apple Mail is not working — check System Settings → Privacy &\n"
        "Security → Automation (osascript must be allowed to control Mail)\n"
        "or wire up a non-Mail.app notification channel.\n"
    )
    return False
