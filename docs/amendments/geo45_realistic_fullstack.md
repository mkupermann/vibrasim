# GEO-45 — Full hardened stack under REALISTIC noise (entity-res + multi-hop + grounding)

## Motivation
GEO-39 validated the stack on CLEAN data. GEO-43/44 showed noise breaks pure retrieval but an entity-
resolution front-end fixes it. GEO-45 is the ultimate test: the FULL hardened system (entity resolution +
multi-hop chaining + grounded resolution) on a NOISY multi-hop task, with vs without the front-end — does the
complete deployable system handle realistic messy data?

## Pre-registration (locked BEFORE run)
- Noisy KB: 10 people -> team (paraphrased + typo'd facts) + team -> city facts. Queries reference people by
  name (clean query).
- Task: "Which city does <P> work in?" (person -> team -> city, 2 hops) on the NOISY store.
- (a) WITHOUT front-end: pure embedding multi-hop. (b) WITH entity-resolution front-end: resolve the person
  name to the stored entity, retrieve that entity's team fact, then chain. 
- Metric: 2-hop accuracy. Bars: (b) >= 0.8 AND (b) > (a) by >= 0.2 (the front-end makes the noisy full stack
  work). Honest characterization either way.
