# JEP-419 — Teaching English (2): a synonym vocabulary from Fernald's dictionary

## Motivation
Michael supplied real English resources (Fernald, "English Synonyms and Antonyms"). The LLM teacher reads the
dictionary and teaches the substrate a curated set of clean, interchangeable synonyms so it understands varied phrasing
broadly. Also fixes synonym PERSISTENCE through consolidation/compaction. No transformer in the substrate.

## Method
The LLM distills ~33 safe synonym pairs (variant→canonical) from Fernald (the book warns most synonyms carry nuance, so
the teacher curates). Teach via "X means Y"; verify the substrate understands facts/questions phrased with synonyms;
verify the vocabulary persists (synonyms now carried through `consolidate_closure`/`compact` and saved in meta.json).

## Pre-registered bars
- **J419a:** ≥25 synonym pairs taught and stored, both seeds (0, 7).
- **J419b:** ≥7/8 facts taught with one word are understood when asked with a synonym (big/large, fast/quick, …).
- **J419c:** the vocabulary persists across save/load; `tests/test_conversation.py` passes.

## Result: **PASS** — 33 synonyms taught, **8/8** synonym Q&A, persists across save/load, 10 tests pass (both seeds).
Fixed: synonyms now carried through consolidation and compaction (they were dropped, like closed_relations once was).

## Verdict: **PASS — the substrate gained an English synonym vocabulary from a real dictionary**
The LLM teacher gave the substrate a curated synonym vocabulary from Fernald; it now understands the same fact/question
phrased with different words (big≈large, smart≈intelligent, …), and the vocabulary is durable. Concrete progress on
"teach English first": broader UNDERSTANDING of varied phrasing. (It still does not generate fluent prose — that is the
LLM's role.) No transformer in the substrate.
