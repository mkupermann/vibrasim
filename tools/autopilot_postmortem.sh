#!/usr/bin/env bash
# EQMOD autopilot post-vacation review.
# Run this when you get back. One-glance summary of the 14 days.

set -uo pipefail

REPO="/Users/mkupermann/Documents/GitHub/EQMOD"
STATE_DIR="$HOME/.eqmod/autopilot"

cd "$REPO" || exit 1

echo "=================================================================="
echo "EQMOD autopilot post-vacation review — $(date -Iseconds)"
echo "=================================================================="

echo ""
echo "--- QUEUE STATE ---"
"$REPO/.venv/bin/python" - <<'PY'
import yaml
from pathlib import Path
q = yaml.safe_load(Path("/Users/mkupermann/Documents/GitHub/EQMOD/.eqmod/autopilot/QUEUE.yaml").read_text())
for i in q.get("items") or []:
    print(f"  {i.get('id', '?'):6s}  {i.get('status', '?'):12s}  attempts={i.get('attempts', 0)}/3  {i.get('title', '')[:60]}")
PY

echo ""
echo "--- HUMAN_NEEDED ENTRIES ---"
if [[ -f "$STATE_DIR/HUMAN_NEEDED.md" ]]; then
  cat "$STATE_DIR/HUMAN_NEEDED.md"
else
  echo "  (none)"
fi

echo ""
echo "--- AUTOPILOT BRANCHES (local + remote) ---"
git fetch origin --quiet 2>/dev/null || true
git branch -a --list 'autopilot/*' | sed 's/^/  /'

echo ""
echo "--- AUTOPILOT COMMITS (since vacation start, all autopilot branches) ---"
git log --all --author="Claude" --since="14 days ago" --pretty="  %h %ad %s" --date=short | head -100

echo ""
echo "--- LOGBOOK TAIL (last 80 lines) ---"
tail -80 "$REPO/LOGBOOK.md"

echo ""
echo "--- SESSION-LOG LAST RUN ---"
tail -50 "$STATE_DIR/session.log" 2>/dev/null || echo "  (no session log)"

echo ""
echo "=================================================================="
echo "Next steps:"
echo "  1. Review each autopilot/<G-id> branch. PASS items: validate acceptance is honest. NULL items: read postmortem."
echo "  2. For items to keep: git checkout main && git merge --no-ff autopilot/<G-id>"
echo "  3. For items to discard: git branch -D autopilot/<G-id> && git push origin --delete autopilot/<G-id>"
echo "  4. Stop the launchd jobs: launchctl unload ~/Library/LaunchAgents/com.eqmod.autopilot.plist"
echo "                            launchctl unload ~/Library/LaunchAgents/com.eqmod.watchdog.plist"
echo "  5. Clear runtime state if starting fresh: rm -rf ~/.eqmod/autopilot/{current_item.txt,last_tick.txt,session.log}"
echo "=================================================================="
