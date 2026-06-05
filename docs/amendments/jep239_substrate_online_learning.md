# JEP-239 — does the substrate learn the relational store ONLINE (continual, no catastrophic forgetting)?

Pre-registered 2026-06-05 (BEFORE the run). JEP-232..238 BATCH-trained the substrate relational store (120 passes
over all facts). EQMOD's theme is "learns from every interaction" (literal) — so: can the substrate add facts ONE AT
A TIME with a few LOCAL updates, remembering old facts (no catastrophic forgetting) and learning the new one? This
is the continual-learning question for the energy-based relational store.

## Method (no transformer; online contrastive-Hebbian)
- Present is-a facts sequentially. After each new fact, run only a FEW local `train_epoch` updates (not a full
  retrain) under two regimes:
  - **pure online**: update on the NEW fact only.
  - **rehearsal**: update on the new fact + R random previously-seen facts (interleaved replay).
- After each addition, measure child→parent recall over ALL facts seen so far (old + new). Seeds 42 & 7. Up to 18
  facts (within the JEP-232 ~20 capacity, so any forgetting is interference, not capacity).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J239a | Online LEARNS the new fact | the just-added fact is recalled immediately ≥ 0.9 of the time, across the stream (both seeds) |
| J239b | Pure online FORGETS (characterize) | pure-online recall over all-facts-so-far drops below 0.7 before 18 facts (interference, not capacity) — OR, if it holds, that is the finding |
| J239c | Rehearsal MAINTAINS | rehearsal recall over all-facts-so-far stays ≥ 0.85 through 18 facts (both seeds) |
| J239d | Rehearsal beats pure online | at 18 facts, rehearsal all-facts recall > pure-online by ≥ 0.15 (both seeds) |

PASS = J239a + J239c + J239d (the substrate learns the store online WITH rehearsal; J239b characterizes pure-online
forgetting either way). NULL/finding: if pure online does NOT forget (J239b "holds"), continual learning is free
here (a positive surprise, recorded as such); if rehearsal does not maintain (J239c fails), online learning needs
more than replay. No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J239a PASS (a few updates on one fact fit it). J239b: pure online FORGETS — the contrastive-Hebbian update on one
fact (free/clamped phases over the whole net) perturbs the shared W, drifting old attractors; all-facts recall falls
below 0.7 well before capacity (the classic continual-learning interference, sharper than vanilla Hopfield outer-
product because contrastive updates are not simply additive). J239c PASS — interleaved rehearsal re-anchors old
attractors, holding ≥ 0.85. J239d PASS — rehearsal >> pure online at 18 facts. RISK (calibration): vanilla Hopfield
Hebb IS incrementally robust (additive outer products) — if EnergyNet's contrastive rule behaves additively, pure
online might NOT forget much and J239b "holds" (the positive surprise). Net: rehearsal works (a/c/d); pure-online
forgetting is the open call I lean toward FORGETS but flag the additive-Hebb counter-possibility. Established
(continual learning, catastrophic forgetting, rehearsal/replay — McCloskey-Cohen 1989, Robins 1995), named; no
novelty — the value is characterizing online learnability of the substrate relational store.
