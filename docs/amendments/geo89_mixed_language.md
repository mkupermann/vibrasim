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
