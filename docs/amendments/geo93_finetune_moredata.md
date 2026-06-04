# GEO-93 — Does fine-tuning help with SUBSTANTIAL data? (validate the GEO-92 claim)

## Motivation
GEO-92 (10 pairs) was data-limited and I CLAIMED fine-tuning helps with "hundreds+" without testing it. GEO-93
tests that claim directly: ~120 query<->fact pairs with a SYSTEMATIC vocabulary gap (colloquial query vs formal
fact), train/test split, fine-tune, and check if retrieval improves with substantial data. Validates or refutes
my own assertion — honesty demands testing it.

## Pre-registration (locked BEFORE run)
- ~40 entities, each with a colloquial query and a formal fact using DIFFERENT vocabulary (a real gap the
  general embedder may not bridge). 120 pairs via templates. Split 100 train / 20 test (disjoint entities).
- Fine-tune all-MiniLM-L6-v2 (MultipleNegativesRankingLoss) on 100 train pairs; test held-out 20.
- Metric: held-out retrieval hits@1, frozen vs fine-tuned. Bar: fine-tuned >= frozen + 0.1 (FT helps with
  substantial data, validating the claim). NULL if it doesn't even with 100 pairs (refutes my claim — honest).
