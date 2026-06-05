# JEP-338 — Validated-on-real-content at scale (~150 facts, multi-module, engine-read)

## Motivation
JEP-337 validated the whole system on a 43-fact corpus (1 module). Push the envelope: a larger engine-READ corpus
(~150 facts spanning several taxonomy forests + properties + causal) that forces MULTI-MODULE routing, and confirm
the full reasoning suite still matches the engine at that scale. Bridges the gap between routing's synthetic scale
test (JEP-307/312) and real engine-parsed content. No transformer.

## Method
Programmatically generate engine-readable sentences ("A {child} is a {parent}.", "A {x} can {verb}.",
"{cause} causes {effect}.") forming several taxonomy trees (depth 3-4, branching) + properties + causal edges,
~150 sentences. `eng.read` all → `mem.ingest_engine` → save → reload → reason vs the engine.

## Pre-registered bars (BEFORE the run)
- **J338a (scale + multi-module):** ≥ 120 facts bridged across ≥ 3 modules; is-a multi-hop matches the engine
  ≥ 0.90 on a balanced battery, both seeds (0, 7).
- **J338b (inheritance + abduction at scale):** property inheritance and abduction match the engine ≥ 0.90, both
  seeds.
- **J338c (persists):** reloaded answers identical to pre-save.

Predicted most-likely failure: the engine may not parse some generated names as concepts (tokenization), shrinking
the bridged fact count below 120 — report the parse rate; or deep multi-hop across modules could dip (routing
should hold per JEP-307). If J338a misses, report whether it's parse-coverage or cross-module recall.

## Result (seeds 0, 7): **PASS** (after scaling the input)
- **First cut:** 103 facts / 3 modules — reasoning all 1.0, but fact count < the pre-registered 120 (my name pool
  capped at ~70 concepts). Scaled the generator's name pool (2-syllable product) to reach the bar — NOT a bar move.
- **J338a:** **190 facts / 5 modules**, is-a multi-hop vs engine = **1.0**, both seeds. **PASS.**
- **J338b:** inheritance = **1.0**, abduction correct, both seeds. **PASS.**
- **J338c:** reloaded answers identical. **PASS.**

## Verdict: **PASS**
The full reasoning suite holds on a 190-fact engine-READ corpus spanning 5 modules — is-a multi-hop, property
inheritance, and abduction all match the engine at 1.0, durably. Confirms routing + reasoning scale on real
engine-parsed content, not just synthetic facts (JEP-307/312) or a single module (JEP-337). Honest: the first cut
under-shot the fact-count bar because the name pool was too small; scaled the input to meet it, bar unchanged. No
transformer.
