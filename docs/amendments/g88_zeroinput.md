# G88 — Zero-input diagnostic: is the latching spontaneous or stim-coupled?

Pre-registered: 2026-06-03 (BEFORE the run). G86 showed control latches even quiet + disconnected,
which I attributed to intrinsic activity WITHOUT instrumenting it. This diagnostic settles it: run
the quiet + disconnected substrate with NO injection at all during STIM. Compare to the normal STIM arm.

## Bars (locked pre-run)
| ID | Criterion | Interpretation |
|----|-----------|----------------|
| G88-spontaneous | zero-input run: any region peak bridge > 3.0 | substrate latches with NO input -> no stable blank state -> deadlock FUNDAMENTAL (confirms close) |
| G88-coupled | zero-input run: all regions stay <= 3.0 | latching needs input -> G84-G86 contamination was stim-COUPLED -> fixable -> memory REOPENABLE |

Honest diagnostic; either outcome sharpens the causal model. No PASS/NULL — it determines whether the
memory close is final or whether a fixable isolation route remains.

## RESULT (2026-06-03): INPUT-DEPENDENT — there IS a stable blank state (corrects G86)

| arm | peak stim-region bridge | peak ctrl-region bridge | firings during STIM |
|-----|-------------------------|-------------------------|---------------------|
| ZERO-INPUT | 1.00 | 1.00 | 0 |
| STIM | 5.89 | 5.79 | 77,850 |

**Zero input -> perfectly BLANK (1.00, zero firing).** The substrate HAS a stable blank state. This
REFUTES the G86 conclusion that latching is intrinsic. With stim, BOTH regions latch AND there are
77,850 firings = a RUNAWAY SELF-IGNITION cascade (BET-105 phenomenon) that reaches control despite
disconnection (emit_speed=6 + cull + bridge-cut don't contain a cascade of this magnitude). So
control latching is STIM-COUPLED RUNAWAY, not fundamental. **The memory question is REOPENED:** the
fix is to write WITHOUT triggering the runaway — drive LOCAL stim co-firing with low intensity so the
cascade never ignites and control stays blank. G89 sweeps stim intensity low.
