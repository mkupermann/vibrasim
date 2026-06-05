# JEP-156 — controlled GENRE minimal-pair + bare-NP precision guard (isolating the cause of the parse gate)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 with a bare-NP subject guard, Hearst extracts genuine taxonomy at HIGH precision (>0.7) from encyclopedic prose
  with KNOWN ground truth, while the SAME extractor stays NEAR-ZERO on Boole (guard cuts its 326 spurious candidates
  sharply) — isolating GENRE as the causal variable and clearing the gate on the right genre. MOST-LIKELY MISS: the
  bare-NP guard too strict (kills genuine encyclopedic pairs) or too loose (still passes Boole fragments).

## Acceptance (characterization)
- Same Hearst+guard extractor on two genres. Report: encyclopedic precision/recall vs KNOWN ground truth; Boole
  spurious-candidate reduction. Demonstrating GENRE (not extractor) as the cause via a controlled minimal pair is
  the finding. Established (Hearst patterns; constituency/NP-chunking); named; no novelty.

## Result — PASS (HIT)
| genre (SAME Hearst+bareNP extractor) | result |
|--------------------------------------|--------|
| Encyclopedic (known ground truth, 14 gold pairs) | precision 0.87, recall 0.93 (13 TP, 2 FP, 1 FN) |
| Boole (logic/philosophy prose) | 62 pairs, ALL fragments/pronouns ('it IS-A fact', 'a IS-A constituent'), ~0 genuine |

CONCLUSIVE controlled minimal pair: the same classical Hearst + bare-NP extractor yields genuine taxonomy at 0.87
precision on encyclopedic prose but ~0 genuine pairs on Boole — GENRE is the causal variable, not the extractor.
The bare-NP subject guard (short NP: optional quant/article + <=2 adjectives + head noun, no conjunctions/preps/
clause markers) FIXES the JEP-155 precision leak (Boole candidates 326 -> 62, and the 62 are still all fragments).
HONEST minor edges (not genre confounds): the 2 encyclopedic FPs ('bark','fly') come from the 'such as' list parser
grabbing trailing VPs ('...have bark','...can fly'); the 1 FN (penguin) from 'a bird that cannot fly' — the trailing
relative clause makes the parent NP non-bare, correctly rejected but the pair lost. POSITIVE HEADLINE: on the RIGHT
genre, the engine bootstraps genuine taxonomy from REAL prose at 0.87 precision with classical Hearst + NP-chunking,
NO transformer — concrete progress on the learn-from-sources goal. The learn-from-sources path is: encyclopedic
register + Hearst + bare-NP guard + the engine's existing parse->bind->infer. Prediction HIT; tally 51/71.
Established (Hearst 1992 lexico-syntactic patterns; NP chunking); named; no novelty.
