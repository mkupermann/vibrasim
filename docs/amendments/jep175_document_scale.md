# JEP-175 — full-DOCUMENT scale: read a multi-paragraph article, reason across topics

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 aggregate recall holds ~0.85-0.90 at document scale (read() is sentence-local, no degradation); cross-topic
  questions answered correctly (the knowledge graph integrates across paragraphs). RISK: cross-paragraph coreference
  accumulation, or a topic-boundary issue.

## Result — PASS (HIT): recall 0.90 -> 0.93 after a relative-clause fix, precision perfect, cross-topic works
Read a 29-sentence, 4-paragraph encyclopedic document (mammals, birds, microbes, plants). Aggregate recall 27/30
(0.90) initially; precision PERFECT (0 spurious among 6 wrong probes). CROSS-TOPIC multi-hop reasoning works:
- 'is a poodle an animal?' -> 4-hop chain across a paragraph.
- 'is a heart part of an animal?' -> Yes (part-of/is-a interaction spanning facts).
- 'does a virus cause pain?' -> Yes (3-hop causal chain virus->infection->inflammation->pain across the document).
- 'is an oak a living thing?' -> Yes (cross-paragraph).
Initial misses: lion/tiger (the known 'such as ... are predators' double-binding ambiguity, left unforced) and
penguin->bird (the relative clause 'a bird that cannot fly' — predicate NP failed the bare-NP guard, making 'is a
penguin an animal?' wrongly 'No'). FIXED the penguin case: truncate a predicate's trailing relative clause ('a bird
that cannot fly' -> 'a bird') in the copula handler. After the fix: recall 0.93 (28/30), penguin->bird recovered
('is a penguin an animal?' -> 'Yes. A penguin is a bird, a bird is an animal.'), precision still perfect, no
regression. Only the genuine NL double-binding ambiguity remains. So the learn-from-prose -> reason pipeline operates
at DOCUMENT scale (multi-paragraph, multi-topic) with ~0.93 recall / perfect precision and correct cross-topic
multi-hop reasoning. 57/57 regression tests green (+1). Prediction HIT; tally 67/91. Established (lexico-syntactic
extraction at document scale); named; no novelty.
