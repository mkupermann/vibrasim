# G72 — Consolidation sleep-sweep: keep the engram, clear the slate

Pre-registered: 2026-06-03 (BEFORE the run). G64–G71 exhausted the firing-side and leak fixes. The
sharp diagnosis: refractory makes the WRITE selective (stim-frac 0.83) but recall caps at 0.44
because control bridges DRIFT UP IN POST (the bistable well pulls anything above mid toward high). A
continuous leak can't fix it (kills stim too). The right tool is a DISCRETE consolidation sweep at
STIM end: blank every NON-consolidated bridge to baseline, keeping only the locked stim engram. This
is biologically the actual solution (sleep consolidation: clear working activity, retain consolidated
memory). Because refractory makes stim co-fire far more than control, only stim crosses the
consolidation threshold; the sweep then erases control's drift before POST → clean selective recall.

## Method
BET-099 protocol + t_refractory=0.5 + consolidation, sweeping `bridge_consolidate_threshold`
∈ {3.5, 4.0, 4.5}. NEW: at STIM end, after clearing the field, blank all non-consolidated bridges
to bistable_low. Arms LOC + UNI. Fraction-selective metric. Seed 42 (replicate any pass).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G72a | Selective write | ∃ threshold: LOC STIM fraction-selective ≥ 0.5 |
| G72b | Persistent recall | same threshold: LOC POST (≥ stim_end+2000 s) fraction-selective ≥ 0.5 |
| G72c | Uniform control fails | same threshold: UNI POST fraction-selective < 0.25 |

PASS = G72a–c at one threshold → the sleep-sweep gives the programme's FIRST selective persistent
memory: consolidate the stim engram, erase everything else. Replicate across seeds (G73) before any
claim. NULL: if control also consolidates (its co-firing crosses the threshold too) or stim fails to
consolidate, the deadlock is robust even to discrete consolidation — the write=leak identity is
fundamental, and the refractory 0.44 stands as the honest high-water mark. This is the LAST
write-rule attempt; pivot if NULL. No post-hoc threshold tuning (sweep pre-registered).
