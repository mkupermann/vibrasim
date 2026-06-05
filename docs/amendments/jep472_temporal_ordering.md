# JEP-472 — Temporal/event ordering: before/after reasoning (the narrative gap)

## Motivation
The conversational brain handles static facts (is-a, part-of, causes, properties, affect) but has NO
temporal/event ordering — "X comes before Y" stores nothing, "what comes after X?" abstains. Real
narrative text (the books Michael fed it) is sequences of events, so this is a core gap behind the
narrative wall. JEP-472 adds before/after as a TRANSITIVE relation, with forward/backward and multi-hop
queries.

## Method (`world/conversation.py`, `world/brain_query.py`, runner)
- Parse "X (comes|happens|happened|is|was|occurs) before Y" → `(X, before, Y)`; "...after Y" →
  `(Y, before, X)`. (`conversation.py`, before the SVO fallback.)
- `brain_query`: "what comes/happens after X?" → the Y with `(X, before, Y)`; "what comes before X?" →
  the Y with `(Y, before, X)`; "is X before Y?" → TRANSITIVE reachability over `before` edges; "is X
  after Y?" → transitive `(Y before X)`. (`_before_reachable` BFS.)

## Pre-registered PREDICTION + bars (BEFORE the run, via live Conversation)
World: "Breakfast happens before lunch." + "Lunch happens before dinner." + "The egg comes before the
chicken."
- **J472a (forward/backward):** "what comes after breakfast?" → lunch; "what comes before dinner?" →
  lunch; "what comes after the egg?" → chicken. Both seeds.
- **J472b (multi-hop transitivity):** "is breakfast before dinner?" → yes (breakfast→lunch→dinner); "is
  dinner before breakfast?" → no. Both seeds.
- **J472c (no spurious + suites green):** "is breakfast before the egg?" → no (different chains);
  substrate_memory + conversation suites pass.

PASS = the brain reasons about event order forward, backward, and transitively. NULL if parsing/queries
fail. Bars locked; no retuning. Established (transitive relation reasoning), named; a new capability, not
new science. No transformer.

## RESULT (2026-06-05): **PASS** — event-order reasoning works (forward, backward, transitive)

Both seeds, via live Conversation ("Breakfast happens before lunch." + "Lunch happens before dinner." +
"The egg comes before the chicken."):
- "what comes after breakfast?" → **Lunch**; "what comes before dinner?" → **Lunch**; "what comes after
  the egg?" → **Chicken**
- "is breakfast before dinner?" → **Yes** (multi-hop breakfast→lunch→dinner); "is dinner before
  breakfast?" → **No**; "is breakfast before the egg?" (different chains) → **No**

J472a ✓ · J472b ✓ · J472c ✓ (substrate_memory 14/14 + conversation 10/10 green) → **PASS, both seeds.**

## Verdict: the narrative gap's first rung — event ordering
The brain now stores `before` as a transitive relation and answers forward ("what comes after X?"),
backward ("what comes before X?"), and transitive ("is X before Y?") event-order questions, with no
spurious cross-chain links. This is the first concrete capability toward narrative (sequence) text,
which was a core gap behind the books wall. Established transitive-relation reasoning, named; a new
capability, not new science. No transformer.
