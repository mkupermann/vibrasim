"""EQMOD autopilot Opus postmortem.

ONLY entry point that may invoke Opus 4.7. Called by run_autopilot.sh after
the postflight has set a NULL or FAIL verdict on the current item. Argument:
the item id.

The Opus session is single-shot — it reads the brief, the LOGBOOK entry the
postflight just wrote, the diff on autopilot/<id>, and produces a longer
postmortem appended to LOGBOOK.md. It does NOT modify code, run tests, or
attempt to "rescue" the item.

This is the only Opus invocation during the vacation. Hard-gated.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: autopilot_opus_postmortem.py <item-id>", file=sys.stderr)
        sys.exit(2)

    item_id = sys.argv[1]

    prompt = f"""You are writing a postmortem for EQMOD autopilot item {item_id}.

The autopilot ran a session on this item with Sonnet 4.6 and the postflight
script set its verdict to NULL or FAIL. Your single job: write a one-page
postmortem appended to LOGBOOK.md.

Context to read (in order):
  1. .eqmod/autopilot/QUEUE.yaml — the locked pre-registered acceptance for {item_id}
  2. .eqmod/autopilot/CHARTER.md — the operating envelope the session ran under
  3. The item's brief under docs/amendments/
  4. The latest LOGBOOK.md entry for this session (5-line short version)
  5. The full diff: git log autopilot/{item_id} --not main, plus git diff main..autopilot/{item_id}

Write a postmortem with these sections:
  - What the acceptance asked for
  - What the substrate actually produced
  - Most likely mechanism for the gap (one paragraph, no deflection)
  - Whether the gap is in the implementation, hypothesis, or acceptance spec
  - Recommended next step if Michael wants to re-queue: redesign the acceptance,
    fix the implementation, abandon the hypothesis, or close

Append the postmortem to LOGBOOK.md under a heading like:
    ## {item_id} — Opus postmortem ({{today's date}})

DO NOT edit code. DO NOT edit tests. DO NOT edit marker_protocol files. DO NOT edit QUEUE.yaml.
DO NOT push. Just append to LOGBOOK and exit.
"""

    cmd = [
        "claude",
        "--print",
        "--model", "claude-opus-4-7",
        "--max-turns", "20",
        "--permission-mode", "acceptEdits",
        "--allowed-tools", "Read,Edit,Bash,Grep,Glob",
        prompt,
    ]
    subprocess.run(cmd, cwd=REPO, check=False)


if __name__ == "__main__":
    main()
