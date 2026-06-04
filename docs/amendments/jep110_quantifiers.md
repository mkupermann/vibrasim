# JEP-110 — quantified questions (universal/existential), Boole's own subject

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: "is every dog an animal?" -> Yes (taxonomy is_a); "can all birds fly?" -> No, with the penguin
  counterexample named; "are all poodles dogs?" -> Yes. MOST-LIKELY MISS: the all/every parse forms or the
  no-instances edge.

## Acceptance
- PASS: quantifier battery = 100%. Established (universal quantification over a taxonomy + defeasible properties),
  named; no novelty.

## Result — PASS (HIT)
Quantifier battery 5/5: "is every dog an animal?" -> Yes; "are all poodles dogs?" -> Yes; "is every poodle an
animal?" -> Yes (multi-hop universal); "can all birds fly?" -> "No - not all. For example, a penguin cannot fly."
(named counterexample); "do all robins fly?" -> "Yes, all robins can fly." Prediction HIT; tally 13/22; 21 tests
gated green. Universal IS-A reduces to taxonomy is_a (a category subsumes another); universal property checks all
instances with defeasible exceptions. Established (universal quantification), named; no novelty. HONEST: universal
over KNOWN instances (open-world: silent about unobserved instances).
