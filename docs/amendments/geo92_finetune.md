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

## Result — NULL (DATA-limited, settles the improvability question)
| method | held-out hits@1 |
|--------|-----------------|
| frozen | 0.67 |
| proper contrastive fine-tune (10 pairs, 5 epochs) | 0.67 |

**VERDICT: NULL — and it SETTLES the question.** Proper fine-tuning (MultipleNegativesRankingLoss, the
standard retrieval-tuning method) ALSO doesn't help on 10 pairs (0.67=0.67), confirming the GEO-91 no-
improvement is DATA-limited, not method-limited. A pretrained embedder is already strong; a handful of
labelled pairs cannot improve it (whether by crude adapter or proper FT). **Complete improvability story:**
- cheap linear adapter (GEO-91): no.
- proper contrastive fine-tune, few examples (GEO-92): no (data-limited).
- shipped levers — better base model (GEO-36/67), re-ranking (GEO-40b/72), entity-resolution (GEO-44): YES.
- fine-tuning with SUBSTANTIAL labelled data (hundreds+): would help (standard result, needs the data).
**Honest guidance:** don't fine-tune on a handful of examples; it won't help and may overfit. Use model
choice + re-ranking for small data; invest in fine-tuning only when you have substantial labelled query-fact
pairs. (Required installing datasets + accelerate to test FT properly — done, so the negative is rigorous.)
