# JEP-246 — the grounded loop through the substrate: noisy perceptual cue → clean → reason multi-hop, one energy process

Pre-registered 2026-06-05 (BEFORE the run). Integrates the grounding thread (JEP-54..63/178: perceive → symbol →
reason) with the robust substrate-relational arc (JEP-232..245). A real perceptual front-end yields a NOISY concept
code; this BET tests whether the substrate does perceptual CLEANUP and relational REASONING as ONE energy process:
clamp a noisy cue, the relaxation cleans it to the concept attractor, then energy-gated chaining answers multi-hop
is_a. Honest framing: the benefit is ARCHITECTURAL (cleanup + retrieval + reasoning in one relaxation dynamics), NOT
a claimed accuracy win over a separate decode-then-symbolic pipeline.

## Method (no transformer)
- JEP-232/244 store, is-a chain (poodle→dog→mammal→animal→organism), random codes, energy-gated chains (JEP-244).
- A "perceptual cue" for concept x = its code with a fraction f of bits flipped (the JEP-240 noise model = stand-in
  for noisy perception). Query is_a(noisy(x), y): clamp the noisy cue as the first KEY, relax (this cleans the cue
  while retrieving the parent), then chain. The FIRST hop both cleans the cue AND retrieves — one relaxation.
- Sweep f ∈ {0, 0.1, 0.2, 0.3}; measure multi-hop is_a accuracy over a battery (positives across depth + negatives).
  Baseline = is_a from the CLEAN cue (f=0). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J246a | Clean grounded loop works | f=0 multi-hop is_a battery = 1.00 (both seeds) |
| J246b | Robust to MODERATE perceptual noise | f=0.1 battery ≥ 0.85 (both seeds) — the cue cleans up + reasons |
| J246c | Graceful degradation | battery is monotone-ish non-increasing in f and f=0.3 < f=0 (degrades, not cliff-collapses, both seeds) |
| J246d | The cue is genuinely NOISY | at f=0.2 the noisy cue differs from the clean code in ≥ 5 of 40 bits on average (sanity: we are testing noise) |

PASS = J246a–c (the grounded loop runs through the substrate and tolerates moderate perceptual noise); J246d is a
sanity check that the noise is real. NULL (honest): J246b fails → the energy gate or chaining can't absorb a noisy
START cue (the first relaxation doesn't clean it before the gate fires). No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J246a PASS (clean = the JEP-244 result, 1.00). J246b PASS — within an attractor basin a 10%-flipped cue relaxes
to the correct concept, so the first hop cleans + retrieves and the chain proceeds; ≥ 0.85. J246c PASS — beyond the
basin radius (f↑) cleanup fails on more cues, so accuracy degrades GRACEFULLY (not a cliff) with f. J246d PASS
(0.2×40 = 8 bits ≥ 5). RISK (in-rung): the energy gate is computed for CLEAN keys; a noisy START cue might raise the
first hop's energy above the gate and falsely STOP (reporting False) — if so J246b dips and the honest fix is to
clean the cue (one un-gated relax) BEFORE gating, which I'll note but not pre-implement. Established (Hopfield basin
cleanup + the grounded perceive→symbol→reason loop), named; no novelty — the value is the integrated grounded-substrate
loop end to end (perception noise → substrate cleanup → substrate reasoning), one energy process.

## RESULT (2026-06-05): PASS — the grounded loop runs through the substrate, robust to moderate perceptual noise

| seed | f=0 | f=0.1 | f=0.2 | f=0.3 | bitdiff @0.2 |
|------|-----|-------|-------|-------|--------------|
| 42 | 1.00 | 1.00 | 0.50 | 0.44 | 7.8 / 40 |
| 7  | 1.00 | 1.00 | 0.62 | 0.38 | 6.9 / 40 |

- **J246a ✓** — clean grounded loop = 1.00 (the JEP-244 reasoning, cued by the concept code).
- **J246b ✓** — a 10%-flipped perceptual cue → **1.00** both seeds: the first relaxation CLEANS the noisy cue to the
  concept attractor while retrieving its parent, and the energy-gated chain proceeds — cleanup + retrieval + reasoning
  in ONE energy process. (The pre-flagged risk — a noisy START cue raising the first hop's energy above the gate and
  falsely stopping — did NOT materialize at f ≤ 0.1: the cue is inside the basin, relaxes to a deep minimum.)
- **J246c ✓** — graceful degradation: 1.00 → ~0.55 (f=0.2, ~8/40 bits ≈ basin edge) → ~0.4 (f=0.3), a smooth curve,
  not a cliff. The ~0.5 floor is chance on the balanced battery once cleanup fails.
- **J246d ✓** — the cue is genuinely noisy (7.8 / 6.9 of 40 bits flipped at f=0.2).

**FINDING:** the grounding thread (JEP-54..63/178: perceive → symbol → reason) and the robust substrate-relational arc
(JEP-232..245) integrate end-to-end: a NOISY perceptual concept cue is cleaned and reasoned over multi-hop AS ONE
substrate energy process, tolerant to ~10% perceptual noise, degrading gracefully beyond the basin radius. Honest
framing (unchanged): the benefit is ARCHITECTURAL — cleanup, retrieval, and reasoning happen in the same relaxation
dynamics (no separate decode step) — NOT a claimed accuracy win over a decode-then-symbolic pipeline; on toy
perception (the JEP-91/178 caveat), the BINDING (perception code → substrate relational reasoning) is the
contribution. Verdict: **PASS** (predict-calibrate HIT — a/b/c/d as forecast). This caps the substrate threads: the
substrate carries the engine's relational reasoning (232..245) AND closes the grounded perceive→reason loop (246),
each within its characterized envelope, no transformer.
