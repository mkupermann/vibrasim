# JEP-366 — Does construction composition emerge? (the crux for the per-type cost)

## Motivation
JEP-365's optimism ("pay per atomic construction TYPE, ~hundreds") only holds if learned constructions COMPOSE — if a
sentence combining two known structures can be parsed from the known pieces without teaching the combination. If
instead every COMBINATION must be taught as its own template, the cost is combinatorial (exponential in depth), and a
bounded domain is far less reachable than 365 suggests. This experiment resolves that crux directly. No transformer.

The test case is recursive embedding: a relative clause inside a main clause.
- main (active) construction: "The X VERBed the Y" -> (X, VERB, Y)  [known]
- relative-clause construction: "The X that VERBed the Y ..." -> the embedded (X, VERB, Y)  [known]
- COMBINED, never taught together: "The dog that chased the cat ate the mouse"
  = main (dog, ate, mouse) + relative (dog, chased, cat).

## Method (real substrate machinery only: the SAME induced templates + a generic reduce-and-parse)
1. **J366a — flat templates fail (baseline):** apply each learned FLAT template directly to the combined sentence.
   A flat anti-unification template has fixed positions, so it cannot match the longer embedded structure. Predict the
   main fact (dog, ate, mouse) is NOT recovered by any flat template alone.
2. **J366b — recursive application of KNOWN templates:** a generic, knowledge-free reducer: detect an embedded relative
   clause by the marker "that", extract its fact with the relative template, REMOVE the relative clause from the
   sentence, then apply the main active template to the reduced sentence. Does composing the SAME learned templates via
   reduction recover BOTH facts (main + relative) with no new taught knowledge? This tests whether composition is
   reachable by a generic compositional parser over learned constructions.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction (genuinely uncertain — stated before running): **J366a True (flat fails), J366b PASS** — composition IS
reachable by recursive application of learned templates, because the embedding is marked ("that") and reduction is a
generic structural operation requiring no new world knowledge. If so, the per-type cost (365) holds: you pay per
ATOMIC construction, and combinations come free from a compositional parser. If J366b FAILS, every combination needs
teaching and 365 is optimistic — that is the important negative finding.

- **J366a (flat fails):** no single learned flat template yields the correct main fact (dog, ate, mouse) from the
  combined sentence, both seeds (0, 7).
- **J366b (composition via reduction):** the reduce-and-parse recovers BOTH (dog, ate, mouse) AND (dog, chased, cat)
  from the never-taught combined sentence, using only the two separately-learned templates; and generalizes to a
  second combined sentence with different fillers, both seeds.

Honest framing: J366b tests composition of the SAME learned constructions via a generic parser — it does NOT teach the
combination. A PASS means atomic constructions compose (the strong, optimistic result); a NULL means the cost is
combinatorial. Either is the finding; I predict PASS but flag real uncertainty about the reducer's brittleness. No
transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — both bars)
- **J366a (flat fails): PASS** — applying each learned flat template directly to "The dog that chased the cat ate the
  mouse" yielded **None** for both (positions don't line up with the longer embedded structure). A flat anti-
  unification template cannot match a recursively embedded sentence. Both seeds.
- **J366b (composition via reduction): PASS** — the generic reduce-and-parse recovered BOTH facts from the never-
  taught combination: main **(dog, ate, mouse)** + relative **(dog, chased, cat)**, using only the two separately-
  learned templates; and generalized to "The man that saw the bird ate the worm" → **(man, ate, worm)** + **(man,
  saw, bird)**. Both seeds.

### Honest caveat (what is engineered vs learned)
The two *constructions* are learned from examples; the facts are recovered with no new taught knowledge about these
sentences. BUT the recursive **reducer itself is engineered** — I wrote the "find `that`, extract with the relative
template, splice it out, parse the remainder" strategy. So composition is reachable *with a generic recursive parser*,
but that parser does not emerge on its own (consistent with JEP-363: the abstracting/parsing *mechanism* is general
and must be engineered or taught, not invented by the system). This is engineered structure operating over learned
content — exactly the allowed division in CLAUDE.md (ports/parsers engineered; internals/constructions learned). It
is NOT a claim that the system discovered how to compose by itself.

## Verdict: **PASS — composition holds the per-type cost, via an engineered generic parser**
Learned constructions COMPOSE: a sentence combining two known structures, never taught together, is parsed from the
pieces by a generic recursive reducer over the SAME learned templates — recovering all facts and generalizing to new
fillers. This resolves the crux from JEP-365 in the *optimistic* direction: the teaching cost scales with **atomic**
construction types, not their combinations, because a recursive parser handles the combinations for free. The honest
boundary (JEP-363) stands: that recursive parser is engineered, not emergent. Net: under the no-LLM rule, a bounded
factual domain is reachable at per-atomic-type cost, with composition supplied by an engineered compositional parser
over learned constructions. No transformer.
