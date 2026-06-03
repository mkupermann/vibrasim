# G131 — Can the substrate LEARN an A->B association? (decisive learnability test)

## Motivation
"Human-like communication" requires LEARNING (understanding + generating). This test puts evidence on
whether the substrate can learn the SIMPLEST thing — a single A->B association — using its own plasticity
(STDP/BTSP/correlation). If it cannot learn even A->B, it categorically cannot learn language.

## Pre-registration (locked BEFORE run)
TRAIN: repeatedly (N=60) present stimulus A (inject at x=7) then stimulus B (x=15), interleaved, so
plasticity could wire A->B. PROBE: present A ALONE, measure B-region firing vs (i) UNTRAINED control and
(ii) a control region C (x=23) for specificity. Both seeds.

**Bars (locked):**
- G131 PASS (learned): trained A->B response > 1.5x untrained AND > 1.5x control-region C, both seeds.
NULL otherwise → the substrate cannot form associations.

## Result
Both seeds: trained A→B = 0.0, untrained = 0.0, control C = 0.0. **VERDICT: NULL (no learning signal),
but the readout is INCONCLUSIVE.**

## Honest note — weak readout
All-zeros means the B-region activity probe captured nothing (no `k_fired` boolean read; the charge
fallback is 0 because charge doesn't propagate A→B over 8 units, G106/G130). So this shows NO
trained-vs-untrained difference (no learning signal) but does NOT cleanly prove non-learning — a dead
probe also reads zero. Recorded as inconclusive, not a clean NULL. The substrate's inability to form
selective persistent associations is already established robustly by the ~70-experiment memory programme
(G33–G96); G131 adds nothing clean to that. See HUMAN_AI_CAMPAIGN.md.
