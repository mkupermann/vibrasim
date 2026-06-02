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

## RESULT (2026-06-03): NULL — control CONSOLIDATES too; deadlock proven at the root

| threshold | stim-frac | post-frac | uni-post | consolidated (LOC / UNI) |
|-----------|-----------|-----------|----------|--------------------------|
| 3.5 / 4.0 / 4.5 | 0.83 | 0.44 | 0.20 | 13–14 / 9 |

Same 0.44 plateau at every threshold, AND the sleep-sweep "kept 9 consolidated" in the UNIFORM arm:
**control bridges cross the consolidation threshold and lock too.** Keeping consolidated bridges keeps
control's. No threshold separates stim from control consolidation.

**Definitive root finding.** The control region is never blank — it co-fires and consolidates at a
rate indistinguishable from stim by ANY plasticity/consolidation/sweep rule, because the substrate
is HOMOGENEOUSLY ACTIVE. This is the write=leak deadlock proven at the mechanism's root: not a tuning
gap but a structural fact. The write-rule / consolidation / sleep family (G64–G72) is exhausted. The
honest high-water mark is REFRACTORY (t_refractory=0.5): selective WRITE 0.83 + recall 0.44 (region
-mean), the best the BET-089→G72 programme ever achieved — but control consolidates at the bridge
level, so even that is not clean. Pivot.
