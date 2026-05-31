"""Realtime, text-only results viewer for BET experiments.

Tails every tools-written `bet*_out.txt` in the repo and prints ONLY the
result-relevant lines (test header, acceptance bars, VERDICT block, PASS/NULL/
FAIL, milestone markers, probe results). The per-checkpoint progress spam
([WARM]/[STIM]/[POST] ...) is filtered out.

Usage:
    python tools/watch_results.py          # live tail, Ctrl+C to stop
    python tools/watch_results.py --once    # print current results once and exit

Stdlib only — runs with any Python, no venv needed.
"""
import os
import re
import sys
import time
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Windows consoles default to cp1252 and choke on → — etc. in the logs.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# INCLUDE result lines; EXCLUDE per-checkpoint progress.
INCLUDE = re.compile(
    r"(^=== |VERDICT|^\s*T\d{2,3}[a-z]\b|BET-\d+\s*:|^\s*(PASS|NULL|FAIL)\b"
    r"|\bDONE\b|^>>>|fire ratio|_RESULT|flux_ref|wall budget)", re.I)
EXCLUDE = re.compile(r"\[(WARM|CAL|STIM|POST|SMOKE)\]")


def emit(fname, line):
    line = line.rstrip()
    if not line:
        return
    if EXCLUDE.search(line):
        return
    if INCLUDE.search(line):
        tag = os.path.basename(fname)[:-8]  # strip "_out.txt"
        print(f"[{tag}] {line.strip()}", flush=True)


def scan_once():
    for f in sorted(glob.glob(os.path.join(REPO, "bet*_out.txt"))):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    emit(f, line)
        except OSError:
            pass


def watch():
    print("=== BET results watcher — live (Ctrl+C to stop) ===", flush=True)
    offsets = {}
    # Start at end of existing files so we only show NEW results, but print a
    # one-line note of the most recent verdict already on disk.
    for f in glob.glob(os.path.join(REPO, "bet*_out.txt")):
        try:
            offsets[f] = os.path.getsize(f)
        except OSError:
            offsets[f] = 0
    while True:
        for f in sorted(glob.glob(os.path.join(REPO, "bet*_out.txt"))):
            try:
                size = os.path.getsize(f)
            except OSError:
                continue
            prev = offsets.get(f, 0)
            if size < prev:          # file was overwritten (re-run) → restart
                prev = 0
            if size == prev:
                continue
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    fh.seek(prev)
                    chunk = fh.read()
                    offsets[f] = fh.tell()
            except OSError:
                continue
            for line in chunk.splitlines():
                emit(f, line)
        time.sleep(1.0)


if __name__ == "__main__":
    if "--once" in sys.argv:
        scan_once()
    else:
        try:
            watch()
        except KeyboardInterrupt:
            print("\n[watcher stopped]", flush=True)
