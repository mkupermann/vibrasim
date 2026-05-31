# BET-126 — Analog superposition restores systematic generalization

Pre-registered: 2026-05-31 (BEFORE the run). Fresh bet from the BET-125 NULL
diagnosis (NOT a re-tune of BET-125). Same comparison task, same systematic
held-out split. ONE change with a mechanistic prediction:

**Hypothesis.** sign() in `bundle` destroys the analog superposition a linear
readout needs to unbind a slot and recover a symbol's value. With ANALOG bundle
(superpose WITHOUT sign), code = bind(role_l,hv[i]) + bind(role_r,hv[j]), and
W·code with W = w_l⊙role_l − w_r⊙role_r computes v[i]−v[j] for ANY pair, so a
single linear readout generalizes SYSTEMATICALLY to held-out symbol combinations.

New substrate primitive under test: `bundle_analog` (graded superposition — matches
the substrate's own tanh-graded activations; the ±1 sign was an unnecessary
discretization).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T126a | Systematic generalization | linear readout on ANALOG codes held-out acc >= 0.85 |
| T126b | Mechanism, not luck | analog beats sign-bundle (BET-125 0.611) by >= 0.15 |
| T126c | Composition carries it | no-binding analog control held-out acc < 0.65 |
| T126d | Relation learned | shuffled-label analog control held-out acc < 0.65 |

PASS = T126a-d. PASS confirms the diagnosed mechanism AND banks the first
SYSTEMATIC (symbolic-combination) generalization on the substrate — the property
language needs, achieved with analog VSA composition + an online linear readout, no
transformer. NULL would refute the mechanism and re-open the question.

## RESULT (2026-05-31): NULL/partial — mechanism confirmed in direction, bar not cleared

| metric | value | bar |
|--------|-------|-----|
| analog-bundle held-out acc | **0.806** | T126a >=0.85 ✗ |
| sign-bundle held-out acc | 0.611 | — |
| analog − sign | +0.194 | T126b >=0.15 ✓ |
| no-binding analog control | 0.306 | T126c <0.65 ✓ |
| shuffled-label analog control | 0.417 | T126d <0.65 ✓ |

T126a ✗, T126b ✓, T126c ✓, T126d ✓ → **NULL/partial**. The diagnosed mechanism is
CONFIRMED in direction: removing the sign() clamp jumped systematic held-out
accuracy 0.611 → 0.806 (+0.19, exactly the predicted large effect), and both
controls still collapse — so analog superposition really does restore the
linear-recoverability a systematic readout needs. But it did not clear the locked
0.85 bar.

**Residual mechanism (-> BET-127, fresh).** With analog codes the labels ARE
sign(v[i]−v[j]); the only error source left is crosstalk noise in the unbound slot
(code⊙role_l ≈ hv[i] + role_l·role_r·hv[j]), which corrupts value recovery near the
v[i]≈v[j] boundary. That noise scales as ~1/sqrt(D). Prediction: held-out accuracy
rises monotonically with hypervector dimension D and crosses 0.85 → ~1.0 at
sufficient D. BET-127 sweeps D for a systematic-generalization SCALING LAW.
