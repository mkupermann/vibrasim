# G69 — The LEAKY write: exploit the temporal structure of the drive

Pre-registered: 2026-06-03 (BEFORE the run). G64–G68 establish that EVERY firing-side lever (local
emission, k-WTA, refractory, threshold, combos) reproduces the write/contain tension and fails
identically — because the leak is NOT in firing dynamics. Reading the write rule
(apply_correlation_plasticity) makes it explicit: the bistable well is "no input = HOLD", so any
control bridge nudged past the midpoint is held and consolidated. The leak is the well, not firing.

**The evolution (new mechanism): a LEAKY write.** `bridge_leak_rate` adds a continuous downward
pull toward `bistable_low`, so a bridge stays high ONLY while continuously reinforced. This breaks
"no input = hold." The key insight every prior mechanism ignored: stim co-fires CONTINUOUSLY
(driven by injection) while control co-fires INTERMITTENTLY (ambient). With a leak, stim's
continuous drive beats the leak (holds → consolidates) while control's intermittent drive cannot
keep up (decays back to low between bumps → never consolidates). Selectivity emerges from the
TEMPORAL STRUCTURE of the drive, not its spatial location or firing competition.

## Method
BET-099 correlation-memory protocol + `bridge_leak_rate` ∈ {0.1, 0.2, 0.3} + consolidation on
(`bridge_consolidate_threshold`=5.0, so stim bridges that hold high get locked for persistence).
Arms: LOC + UNI per leak. Fraction-selective metric. Seed 42 (replicate any pass across seeds).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G69a | Some leak WRITES selectively | ∃ leak: LOC STIM fraction-selective ≥ 0.5 |
| G69b | …and RECALLS persistently | the SAME leak: LOC POST (≥ stim_end+2000 s) fraction-selective ≥ 0.5 |
| G69c | …with the uniform control failing | the same leak: UNI POST fraction-selective < 0.25 |

PASS = G69a–c at one leak → the leaky write gives the programme's FIRST selective persistent
memory: temporal-structure selectivity breaks the write=leak deadlock where spatial/firing fixes
could not. A milestone — replicate across seeds (G70) before any claim. NULL: if no leak both writes
and recalls selectively (e.g. every leak that decays control also decays stim, or control's ambient
co-firing is continuous enough to hold), the deadlock is robust even to temporal-structure
exploitation — the write=leak identity is deeper than the well's hold dynamics. Honest either way.
No post-hoc threshold tuning (leak sweep pre-registered; "works" = all three bars at one leak).

## RESULT (2026-06-03): NULL — leak too strong; it decays stim BEFORE it consolidates

| run | leak {0.1,0.2,0.3} | stim-frac | post-frac |
|-----|--------------------|-----------|-----------|
| G69 (leaky alone) | all | 0.00 | 0.00 |
| G69R (leaky + refractory=0.5) | all | 0.00 | 0.00 |

Both NULL — stim-frac 0.00 at every leak. The leak (even 0.1) kills the WRITE: it decays stim
bridges faster than co-firing can climb them to the consolidation threshold during STIM, so nothing
latches. Notably G69R had refractory=0.5 (which alone gave a 0.83 write, G66) — adding the leak
dropped it to 0.00. **Diagnosis:** the leak must NOT act during STIM (it prevents consolidation); it
should only clear the control recall-leak in POST. The right design: refractory (selective write) +
consolidation (lock stim during STIM) + a WEAK leak (decay unconsolidated control in POST). Tested
as G70a (refractory + consolidation, no leak) and G70b (refractory + consolidation + weak leak),
in parallel. If both NULL, the write-rule evolution is exhausted -> pivot to a structurally different
approach.
