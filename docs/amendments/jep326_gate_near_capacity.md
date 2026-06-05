# JEP-326 — Does per-relation gating matter NEAR CAPACITY? (the regime JEP-325 missed)

## Motivation
JEP-325 NULL: per-relation gating showed no benefit at fan-out 15 because the store was far below capacity. Applying
the lesson it produced (#5: stress the variable into the effect's regime), test the RIGHT regime: a single module
loaded near K*≈D/32, where single-valued `isa` edges keep a HIGH gate while a high-fan-out relation's per-value
similarity is LOW — so an isa-calibrated gate should over-reject it while the relation's own gate captures it. This
validates (or refutes) keeping the per-relation-gate refactor. No transformer.

## Method
One forced single module (module_cap huge) filled with ~110 single-valued `isa`-style filler facts (high gate) PLUS
a high-fan-out target relation (`eats` with k=20 objects). Compare full-set recall of the target via (a) the
isa-calibrated single gate vs (b) the target relation's own gate.

## Pre-registered bars (BEFORE the run)
- **J326a (per-relation gate recovers near capacity):** at near-capacity load, target-relation recall with the
  per-relation gate ≥ 0.90, both seeds (0, 7).
- **J326b (contrast is real):** the SINGLE isa-gate recall is materially lower (per-relation − single ≥ 0.15 on at
  least one seed), demonstrating per-relation gating is NEEDED here — OR, if both stay high, honestly report that
  even near capacity one gate suffices (refuting the justification, and I'd then revert the refactor).

Predicted most-likely failure / fork: it's possible the modular routing already isolates each key so fan-out load
doesn't interact with isa load, leaving no contrast even near capacity — in which case J326b fails and the honest
conclusion is the per-relation gate is unnecessary (revert). Either way the finding is decisive about keeping the code.

## Result (seeds 0, 7): decisive — **single gate suffices; JEP-325 refactor REVERTED**
Sweep (single module; high-fan-out `eats` with k objects amid `load` single-valued isa fillers):

| k | load | single-gate recall | per-relation recall | gap | isa_gate | eats_gate |
|---|------|--------------------|---------------------|-----|----------|-----------|
| 10 | 20 | 1.00 | 1.00 | 0.00 | 0.072 | 0.070 |
| 20 | 20 | 1.00 | 1.00 | 0.00 | 0.065 | 0.059 |
| 30 | 20 | 1.00 | 1.00 | 0.00 | 0.057 | 0.055 |
| 10 | 110 | 1.00 | 1.00 | 0.00 | 0.036 | 0.035 |
| 20 | 110 | 1.00 | 1.00 | 0.00 | 0.035 | 0.034 |
| 30 | 110 | 0.97 | 1.00 | **0.03** | 0.034 | 0.032 |

- **J326a:** per-relation recall ≥0.90 everywhere. **True.**
- **J326b:** contrast ≥0.15? **False** — max gap = **0.033**. The isa-gate and eats-gate are nearly IDENTICAL in
  every cell, because per-value similarity is set by MODULE LOAD (shared across relations, ~1/√load), not per-key
  fan-out. A single gate suffices even near capacity.

## Verdict: decisive negative → **action taken**
Per-relation gating gives no meaningful benefit (≤0.033). Per the discipline (don't keep unjustified complexity),
the JEP-325 `BrainQuery` per-relation-gate refactor is **REVERTED** to a single auto-calibrated gate; 10 substrate
tests + JEP-322 + the GUI ask path remain green/correct. This also recontextualizes JEP-323's "per-relation gate"
fix: most of that improvement was the corrected compound target, not the gate — the gate effect is ≤0.03. Honest
loop: added a feature (325), tested its justification (326), found none, removed it. No transformer.

