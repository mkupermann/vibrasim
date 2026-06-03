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
_(pending run)_
