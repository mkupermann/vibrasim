# Durable Substrate Reasoning — Programme Summary (JEP-294..320)

One-page overview of the arc that turned the substrate's memory from RAM-only into a durable, growing, reasoning,
self-organizing knowledge store — entirely on substrate-native VSA primitives (`world/vsa`,
`world/substrate_memory`). **No LLM, no transformer, no pretrained model.** All methods are established (HRR/VSA
binding, modular capacity, permutation binding, hash-routed associative memory, Kanerva analogy, ILP-style rule
induction), named as such; the contribution is the substrate-native assembly + the measured envelope + the honest
record.

## The question it answers
Michael: "How is the memory stored — is it a file? It can't die when the program closes. Store it and let it grow
like a brain. Keep German politics and Hungarian politics distinct. Learn like a human."

## What was built (each an amendment, pre-registered, PASS unless noted)
**Storage & durability**
- 294 instance binding (Germany≠Hungary) + capacity law K*≈D/32, linear in D.
- 295 durable persistence — a folder of files, survives close+reopen, cross-process (hashlib-seeded atoms).
- 296 unbounded growth — auto module-add (neurogenesis).
- 307 module-aware routing — multi-hop scales (fixes 306 NULL).
- 312 high-load — holds 0.93–0.95 to ~4,600 facts / 46 modules.
- 313 NULL → 315 noise fix — dimension is the noisy-cue lever (D=8192 tolerates ~20% corruption).

**Reasoning (all over the persistent store, matching the engine)**
- 297 NULL → 298 directed binding (permutation) → transitive multi-hop.
- 299/300 bridge the Understanding Engine's full taxonomy (is-a, part-of, causal, property) — reason after reload.
- 301 cross-relation inheritance (is-a climb ∘ relation), 303 DAG (set-valued), 305 negation + defeasible
  exceptions, 308 abduction (reverse 'why?'), 309 contradiction detection, 310 symmetric, 311 located-in,
  314 analogy.

**Meta-learning — learns the rules, and folds them back in**
- 316 induce relation algebra (symmetry/transitivity); 317 induce transitivity on a cover-only store from K labeled
  examples; 318 discover inverse pairs; 319 induce 2-relation composition (grandparent=parent∘parent); 321 induce a
  RECURSIVE rule (ancestor = transitive closure of parent).
- 323 CLOSE THE LOOP: materialize an induced rule into the store (forward-chaining) so the derived relation is
  directly queryable, persists, and COMPOUNDS (great-grandparent via materialized grandparent).

**Usable + locked-in**
- 320 grand integration capstone (all 11 operations in one reloaded store).
- 322 `world/brain_query.BrainQuery` + `tools/ask_brain.py` CLI — ask the durable brain questions
  ("is a poodle an animal?", "what causes cancer?"). One auto-gate (325 added per-relation gating → 326 proved it
  unnecessary, gap ≤0.03 → reverted; honest add→test→remove loop).
- 324 the teaching GUI gains an "Ask:" box — teach by sentence then ask in the same window; `ingest_engine`
  completed to bridge negatives + the causal inverse so exceptions and abduction work end-user.
- 327 perceive a written WORD from pixels → recognize letters → reason about it from the durable store (see→read→
  understand, 1.0); 328 PARTIAL characterizes the edit-distance cure's noise regime.
- `tests/test_substrate_memory.py` (10 tests inc. BrainQuery) under the permanent gate; 133 tests green.
- Teaching GUI persists both percepts (295) and taught facts (302) across sessions.

## Honesty record
3 NULLs (297 direction-ambiguity, 306 multi-hop scale collapse, 313 noise) — each diagnosed and fixed
(298/307/315). 3 first-cut misses (293 features, 301/317 my ground-truth/composition logic) — root-caused to the
experiment, not the substrate. All in `docs/PREDICTION_LOG.md`; two new calibration classes (#13 superposed-noise,
#14 multi-hop routing) in `docs/patterns/calibration_lessons.md`. No bar ever moved post hoc.

## Honest limits (named, not hidden)
Per-module capacity ≈ D/32 (widen D / add modules); noisy-cue tolerance set by D; cover-only transitivity needs a
few labeled examples; rule induction covers symmetry/transitivity/inverse/2-composition (not yet arbitrary n-ary
or recursive rules); richer real senses (mic/camera) remain a wall. Pattern:
`docs/patterns/durable_vsa_relational_memory.md`.
