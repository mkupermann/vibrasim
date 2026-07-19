"""Continuous headless laboratory loop — keeps running until stop file.

Stop: create file ``.eqmod_lab_stop`` at repo root (or Ctrl+C).

Logs: ~/.eqmod/bet/LAB_CONTINUOUS.log  (and stdout)

Usage:
    python tools/lab_continuous.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = ROOT / ".eqmod_lab_stop"
LOG_DIR = Path.home() / ".eqmod" / "bet"
LOG = LOG_DIR / "LAB_CONTINUOUS.log"
STATUS = LOG_DIR / "LAB_STATUS.json"
PY = sys.executable

# Queue of headless lab jobs (smoke = fast heartbeat; full = science)
# After each full cycle, loop again with smokes + occasional fulls.
CYCLE = [
    ("BP-A1-smoke", [str(ROOT / "tools" / "run_bp_a1_field_bind.py"), "--smoke"]),
    ("BP-B3-smoke", [str(ROOT / "tools" / "run_bp_b3_multibit_molecule.py"), "--smoke"]),
    ("BP-B5-smoke", [str(ROOT / "tools" / "run_bp_b5_fingerprint_under_motion.py"), "--smoke"]),
    ("BP-B6-smoke", [str(ROOT / "tools" / "run_bp_b6_two_species_coexistence.py"), "--smoke"]),
    ("BP-B7-smoke", [str(ROOT / "tools" / "run_bp_b7_fingerprint_ambient.py"), "--smoke"]),
    ("BP-D1-smoke", [str(ROOT / "tools" / "run_bp_d1_matter_position_plus_species.py"), "--smoke"]),
    ("BP-A2-smoke", [str(ROOT / "tools" / "run_bp_a2_density_ratio.py"), "--smoke"]),
]


def log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now().isoformat(timespec='seconds')}  {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_status(payload: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_job(name: str, argv: list[str]) -> int:
    log(f"START {name}: {' '.join(argv)}")
    write_status({
        "state": "RUNNING",
        "job": name,
        "cmd": argv,
        "pid": None,
        "started": datetime.now().isoformat(timespec="seconds"),
        "log": str(LOG),
    })
    try:
        proc = subprocess.run(
            [PY, *argv],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # tail last lines into continuous log
        tail = (proc.stdout or "")[-2000:]
        if proc.stderr:
            tail += "\n[stderr]\n" + proc.stderr[-1000:]
        for line in tail.strip().splitlines()[-15:]:
            log(f"  | {line}")
        log(f"DONE {name} exit={proc.returncode}")
        write_status({
            "state": "IDLE_BETWEEN_JOBS",
            "last_job": name,
            "last_exit": proc.returncode,
            "finished": datetime.now().isoformat(timespec="seconds"),
            "log": str(LOG),
        })
        return proc.returncode
    except Exception as exc:
        log(f"FAIL {name}: {exc}")
        write_status({"state": "ERROR", "job": name, "error": str(exc), "log": str(LOG)})
        return 1


def main() -> int:
    if STOP.exists():
        STOP.unlink()
    log("=" * 60)
    log("LAB CONTINUOUS started (headless). Stop: create .eqmod_lab_stop")
    log(f"python={PY}")
    log(f"log={LOG}")
    cycle_n = 0
    try:
        while not STOP.exists():
            cycle_n += 1
            log(f"===== CYCLE {cycle_n} =====")
            for name, argv in CYCLE:
                if STOP.exists():
                    break
                run_job(name, argv)
                # brief pause so status file is readable between jobs
                time.sleep(1.0)
            if STOP.exists():
                break
            log(f"cycle {cycle_n} complete; sleeping 5s before next cycle")
            write_status({
                "state": "SLEEPING",
                "cycle": cycle_n,
                "next_in_sec": 5,
                "log": str(LOG),
            })
            for _ in range(5):
                if STOP.exists():
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        log("KeyboardInterrupt — lab continuous stopping")
    log("LAB CONTINUOUS stopped")
    write_status({
        "state": "STOPPED",
        "stopped": datetime.now().isoformat(timespec="seconds"),
        "log": str(LOG),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
