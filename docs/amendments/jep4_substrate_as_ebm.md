# JEP-4 — The substrate's genuine benefit: energy-based inference by RELAXATION + LOCAL learning

## The question (Michael)
"How can we use the substrate as a technology for [JEPA/EBM/MPC] that is a benefit?"

## The honest answer
JEPA/EBM/MPC are normally trained by BACKPROP and inferred by GRADIENT DESCENT. The substrate's native
primitives are the backprop-free alternatives to BOTH:
- EBM INFERENCE (argmin energy) == physical RELAXATION (let dynamics settle). Hopfield (1982) is an EBM whose
  inference IS settling and whose learning IS Hebbian/local. This is the substrate's native mode.
- LEARNING the energy == LOCAL plasticity (STDP/BTSP), not global backprop.
- JEPA's predict-in-latent + minimize-error == PREDICTIVE CODING (Rao-Ballard / Friston free energy), which is
  energy-based, local, and substrate-friendly. Active inference = MPC (act to minimize expected free energy).
The benefit is ARCHITECTURAL: the substrate is an analog energy-minimization machine with local learning -
exactly what an EBM is off the digital computer. NOT a speed/accuracy win today; an in-principle backprop-free,
relaxation-based realization. Honest limit: the substrate MEMORY thread closed NEGATIVE (G88-96) - holding
persistent learned content is the substrate's known weak point, so "substrate as the world-model store" is not
yet supported; "substrate as the energy-minimization ENGINE / local learner" is the defensible benefit.

## Pre-registration (locked BEFORE run)
Demonstrate substrate-native energy-based inference with NO backprop and NO global optimizer:
- Store K binary patterns in an associative energy E(s) = -0.5 s^T W s via the LOCAL Hebbian rule
  W = sum_p p p^T (diagonal zeroed). This is the STDP/Hebbian analogue - local, no backprop.
- INFER (recall) by RELAXATION: present a corrupted cue, asynchronously flip units to descend energy until
  fixed point. This is the substrate's settling dynamics = the EBM argmin.
- Metric: bit-recall accuracy from corrupted cues (30% flips), averaged over patterns/trials. Energy must
  decrease monotonically under relaxation (sanity that it IS energy descent).
- Baselines: the corrupted cue itself (no relaxation); a random readout.
- Bars: relaxation recall >= 0.9 bits correct at K <= 0.1*Nunits AND >> cue/random AND energy monotonically
  non-increasing. PASS = substrate-native (local-learn + relax) energy inference works. Report capacity curve
  honestly (Hopfield capacity ~0.14N; recall degrades past it - expected, reported not hidden).
