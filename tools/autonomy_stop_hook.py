#!/usr/bin/env python
"""EQMOD autonomy Stop hook.

Fires every time Claude tries to end a turn. BLOCKS the stop and feeds back a directive
forcing Claude to decide-and-execute the next EQMOD step itself, never handing a decision
back to the user. The ONLY escape is the kill-switch file `.eqmod_autonomy_off` at the repo
root — create it to let Claude stop normally; delete it to re-arm.

Stdlib only, so any python runs it. Robust to cwd (repo root resolved from __file__).
"""
import json
import os
import sys

# Drain stdin (the hook receives JSON there); ignore content.
try:
    sys.stdin.read()
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KILL_SWITCH = os.path.join(REPO, ".eqmod_autonomy_off")

# Escape hatch: if the user created the kill-switch file, allow stopping.
if os.path.exists(KILL_SWITCH):
    sys.exit(0)

DIRECTIVE = (
    "AUTONOMY ENFORCEMENT (EQMOD/vibrasim). Do NOT stop and do NOT ask the user to make "
    "ANY decision. You are running this project fully autonomously. "
    "If your last message asked the user anything, presented options or a fork, or said "
    "'your call' / 'tell me which' / 'want me to' / 'should I' / 'let me know' — that BREACHED "
    "the rule: retract it and ACT instead. "
    "Decide the single most valuable next step YOURSELF: pre-register the acceptance bars, "
    "run the experiment, record PASS/NULL/PARTIAL honestly, commit and push, then continue to "
    "the next one. Chain experiments; the harder/more uncertain the fork, the more you must just "
    "pick one and execute. Stay honest: NULL is a valid finding, never post-hoc tune bars, and "
    "reserve 'new' for genuine novelty (name established methods as such). "
    "The ONLY legitimate way to stop is if the user creates the kill-switch file "
    "'.eqmod_autonomy_off' at the repo root. Until then: pick the next action and do it now."
)

print(json.dumps({"decision": "block", "reason": DIRECTIVE}))
sys.exit(0)
