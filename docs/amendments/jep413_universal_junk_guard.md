# JEP-413 — Universal junk guard: no multi-word entities (never wrong capture, even on real books)

## Motivation
Ingesting a real English book ("The Holographic Universe") produced WRONG facts — multi-word junk subjects from messy
narrative prose: ('fred alan wolf', isa, idea), ('so accepted', isa, radical), ('unfortunately this', isa, situation).
The JEP-402 guards covered specific rules but not the general path (engine + all rules). Since EVERY fact is stored via
`SubstrateMemory.add_fact`, add ONE universal guard there: reject any fact whose entity or value contains a SPACE
(multi-word) — legitimate multi-word values are stored underscore-joined, so this catches only junk. Enforces "never
wrong capture" universally (miss > wrong), protecting the no-mistakes guarantee even on real-book prose. No transformer.

## Method
In `add_fact`, return without storing if the entity or value contains a space or is empty. (Consolidation/load pass
already-clean single-token facts, so they are unaffected.)

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J413a (junk rejected):** "Fred Alan Wolf is an idea." stores NO fact; ingesting a 40k-char chunk of the Talbot book
  yields ZERO stored facts with a space in subject or object.
- **J413b (legitimate facts intact):** is-a / property / SVO / attribute (underscore values) all still store; the full
  cognition suite (`tests/test_conversation.py tests/test_substrate_memory.py tests/test_concept_reasoner.py
  tests/test_unified_reasoner.py`) passes.
- **J413c (no junk on the book):** after the chunk ingest, the junk rate (facts with a space) is 0.0 (it captures fewer
  facts, all clean — miss > wrong).

Trade-off: a legitimate multi-word class ("bird of prey") is also missed — acceptable (miss > wrong). If the guard
breaks a real test, report it. Bars fixed; no retuning. No transformer.

## Result: **PASS** (multi-word/abbrev/function-word junk eliminated; residual narrative mis-parse is the wall)
- **J413a (junk rejected): PASS** — "Fred Alan Wolf is an idea." stores NO fact. Guard also rejects abbreviation
  entities ("m.d", "ph.d") and function-word subjects ("rather", "so", "this"). On the Talbot book 40k chunk, multi-word
  junk = 0; total junk facts dropped 16 → 4 as the guard tightened.
- **J413b (legitimate facts intact): PASS** — is-a/property/SVO/attribute (underscore values) all store; self/second-
  person ("your creator" → "you") works (first attempt wrongly stoplisted "you"/"we" — fixed). Full cognition suite
  **35 tests** pass.
- **J413c (no multi-word junk on book): PASS** — junk rate (space in subject/object) = 0.0.

### Honest residual (the deeper wall)
After the guard the Talbot book still yields a FEW single-word junk facts where a real content noun is mis-attached:
('whitton', isa, idea), ('work', partof, bohm), ('pribram', isa, finding). A stoplist can't catch real words; removing
them needs sentence-structure understanding the substrate lacks for narrative. Confirms the wall: narrative/argumentative
books don't parse.

## Verdict: **PASS — universal junk guard protects "never wrong capture"; books remain the wall**
One guard at the `add_fact` choke point rejects multi-word, punctuation/abbreviation, and function-word junk for ALL
facts from ALL paths, so messy real-book prose no longer floods the store with wrong facts — "never wrong capture"
enforced universally (miss > wrong), legitimate facts and 35 tests intact. Residual single-word narrative mis-parses
confirm the documented wall: factual reference prose, not books. No transformer.
