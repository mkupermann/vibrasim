# Pattern — Geometric reasoner: generator-free neuro-symbolic reasoning over an LLM

**Reusable mechanism** distilled from EQMOD-3 (GEO-1..23). Reference implementation:
`tools/geometric_reasoner.py` (self-test PASS). CPU, sentence-transformers + numpy.

## What it is
A grounded reasoning layer ON an LLM embedding space (NOT a generator, NOT a replacement for an LLM):
- **Grounded retrieval + abstention** — embed facts once; answer by nearest-neighbour; if max cosine <
  tau, say "I don't know" instead of confabulating (GEO-15, GEO-23). This is the value-add over generation.
- **Multi-hop chaining** — iterative retrieval: each hop's resolved object becomes the next hop's bridge
  entity (GEO-16/17; robust to distractors + paraphrase to a few hundred facts / 2-3 hops, GEO-22).
- **Symbolic aggregation** — count/filter/compare over the structured `meta` payloads, because pure
  geometry cannot count/negate/compare (GEO-18, GEO-20).

## When to use
You have a bounded fact store and want grounded, updatable, hallucination-free Q&A + multi-hop lookups on a
PC without running a generative model. Add new facts at runtime (no retraining). Drop to the symbolic layer
for "how many / not / larger".

## When NOT to use
Open-domain NLU, text generation, or questions needing world knowledge outside the store — those need an
actual LLM generator. Numbers saturate on clean entities; expect sub-0.9 multi-hop beyond a few hundred
facts or 3+ hops (GEO-22). Calibrate `abstain_tau` on your own answerable/unanswerable split (GEO-23).

## API
```python
r = GeometricReasoner(abstain_tau=0.45)
r.add_fact("Alice works at Acme.", subject="Alice", relation="works_at", object="Acme")
r.ask("Where does Alice work?")                       # -> grounded answer or "I don't know"
r.chain(["What company does Alice work at?", "What city is {bridge} in?"])   # multi-hop
r.count_where(lambda m: m.get("object") == "Boston")  # symbolic aggregate
```
