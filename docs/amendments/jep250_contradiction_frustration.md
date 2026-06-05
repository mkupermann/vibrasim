# JEP-250 — contradiction as energy FRUSTRATION: can the substrate natively flag an inconsistent fact?

Pre-registered 2026-06-05 (BEFORE the run). JEP-249 noted the substrate store holds POSITIVE edges with no native
negation. This BET tests whether a CONTRADICTION can be represented and detected NATIVELY via energy frustration:
assert X→Y AND X→(not Y) by training the key X toward both `code[Y]` and its anti-pattern `−code[Y]`; the shared
key is pulled to opposite value attractors → FRUSTRATION → a shallower (higher) energy minimum + ambiguous retrieval.
If so, energy/confidence flag inconsistency natively, complementing the engine's symbolic `consistency_audit`.

## Method (no transformer; Ising-style frustration)
- JEP-232 store. CONSISTENT key: train only `concat(code[X], code[Y])`. CONTRADICTED key: train BOTH
  `concat(code[X], code[Y])` AND `concat(code[X], −code[Y])` (same key, opposite value = the negation).
- For each key, retrieve (clamp key, relax) and measure: (1) settled ENERGY; (2) retrieval CONFIDENCE = max over the
  value slot of `|val · code[Y]|` (clean match to +Y or −Y = high; frustrated mush = low). Several consistent +
  several contradicted keys in one net (within capacity). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J250a | Contradiction RAISES energy | mean energy(contradicted) > mean energy(consistent) by ≥ 20% of the consistent magnitude (both seeds) |
| J250b | Contradiction LOWERS confidence | mean confidence(contradicted) < mean confidence(consistent) by ≥ 0.30 (normalized by KEY), both seeds |
| J250c | A threshold SEPARATES them | a single energy cut classifies consistent vs contradicted keys at ≥ 0.85 accuracy (both seeds) |
| J250d | Consistent facts still recalled | every consistent key retrieves its correct Y (frustration is confined to the contradicted keys), both seeds |

PASS = J250a–c → the substrate NATIVELY flags a contradiction by energy frustration: an inconsistent fact sits in a
shallower, ambiguous minimum, energy-separable from consistent facts. NULL/finding: if J250a fails (energies equal),
the opposite-value patterns do NOT frustrate here (the net stores one and drops the other cleanly, no frustration) —
then contradiction stays purely symbolic. No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. The two patterns for a contradicted key share the KEY half but have OPPOSITE value halves, so the
contrastive-Hebbian updates to the key→value weights partially CANCEL → no deep clean attractor for that key →
shallower (higher) energy (J250a) and an ambiguous value that matches neither +Y nor −Y well (J250b), energy-
separable from consistent deep minima (J250c), while consistent keys are unaffected (J250d). This is Ising
frustration (competing constraints with no satisfying ground state) used as a native inconsistency signal. RISK
(in-rung): the net might just store ONE of the two opposite patterns (winner-take-all) and look CONSISTENT (deep
energy, clean retrieval of one) → J250a/b fail and contradiction does NOT frustrate — a clean NULL either way; check
whether the contradicted retrieval is ambiguous (frustration) or cleanly one-sided (winner-take-all). Established
(Ising frustration, Hopfield spurious/mixed states, contrastive-Hebbian), named; no novelty — the value is testing
whether the substrate has a NATIVE consistency signal or whether consistency stays symbolic.

## RESULT (2026-06-05): NULL — energy does NOT flag contradiction (confounded by training frequency); consistency stays symbolic

| seed | energy consistent / contradicted | confidence consistent / contradicted | sep-acc | all-consistent-recalled |
|------|----------------------------------|--------------------------------------|---------|-------------------------|
| 42 | −101.9 / **−119.1** | 0.53 / 0.53 | 0.00 | False |
| 7  | −98.8 / −103.9 | 0.79 / 0.31 | 0.38 | False |

- **J250a ✗ (prediction WRONG, in the opposite direction)** — the contradicted key came out DEEPER (lower energy),
  not shallower: a contradicted key is trained on TWO patterns (Y and −Y), so it receives ~2× the contrastive-Hebbian
  updates → larger weights → LOWER energy. The JEP-249 support→depth effect CONFOUNDS the frustration signal (more
  training dominates any frustration-induced shallowing). J250c ✗ (energy can't separate). 
- **J250b partial** — the CONFIDENCE/ambiguity signal DOES show frustration on seed 7 (0.79 vs 0.31: the contradicted
  value matches neither +Y nor −Y) but NOT on seed 42 (0.53 vs 0.53) — not robust.
- **J250d ✗** — the conflicting opposite-value patterns degrade the store (not all consistent facts recalled): the
  frustration spills over and interferes, rather than staying confined.

**FINDING (a clean NULL that CONFIRMS the noted limit by test):** the substrate does NOT natively flag a contradiction
by energy. Two mechanisms defeat it: (1) energy is confounded by TRAINING FREQUENCY (a contradicted key, having more
patterns, is DEEPER not shallower — exactly the JEP-249 effect, here a confound), and (2) the conflicting patterns
INTERFERE with the rest of the store (J250d). The confidence/ambiguity signal partially indicates frustration but is
seed-dependent. So NEGATION and CONTRADICTION are NOT native to the positive-edge attractor store — they stay in the
SYMBOLIC layer (the engine's `not_properties` + `consistency_audit`), exactly the boundary JEP-249/the pattern doc
noted, now established by test rather than assertion. CALIBRATION: I predicted frustration → higher energy; it was
LOWER, because I did not carry forward JEP-249 (support deepens energy) as a confound for the unequal-pattern-count
design — the recurring lesson "carry your own lessons forward" (cf. JEP-154). Verdict: **NULL** (the honest finding:
the substrate's energy is a plausibility/confidence signal for POSITIVE facts, not a consistency signal). Established
(Ising frustration, Hopfield mixed states), named; no novelty.
