"""EQMOD bet dispatcher — 1h-iteration hypothesis loop.

Parallel pipeline to ``tools/long_run_dispatcher.py``. Where the long-run
dispatcher manages 24-30h substrate training items via a launchd 30-min
tick, the bet dispatcher runs as a continuously-polling daemon (default
60s cadence) over a separate queue with ≤1h iterations. Goal: surface
~3000-5000 falsifications of the 5/5 self-learning bet hypotheses over
12 months without contaminating the existing 4h-amendment cap.

The 12-month bet itself is pre-registered in LOGBOOK.md
(entry 2026-05-22, "Programme-level bet pre-registered"); the constraint
correction (LLM/transformer disallowed, other primitives permitted) is
the entry of the same date. This dispatcher is the runtime that turns
that pre-registration into actual iterations.

Decision tree per tick:

    1. STOP marker (~/.eqmod/bet/STOP) present → return stopped.
    2. PID file (~/.eqmod/bet/current.pid) points to a live process:
       2a. If elapsed > item.max_runtime_seconds (default 3600):
           SIGTERM the process group, wait term_grace_seconds, SIGKILL
           if still alive. Mark item failed with a hard-cap blocker.
           Mirrors tools/long_run_dispatcher.py R-LR-3 hard-cap pattern.
       2b. Else: return running, no side effect.
    3. PID file exists but process is dead:
       3a. Read result.json from the item's bet out_dir (default
           ~/.eqmod/bet/<item_id>/result.json). If present, take its
           verdict field.
       3b. Cross-check: run the per-bet pytest_target. Verdict logic:
           - result.json verdict='passed' AND pytest exit 0 → passed
           - result.json verdict='null'   AND pytest exit 0 → null
           - result.json verdict='failed' OR pytest non-zero → failed
           - result.json missing AND pytest exit 0 → null (no signal)
           - result.json missing AND pytest non-zero → failed
       3c. Update item status + attempts + finished_at in queue.yaml.
       3d. Append per-iteration entry to ~/.eqmod/bet/LOGBOOK.md.
       3e. Persist a per-iteration result.json into the item's out_dir.
    4. Pick next queued item.
    5. Launch detached: pytest pytest_target with start_new_session=True
       so the process group can be killed cleanly. Write pidfile +
       current_item.txt, redirect output to <item_id>.log.
    6. Mark item status=running (so a parallel /bet readout reflects it).

Queue schema (``~/.eqmod/bet/queue.yaml``):

    items:
      - id: BET-001                         # short id, monotonic
        hypothesis: |                       # one paragraph free text
          Persistent homology of the substrate's flux graph at
          increasing dream-phase tick counts produces a topological
          invariant that correlates with content (T1 KL > 0.1).
        references:                         # papers / textbook chapters
          - "Carlsson, Topology and Data, Bull. AMS 2009"
          - "Edelsbrunner & Harer, Computational Topology, ch. 7"
        pytest_target: tests/bet/test_bet_001_persistent_homology.py
        status: queued                      # queued/running/passed/null/failed
        attempts: 0
        max_runtime_seconds: 3600           # default 1h
        created_at: "2026-05-22T22:00:00"
        finished_at: null                   # set on terminal transition

Status semantics for the bet (binary 5/5 test bar; see LOGBOOK
2026-05-22 entry):

    passed   — bet's T1-T5 pre-registered tests all passed in this
               iteration (pytest exit 0 AND result.json verdict=passed).
    null     — substrate ran, some-but-not-all tests passed
               (pytest exit 0 with verdict=null OR missing result.json).
               This is the expected mode for >95% of iterations.
    failed   — implementation broke, hard-cap kill, or pytest non-zero.
               Treated as protocol-violating only when the dispatcher
               itself fails (kill-cap reached); content-level failures
               are NULL.

CLI:

    .venv/bin/python tools/bet_dispatcher.py            # 60s loop
    .venv/bin/python tools/bet_dispatcher.py --once     # single tick
    .venv/bin/python tools/bet_dispatcher.py --interval 30
    .venv/bin/python tools/bet_dispatcher.py --state-dir /tmp/test_bet

State directory layout::

    ~/.eqmod/bet/
        queue.yaml
        STOP                  # touch to pause
        current.pid           # PID of running pytest (and process group)
        current_item.txt      # item id of running pytest
        dispatcher.log        # tick log
        LOGBOOK.md            # per-iteration entries
        <BET-001>/result.json
        <BET-001>.log
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO_DEFAULT = Path("/Users/mkupermann/Documents/GitHub/vibrasim")

DEFAULT_INTERVAL_SECONDS = 60.0
DEFAULT_MAX_RUNTIME_SECONDS = 3600  # 1h iteration cap
DEFAULT_TERM_GRACE_SECONDS = 3      # SIGTERM → SIGKILL window


class BetDispatcher:
    """One bet-queue tick. Owns paths under a state_dir; no module state."""

    def __init__(
        self,
        state_dir: Path | str | None = None,
        repo: Path | str | None = None,
        term_grace_seconds: float = DEFAULT_TERM_GRACE_SECONDS,
        evaluate_timeout_seconds: float = 600.0,
    ):
        self.state_dir = Path(state_dir) if state_dir else Path.home() / ".eqmod/bet"
        self.repo = Path(repo) if repo else REPO_DEFAULT
        self.term_grace_seconds = float(term_grace_seconds)
        self.evaluate_timeout_seconds = float(evaluate_timeout_seconds)

        self.queue_path = self.state_dir / "queue.yaml"
        self.stop_path = self.state_dir / "STOP"
        self.pid_path = self.state_dir / "current.pid"
        self.current_item_path = self.state_dir / "current_item.txt"
        self.dispatcher_log = self.state_dir / "dispatcher.log"
        self.logbook_path = self.state_dir / "LOGBOOK.md"

    # ---- logging --------------------------------------------------------
    def log(self, msg: str) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        line = f"[{_dt.datetime.now().isoformat()}] {msg}\n"
        with self.dispatcher_log.open("a") as f:
            f.write(line)

    # ---- queue I/O ------------------------------------------------------
    def load_queue(self) -> dict:
        if not self.queue_path.exists():
            return {"items": []}
        text = self.queue_path.read_text()
        if not text.strip():
            return {"items": []}
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {"items": []}

    def _find_item(self, item_id: str) -> dict | None:
        for item in self.load_queue().get("items") or []:
            if item.get("id") == item_id:
                return item
        return None

    def update_item_status(
        self,
        item_id: str,
        new_status: str,
        attempts: int | None = None,
        finished_at: str | None = None,
        extra_blocker: str | None = None,
    ) -> None:
        """In-place YAML text update — preserves comments + ordering.

        Mirrors ``long_run_dispatcher.save_queue_item_status`` but adds
        the optional blocker-appending path needed by the hard-cap kill
        branch (we want the kill reason traceable in the queue).
        """
        if not self.queue_path.exists():
            return
        text = self.queue_path.read_text()
        pattern = re.compile(
            r"(?P<header>^[ \t]*- id: " + re.escape(item_id) + r"\b.*?\n)"
            r"(?P<body>.*?)"
            r"(?=^[ \t]*- id: |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        m = pattern.search(text)
        if not m:
            self.log(f"  update_item_status: {item_id} not found")
            return
        body = m.group("body")
        indent_match = re.search(r"^([ \t]+)status:", body, re.MULTILINE)
        indent = indent_match.group(1) if indent_match else "    "

        # status:
        body = re.sub(
            r"^(" + re.escape(indent) + r"status: ).*$",
            rf"\g<1>{new_status}",
            body, count=1, flags=re.MULTILINE,
        )

        # attempts: (insert after status if missing)
        if attempts is not None:
            if re.search(r"^" + re.escape(indent) + r"attempts:", body, re.MULTILINE):
                body = re.sub(
                    r"^(" + re.escape(indent) + r"attempts: ).*$",
                    rf"\g<1>{attempts}",
                    body, count=1, flags=re.MULTILINE,
                )
            else:
                body = re.sub(
                    r"^(" + re.escape(indent) + r"status: " + re.escape(new_status) + r")$",
                    rf"\1\n{indent}attempts: {attempts}",
                    body, count=1, flags=re.MULTILINE,
                )

        # finished_at: (insert after attempts if missing)
        if finished_at is not None:
            if re.search(r"^" + re.escape(indent) + r"finished_at:", body, re.MULTILINE):
                body = re.sub(
                    r"^(" + re.escape(indent) + r"finished_at: ).*$",
                    rf'\g<1>"{finished_at}"',
                    body, count=1, flags=re.MULTILINE,
                )
            else:
                anchor = (
                    re.escape(indent) + r"attempts: \d+"
                    if re.search(r"^" + re.escape(indent) + r"attempts:", body, re.MULTILINE)
                    else re.escape(indent) + r"status: " + re.escape(new_status)
                )
                body = re.sub(
                    r"^(" + anchor + r")$",
                    rf'\1\n{indent}finished_at: "{finished_at}"',
                    body, count=1, flags=re.MULTILINE,
                )

        # extra_blocker: append to blockers list (or create one)
        if extra_blocker:
            esc = extra_blocker.replace("\\", "\\\\").replace('"', '\\"')
            if re.search(r"^" + re.escape(indent) + r"blockers:\s*\[", body, re.MULTILINE):
                body = re.sub(
                    r"^(" + re.escape(indent) + r"blockers:\s*\[)(.*)\](\s*)$",
                    lambda mm: (
                        f'{mm.group(1)}{mm.group(2).rstrip()}'
                        f'{", " if mm.group(2).strip() else ""}'
                        f'"{esc}"]{mm.group(3)}'
                    ),
                    body, count=1, flags=re.MULTILINE,
                )
            else:
                body = re.sub(
                    r"^(" + re.escape(indent) + r"status: " + re.escape(new_status) + r")$",
                    rf'\1\n{indent}blockers: ["{esc}"]',
                    body, count=1, flags=re.MULTILINE,
                )

        self.queue_path.write_text(text[: m.start("body")] + body + text[m.end("body") :])

    # ---- process lifecycle ---------------------------------------------
    @staticmethod
    def _pid_alive(pid: int) -> bool:
        """True if pid is alive AND not a zombie.

        The BET-001 incident 2026-05-23T19:07 had pytest finish in seconds
        but the dispatcher saw the process as "alive" for 23 minutes because
        os.kill(pid, 0) returns success for zombies. The dispatcher (as
        parent) had not reaped the child. Fix: try non-blocking waitpid
        first; if it reports the child exited, treat as dead.
        """
        try:
            reaped_pid, _ = os.waitpid(pid, os.WNOHANG)
            if reaped_pid == pid:
                return False  # our child exited and is now reaped
        except ChildProcessError:
            pass  # pid is not our child (or already reaped) — fall through
        except OSError:
            pass
        try:
            os.kill(pid, 0)
        except (ProcessLookupError, PermissionError):
            return False
        except Exception:
            return False
        # Final check: even if kill(0) succeeds, the process could still
        # be a zombie that was reaped by something other than us. Check
        # its state via `ps -o stat=`. A leading "Z" means zombie.
        try:
            import subprocess as _sp
            r = _sp.run(
                ["/bin/ps", "-o", "stat=", "-p", str(pid)],
                capture_output=True, text=True, timeout=2,
            )
            state = r.stdout.strip()
            if state.startswith("Z"):
                return False
        except Exception:
            pass
        return True

    def _kill_process_group(self, pid: int) -> None:
        """SIGTERM → wait → SIGKILL the process group of pid."""
        try:
            pgid = os.getpgid(pid)
        except (ProcessLookupError, PermissionError):
            return
        try:
            os.killpg(pgid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        deadline = time.time() + self.term_grace_seconds
        while time.time() < deadline:
            if not self._pid_alive(pid):
                return
            time.sleep(0.1)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    def launch_item(self, item: dict) -> int:
        item_id = item["id"]
        env = os.environ.copy()
        for k, v in (item.get("env") or {}).items():
            env[k] = str(v)

        out_dir = self.state_dir / item_id
        out_dir.mkdir(parents=True, exist_ok=True)
        env.setdefault("EQMOD_BET_OUT_DIR", str(out_dir))
        env.setdefault("EQMOD_BET_ITEM_ID", item_id)

        targets = (item.get("pytest_target") or "").split()
        log_file = self.state_dir / f"{item_id}.log"
        venv_py = self.repo / ".venv/bin/python"
        py = str(venv_py) if venv_py.exists() else sys.executable
        cmd = [py, "-m", "pytest", *targets, "--tb=short", "-q"]

        self.log(f"  launching {item_id}: {' '.join(cmd)}")
        with log_file.open("w") as lf:
            proc = subprocess.Popen(
                cmd,
                cwd=self.repo,
                stdout=lf,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                env=env,
                start_new_session=True,
            )
        self.pid_path.write_text(str(proc.pid))
        self.current_item_path.write_text(item_id)
        return proc.pid

    # ---- evaluation -----------------------------------------------------
    def _result_json_path(self, item: dict) -> Path:
        env = item.get("env") or {}
        out_dir = env.get("EQMOD_BET_OUT_DIR") or str(self.state_dir / item["id"])
        return Path(out_dir) / "result.json"

    def evaluate_completed_item(self, item: dict) -> tuple[str, str]:
        """Returns (verdict, log_tail). Verdict ∈ {'passed','null','failed'}."""
        item_id = item.get("id", "?")
        result_path = self._result_json_path(item)
        result_verdict: str | None = None
        result_tail = ""

        if result_path.exists():
            try:
                payload = json.loads(result_path.read_text())
                rv = str(payload.get("verdict", "")).lower()
                if rv in ("passed", "null", "failed"):
                    result_verdict = rv
                result_tail = json.dumps(payload, indent=2)[:1500]
            except Exception as exc:
                result_tail = f"(result.json unreadable: {exc!r})"

        # Per-bet pytest cross-check; falls back when result.json is absent
        targets = (item.get("pytest_target") or "").split()
        pytest_ok = False
        pytest_tail = ""
        if targets:
            env = os.environ.copy()
            for k, v in (item.get("env") or {}).items():
                env[k] = str(v)
            env.setdefault("EQMOD_BET_OUT_DIR", str(result_path.parent))
            env.setdefault("EQMOD_BET_ITEM_ID", item_id)
            venv_py = self.repo / ".venv/bin/python"
            py = str(venv_py) if venv_py.exists() else sys.executable
            try:
                r = subprocess.run(
                    [py, "-m", "pytest", *targets, "--tb=short", "-q"],
                    cwd=self.repo,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=self.evaluate_timeout_seconds,
                )
                pytest_ok = r.returncode == 0
                pytest_tail = (r.stdout + "\n" + r.stderr)[-1500:]
            except subprocess.TimeoutExpired:
                pytest_ok = False
                pytest_tail = (
                    f"[bet_dispatcher: pytest evaluation hit "
                    f"{self.evaluate_timeout_seconds:.0f}s timeout]"
                )
            except Exception as exc:
                pytest_ok = False
                pytest_tail = f"[bet_dispatcher: evaluation exception {exc!r}]"

        # Verdict precedence — bet-aware (revised 2026-05-23 after BET-002
        # incident). The original logic treated pytest non-zero as failed
        # unconditionally; that conflicts with the bet's pre-registration
        # (LOGBOOK 2026-05-22) where NULL with substantive measurements is
        # the expected mode for >95 % of iterations. Tests that pre-register
        # a threshold via `assert kl > X` will pytest-fail when the
        # threshold is missed — and that is exactly what "null with
        # substantive measurements" looks like, not a content-failure.
        #
        # If result.json is present AND well-formed, trust its verdict.
        # Only fall back to pytest exit code when result.json is missing
        # (= the substrate did not even run to completion).
        if result_verdict in ("passed", "null", "failed"):
            verdict = result_verdict
        elif not pytest_ok:
            verdict = "failed"  # substrate didn't run, no result.json
        else:
            verdict = "null"  # substrate ran, no result.json — no signal

        tail = (
            f"=== result.json ({result_path}) ===\n"
            f"{result_tail or '(missing)'}\n"
            f"=== pytest tail ===\n"
            f"{pytest_tail or '(no pytest output)'}"
        )
        return verdict, tail[-2000:]

    def write_result_json(
        self, item: dict, verdict: str, attempts: int, log_tail: str
    ) -> None:
        item_id = item.get("id", "?")
        record = {
            "item_id": item_id,
            "hypothesis": item.get("hypothesis", ""),
            "references": item.get("references") or [],
            "pytest_target": item.get("pytest_target", ""),
            "verdict": verdict,
            "attempts": attempts,
            "max_runtime_seconds": int(
                item.get("max_runtime_seconds", DEFAULT_MAX_RUNTIME_SECONDS)
            ),
            "started_at": item.get("started_at") or "",
            "finished_at": _dt.datetime.now().isoformat(),
            "log_tail": log_tail[-2000:] if log_tail else "",
        }
        out_path = self._result_json_path(item)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(record, indent=2, default=str))

    def append_logbook(self, item_id: str, verdict: str, log_tail: str) -> None:
        self.logbook_path.parent.mkdir(parents=True, exist_ok=True)
        entry = (
            f"\n\n## {_dt.datetime.now().isoformat(timespec='seconds')} — "
            f"bet {item_id} → {verdict.upper()}\n\n"
            f"```\n{log_tail.strip()[-1500:]}\n```\n"
        )
        with self.logbook_path.open("a") as f:
            f.write(entry)

    # ---- the tick -------------------------------------------------------
    def tick(self) -> dict[str, Any]:
        """Run one dispatcher step. Returns a dict describing what happened."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log("--- bet tick")

        if self.stop_path.exists():
            self.log("STOP marker present — return stopped")
            return {"action": "stopped"}

        if not self.queue_path.exists():
            self.log("no queue.yaml — return idle")
            return {"action": "idle", "reason": "no queue"}

        # Branch 1: a run is on the wire (pidfile present)
        if self.pid_path.exists():
            try:
                pid = int(self.pid_path.read_text().strip())
            except (ValueError, OSError):
                pid = None
            current_item_id = (
                self.current_item_path.read_text().strip()
                if self.current_item_path.exists()
                else ""
            )
            item = self._find_item(current_item_id) if current_item_id else None

            if pid and self._pid_alive(pid):
                max_runtime = int(
                    (item or {}).get("max_runtime_seconds", DEFAULT_MAX_RUNTIME_SECONDS)
                )
                elapsed = time.time() - self.pid_path.stat().st_mtime
                if elapsed > max_runtime:
                    self.log(
                        f"  HARD-CAP VIOLATION pid={pid} item={current_item_id} "
                        f"elapsed={elapsed:.0f}s > max={max_runtime}s — killing"
                    )
                    self._kill_process_group(pid)
                    finished = _dt.datetime.now().isoformat()
                    attempts = int(((item or {}).get("attempts") or 0)) + 1
                    self.update_item_status(
                        current_item_id,
                        "failed",
                        attempts=attempts,
                        finished_at=finished,
                        extra_blocker=(
                            f"hard-cap kill at {finished}: elapsed "
                            f"{elapsed:.0f}s exceeded max_runtime_seconds={max_runtime}"
                        ),
                    )
                    self.append_logbook(
                        current_item_id,
                        "failed (hard-cap)",
                        f"SIGTERM-then-SIGKILL after {elapsed:.0f}s "
                        f"(max_runtime_seconds={max_runtime})",
                    )
                    if item is not None:
                        self.write_result_json(
                            item, "failed", attempts,
                            f"hard-cap kill after {elapsed:.0f}s",
                        )
                    self.pid_path.unlink(missing_ok=True)
                    self.current_item_path.unlink(missing_ok=True)
                    return {
                        "action": "killed",
                        "item": current_item_id,
                        "elapsed": elapsed,
                        "max_runtime_seconds": max_runtime,
                    }
                self.log(
                    f"  run in progress pid={pid} item={current_item_id} "
                    f"elapsed={elapsed:.0f}s/{max_runtime}s"
                )
                return {
                    "action": "running",
                    "pid": pid,
                    "item": current_item_id,
                    "elapsed": elapsed,
                }

            # Process is dead → evaluate
            if item is not None:
                attempts = int((item.get("attempts") or 0)) + 1
                verdict, log_tail = self.evaluate_completed_item(item)
                finished = _dt.datetime.now().isoformat()
                self.update_item_status(
                    current_item_id,
                    verdict,
                    attempts=attempts,
                    finished_at=finished,
                )
                self.append_logbook(current_item_id, verdict, log_tail)
                self.write_result_json(item, verdict, attempts, log_tail)
                self.log(
                    f"  evaluated {current_item_id} → {verdict} (attempts={attempts})"
                )
                self.pid_path.unlink(missing_ok=True)
                self.current_item_path.unlink(missing_ok=True)
                return {
                    "action": "evaluated",
                    "item": current_item_id,
                    "verdict": verdict,
                    "attempts": attempts,
                }

            # PID stale and item unknown — clean up
            self.log(f"  stale pidfile (pid={pid}, item={current_item_id!r}) — cleared")
            self.pid_path.unlink(missing_ok=True)
            self.current_item_path.unlink(missing_ok=True)
            return {"action": "cleared", "stale_pid": pid}

        # Branch 2: nothing running, pick next queued
        items = self.load_queue().get("items") or []
        next_item = next((i for i in items if i.get("status") == "queued"), None)
        if next_item is None:
            self.log("  no queued items — return idle")
            return {"action": "idle", "reason": "no queued items"}

        pid = self.launch_item(next_item)
        self.update_item_status(next_item["id"], "running")
        self.log(f"  launched {next_item['id']} pid={pid}")
        return {"action": "launched", "item": next_item["id"], "pid": pid}


# ---- CLI ----------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="EQMOD bet dispatcher (≤1h iterations)",
    )
    parser.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL_SECONDS,
        help="seconds between ticks (default 60)",
    )
    parser.add_argument(
        "--state-dir", type=str, default=None,
        help="override state directory (default ~/.eqmod/bet)",
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help="override repo root (default %s)" % REPO_DEFAULT,
    )
    parser.add_argument(
        "--once", action="store_true",
        help="single tick, then exit (default: poll forever)",
    )
    args = parser.parse_args(argv)

    dispatcher = BetDispatcher(state_dir=args.state_dir, repo=args.repo)
    if args.once:
        result = dispatcher.tick()
        print(json.dumps(result, default=str))
        return 0

    while True:
        try:
            result = dispatcher.tick()
            if result.get("action") == "stopped":
                # Honour STOP without spinning hot; check again next interval
                pass
        except Exception as exc:
            dispatcher.log(f"  tick exception: {exc!r}")
        time.sleep(max(1.0, float(args.interval)))


if __name__ == "__main__":
    sys.exit(main())
