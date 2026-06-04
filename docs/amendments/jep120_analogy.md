# JEP-120 — relational analogy in the engine ("A is to B as C is to ?")

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: find the relation linking A->B, apply to C ("dog is to puppy as cat is to ?" -> "Kitten."); report
  failure when it can't complete. MOST-LIKELY MISS: the analogy parse, or multiple relations linking A,B.

## Acceptance
- PASS: analogy battery = 100%. Established (relational analogy; JEP-71b did it standalone with VSA), named; no novelty.

## Result — PASS (HIT)
Analogy battery 4/4: "dog is to puppy as cat is to?" -> "Kitten."; "...as cow is to?" -> "Calf."; with a leading
"what is" -> "Kitten."; unsolvable -> "I can't complete that analogy." Prediction HIT; tally 20/34; 27 tests gated
green. The engine finds the relation linking A->B and applies it to C — relational analogy (Gentner structure-
mapping in its simplest form; JEP-71b did it standalone with VSA). Established, named; no novelty. HONEST: needs the
analogous relation explicitly present for C; multi-relation A->B picks any shared relation.
