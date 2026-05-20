"""Telegram receiver — bidirectional autopilot control.

Long-polls Telegram getUpdates and dispatches commands from the
whitelisted chat to handlers that touch the autopilot state.

Whitelist source: ~/.eqmod/autopilot/notify_config.json may contain
a top-level "telegram_whitelist_chat_ids" array. Falls back to a
single chat_id from "telegram_chat_id" (the recipient itself —
the sender of incoming commands is the recipient of outgoing alerts).

Single-instance via lock file. Persists last update_id so restart
doesn't reprocess already-handled messages.

Designed to run continuously under launchd
(com.eqmod.notify-receiver.plist, KeepAlive=true).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from notify_telegram import load_config, send_telegram  # noqa: E402

STATE_DIR = Path.home() / ".eqmod/autopilot"
QUEUE_SHORT = REPO / ".eqmod/autopilot/QUEUE.yaml"
QUEUE_LONG = Path.home() / ".eqmod/long-run/queue.yaml"
STOP_SHORT = STATE_DIR / "STOP"
STOP_LONG = Path.home() / ".eqmod/long-run/STOP"
SESSION_LOG = STATE_DIR / "session.log"
LOGBOOK = REPO / "LOGBOOK.md"
LAST_UPDATE = STATE_DIR / "telegram_last_update_id"
LOCK_PATH = STATE_DIR / "telegram_receiver.lock"
RECEIVER_LOG = STATE_DIR / "telegram_receiver.log"

LONG_POLL_TIMEOUT_S = 25  # Telegram's recommended max


def log(msg: str) -> None:
    RECEIVER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RECEIVER_LOG.open("a") as f:
        f.write(f"[{_dt.datetime.now().isoformat()}] {msg}\n")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except Exception:
        return False


def whitelist() -> set[int]:
    cfg_path = STATE_DIR / "notify_config.json"
    if not cfg_path.exists():
        return set()
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        return set()
    ids: set[int] = set()
    for v in cfg.get("telegram_whitelist_chat_ids") or []:
        try:
            ids.add(int(v))
        except (TypeError, ValueError):
            pass
    primary = cfg.get("telegram_chat_id")
    if primary is not None:
        try:
            ids.add(int(primary))
        except (TypeError, ValueError):
            pass
    return ids


def cmd_help(_args: str) -> str:
    return (
        "Available commands:\n"
        "/status — short + long-run queue summary, current item, STOP state\n"
        "/queue — last 10 items in short queue with status\n"
        "/stop — set STOP marker (autopilot pauses next tick)\n"
        "/resume — remove STOP marker\n"
        "/health — run health-check, return summary\n"
        "/note <text> — append a dated note to LOGBOOK.md\n"
        "/logs [n] — recent session.log lines (default 20, max 100)\n"
        "/help — this message"
    )


def _queue_counter(path: Path) -> str:
    if not path.exists():
        return "(no file)"
    try:
        q = yaml.safe_load(path.read_text())
        items = q.get("items") or []
        c = Counter((str(i.get("status")) if i.get("status") is not None else "queued") for i in items)
        return " ".join(f"{k}={v}" for k, v in sorted(c.items()))
    except Exception as exc:
        return f"(parse error: {exc!r})"


def cmd_status(_args: str) -> str:
    short = _queue_counter(QUEUE_SHORT)
    longrun = _queue_counter(QUEUE_LONG)
    current = "(none)"
    cur_path = STATE_DIR / "current_item.txt"
    if cur_path.exists():
        try:
            current = cur_path.read_text().strip() or "(empty)"
        except Exception:
            pass
    stop_short = "STOP set" if STOP_SHORT.exists() else "running"
    stop_long = "STOP set" if STOP_LONG.exists() else "running"
    return (
        f"Short queue: {short}\n"
        f"Long-run queue: {longrun}\n"
        f"Current short item: {current}\n"
        f"Short autopilot: {stop_short}\n"
        f"Long-run dispatcher: {stop_long}"
    )


def cmd_queue(_args: str) -> str:
    if not QUEUE_SHORT.exists():
        return "(no short queue)"
    try:
        q = yaml.safe_load(QUEUE_SHORT.read_text())
    except Exception as exc:
        return f"queue parse error: {exc!r}"
    items = (q.get("items") or [])[-10:]
    lines = []
    for i in items:
        iid = (i.get("id") or "?")[:10]
        st = str(i.get("status")) if i.get("status") is not None else "queued"
        atp = i.get("attempts", 0)
        lines.append(f"{iid:<10s}  {st:<10s}  attempts={atp}")
    return "Last 10 items:\n" + "\n".join(lines)


def cmd_stop(_args: str) -> str:
    STOP_SHORT.write_text(
        f"Set via Telegram /stop at {_dt.datetime.now().isoformat()}\n"
    )
    return "STOP marker set. Short autopilot pauses at next launchd tick (≤30 min)."


def cmd_resume(_args: str) -> str:
    if STOP_SHORT.exists():
        STOP_SHORT.unlink()
        return "STOP marker removed. Short autopilot resumes at next tick."
    return "No STOP marker — autopilot already running."


def cmd_health(_args: str) -> str:
    try:
        r = subprocess.run(
            [str(REPO / ".venv/bin/python"),
             str(REPO / "tools/autopilot_health_check.py")],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode == 0:
            return "health-check: all clear"
        # Read the freshly-written log tail
        tail = ""
        if (STATE_DIR / "health_check.log").exists():
            with (STATE_DIR / "health_check.log").open() as f:
                lines = f.readlines()
            tail = "".join(lines[-15:])[:2000]
        return (
            f"health-check: issues (exit {r.returncode})\n"
            f"recent log:\n{tail}"
        )
    except Exception as exc:
        return f"health-check failed to run: {exc!r}"


def cmd_note(args: str) -> str:
    args = args.strip()
    if not args:
        return "Usage: /note <text>"
    if not LOGBOOK.exists():
        return f"LOGBOOK.md missing at {LOGBOOK}"
    entry = (
        f"\n\n## {_dt.date.today().isoformat()} — note via Telegram "
        f"{_dt.datetime.now().strftime('%H:%M:%S')}\n\n{args}\n"
    )
    with LOGBOOK.open("a") as f:
        f.write(entry)
    return f"Appended {len(args)} chars to LOGBOOK.md."


def cmd_logs(args: str) -> str:
    try:
        n = int(args.strip() or "20")
    except ValueError:
        n = 20
    n = max(1, min(n, 100))
    if not SESSION_LOG.exists():
        return "(no session.log)"
    with SESSION_LOG.open() as f:
        lines = f.readlines()
    return f"Last {n} session.log lines:\n" + "".join(lines[-n:])[:3500]


COMMANDS = {
    "/help": cmd_help,
    "/status": cmd_status,
    "/queue": cmd_queue,
    "/stop": cmd_stop,
    "/resume": cmd_resume,
    "/health": cmd_health,
    "/note": cmd_note,
    "/logs": cmd_logs,
}


def process_update(update: dict, allowed: set[int]) -> None:
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id not in allowed:
        log(f"  rejected sender chat_id={chat_id}")
        return

    text = (message.get("text") or "").strip()
    if not text:
        return

    parts = text.split(maxsplit=1)
    cmd_raw = parts[0].lower()
    # Strip @botname suffix if present
    cmd = re.sub(r"@\w+$", "", cmd_raw)
    args = parts[1] if len(parts) > 1 else ""

    handler = COMMANDS.get(cmd)
    if not handler:
        log(f"  unknown command {cmd!r} from {chat_id}")
        send_telegram(
            "Unknown command",
            f"Got: {cmd_raw!r}\n\n{cmd_help('')}"
        )
        return

    log(f"  cmd {cmd!r} from {chat_id} args_len={len(args)}")
    try:
        reply = handler(args)
    except Exception as exc:
        reply = f"Command {cmd} crashed: {exc!r}"
        log(f"  handler error: {exc!r}")
    subject = cmd[1:].upper() if cmd.startswith("/") else cmd.upper()
    send_telegram(subject, reply)


def acquire_lock() -> bool:
    if LOCK_PATH.exists():
        try:
            pid = int(LOCK_PATH.read_text())
            if pid_alive(pid):
                return False
        except (ValueError, FileNotFoundError):
            pass
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(str(os.getpid()))
    return True


def main() -> int:
    if not acquire_lock():
        print(f"Another receiver instance is running. Lock: {LOCK_PATH}", file=sys.stderr)
        return 1

    log("--- receiver starting up")
    try:
        token, _ = load_config()
        allowed = whitelist()
        if not token:
            log("no telegram_bot_token in notify_config.json — abort")
            return 1
        if not allowed:
            log("no whitelist chat_ids — abort (would silently drop all messages)")
            return 1
        log(f"whitelist={allowed}")

        offset: int | None = None
        if LAST_UPDATE.exists():
            try:
                offset = int(LAST_UPDATE.read_text().strip()) + 1
            except ValueError:
                offset = None

        while True:
            try:
                params = {"timeout": LONG_POLL_TIMEOUT_S}
                if offset is not None:
                    params["offset"] = offset
                url = (
                    f"https://api.telegram.org/bot{token}/getUpdates?"
                    + urllib.parse.urlencode(params)
                )
                with urllib.request.urlopen(
                    url, timeout=LONG_POLL_TIMEOUT_S + 10
                ) as resp:
                    payload = json.loads(resp.read().decode())
                if not payload.get("ok"):
                    log(f"telegram api not ok: {payload}")
                    time.sleep(10)
                    continue
                for update in payload.get("result", []):
                    process_update(update, allowed)
                    new_offset = update["update_id"] + 1
                    if offset is None or new_offset > offset:
                        offset = new_offset
                        LAST_UPDATE.write_text(str(update["update_id"]))
            except (urllib.error.URLError, TimeoutError) as exc:
                log(f"network: {exc!r}")
                time.sleep(10)
            except json.JSONDecodeError as exc:
                log(f"json: {exc!r}")
                time.sleep(10)
            except KeyboardInterrupt:
                log("KeyboardInterrupt — exiting")
                return 0
            except Exception as exc:
                log(f"poll error: {exc!r}")
                time.sleep(30)
    finally:
        LOCK_PATH.unlink(missing_ok=True)
        log("--- receiver exiting")


if __name__ == "__main__":
    sys.exit(main())
