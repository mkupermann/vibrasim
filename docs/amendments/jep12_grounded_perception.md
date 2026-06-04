# JEP-12 — grounding the world model in PERCEPTION (learn SR from observations, not state indices)

## Motivation
JEP-4..11 used privileged STATE INDICES. The real JEPA test is learning the world model from RAW OBSERVATIONS:
the agent sees a high-dim, noisy sensory vector per state and must (a) learn a representation that identifies
states (perception), then (b) learn SR/value over that representation and plan. This is the honest step toward
"understanding from perception" rather than from a god's-eye state label.

## Pre-registration (locked BEFORE run)
- Maze (DFS tree). Each cell emits a HIGH-DIM NOISY observation: a fixed random signature per cell + Gaussian
  noise each visit (so same state != identical vector; the agent must generalize). Observation dim >> states.
- Perception: a LOCAL contrastive/temporal-coherence encoder maps observations -> latent; same-state (temporally
  adjacent, denoised) cluster together. Then a discrete code via nearest learned prototype (online clustering).
- World model: learn SR by LOCAL TD over the PERCEIVED codes (not true indices). Plan by SR-value (JEP-11).
- Bars: (1) perceptual state-identification accuracy (perceived code == true cell) >= 0.9 under noise;
  (2) SR-value navigation on PERCEIVED states reaches >= 0.85 AND >> Euclidean-greedy AND >> random. PASS =
  the substrate-native loop works FROM PERCEPTION (noisy high-dim obs), not privileged indices. NULL otherwise.
- Methods (contrastive learning, online prototype clustering, SR/TD, value planning) established - named so.

## Result — NULL (a real tension: temporal-coherence collapses states it must distinguish)
| measure | value |
|---------|-------|
| perceptual state-ID accuracy (noise) | 0.41 |
| SR-value nav on perceived states | 0.24 |
| Euclid / random | 0.09 / 0.34 |

**VERDICT: NULL — informative.** The contrastive temporal-coherence encoder ATTRACTS temporally-adjacent
(neighbouring) cells, which collapses adjacent states together -> poor state IDENTIFICATION (0.41), so grounded
planning fails (0.24). This reveals a genuine tension: slow-feature/coherence (good for smooth value/geodesic
structure, JEP-5/11) directly CONFLICTS with state DISCRIMINATION (needed for perception). One encoder forced to
do both does neither well. The fix is architectural: SEPARATE perception (discriminate states from raw obs -
averaging denoises a 64-dim signature easily) from VALUE (SR smoothness over identified states). JEP-12b. Bars
locked, not tuned.
