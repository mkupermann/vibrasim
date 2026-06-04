# GEO-89 — Mixed-language KB (German + English facts and queries)

## Motivation
The user works in German; a realistic personal KB mixes German and English (notes, contacts). GEO-46 tested
DE-query -> EN-fact. GEO-89 tests a MIXED-language store (some facts German, some English) with both German
and English queries via the multilingual model — the realistic bilingual personal-use scenario.

## Pre-registration (locked BEFORE run)
- Model: paraphrase-multilingual-MiniLM-L12-v2.
- KB: 6 facts in German + 6 in English (mixed personal facts). 10 queries: some German, some English, some
  cross-language (German query -> English fact and vice versa).
- Metric: retrieval hits@1. Bar: >= 0.8 (the multilingual model handles a mixed-language KB + queries).
  NULL if language mix degrades it. Compare to an English-only model (expected to fail on German).

## Result — PASS (bilingual personal KB works)
| model | mixed-language hits@1 |
|-------|------------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | **1.00** |
| all-MiniLM-L6-v2 (English-only) | 0.60 |

**VERDICT: PASS.** The multilingual model handles a MIXED German+English KB with cross-language queries at
1.00 — German queries retrieve both German and English facts and vice versa ("Wer macht die Buchhaltung?" ->
Tom's English fact; "Who is the lawyer?" -> Maria's German fact). The English-only model fails on German
(0.60). **Directly useful for the German-speaking user:** keep a mixed German/English personal KB (notes,
contacts) and query in either language — set `GeometricReasoner(model_name="paraphrase-multilingual-MiniLM-
L12-v2")`. The shared multilingual embedding space maps both languages to the same semantic geometry (a
property of the embeddings, GEO-46/69). The bilingual personal-use scenario the user would actually have works.
