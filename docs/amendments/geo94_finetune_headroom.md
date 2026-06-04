# GEO-94 — Fine-tuning WITH genuine headroom: teach an English model cross-lingual retrieval

## Motivation
GEO-91/92/93 couldn't test fine-tuning improvement (data-limited or no headroom). GEO-89 gives REAL headroom:
the English-only model is weak on German queries (0.60). GEO-94 fine-tunes the English model on German-query
-> English-fact pairs and tests whether it LEARNS cross-lingual retrieval (improving from ~0.60). This finally
tests whether fine-tuning improves retrieval where frozen genuinely fails — settling the improvability question.

## Pre-registration (locked BEFORE run)
- English-only model all-MiniLM-L6-v2. ~80 German-query/English-fact training pairs (varied) + 20 held-out
  (disjoint content).
- Fine-tune (MultipleNegativesRankingLoss). Frozen vs fine-tuned held-out German->English retrieval hits@1.
- Bar: fine-tuned >= frozen + 0.15 (FT teaches cross-lingual retrieval). NULL if it doesn't learn it.
  Frozen expected ~0.5-0.7 (genuine headroom); a multilingual model would already be ~1.0 (the alternative).
