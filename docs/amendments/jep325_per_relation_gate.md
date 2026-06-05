# JEP-325 — Per-relation gating in BrainQuery (robustness at fan-out, applies JEP-323 lesson)

## Motivation
`BrainQuery` calibrates ONE gate on the `isa` relation. JEP-323 showed high-fan-out keys (a relation with many
values per subject) have lower per-value similarity, so an isa-calibrated gate over-rejects them. Make BrainQuery
compute a gate PER relation (cached, calibrated on that relation's own edges), so `why`/`what`/property answers stay
correct when a cause has many effects or an entity relates to many things. Established per-channel calibration,
named as such. No transformer.

## Pre-registered bars (BEFORE the run)
- **J325a (fan-out robustness):** on a store with high-fan-out relations (an effect with 5 causes; an entity that
  `eats` 6 things), per-relation-gated BrainQuery returns the FULL correct set for `why`/`what` ≥ 0.95, where the
  single isa-gate drops members; both seeds (0, 7). Report the single-gate baseline for contrast.
- **J325b (no regression):** the JEP-322 simple cases still answer correctly; substrate gate still green.

Predicted most-likely failure: a relation with too few edges to calibrate (1-2) gives a noisy gate; fall back to the
isa/global gate when a relation has <3 edges. If J325a misses on a sparse relation, report it (calibration-sample
floor), don't tune.

## Result (seeds 0, 7): **NULL / PARTIAL** — bars pass but the motivation was not demonstrated
- **J325a:** per-relation-gated `why`/`what` return the full set = **1.0** at fan-out 5 AND at fan-out 15. But the
  **single-gate baseline ALSO = 1.0** at both — so there is NO contrast. The hypothesis (an isa-calibrated gate
  over-rejects high-fan-out relations) is **FALSE at sub-capacity scales**: the store (~33 facts ≪ K*=128) keeps
  every value's similarity well above the gate regardless of fan-out, so one gate suffices.
- **J325b:** simple cases unaffected; 10 substrate tests + JEP-322 still PASS (the refactor is regression-free).

## Verdict: **NULL / PARTIAL** (honest)
The per-relation gate did not demonstrate a benefit here — at fan-out up to 15 in a sub-capacity store, the single
isa-gate is equally correct. So JEP-325's experiment is **uninformative about its own premise** (a vacuous pass).
The code change is RETAINED because it is regression-free AND independently justified by JEP-323, where a
per-relation gate WAS needed (a materialized closure with fan-out 7 fell below a parent-calibrated gate) — a store
BrainQuery may well query. Honest distinction: per-relation gating matters near capacity / after materialization
(shown in 323), not at the low fan-out this test used. No bar was moved; the negative is recorded as the finding.
Lesson: a stress test must push the variable into the regime where the effect lives (calibration #5) — fan-out
alone, far below capacity, doesn't stress the gate.

