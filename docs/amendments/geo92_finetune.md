# GEO-92 — Does PROPER contrastive fine-tuning improve retrieval (vs the crude adapter, GEO-91)?

## Motivation
GEO-91: a crude linear adapter didn't help (data-limited or method-limited?). GEO-92 tests the PROPER method —
contrastive fine-tuning (MultipleNegativesRankingLoss) of a tiny sentence-transformer on the domain query<->
fact pairs — to settle whether the no-improvement is METHOD-limited (crude adapter) or DATA-limited (too few
examples). Completes the improvability question.

## Pre-registration (locked BEFORE run)
- Same vocabulary-gap domain (GEO-91), 16 query-fact pairs, 10 train / held-out 6.
- Fine-tune all-MiniLM-L6-v2 with MultipleNegativesRankingLoss, few epochs, on the 10 train pairs.
- Metric: held-out retrieval hits@1, frozen vs fine-tuned. Bar: fine-tuned >= frozen + 0.1 (proper FT helps).
  NULL if no improvement (DATA-limited — confirms GEO-91 wasn't just a bad method). Honest either way.
