# BET-146 — Does a GATED cell extend the working-memory horizon past the ungated wall? (confirms BET-145's diagnosis)

Pre-registered: 2026-06-05 (BEFORE the run). BET-145 found that long-delay selective recall fails past D≈14 for
ALL learning rules — reservoir, e-prop, AND exact RTRL — because the ungated leaky-tanh cell cannot HOLD memory
(vanishing memory/gradient, Bengio 1994), not because of the credit-assignment rule. The established fix is a
GATED memory cell (LSTM/GRU/JANET): a multiplicative forget/retain gate lets a unit latch its value (f→1) and
persist indefinitely. BET-146 tests this directly: a forget-gated cell (JANET-style), trained with the SAME
exact online RTRL (no BPTT), at the delays where the ungated cell collapsed. Established architectural fix,
named as such — the contribution is confirming the diagnosis + achieving long-delay selective recall online
without BPTT, not new mathematics.

## Method
Same delayed-selective-recall-with-distractors task (K=4, chance 0.25). Gated cell (H=20):
`z = tanh(W_z x + U_z h_prev)`, `f = sigmoid(W_f x + U_f h_prev + b_f)` (b_f init +1, standard retain-bias),
`h = f⊙h_prev + (1−f)⊙z`. Trained by exact RTRL (forward-mode influence tensor through both gates), online,
no BPTT. Compared to the ungated RTRL numbers from BET-145.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| BET-146a | Sanity (trainer learns) | gated-RTRL ≥ 0.90 at D=1 |
| BET-146b | **Gating extends the horizon** | gated-RTRL ≥ 0.80 at D=24 (ungated was ~chance there) |
| BET-146c | Attributable to gating | gated-RTRL(D=24) ≥ ungated-RTRL(D=24) + 0.40 |

## Verdicts (pre-registered)
- **PASS** (a,b,c): a gated memory cell extends the working-memory horizon far past the ungated wall, learned
  online by exact RTRL with NO BPTT → confirms BET-145's architectural diagnosis (the bottleneck was the
  ungated cell, not credit assignment) AND demonstrates long-delay selective recall. The lever is the
  architecture (gating), an established fix, named as such.
- **PARTIAL** (b holds at a shorter delay, e.g. ≥0.80 at D=16 but <0.80 at D=24): gating helps but does not
  fully solve D=24 → partial confirmation; the horizon extends but not unboundedly at this size/budget.
- **NULL** (b fails): even a gated cell with exact RTRL can't learn D=24 → the bottleneck is NOT (only) gating
  — learnability, not representability, is the wall (e.g. RTRL/online-SGD can't find the latch solution).
  Honest either way.

No post-hoc tuning; architecture + hyperparameters fixed pre-run. The D=1 sanity guards against a buggy
gated-RTRL impl being read as a capability result.
</content>
