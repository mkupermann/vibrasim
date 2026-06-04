# JEP-16 — integrated substrate-native world-model agent (capstone)

## Motivation
Combine every VALIDATED piece into ONE runnable agent and verify the complete capability end-to-end:
- perception from noisy high-dim observations (JEP-12c: discriminate + multi-glance denoise),
- world model learned by LOCAL TD = substrate BTSP (JEP-9/11: Successor Representation),
- value-based planning (JEP-11: SR-as-value, optimal),
- instant REWARD retargeting (JEP-14b: V=M@r),
- adaptation to TRANSITION changes via explicit-model edit + MPC replan (JEP-15b).
All local / backprop-free, no privileged state indices.

## Pre-registration (locked BEFORE run)
- Looped maze; agent perceives noisy obs (no indices). One agent object exposes: perceive(), learn SR (TD),
  plan(goal) via SR-value, retarget(new_goal) instantly, adapt(block_edge)+replan via explicit model.
- Acceptance (all must hold): (a) navigation to random goals from PERCEPTION >= 0.9; (b) instant retarget to a
  second goal mid-episode >= 0.9 (no relearning); (c) after a blocked passage, model-edit + MPC replan reaches
  detoured goals >= 0.9 (zero SR relearning). PASS = the integrated substrate-native agent works end-to-end.
  NULL if any sub-capability fails. All methods established - named as such.

## Result — PASS
| capability | reach |
|------------|-------|
| (a) navigation from noisy PERCEPTION (no privileged indices) | 1.00 |
| (b) instant RETARGET to new goals (zero relearning) | 1.00 |
| (c) ADAPT to blocked passage (local model edit + MPC replan) | 1.00 |

**VERDICT: PASS.** The integrated substrate-native agent works END-TO-END. From noisy high-dim perception with
NO privileged state indices, ONE agent: perceives + denoises, learns a world model by LOCAL TD (= substrate
BTSP) as a Successor Representation, plans by SR-value, instantly retargets to new goals, and adapts to
transition changes via a local model edit + MPC replan - all local, all backprop-free. This is the EQMOD-4
capstone: the JEPA/EBM/MPC paradigm realized substrate-natively for a grounded, adaptive world-model agent at
toy scale. Honest scope: gridworld navigation/control, not human-level conceptual understanding (open). All
methods established (SR/TD, prototype clustering, value iteration / MPC), named as such.
