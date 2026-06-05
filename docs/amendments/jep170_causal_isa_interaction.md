# JEP-170 — causal / taxonomy INTERACTION, and its ASYMMETRY with mereology

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 causes_effect does NOT follow is-a (gap), parallel to part-of. Valid: effect-side (X causes Y, Y is-a Z =>
  X causes Z) and cause-side subtype inheritance (X is-a W, W causes Y => X causes Y). Both tractable, same leak risk.

## Result — PASS (HIT) + a genuine relation-type ASYMMETRY captured
Confirmed the gap (both False). Implemented the two VALID causal/is-a interactions:
1. EFFECT-side UP: X causes Y, Y is-a Z => X causes Z ('smoking causes cancer, a cancer is a disease' -> smoking
   causes a disease). causes_effect(smoking,disease)/condition = True.
2. CAUSE-side subtype: a subtype inherits its supertypes' causal powers ('a poodle is a dog, a dog causes allergies'
   -> a poodle causes allergies). Seeded the causal search with x AND its is-a ancestors.
THE KEY ASYMMETRY (vs JEP-169 mereology): an effect's SUBtype is NOT entailed — causes_effect(smoking,lung_cancer)
stays FALSE even though lung-cancer is-a cancer, because 'smoking causes cancer' does not mean it causes every KIND
of cancer (the effect is kind/existential, not distributive). Contrast mereology, where a whole's subtype DOES
inherit the part (a poodle has a heart). So the engine now models that DIFFERENT relation types interact with
taxonomy under DIFFERENT, correct rules — parts distribute to subtypes, effects do not. Negatives hold:
causes_effect(animal,allergy) False (supertype doesn't inherit), causes_effect(disease,smoking) False (asymmetric).
52/52 regression tests green (+1) incl. the existing causal/intervention tests (do-operator preserved). Prediction
HIT; tally 62/86. Established (causal inference, kind-level vs distributive semantics); named; no novelty.
