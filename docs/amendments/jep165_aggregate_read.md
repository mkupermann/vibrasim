# JEP-165 — aggregate read() on a realistic connected encyclopedic paragraph (the honest number)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 high precision (>0.9, conservative guards) but moderate recall (~0.7-0.8, losing relative clauses / complex
  predicates / some pronouns). Precision > recall. MOST-LIKELY MISS: recall higher than expected, or an FP dent.

## Result — precision HIT, recall MISS (over-predicted); aggregate recall 0.60
| relation | recall |
|----------|--------|
| is-a | 0.62 (8/13) |
| part-of | 0.25 (1/4) |
| causal | 1.00 (3/3) |
| AGGREGATE | 0.60 (12/20) |
Precision: 0 spurious is-a among 10 wrong probes (high precision, as predicted). RECALL 0.60 — LOWER than predicted
0.7-0.8: I OVER-predicted recall. The aggregate test reveals the per-category 8/8 (JEP-162/163) OVERSTATED real-prose
readiness — connected prose MIXES structures. Honest miss diagnosis (most misses TRACTABLE):
- part-of 'X has Y' ('A fish has gills', 'A bird has feathers and wings') NOT implemented -> 3 part misses. TRACTABLE.
- adjectival parent not reduced to head noun ('a warm-blooded animal' -> parent 'warm-blooded animal' not 'animal').
  TRACTABLE (take head noun).
- irregular plural 'wolves' -> 'wolve' (the -ves->-f rule: wolf/leaf/life) not handled. TRACTABLE bug.
- relative clause 'A salmon, which is a fish, ...' not handled (harder; expected).
- 'Felines such as lions and tigers are predators' -> read got lion->feline (correct!) not lion->predator (double
  binding is genuinely ambiguous; partly a gold-construction issue).
HONEST LESSON: per-category tests OVERSTATE readiness; the AGGREGATE number on connected prose (0.60 recall, high
precision) is the honest one. Precision HIT, recall MISS; tally 57/81. Follow-up JEP-166 implements the tractable
fixes (has-part pattern, -ves singularization, head-noun reduction). Established (extraction eval); named; no novelty.
