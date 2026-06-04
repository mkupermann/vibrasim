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

## Result — INCONCLUSIVE (no headroom; honest test-design flaw)
| method | held-out hits@1 |
|--------|-----------------|
| frozen | 1.00 |
| fine-tuned (99 pairs) | 1.00 |

**VERDICT: INCONCLUSIVE.** The frozen model was ALREADY at ceiling (1.00) on the held-out set — the test
facts were distinct roles, so retrieval was trivially easy and there was NO HEADROOM to show fine-tuning
improvement. So this does NOT validate or refute the "fine-tuning helps with substantial data" claim; the
test was uninformative (my design flaw — I needed a task where frozen retrieval is WEAK, ~0.5-0.7, which I
could not construct cleanly with synthetic data without an artificial gap).

## Honest correction to the improvability claim (GEO-91/92/93)
Across three attempts I could NOT demonstrate that fine-tuning improves retrieval at PC scale with synthetic
data: GEO-91 (crude adapter, data-limited), GEO-92 (proper FT, 10 pairs, data-limited), GEO-93 (proper FT,
99 pairs, but frozen at ceiling — no headroom). So I should NOT assert "fine-tuning helps with hundreds+" as
if I showed it — I did not. Honest position: fine-tuning embedders on labelled retrieval pairs is a STANDARD,
well-established improvement method in the literature (MultipleNegativesRankingLoss etc.), but THIS programme
did not demonstrate it, because (a) too few examples, or (b) the synthetic tasks left no headroom. What I CAN
stand behind (demonstrated here): better base model (GEO-36/67), re-ranking (GEO-40b/72), entity-resolution
(GEO-44) improve retrieval. Fine-tuning is plausible-but-undemonstrated at this scale. 19th self-correction:
I over-asserted in GEO-92; corrected here.
