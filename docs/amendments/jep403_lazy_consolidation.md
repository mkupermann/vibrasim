# JEP-403 — Lazy consolidation: reliable deep reasoning for interactive (GUI) teaching

## Motivation
The GUI/talk loop teaches via single statements (`say`), which — unlike bulk `read_text` (JEP-372) — does NOT
auto-consolidate. So a user who teaches a deep chain interactively and then asks a multi-hop question gets the
un-consolidated BFS path, which degrades at scale (JEP-368). Fix: consolidate LAZILY — mark the store dirty when a
statement adds facts, and consolidate once before answering a reasoning question if dirty (then clear the flag). This
keeps teaching cheap (no rebuild per statement) while guaranteeing deep reasoning is reliable whenever a question is
asked. No transformer.

## Method
- `Conversation`: a `_dirty` flag set true in `_learn_one` when facts are added.
- In `say`, before answering a QUESTION, if `_dirty`, call `consolidate()` and clear the flag.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: interactive teaching (statement-by-statement) yields reliable deep multi-hop at a scale where the
un-consolidated walk would degrade; consolidation runs lazily (only before a question after new teaching); no regression.

- **J403a (interactive deep reasoning):** teach a deep taxonomy via individual `say()` statements (≥80 nodes, depth ~8,
  NOT via read_text), then ask deep is-a questions → accuracy ≥0.95, both seeds (0, 7).
- **J403b (lazy, not per-statement):** consolidation runs only before a question after new facts (the store's
  `closed_relations` is set after the first question, and teaching many statements without a question does not
  consolidate), both seeds.
- **J403c (no regression):** a single teach→ask still works ("A poodle is a dog. A dog is a mammal." → "is a poodle a
  mammal?" yes); `pytest -m "not slow" tests/test_conversation.py` passes.

If lazy consolidation makes interactive deep reasoning unreliable or over-consolidates, report it. Predicted clean.
Bars fixed; no retuning. No transformer.

## Result
(filled after the run)
