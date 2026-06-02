# G65 — Competitive inhibition (k-WTA): suppress control co-firing for a selective write

Pre-registered: 2026-06-02 (BEFORE the run). G64 localized the leak: control bridges latch because
control atoms CO-FIRE on their own (ambient field), independent of stim's emission range. The
inhibition half of the directional self-limiting write targets exactly this: a global
k-WINNER-TAKE-ALL firing rule (`global_wta_k`) — only the top-K most-charged atoms fire each tick;
weakly-driven atoms are laterally suppressed. The stim region (n=40 direct injection → high charge)
wins the competition and fires/co-fires; the control region (weak ambient charge) is suppressed →
no control co-firing → no control latch → selective write. This is a genuinely NEW mechanism vs the
~30 prior memory experiments.

## Method
BET-099 correlation-memory protocol + `global_wta_k` ∈ {5, 10, 20}. Arms: LOC + UNI at each k.
Fraction-selective metric (stim_mean>3 AND ctrl_mean<3). Seed 42 (replicate any pass across seeds).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G65a | Some k WRITES selectively | ∃ k: LOC fraction of STIM checkpoints selective ≥ 0.5 |
| G65b | …and RECALLS persistently | the SAME k: LOC fraction of POST checkpoints (≥ stim_end+2000 s) selective ≥ 0.5 |
| G65c | …with the uniform control failing | the same k: UNI POST selective fraction < 0.25 |

PASS = G65a–c at one k → competitive inhibition gives the programme's first SELECTIVE PERSISTENT
memory: suppressing weakly-driven (control) firing lets only the strongly-driven (stim) write
latch and persist. Would break the deadlock's firing form and reopen cognition. Replicate across
seeds (G66) before any claim. NULL: if no k both writes and recalls selectively, even competitive
inhibition cannot separate the write from the leak — the contamination survives (control still
latches via residual co-firing or well drift), deepening the deadlock. Honest either way. No
post-hoc threshold tuning (k sweep pre-registered; "works" = all three bars at one k).
