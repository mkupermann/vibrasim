# JEP-396 — Discussion: synthesize what was learned ("tell me about X"), including parts

## Motivation
Michael's vision includes the substrate DISCUSSING what it learned. `describe` already synthesizes a concept's class +
inherited properties + count ("A poodle is a dog; it can bark; it has 4 legs"), but it OMITS part-of knowledge it has
read ("a tail is part of a dog"). Validate discussion-synthesis on read prose and enrich `describe` to include parts,
so "tell me about X" reflects everything the substrate knows about X. No transformer.

## Method
- Validate `describe` synthesizes class + inherited property + count from read prose.
- Add parts to `describe`: include things that are part-of X (or an ancestor of X), e.g. "it has a tail".

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: discussion synthesizes class/property/count (already works) and now also parts; no regression.

- **J396a (class + property + count):** after reading a small article, `say("tell me about a poodle")` mentions its
  class (dog), an inherited property (bark), and the count (4 legs), both seeds (0, 7).
- **J396b (parts included):** `say("tell me about a dog")` mentions a PART it read ("tail"), both seeds.
- **J396c (no regression):** a concept with no parts still describes cleanly (no empty "it has ."); `pytest -m "not
  slow" tests/test_conversation.py` passes.

If adding parts produces malformed output or duplicates, report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PARTIAL** (parts added — the goal — but consolidation degraded parent specificity)
- **J396a (class + property + count): PASS** — "tell me about a poodle" → "a poodle is a dog; it can bark; it has 4
  legs; ...". Both seeds.
- **J396b (parts included): PASS** — "tell me about a dog" → "...it has a leg, a tail." The part-of knowledge is now
  synthesized in the discussion. Both seeds.
- **J396c (clean + no regression): PARTIAL** — output is well-formed (a partless concept describes cleanly, no
  malformed "it has ."), and the suite is **10 passed**. BUT "tell me about a rose" → "a rose is a **plant**" not "a
  rose is a **flower**": after closure consolidation, rose→flower AND rose→plant are both DIRECT edges, so `describe`'s
  `query(x,"isa")` returns an arbitrary ancestor (plant) rather than the MOST-SPECIFIC one (flower). The answer is
  correct (a rose IS a plant) but less informative than it should be.

## Verdict: **PARTIAL — discussion now includes parts; consolidation flattened parent-specificity in `describe`**
The discussion goal is met: "tell me about X" synthesizes class + inherited properties + count + PARTS from read prose,
well-formed. The honest finding J396c surfaced: closure consolidation materializes ALL ancestor is-a edges, so
`describe`'s single-best `query(x,"isa")` no longer reliably returns the most-specific parent (it may return any
ancestor). That makes descriptions correct but less informative ("a rose is a plant" vs "a flower"). This is a real,
clean quality fix — select the most-specific parent among the materialized ancestors — pre-registered as JEP-397. Bars
not moved. No transformer.
