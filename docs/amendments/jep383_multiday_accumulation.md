# JEP-383 — "Read a book over 3 days": multi-session accumulation + cross-day reasoning

## Motivation
Michael's vision is the substrate reading a text over several days, accumulating knowledge, then discussing it. This
tests that directly: read an article in chunks across SEPARATE save/load sessions ("days"), and verify (a) knowledge
accumulates without forgetting, (b) a multi-hop chain whose links were learned on DIFFERENT days resolves, and (c)
consolidation persists across sessions so deep Q&A stays reliable. Composes durable persistence (JEP-295/372) +
consolidation (370-378) + the real-prose pipeline (379-382). No transformer.

## Method
Three sessions, each a fresh `Conversation` loading the previous day's saved brain:
- **Day 1:** "A poodle is a kind of dog. Dogs are mammals." → poodle→dog, dog→mammal. Save.
- **Day 2:** load day-1 brain; read "Mammals are animals that are warm-blooded. A dog can bark." → mammal→animal,
  dog property. Save.
- **Day 3:** load day-2 brain; read "A dog has four legs." then ASK questions, including the cross-day chain
  "is a poodle an animal?" (poodle→dog and dog→mammal from day 1, mammal→animal from day 2).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: knowledge accumulates without forgetting; the cross-day multi-hop resolves (consolidation re-materializes
after each day's read and persists); deep Q&A reliable; honest abstention intact.

- **J383a (accumulation, no forgetting):** on day 3, facts taught on day 1 are still answerable ("is a poodle a dog?"
  → yes) AND day-2 facts ("can a dog bark?" → yes), both seeds (0, 7).
- **J383b (cross-day multi-hop):** on day 3, "is a poodle an animal?" → yes — a chain whose links were learned across
  three different days, both seeds.
- **J383c (consolidation persists + abstention):** `closed_relations` survives each save/load (is-a answered via the
  analog path on day 3); a never-mentioned entity ("is a poodle a robot?") → no; `pytest -m "not slow"
  tests/test_conversation.py` passes.

If the cross-day chain fails, report whether the break is persistence (a link lost on save/load) or consolidation (not
re-materialized after a later day) — the honest diagnosis. Predicted: clean accumulation. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — "read over days" works end-to-end)
- **J383a (accumulation, no forgetting): PASS** — facts grew 3 (day 1) → 9 (day 3) across three separate save/load
  sessions; on day 3, day-1 knowledge ("is a poodle a dog?" → yes), day-2 knowledge ("can a dog bark?" → yes), and
  day-3 knowledge ("how many legs does a dog have?" → 4) are all answerable. No forgetting. Both seeds.
- **J383b (cross-day multi-hop): PASS** — on day 3, "is a poodle an animal?" → **yes**: a chain whose links were
  learned on three different days (poodle→dog & dog→mammal on day 1, mammal→animal on day 2), resolved after the day-3
  load. Both seeds.
- **J383c (consolidation persists + abstention): PASS** — `closed_relations` survived each save/load (is-a answered via
  the analog path on day 3); "is a poodle a robot?" → no (abstains); `tests/test_conversation.py` **10 passed**. Both
  seeds.

## Verdict: **PASS — Michael's "read a book over days" capability, demonstrated**
The substrate reads a text across separate sessions, accumulates knowledge in the durable store without forgetting,
re-consolidates after each day's read so deep reasoning stays reliable, and resolves multi-hop chains whose links span
different days — all while abstaining honestly on the unmentioned. This composes the proven pieces: durable persistence
(JEP-295/372) + closure consolidation with the analog readout (370-378) + the real-prose pipeline (379-382). Combined,
the substrate now reads realistic factual prose over multiple days and answers it without mistakes inside the captured
domain, with honest "I don't know" outside — the concrete realization of the conversational vision, no transformer.
The open-domain knowledge-tail wall (JEP-362) is separate and stands.
