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
        "/results — natural-language: achieved + running + recommendation\n"
        "/status — short + long-run queue summary, current item, STOP state\n"
        "/queue — last 10 items in short queue with status\n"
        "/requeue <id> — set item back to queued (explicit retry, attempts unchanged)\n"
        "/fail <id> <reason> — operator-administrative closure with reason in blockers\n"
        "/stop — set STOP marker (autopilot pauses next tick)\n"
        "/resume — remove STOP marker\n"
        "/health — run health-check, return summary\n"
        "/note <text> — append a dated note to LOGBOOK.md\n"
        "/logs [n] — recent session.log lines (default 20, max 100)\n"
        "/help — this message"
    )


def _update_status_in_text(
    text: str,
    item_id: str,
    new_status: str,
    extra_blocker: str | None = None,
) -> str:
    """In-place YAML text mutation — preserves comments + format.

    Same pattern as autopilot_postflight._update_item_status_in_text;
    duplicated here intentionally so the receiver does not import the
    postflight module (which imports autopilot_mail and yaml-dumps).
    """
    pattern = re.compile(
        r"(?P<header>^[ \t]*- id: " + re.escape(item_id) + r"\b.*?\n)"
        r"(?P<body>.*?)"
        r"(?=^[ \t]*- id: |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        raise ValueError(f"item {item_id} not found in QUEUE.yaml text")
    body = m.group("body")
    indent_match = re.search(r"^([ \t]+)status:", body, re.MULTILINE)
    indent = indent_match.group(1) if indent_match else "    "
    body = re.sub(
        r"^(" + re.escape(indent) + r"status: ).*$",
        rf"\g<1>{new_status}",
        body, count=1, flags=re.MULTILINE,
    )
    if extra_blocker:
        # Append to the blockers list if present; otherwise insert one.
        if re.search(r"^" + re.escape(indent) + r"blockers:\s*\[", body, re.MULTILINE):
            # blockers: [...] inline list — append before the closing ]
            esc = extra_blocker.replace("\\", "\\\\").replace('"', '\\"')
            body = re.sub(
                r"^(" + re.escape(indent) + r"blockers:\s*\[)(.*)\](\s*)$",
                lambda mm: f'{mm.group(1)}{mm.group(2).rstrip()}, "{esc}"]{mm.group(3)}',
                body, count=1, flags=re.MULTILINE,
            )
        else:
            # Insert a blockers line right after status
            esc = extra_blocker.replace("\\", "\\\\").replace('"', '\\"')
            body = re.sub(
                r"^(" + re.escape(indent) + r"status: \w+)$",
                rf'\1\n{indent}blockers: ["{esc}"]',
                body, count=1, flags=re.MULTILINE,
            )
    return text[: m.start("body")] + body + text[m.end("body") :]


def cmd_requeue(args: str) -> str:
    iid = args.strip().split()[0] if args.strip() else ""
    if not iid:
        return "Usage: /requeue <item-id>"
    try:
        text = QUEUE_SHORT.read_text()
        new = _update_status_in_text(text, iid, "queued")
        QUEUE_SHORT.write_text(new)
        return f"{iid}: status set to queued. Will fire on next launchd tick if blockers satisfied."
    except ValueError:
        return f"{iid}: not found in QUEUE.yaml"
    except Exception as exc:
        return f"requeue {iid} failed: {exc!r}"


def cmd_fail(args: str) -> str:
    parts = args.strip().split(maxsplit=1)
    if not parts:
        return "Usage: /fail <item-id> <reason>"
    iid = parts[0]
    reason = parts[1] if len(parts) > 1 else "Operator-administrative closure via Telegram"
    blocker_note = (
        f"Operator closure {_dt.datetime.now().isoformat()} via Telegram /fail: {reason}"
    )
    try:
        text = QUEUE_SHORT.read_text()
        new = _update_status_in_text(text, iid, "failed", extra_blocker=blocker_note)
        QUEUE_SHORT.write_text(new)
        return f"{iid}: status=failed. Reason appended to blockers."
    except ValueError:
        return f"{iid}: not found in QUEUE.yaml"
    except Exception as exc:
        return f"fail {iid} failed: {exc!r}"


# Rule-based item summaries — kept in this file rather than a separate
# config so the receiver has no extra import / load step. Descriptions
# are deliberately specific and don't claim more than the item achieved.
ITEM_SUMMARIES = {
    "R-13": "Bridge-spectrum observable scaffolded; nullte architektonisch (Inhalt-Coupling-Test)",
    "R-14": "Synthesis-Sweep: Q=3 gain=1 lockt firings über baseline",
    "R-15": "R-LR-8 Infrastructure: flux-snapshot + salvaged bridge_spectrum + R-LR-8 scaffold",
    "R-16": "Architektur-Firewall quantitativ: KL=0.0 EN vs Weißrauschen — Inhalt-Blockade total",
    "R-17": "G24 implementiert; administratively failed wegen Acceptance-Scope-Bug (in R-18 verschoben)",
    "R-17b": "G24 (energy-weighted flux) mechanisch verifiziert — 12/12 tests grün",
    "R-18": "G24-Verifikation: bricht die energie-gewichtete Plastizität die Firewall bei 50k Ticks?",
    "R-19": "Pipeline-Smoke-Suite — Defence-Layer-Regression-Tests",
    "R-LR-1": "Encoder-free 1.8M Ticks: Substrat formt 1358 Atome + 3188 Brücken aus Roh-Audio; Synthese dominiert babble",
    "R-LR-2": "Cochlea-baseline 1.8M: NULL, gleicher Synthese-Bottleneck",
    "R-LR-3": "Encoder-free 30x20x10 voxels: gekillt nach 39h Hard-cap-Verstoß",
    "R-LR-4": "Encoder-free + extended dream phase",
    "R-LR-8": "Encoder-free + tuned synthesis + bridge-spectrum (full-scale G24-unabhängig)",
}


def _terminal_status(item: dict) -> str | None:
    """Return one of {'passed', 'failed', 'null'} or None if not terminal."""
    st = item.get("status")
    if st == "passed":
        return "passed"
    if st == "failed":
        return "failed"
    # YAML null → Python None; literal "None" → str
    if st is None or str(st) in ("null", "None"):
        if item.get("attempts", 0) > 0 or item.get("finished_at"):
            return "null"
    return None


def _describe_item(item: dict) -> str:
    iid = item.get("id") or "?"
    return ITEM_SUMMARIES.get(iid, item.get("title", "?")[:80])


def _summarise_achievements(short_items: list, long_items: list) -> list[str]:
    """One bullet per recently-terminal item, newest first."""
    combined = []
    for src in (short_items, long_items):
        for it in src:
            term = _terminal_status(it)
            if not term:
                continue
            ts = it.get("last_session") or it.get("finished_at") or ""
            combined.append((ts, term, it))
    combined.sort(key=lambda t: t[0], reverse=True)

    bullets = []
    for _, term, it in combined[:10]:
        iid = it.get("id") or "?"
        desc = _describe_item(it)
        verb = {"passed": "passed", "failed": "failed", "null": "null"}[term]
        bullets.append(f"{iid} {verb}: {desc}")
    return bullets


def _summarise_running(short_items: list, long_items: list) -> list[str]:
    bullets = []
    # Current short-queue item (if a wrapper is active)
    cur_path = STATE_DIR / "current_item.txt"
    if cur_path.exists():
        try:
            cid = cur_path.read_text().strip()
            it = next((i for i in short_items if i.get("id") == cid), None)
            if it:
                bullets.append(f"Short: {cid} — {_describe_item(it)}")
        except Exception:
            pass
    # Long-run
    lr_pid = Path.home() / ".eqmod/long-run/current.pid"
    lr_item = Path.home() / ".eqmod/long-run/current_item.txt"
    if lr_pid.exists() and lr_item.exists():
        try:
            cid = lr_item.read_text().strip()
            it = next((i for i in long_items if i.get("id") == cid), None)
            if it:
                import time as _t
                elapsed_h = (_t.time() - lr_pid.stat().st_mtime) / 3600
                bullets.append(
                    f"Long-run: {cid} elapsed {elapsed_h:.1f}h — {_describe_item(it)}"
                )
        except Exception:
            pass
    if not bullets:
        bullets.append("(keine aktive Session, alle Queues warten auf nächsten Launchd-Tick)")
    return bullets


def _summarise_architecture(short_items: list) -> list[str]:
    by_id = {i.get("id"): i for i in short_items}
    bullets = []

    # G24 mechanics state
    r17b = by_id.get("R-17b") or by_id.get("R-17")
    if r17b and r17b.get("status") == "passed":
        bullets.append("G24 Mechanik (energy-weighted flux): implementiert + verifiziert")
    else:
        bullets.append("G24 Mechanik: noch nicht verifiziert")

    # G24 content-coupling state
    r18 = by_id.get("R-18")
    if r18:
        st = _terminal_status(r18)
        if st == "passed":
            bullets.append("G24 Inhalt-Coupling: Firewall gebrochen (KL > 0.01 bei 50k Ticks)")
        elif st == "null":
            bullets.append("G24 Inhalt-Coupling: Firewall hält — energie-gewichtung reicht nicht")
        elif st == "failed":
            bullets.append("G24 Inhalt-Coupling: implementation-bug, retry")
        else:
            bullets.append("G24 Inhalt-Coupling: Verdict ausstehend (R-18 läuft oder queued)")
    else:
        bullets.append("G24 Inhalt-Coupling: nicht geplant")

    # Iteration cap usage
    g24_used = 1 if (r17b and r17b.get("status") in ("passed", "failed")) else 0
    bullets.append(f"Iteration-Cap: G24={g24_used} von 3 Slots verbraucht")

    # Success criterion progress
    bullets.append("Erfolgskriterium 'selbstbestimmt lernend kommunizierend':")
    bullets.append("  selbstbestimmt: schwach (G17-Autopilot-Loop, Legacy-Substrat)")
    bullets.append("  lernend: Inhalt-Coupling-Verdict für G24 hängt ausstehend")
    bullets.append("  kommunizierend: nicht implementiert — G20-G23 im Pivot-Pfad gegated")

    return bullets


def _next_recommendation(short_items: list, long_items: list) -> list[str]:
    by_id = {i.get("id"): i for i in short_items}
    by_lr = {i.get("id"): i for i in long_items}
    bullets = []

    r18 = by_id.get("R-18")
    r18_term = _terminal_status(r18) if r18 else None

    if r18 is None:
        bullets.append("R-18 fehlt im Queue — füge G24-Verifikation hinzu bevor Pivot geprüft wird")
    elif r18.get("status") == "queued":
        bullets.append("R-18 fires demnächst (≤30min). Verdict in ~4h — entscheidend für G24")
    elif r18_term == "passed":
        # R-LR-9 status
        rlr9 = by_lr.get("R-LR-9")
        if rlr9 is None:
            bullets.append("R-18 PASS → queue R-LR-9 für 1.8M-Tick-Vollskala-Verifikation von G24")
        elif rlr9.get("status") == "passed":
            bullets.append("R-LR-9 PASS — erste defensible content-learning-Result. G20-G23 (kommunikation-Pfad) als nächstes")
        elif _terminal_status(rlr9) == "null":
            bullets.append("R-LR-9 NULL bei voller Skala — G25 designen (Energie-DICHTE statt energie-Gewichtung)")
        else:
            bullets.append("R-LR-9 läuft / queued — Verdict abwarten")
    elif r18_term == "null":
        bullets.append("R-18 NULL — Iteration-Cap G24 verbraucht (1 von 3)")
        bullets.append("Nächster Schritt: G25 Amendment designen — Energie-DICHTE als alternative Architektur-Hypothese")
        bullets.append("(Statt energie-gewichtete Plastizität: mehr Quanten injizieren bei hoher Amplitude)")
    elif r18_term == "failed":
        bullets.append("R-18 failed — implementation-bug? Logs prüfen, neu queuen")

    # Long-run pipeline state
    rlr_running = any(
        (Path.home() / ".eqmod/long-run/current.pid").exists()
        for _ in [None]
    )
    rlr_queued = sum(1 for i in long_items if i.get("status") == "queued")
    if rlr_running:
        bullets.append("Long-run dispatcher arbeitet — keine Eingabe nötig")
    elif rlr_queued > 0:
        bullets.append(f"Long-run dispatcher hat {rlr_queued} queued items — fires nächsten Tick")
    else:
        bullets.append("Long-run dispatcher ist leer — neue Hypothesen queue")

    # If queue is empty
    short_queued = sum(1 for i in short_items if i.get("status") == "queued")
    if short_queued == 0 and r18_term is not None:
        bullets.append("Short-queue leer — nächste Amendment-Iteration oder Pivot-Trigger queue")

    return bullets


def cmd_results(_args: str) -> str:
    """Natural-language summary: achievements + running + recommendation."""
    try:
        short_q = yaml.safe_load(QUEUE_SHORT.read_text()) if QUEUE_SHORT.exists() else {}
    except Exception as exc:
        return f"short-queue parse error: {exc!r}"
    try:
        long_q = yaml.safe_load(QUEUE_LONG.read_text()) if QUEUE_LONG.exists() else {}
    except Exception:
        long_q = {}

    short_items = short_q.get("items") or []
    long_items = long_q.get("items") or []

    sections = []

    sections.append("ERREICHT (zuletzt abgeschlossen):")
    for b in _summarise_achievements(short_items, long_items):
        sections.append(f"- {b}")

    sections.append("\nLÄUFT JETZT:")
    for b in _summarise_running(short_items, long_items):
        sections.append(f"- {b}")

    sections.append("\nARCHITEKTUR-STAND:")
    for b in _summarise_architecture(short_items):
        sections.append(f"- {b}")

    sections.append("\nEMPFEHLUNG:")
    for b in _next_recommendation(short_items, long_items):
        sections.append(f"- {b}")

    text = "\n".join(sections)
    # Telegram caps at 4096; leave margin for the subject prefix.
    if len(text) > 3500:
        text = text[:3450] + "\n...(truncated; siehe /status /queue)"
    return text


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
    "/results": cmd_results,
    "/status": cmd_status,
    "/queue": cmd_queue,
    "/requeue": cmd_requeue,
    "/fail": cmd_fail,
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
    # Surface send failures in the log so future "silent /results" incidents
    # are visible at the receiver layer instead of just at Telegram's edge.
    # The 2026-05-20T23:43 incident was diagnosed only because the user
    # reported the missing reply; the receiver had logged a clean handler
    # exit and the Markdown 400 from Telegram had nowhere to surface.
    res = send_telegram(subject, reply)
    if isinstance(res, tuple):
        ok, reason = res
    else:
        ok, reason = bool(res), ""
    if not ok:
        log(f"  send_telegram failed for cmd {cmd!r}: {reason!r}")


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
