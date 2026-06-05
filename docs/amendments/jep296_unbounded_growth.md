# JEP-296 — Unbounded growth past the capacity cliff (auto module-add / neurogenesis)

## Motivation
JEP-294: one bundle blacks out hard at K*≈D/32. JEP-295: memory persists and grows, but only WITHIN that cliff —
add too many facts and recall collapses. A brain doesn't stop at a fixed size. Make growth **unbounded**: when the
current module saturates, automatically spin up a NEW module (the established route — modular VSA / "neurogenesis";
linear total capacity, named as such, not novel) and route new facts there. Recall searches across modules and
takes the best cleanup match. Persisted via JEP-295's file format.

## Pre-registered bars (BEFORE the run)
- **J296a (single-module blacks out, multi-module does not):** store 3×K* = 384 facts at D=4096. A SINGLE bundle
  must drop below 0.90 recovery (demonstrating the cliff); the auto-module store must recover ≥ 0.90, both
  seeds (0, 7).
- **J296b (cross-module not confused):** with the 384-fact multi-module store, each query returns the value bound
  to THAT entity (the correct module wins over spurious matches in other modules) — this is exactly J296a's
  recovery ≥ 0.90, plus an explicit check that an UNtaught entity stays separable (best sim below taught).
- **J296c (persists):** save the multi-module store, load into a FRESH object → recovery unchanged ≥ 0.90.
- **No-regression:** JEP-295 (single-module persistence) bars still hold (≥0.95 / ≥0.90) under the modular code.

Predicted most-likely failure: cross-module crosstalk — a wrong module spuriously yields a value whose cleanup sim
beats the correct module, so multi-module recovery never reaches 0.90 even though each module is individually fine.
If so, J296a FAILS and the honest finding is "modules need disjoint value sub-vocabularies or a module-routing key,"
which I would pre-register as JEP-297 rather than tune here.

## Result
(filled after the run)
