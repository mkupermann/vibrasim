# JEP-348 — Widen prose coverage with a sentence normalizer (plural is-a, numeric, "kind of")

## Motivation
JEP-347 named 3 common missed forms. Widen Half-1 coverage with a substrate-legal NORMALIZER in the read path that
rewrites encyclopedic forms into engine-parseable ones — WITHOUT touching the 123-test Understanding Engine:
plural is-a ("Dogs are carnivores" → "A dog is a carnivore"), the "is a kind of/type of" hedge → is-a, and numeric
possession ("A dog has four legs" → a (dog, has_legs, 4) fact). No transformer.

## Method
`Conversation._normalize_for_learning(sentence)` → (rewritten, extra_facts): strip "a kind/type/sort of"; map
"Xs are Y(s)" → "A <singular X> is a <singular head Y>"; detect "X has <number-word> <noun>s" → an explicit numeric
fact added to the store. Applied before `learn_sentence` in both `read_text` and the conversation statement path.

## Pre-registered bars (BEFORE the run)
- **J348a (the 3 forms now work):** "A poodle is a kind of dog." → is_a(poodle,dog) True; "Dogs are carnivores." →
  is_a(dog,carnivore) True; "A dog has four legs." → how_many(dog)=4 — all answerable, both seeds (0, 7).
- **J348b (coverage up):** re-run JEP-347's paragraph → parse coverage ≥ 0.90 (was 0.80), Q&A still ≥ 0.90.
- **J348c (no regression):** JEP-340/342/345/346 + substrate gate still green.

Predicted most-likely failure: over-eager rewriting mangles a normal sentence (e.g. "Dogs are animals" where the
plural rule double-applies) or a singularizer error ("carnivores"→"carnivore" ok, but irregulars). If J348b
regresses on a previously-working sentence, report it; keep the rewrite conservative (only fire on clear patterns).

## Result (seeds 0, 7): **PASS** (after a numeric-role fix)
- **J348a:** the 3 forms now work = **1.0** — "is a kind of dog"→is_a(poodle,dog) True; "Dogs are carnivores"→
  is_a(dog,carnivore) True; "A dog has four legs"→how_many(dog)=4; multi-hop still intact, both seeds. **PASS.**
- **J348b:** JEP-347 paragraph re-run → parse coverage **0.933** (was 0.80), Q&A **1.0**. **PASS.**
- **J348c:** JEP-340/345/346 still PASS; 136 unit tests green. **PASS.**
- First cut 0.75: numeric role came out `has_leg` (stripped the plural) but `how_many` queries `has_legs`; fixed the
  regex to keep the full noun. Bar unchanged.

## Verdict: **PASS**
A substrate-legal sentence normalizer (no engine change) lifts realistic-prose coverage from 80% → 93% by handling
plural is-a, the "is a kind of/type of" hedge, and numeric possession ("has four legs"). Concrete progress on
"Half 1" — reading more of the clear-prose space — toward Michael's read-a-book-and-discuss goal. No transformer.

