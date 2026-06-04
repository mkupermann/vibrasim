# JEP-97 — engine tier 6: human-like LEARNING a concept from EXAMPLES (shown, not told)

## Why
Third learning mode (after told-facts JEP-92 and correction JEP-96): acquire a NEW concept from a few perceptual
EXAMPLES (like a child shown several birds), form its prototype, recognize new instances, and integrate it into
the comprehension machinery.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 held-out recognition of the new concept >= 0.90 from 5 examples; existing concepts unaffected (>=0.95); after
  "A bird is an animal", grounded comprehension on a NEWLY perceived bird = 100%. MOST-LIKELY MISS: a few-shot mean
  prototype off-center -> some held-out misrecognition if noise high; mitigated by 5 examples + distinct prototype.
  Predict pass.

## Acceptance
- PASS: held-out recognition >= 0.90 AND existing concepts >= 0.95 AND grounded comprehension on the learned
  concept = 100%. Established (prototype/nearest-mean classification - Rosch prototype theory), named; no novelty.

## Calibration (after) — HIT (with perception caveat)
🔮 predicted pass; ACTUAL held-out 1.00 / existing 1.00 / comprehension 1.00. HIT. Tally 6/9. CAVEAT (self-flagged,
as in JEP-91): perception is EASY here (well-separated random prototypes, low noise) so recognition saturates at
1.00 — the contribution is the concept-from-examples LEARNING MODE, not hard perception (JEP-54/56 covers the hard
regime).

## Result — PASS
The engine learns a new concept from 5 perceptual examples (prototype = mean), recognizes held-out instances (1.00),
leaves existing concepts intact (1.00), and integrates the new concept into comprehension: told "A bird is an
animal", a NEWLY perceived bird is inferred to be an animal (1.00); explain -> "Yes. A bird is an animal." This is
the THIRD human-like learning mode in the engine (after told-facts JEP-92 and correction JEP-96). Established
(prototype/nearest-mean classification - Rosch prototype theory), named; no novelty.
