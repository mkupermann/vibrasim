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
    """Send notification. Telegram primary; persists to disk on failure.

    Channel choice 2026-05-20 by user: Telegram bot.
    The autopilot_mail name is retained for back-compat with existing
    call sites (postflight, watchdog, supervisor, health_check); under
    the hood this routes to Telegram via tools/notify_telegram.py.

    On any delivery failure (no Telegram credentials configured,
    network error, Telegram API error) the message is persisted to
    ~/.eqmod/autopilot/unsent_mail_*.txt with the failure reason so
    the health-check surfaces the backlog.

    Returns True on confirmed delivery, False on persist-to-disk.
    """
    import sys as _sys
    _sys.path.insert(0, str(REPO / "tools"))
    try:
        from notify_telegram import send_telegram  # type: ignore
    except Exception as exc:
        _persist_unsent(subject, body, f"notify_telegram import failed: {exc!r}")
        return False

    ok, reason = send_telegram(subject, body)
    if ok:
        return True
    _persist_unsent(subject, body, f"telegram: {reason}")
    return False


def _persist_unsent(subject: str, body: str, failure_reason: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    fallback = STATE_DIR / f"unsent_mail_{stamp}.txt"
    fallback.write_text(
        f"SUBJECT: {subject}\n"
        f"TIMESTAMP: {_dt.datetime.now().isoformat()}\n"
        f"FAILURE: {failure_reason}\n\n"
        f"{body}\n\n"
        "----\n"
        "If you see this file, the Telegram notification channel is\n"
        "not delivering. Check ~/.eqmod/autopilot/notify_config.json\n"
        "(or env EQMOD_TELEGRAM_BOT_TOKEN + EQMOD_TELEGRAM_CHAT_ID) and\n"
        "test with: python tools/notify_telegram.py --test\n"
    )
