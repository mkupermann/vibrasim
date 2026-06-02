# G73 — Quiescent substrate: fast charge decay so only directly-driven atoms fire

Pre-registered: 2026-06-03. The write-rule family (G64–G72) is exhausted; the root cause is that
the control region is NEVER BLANK — it co-fires and consolidates on its own. G64–G72 all operated
on firing SELECTION or the plasticity RULE. G73 targets a genuinely new lever: CHARGE PERSISTENCE
(`tau_membrane`). Atoms hold charge (tau=0.5), so undriven control atoms accumulate enough to fire.
Make charge decay FAST (low tau) → only atoms receiving DIRECT, continuous drive (the stim region,
injected every tick) can reach threshold; control (no direct drive) cannot accumulate → stays blank.
A quiescent substrate suppresses baseline activity WITHOUT suppressing the driven write.

## Method
BET-099 protocol + t_refractory=0.5 (selective write), sweeping `tau_membrane` ∈ {0.05, 0.1, 0.2}
(vs 0.5). Arms LOC + UNI. Fraction-selective metric (locked, as all G64–G72). Seed 42.

## Bars (locked pre-run — standard, identical to G64–G72)
| ID | Criterion | Bar |
|----|-----------|-----|
| G73a | Selective write | ∃ tau: LOC STIM fraction-selective ≥ 0.5 |
| G73b | Persistent recall | same tau: LOC POST (≥ stim_end+2000 s) fraction-selective ≥ 0.5 |
| G73c | Uniform control fails | same tau: UNI POST fraction-selective < 0.25 |

PASS = G73a–c at one tau → a quiescent substrate (fast charge decay) keeps control blank, letting
the refractory write be cleanly selective and persistent: selective persistent memory via making the
MEDIUM quiescent rather than tuning the write rule. Replicate across seeds before any claim. NULL: if
low tau also kills the stim write (stim can't accumulate either) or control still fires/consolidates,
the homogeneous-activity root is robust to charge-persistence control — the deadlock is fundamental
and refractory 0.44 stands as the high-water mark. Honest either way. No post-hoc threshold tuning.
