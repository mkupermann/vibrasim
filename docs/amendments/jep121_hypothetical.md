# JEP-121 — hypothetical / counterfactual reasoning ("if X were a Y, would it be a Z?")

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: assume the hypothetical (X->Y), answer the embedded question, then RETRACT so the KB is unchanged.
  "if a whale were a fish, would it be an animal?" -> Yes (fish->animal); KB unchanged after. MOST-LIKELY MISS:
  the "if ...,...?" parse, pronoun 'it', or retraction leaving residue.

## Acceptance
- PASS: hypothetical battery = 100% AND the KB is unchanged after each hypothetical. Established (assumption-based
  reasoning + belief revision), named; no novelty.

## Result — capability PASS; calibration MISS (the 3 named risks all materialized)
First run 2/5: (1) "would it be" -> I replaced "would"->"is" leaving "be" ("is whale be an animal", garbled);
(2) retraction left an empty-set key for newly-created concepts (rock) -> KB changed; (3) the garbled parse
returned "No". All three were the risks I PREDICTED but did not prevent. Fixed: "would X be"->"is X" substitution,
and delete a newly-created empty key on retract. After fix 5/5: "if a whale were a fish, would it be an animal?"
-> "Yes. A whale is a fish, a fish is an animal."; KB UNCHANGED after (whale still an animal via mammal, NOT a
fish). Counterfactual reasoning under a temporary assumption with clean belief-revision retraction. CALIBRATION:
MISS (predicted 100% first-try); tally 20/35; 28 tests gated green. Established (assumption-based reasoning + belief
revision), named; no novelty. LESSON: predicting a risk is not preventing it — when you name 3 risks, BUILD the
guards before running, don't just hope.
