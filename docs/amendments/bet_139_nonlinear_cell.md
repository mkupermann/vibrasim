# BET-139 — Nonlinear recurrent cell: drift-free, length-generalizing parity

Pre-registered: 2026-05-31 (BEFORE the run). BET-138 falsified "drift"; the real
blocker is that a LINEAR cell cannot represent XOR (Minsky-Papert). Fix, substrate-
native: a NONLINEAR transition via random nonlinear features (the substrate's
tanh projection — the reservoir, but used as the recurrent CELL, not a static map),
with a local linear readout, plus in-loop attractor cleanup to a discrete state.

Cell: next_state_code = cleanup( Wout @ tanh(R @ [state_code ; bit_code]) ), where R
is the substrate's fixed random projection (nonlinear features) and Wout is trained by
a LOCAL one-step rule on the 4 XOR transitions. Cleanup snaps to nearest of {E0,E1}.
Same protocol as BET-137/138: train on single steps only, test lengths 10..20 and 50.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T139a | Length-generalizes | nonlinear-cell acc on len 10..20 >= 0.95 |
| T139b | Nonlinearity is the cause | linear-cell control stays < 0.65 |
| T139c | Extends far | acc on len 50 >= 0.90 |
| T139d | Trained short, local | train exposure = 4 single XOR steps, local rule, no BPTT |

PASS = T139a-d. PASS = a nonlinear recurrent cell built from the substrate's own
random features + attractor cleanup, trained only on single steps by a local rule,
computes a recursive function and generalizes to arbitrary unseen lengths — drift-free
unbounded composition, the property language needs, with no transformer and no BPTT.
NULL bounds it and sends the question to a different cell.

## RESULT (2026-05-31): NULL/partial — nonlinearity helps, but per-step error COMPOUNDS over length

| computer | len 10-20 | len 50 | bar |
|----------|-----------|--------|-----|
| nonlinear cell | 0.700 | 0.682 | T139a >=0.95 ✗, T139c >=0.90 ✗ |
| linear control | 0.460 | — | T139b <0.65 ✓ |

T139a ✗, T139b ✓, T139c ✗ → **NULL/partial**. Nonlinearity is confirmed as the right
axis (0.46 → 0.70), validating the XOR diagnosis. But it does not reach robust
length-generalization. Cause: a slow delta rule leaves per-step accuracy < 100%, and
parity COMPOUNDS it over the sequence (per-step p → p^L; even p=0.97 gives 0.97^15 ≈
0.63). The remaining bottleneck is the PER-STEP classification margin, not
representability. -> BET-140 makes the per-step transition near-exact (ridge
least-squares Wout = the online-local RLS solution) so cleanup always corrects, and
tests length 50/100.
