# GEO-43 — Robustness to a NOISY real-world store (paraphrase, typos, near-duplicate entities)

## Motivation
Every prior test used clean, templated facts. Real knowledge stores are messy: facts phrased inconsistently,
typos, and near-duplicate entity names ("Jon Smith" vs "John Smith"). GEO-43 tests whether the geometric
retrieval/reasoning degrades gracefully under realistic noise — a deployability question.

## Pre-registration (locked BEFORE run)
- 15 person->city facts. Build a NOISY variant: each fact randomly paraphrased (varied templates) + ~10%
  character typos; entity names include near-duplicates (add 5 distractor people with names 1-2 edits from
  real ones, with different cities).
- Query with the CANONICAL question; measure 1-hop retrieval accuracy on CLEAN vs NOISY store.
- Also: near-duplicate confusion rate (does a query for "John Smith" wrongly return "Jon Smith"'s fact?).
- Bars (characterization): report clean vs noisy accuracy + confusion rate. Flag if noisy drops > 0.2 below
  clean (fragile) or holds within 0.1 (robust). Honest either way; no pass/fail tuning.
