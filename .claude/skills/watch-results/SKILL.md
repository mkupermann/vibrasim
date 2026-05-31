---
name: watch-results
description: Show EQMOD test/experiment results in real time, text-only, in the terminal. Triggers on requests to watch test results live, see verdicts as experiments finish, monitor a parallel sweep, or get a quick board of all current BET outcomes. Wraps tools/watch_results.py.
---

# Live Results Watcher

`tools/watch_results.py` tails every `bet*_out.txt` in the repo and prints ONLY
the result-relevant lines (test header, acceptance bars, the `--- VERDICT ---`
block, `PASS/NULL/FAIL`, milestone markers, `wall budget hit`) — the
per-checkpoint `[WARM]/[STIM]/[POST]` progress spam is filtered out. Stdlib only,
no venv needed.

## Use

- **Live tail** (recommended for watching a sweep land):
  ```
  python tools\watch_results.py
  ```
  Prints the current results board on startup, then a
  `--- now watching for NEW results (live) ---` separator, then streams each new
  verdict block the instant a test completes. Ctrl+C to stop. Run it in a
  SEPARATE terminal (it blocks until Ctrl+C).
- **One-shot board** (catch up on all past results, then exit):
  ```
  python tools\watch_results.py --once
  ```

## Notes

- Auto-discovers new `bet*_out.txt` files (so it shows variants a parallel sweep
  creates), and resets correctly when a test is re-run (file overwrite).
- Tolerates non-ASCII on Windows consoles (replaces, never crashes).
- For experiments to stream here, their runner must write stdout DIRECTLY to
  `bet<NNN>_out.txt` (not via `tail`/`grep`, which buffer) and use
  `print(..., flush=True)`. See the `bet-experiment` skill.
- The watcher only reads files; it never touches the experiments. Safe to start,
  stop, and restart any time.
