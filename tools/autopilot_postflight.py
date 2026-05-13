"""EQMOD autopilot postflight check.

Runs AFTER a headless Claude session exits. The session may have ended for any
of: acceptance met, time-budget exhausted, --max-turns hit, 429 rate-limit,
crash. Postflight is the objective referee.

Responsibilities:
    1. Run the item's pre-registered tests; compute objective verdict.
    2. Update QUEUE.yaml status + attempts based ONLY on test outcome
       (Claude does not get to claim its own verdict).
    3. Verify negative control was run if required.
    4. Append a 5-line summary to LOGBOOK.md.
    5. Commit on autopilot/<item-id> branch (as the autopilot, with the hook armed).
    6. Push to origin/autopilot/<item-id>.

Exit non-zero on any sanity failure (e.g. forbidden file edited despite hook).
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE_PATH = REPO / ".eqmod/autopilot/QUEUE.yaml"
STATE_DIR = Path.home() / ".eqmod/autopilot"
CURRENT_ITEM_PATH = STATE_DIR / "current_item.txt"
LOGBOOK_PATH = REPO / "LOGBOOK.md"

# Forbidden paths the autopilot must not have touched in this session's diff.
FORBIDDEN_PATHS = {
    "docs/marker_protocol.md",
    "docs/marker_protocol_G20-G23_addendum.md",
    ".eqmod/autopilot/CHARTER.md",
}


def die(msg: str, code: int = 1) -> None:
    print(f"postflight: FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)


def load_queue() -> dict:
    return yaml.safe_load(QUEUE_PATH.read_text())


def save_queue(q: dict) -> None:
    QUEUE_PATH.write_text(yaml.safe_dump(q, sort_keys=False, allow_unicode=True))


def main() -> None:
    if not CURRENT_ITEM_PATH.exists():
        die("no current_item.txt — preflight did not run this cycle?")
    item_id = CURRENT_ITEM_PATH.read_text().strip()

    queue = load_queue()
    items = queue.get("items") or []
    item = next((i for i in items if i.get("id") == item_id), None)
    if item is None:
        die(f"current item {item_id} not in queue — corrupted state")

    branch_name = f"autopilot/{item_id}"
    r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if r.stdout.strip() != branch_name:
        die(f"not on {branch_name} (HEAD is {r.stdout.strip()})")

    # 1. Forbidden-path diff sanity (defense in depth — hook should have caught earlier).
    r = run(["git", "diff", "main..HEAD", "--name-only"])
    touched = set(r.stdout.strip().splitlines()) if r.stdout.strip() else set()
    blocked = touched & FORBIDDEN_PATHS
    if blocked:
        die(f"forbidden files touched between main..HEAD: {sorted(blocked)}")

    # 2. Determine acceptance test command. Convention: each acceptance entry of the form
    #    "tests/foo.py::bar PASSES ..." gets the prefix before " PASSES" / " FAILS" run as
    #    a pytest target. Negative-control entries are flagged separately.
    accept = item.get("preregistered_acceptance") or []
    pass_targets = []
    fail_targets = []  # negative controls — these MUST fail
    for line in accept:
        m = re.match(r"^(.+?)\s+(PASSES|FAILS)\b", line.strip())
        if not m:
            continue
        target, verdict = m.group(1).strip(), m.group(2)
        # Only treat it as a runnable target if it looks like a pytest node id.
        if "tests/" in target or "::" in target:
            (pass_targets if verdict == "PASSES" else fail_targets).append(target)

    # 3. Run PASS-targets — expect rc=0
    pass_ok = True
    pass_log = ""
    if pass_targets:
        r = run([str(REPO / ".venv/bin/python"), "-m", "pytest", *pass_targets, "--tb=short", "-q"])
        pass_log = (r.stdout + r.stderr)[-2000:]
        pass_ok = r.returncode == 0

    # 4. Run FAIL-targets (negative controls) — expect rc!=0
    ctrl_ok = True
    ctrl_log = ""
    if fail_targets:
        r = run([str(REPO / ".venv/bin/python"), "-m", "pytest", *fail_targets, "--tb=no", "-q"])
        ctrl_log = (r.stdout + r.stderr)[-2000:]
        ctrl_ok = r.returncode != 0  # MUST fail

    # 5. Determine objective verdict
    if not pass_targets and not fail_targets:
        # Item has no runnable test targets — treat as NULL (mis-specified acceptance).
        verdict = "null"
        rationale = "acceptance has no runnable pytest targets"
    elif pass_ok and ctrl_ok:
        verdict = "passed"
        rationale = "all pass-targets passed; all negative controls failed as required"
    elif pass_ok and not ctrl_ok and fail_targets:
        verdict = "null"
        rationale = "pass-targets passed BUT negative control also passed — state detector, not finding"
    else:
        verdict = "null"
        rationale = "pass-targets did not pass"

    # 6. Update queue: status, attempts, last_session
    item["attempts"] = int(item.get("attempts", 0)) + 1
    item["last_session"] = _dt.datetime.now().isoformat()
    if verdict == "passed":
        item["status"] = "passed"
    elif item["attempts"] >= 3:
        item["status"] = "failed"
        rationale += f" (attempts={item['attempts']}, written off per 3-strike rule)"
    else:
        item["status"] = "null"
    save_queue(queue)

    # 7. Append LOGBOOK entry (5 lines as charter requires)
    r = run(["git", "diff", "main..HEAD", "--shortstat"])
    shortstat = r.stdout.strip()
    logbook_entry = (
        f"\n\n## {_dt.date.today().isoformat()} — autopilot session: {item_id}\n\n"
        f"- **Verdict**: {verdict.upper()}\n"
        f"- **Attempts**: {item['attempts']}/3\n"
        f"- **Diff**: {shortstat or 'no changes'}\n"
        f"- **Rationale**: {rationale}\n"
    )
    with LOGBOOK_PATH.open("a") as f:
        f.write(logbook_entry)

    # 8. Stage and commit (autopilot identity, hook armed)
    env = os.environ.copy()
    env["EQMOD_AUTOPILOT"] = "1"

    run(["git", "add", "LOGBOOK.md", ".eqmod/autopilot/QUEUE.yaml"], env=env)
    # Stage any other tracked changes the session made (tests, code).
    run(["git", "add", "-u"], env=env)

    r = run(["git", "status", "--porcelain"], env=env)
    if not r.stdout.strip():
        print(f"postflight: nothing to commit for {item_id} (verdict={verdict})")
        return

    msg = (
        f"autopilot {item_id}: {verdict} (attempt {item['attempts']}/3)\n\n"
        f"{rationale}\n\n"
        f"Co-Authored-By: Claude (autopilot) <noreply@anthropic.com>"
    )
    r = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=REPO, capture_output=True, text=True, env=env,
    )
    if r.returncode != 0:
        die(f"commit failed (hook reject?):\nstdout={r.stdout}\nstderr={r.stderr}")

    # 9. Push to autopilot branch (forced-with-lease only as a safety net, not force).
    r = subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        cwd=REPO, capture_output=True, text=True, env=env,
    )
    if r.returncode != 0:
        # Push failure is not fatal for the session — we have the local commit.
        print(f"postflight: WARN: push failed: {r.stderr}", file=sys.stderr)

    print(f"postflight OK — item={item_id} verdict={verdict} attempts={item['attempts']}/3")


if __name__ == "__main__":
    main()
