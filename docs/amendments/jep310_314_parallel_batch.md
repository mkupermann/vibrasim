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

## Results (seeds 0, 7) — 4 PASS, 1 NULL/PARTIAL

### JEP-310 Symmetric relations — **PASS**
Symmetric recall = **1.0** both directions (query(a,rel)=b AND query(b,rel)=a), persists. Two directed edges
cleanly give symmetry.

### JEP-311 Second transitive relation (located-in) — **PASS**
located-in multi-hop vs closure = **1.0**; is-a accuracy **1.0** (UNAFFECTED by the added relation); paris→earth
True; persists. Distinct role vectors → zero cross-relation interference.

### JEP-312 High-load ceiling — **PASS** (and then some)
Integrated reasoning stays high far past JEP-307's ~900: N=500→0.99, 1000→0.98, 2000→0.95, **4000 (≈4600 facts,
~46 modules)→0.93–0.95**. J312a (≥0.90 to N=2000) **True**; **N\* > 4000** — no ceiling found in range. Routing
makes the durable store scale to thousands of facts; is-a declines only gently (0.98→0.90).

### JEP-313 Noise robustness — **NULL / PARTIAL** (prediction missed)
Recall vs key bit-flip fraction f: 0→1.0, 0.05→0.95/0.97, **0.10→0.88/0.92**, 0.15→0.84/0.85, 0.20→0.73/0.75,
0.30→0.35, 0.40→0.09. **J313a (≥0.90 at f=0.10) FAIL** (seed 0 = 0.88). Decline is graceful/monotone (J313b
characterized). **f\* ≈ 0.05–0.10**, NOT the 0.2–0.3 I predicted. Honest lesson: tolerance of a SUPERPOSED store is
~half the raw `(1−2f)` bit-correlation, because each fact's signal is already ~1/√K and corruption eats that
margin first. New calibration note for [[calibration_lessons]].

### JEP-314 Analogical retrieval (Kanerva) — **PASS**
Direct attribute retrieval **1.0**; analogy ("X's currency as dollar is to USA → peso") **1.0** over 60 analogies,
both seeds. Classic VSA analogy via record-mapping `bind(rec_src, rec_tgt)` works cleanly with 3 attributes/record.

## Batch verdict: 4/5 PASS; JEP-313 NULL/PARTIAL is a genuine finding (noise tolerance lower than predicted, fix =
larger D or redundant encoding for noisy-cue use). Established methods throughout (VSA binding/analogy, modular
capacity), named as such.

