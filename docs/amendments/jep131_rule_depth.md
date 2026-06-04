# JEP-131 — the boundary of structure learning: rule depth x vocabulary size

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 depth-2 discovery stays robust at large vocabulary; depth-3 (|R|^3 candidates, more spurious matches)
  degrades faster with vocabulary size — the combinatorial boundary. MOST-LIKELY MISS: depth-3 holding up
  better/worse than expected.

## Acceptance (characterization)
- Report discovery accuracy across rule-depth {2,3} x vocab-size {few,medium,many}. The degradation IS the
  finding. Established (rule discovery), named; no novelty.

## Result — calibration MISS (3rd over-prediction of structure-learning difficulty); CORRECTED finding
| depth\nbase | 3 | 6 | 10 |
|-------------|---|---|----|
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |

CORRECTION: the script printed a pre-written "finding" claiming degradation — the DATA CONTRADICTS it. Discovery
accuracy is ROBUST (1.00) across depth 2-3 x vocabulary 3-10. WHY: the correct composition matches the target
EXACTLY (F1=1.0) while random spurious chains rarely coincide exactly, so the right rule is UNIQUELY IDENTIFIABLE
even at depth 3. The real limit is NOT accuracy/identifiability but SEARCH COST: |R|^depth candidate chains (depth 3
x vocab 10 = 1000, manageable; depth 5 x vocab 50 = 312M, intractable by brute force). So the boundary is
COMPUTATIONAL (addressable by smarter search), not statistical. CALIBRATION: MISS (predicted depth-3 degradation;
got 1.00). META-INSIGHT: this is the THIRD over-prediction of structure-learning difficulty (JEP-129's spurious-
match worry, and JEP-131's two implicit degradation predictions) — I SYSTEMATICALLY over-estimate how hard learning
structure from CLEAN data is; exact-match/co-occurrence signals are much stronger than my intuition. Durable lesson
logged. Tally 29/45. The honest JEP-69/70 reframe: structure IS learnable from clean data up to the SEARCH-COST
limit; the open problems are NOISY/sparse data (JEP-128), LEARNING the base relations, and search efficiency at
scale — NOT statistical identifiability. Established (rule discovery), named; no novelty.
