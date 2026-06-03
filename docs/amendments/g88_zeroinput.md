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
