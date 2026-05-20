#!/usr/bin/env bash
# Launchd wrapper for the Telegram receiver. Lives in ~/.eqmod/autopilot/
# (outside the repo, outside ~/Documents) so launchd can bash-exec it
# without macOS 15's FDA-on-bash-from-launchd silent-deny issue.
set -u
REPO="/Users/mkupermann/GitHub/EQMOD"
exec "$REPO/.venv/bin/python" "$REPO/tools/notify_telegram_receiver.py"
