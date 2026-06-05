# BET-145 — Delay sweep: does exact (RTRL) / eligibility (e-prop) temporal credit extend PAST the reservoir's memory horizon?

Pre-registered: 2026-06-05 (BEFORE the run). BET-144 was NULL because D=8 sat within a random reservoir's
echo-state memory capacity (reservoir solved it, 0.815) — no deep-credit gap. It also showed symmetric e-prop
(0.613) underperforming both exact RTRL (0.995) and the reservoir. BET-145 sweeps the delay to (a) locate the
reservoir's memory horizon (where readout-only collapses toward chance) and (b) test whether the *trained*
recurrent methods extend past it. Same architecture/hyperparameters as BET-144 (leaky-tanh RNN, H=24, α=0.3,
lr=0.05), only the delay D is swept and N_TRAIN reduced to 2000 for the sweep. Established methods, named.

## Method
Delayed selective recall + distractors, `D ∈ {8, 16, 24, 32}`. Three arms per D: RESERVOIR (readout-only
ridge), RTRL (exact online gradient), E-PROP (eligibility, symmetric). chance = 0.25.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| BET-145a | Reservoir horizon located | RESERVOIR(D=32) ≤ 0.45 (readout-only breaks toward chance) |
| BET-145b | Exact credit extends past horizon | at the smallest D where RESERVOIR ≤ 0.45, RTRL ≥ 0.80 |
| BET-145c | **Eligibility extends past horizon (frontier claim)** | at that same D, E-PROP ≥ 0.70 AND ≥ RESERVOIR + 0.25 |

## Verdicts (pre-registered)
- **PASS** (a,b,c): substrate-native eligibility (e-prop) achieves deep temporal credit *past the reservoir's
  memory horizon* — the cognition frontier reached with an established eligibility method (BTSP-aligned), no
  BPTT/transformer.
- **PARTIAL** (a,b hold, **c fails**): exact RTRL extends past the horizon but e-prop does NOT → the
  substrate-native eligibility approximation is **insufficient for deep temporal credit**; the honest boundary
  is the gap between eligibility and exact online gradient (consistent with BET-144's weak e-prop). This is a
  genuine, informative finding about where the frontier actually lies.
- **NULL** (a fails): the reservoir never breaks within D≤32 → can't create the deep-credit regime with this
  task/capacity; would need longer delay or smaller H.

No post-hoc bar tuning; only D is swept. Negative control = RESERVOIR must collapse for the trained-method
result to be meaningful.

## RESULT (2026-06-05): NULL — the bottleneck is ARCHITECTURAL (ungated vanishing memory), NOT credit assignment

| D | RESERVOIR | RTRL (exact) | E-PROP | chance |
|---|-----------|--------------|--------|--------|
| 8 | 0.853 | 0.875 | 0.495 | 0.25 |
| 16 | 0.432 | **0.290** | 0.260 | 0.25 |
| 24 | 0.282 | 0.258 | 0.258 | 0.25 |
| 32 | 0.265 | 0.273 | 0.260 | 0.25 |

- **145a ✓** — the reservoir breaks by D=16 (0.432) and is at chance by D=24 (memory horizon ≈ D 12–15).
- **145b ✗** — at the break point (D=16), **exact RTRL ALSO collapses (0.290 ≈ chance)** — it does NOT extend
  past the reservoir horizon. (It even underperforms the reservoir's ridge readout at D=16, because once the
  gradient vanishes, SGD-trained weights are worse than a closed-form readout on a random reservoir.)
- **145c ✗** — e-prop likewise collapses (0.260).

**The decisive, honest diagnosis: deep temporal credit assignment is NOT the bottleneck — the ARCHITECTURE
is.** All three methods — readout-only reservoir, eligibility e-prop, AND the *exact* online gradient (RTRL) —
hit the same wall at D≈14. Since exact credit assignment fails identically, the limit is not the learning rule
but the **ungated leaky-tanh cell's vanishing memory/gradient** (the classic long-term-dependency problem,
Bengio et al. 1994 — precisely why gated cells, LSTM/GRU, were invented). An RNN with no multiplicative gating
cannot hold selective memory past its leak horizon, and no credit-assignment method can conjure a capability
the architecture lacks.

**Verdict: NULL for the deep-temporal-credit frontier — but a SHARP, redirecting finding.** This is the
"145b-fails" branch (pre-registration loosely labeled it PARTIAL/mixed; the honest classification is NULL: the
frontier is not reached, and *not* because eligibility ⪇ exact credit, but because exact credit itself fails —
an architectural ceiling). Two takeaways: (1) the e-prop-vs-RTRL gap (BET-144) is real but moot here — both
die at the same horizon; (2) the genuine lever for long-delay working memory is a **gated memory cell**, not a
better credit-assignment rule. That is the established solution (LSTM/GRU); whether a *substrate-native* gate
(e.g. a multiplicative BTSP-modulated path) can extend the horizon is the honest next question — but it is a
known architectural fix, named as such, not new mathematics.
</content>
