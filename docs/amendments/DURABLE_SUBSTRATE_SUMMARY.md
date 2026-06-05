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

**Meta-learning — learns the rules, not just the facts**
- 316 induce relation algebra (symmetry/transitivity) from the fact pattern.
- 317 induce transitivity from K labeled examples on a cover-only store.
- 318 discover inverse relation pairs; 319 induce two-relation composition (grandparent = parent∘parent).

**Lock-in**
- 320 grand integration capstone (all 11 operations in one reloaded store).
- `tests/test_substrate_memory.py` (9 tests) under the permanent gate; 132 tests green.
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
