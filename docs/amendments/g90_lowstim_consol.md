# G90 — Selective persistent memory: low-intensity write + consolidation

Pre-registered: 2026-06-03 (BEFORE the run). G89 showed n=4 stim keeps CONTROL CLEANLY BLANK
(uni-post 0.00, runaway avoided) with stim recall 0.44 -- just under 0.5. The remaining gap is STIM
PERSISTENCE, not control contamination. Since control is now blank, consolidation locks ONLY stim
(the prior failure -- control also consolidating -- is gone). Add bridge_consolidate_threshold to
lock the stim engram. Quiet + disconnected + local + n=4. Sweep threshold {3.5,4,5}. Seed 42.

## Bars (locked pre-run -- standard memory bars)
| ID | Criterion | Bar |
|----|-----------|-----|
| G90a | Selective write | LOC STIM fraction-selective >= 0.5 |
| G90b | Persistent recall | LOC POST (>= stim_end+2000 s) fraction-selective >= 0.5 |
| G90c | Uniform control fails | UNI POST fraction-selective < 0.25 |

PASS = G90a-c at one threshold -> SELECTIVE PERSISTENT MEMORY: low-intensity write (control blank) +
consolidation (locks only stim) breaks the deadlock. Replicate across seeds. NULL = consolidation
still cannot make stim persist selectively (stim write too weak at n=4, or consolidation re-triggers
the runaway). Honest either way. No post-hoc tuning.

## RESULT (2026-06-03): NULL — n=4 write too weak to consolidate (identical to G89)

| threshold | stim-frac | post-frac | uni-post |
|-----------|-----------|-----------|----------|
| 3.5 / 4.0 / 5.0 | 0.33 | 0.44 | 0.00 |

Identical at every threshold = consolidation made NO difference. Why: at n=4 the write is too WEAK
(stim-frac 0.33); stim bridges never reach the consolidation threshold, so nothing locks. Control is
blank (0.00, good) but stim recall stays 0.44. The bind: n=4 too weak to consolidate, n=8+ triggers
the runaway. Need a STRONGER write that does NOT run away -> refractory caps the cascade (G66). G91
combines quiet + disconnected + refractory + consolidation + moderate stim.
