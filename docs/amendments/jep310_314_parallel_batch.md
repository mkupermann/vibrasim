# JEP-310..314 — Parallel batch (5 independent experiments, run concurrently)

Five independent extensions of the durable substrate, pre-registered BEFORE running, executed in parallel. All
substrate-native (world/vsa, world/substrate_memory); no transformer/pretrained. Each writes
~/.eqmod/bet/JEP31x/result.json and its own PASS/NULL/PARTIAL.

## JEP-310 — Symmetric relations (married-to, sibling-of)
Store symmetric facts both directions; query either way. **Bars:** J310a symmetric recall both directions ≥0.95
(query(a,rel)=b AND query(b,rel)=a) both seeds; J310b persists.
Predicted failure: none expected (two directed edges); if a direction misses, routing/storage bug.

## JEP-311 — A second transitive relation (located-in) + non-interference
located-in transitivity (city→country→continent→earth), multi-hop climb like is-a, alongside is-a facts.
**Bars:** J311a located-in multi-hop vs transitive-closure ground truth ≥0.90 both seeds; J311b is-a queries
UNAFFECTED by the added relation (≥0.95); J311c persists.
Predicted failure: cross-relation crosstalk if role vectors not distinct (they are) → expect clean.

## JEP-312 — High-load ceiling (push past JEP-307's ~900 facts)
Sweep N ∈ {500,1000,2000,4000} with routing; integrated reasoning (is-a multi-hop + property). **Bars:** J312a
integrated ≥0.90 to N=2000 both seeds; J312b characterize the curve + find the true ceiling N* (NULL beyond is a
finding, not tuned); neurogenesis engaged.
Predicted failure: per-module load is ~constant (cap), so routing should hold; ceiling likely set by the
value-vocabulary cleanup growing (cleanup is O(V)) — report if accuracy or only speed degrades.

## JEP-313 — Noise robustness (corrupted query cue)
Query with the key vector bit-flipped at fraction f; measure recall vs f. **Bars:** J313a recall ≥0.90 at f=0.10
(10% flips) both seeds; J313b characterize the degradation curve + find f* where recall first <0.90.
Predicted failure: bipolar Hadamard is linear, so recall ≈ (1-2f) signal; expect graceful decline, f* ~0.2-0.3.

## JEP-314 — Analogical retrieval (Kanerva "dollar of Mexico")
Country records = bundle of role-bound attributes (capital, currency, language). Analogy: attribute of target
analogous to a source's = bind(source_attr, bind(source_rec, target_rec)) → cleanup. **Bars:** J314a analogy
accuracy ≥0.90 over several (attr, source, target) triples both seeds; J314b direct attribute retrieval also works.
Predicted failure: bundle crosstalk with few attributes is low; if analogy misses, the role-binding/record
construction is the cause (a representation finding), reported not tuned.

## Results
(filled after the parallel run)
