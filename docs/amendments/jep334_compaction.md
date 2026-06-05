# JEP-334 — Store compaction: reclaim capacity from corrected/overridden facts

## Motivation
JEP-333: correction is override-by-negation; the dead positive fact still occupies bundle capacity. For a long-lived
incrementally-corrected brain, that capacity should be reclaimable. Compaction = rebuild the store from only the
LIVE facts (drop a positive that a direct negation overrides, AND its now-moot negation; KEEP standalone negations,
which are exceptions). Preserves every current answer while freeing capacity. Established log-compaction / GC,
named as such. No transformer.

## Method
`SubstrateMemory.compact()` → a fresh store containing live facts only: for each `(X, not_isa, Y)` with a matching
direct `(X, isa, Y)`, drop BOTH (a resolved correction); for `not_hasprop` vs direct `hasprop`, same; standalone
negations (exceptions over INHERITED facts) are kept. Carries over sentences + learner.

## Pre-registered bars (BEFORE the run)
- **J334a (answers preserved):** every is-a / has_property answer is IDENTICAL before and after compaction
  (incl. corrected ones staying corrected, and exceptions staying exceptions) ≥ 0.98, both seeds (0, 7).
- **J334b (capacity reclaimed):** at scale (many corrections), the compacted store has FEWER facts and ≤ the
  modules of the original, with strictly fewer when corrections exceed a module's worth, both seeds.
- **J334c (persists):** the compacted store saves/loads and answers identically.

Predicted most-likely failure: dropping a positive+negation pair could accidentally remove an exception (a
not_hasprop whose positive is INHERITED, not direct) — the compaction must only pair a negation with a DIRECT
positive. If J334a misses on an exception, that's the bug (over-aggressive pairing), reported not tuned.

## Result (seeds 0, 7): **PARTIAL** — literal bar not met because compaction IMPROVED correctness
- **J334b (capacity reclaimed): PASS** — facts **67 → 27**, modules **2 → 1**, both seeds.
- **J334c (persists): PASS.** Exception (penguin can't fly) survived compaction, both seeds.
- **J334a (answers IDENTICAL pre/post): NOT met (0.944).** The single difference: `is_a(e1, wrong1)` was **True
  pre-compaction (WRONG)** → **False post (correct)**. Diagnosis: at 67-fact/2-module load the `not_isa` correction
  was detected marginally (gate), so the override sometimes missed and the still-present wrong `isa` fact leaked
  through. Compaction PHYSICALLY removed the wrong fact, so the answer is correct regardless of gate. Verified vs
  ground truth: **pre correctness = 0.944, post = 1.000** — compaction *improved* the brain.

## Verdict: **PARTIAL** (honest — the finding is better than the bar)
Compaction reclaims capacity (67→27 facts, 2→1 modules) AND preserves exceptions AND *hardens* corrections:
physically removing a corrected fact is more robust than gate-detected negation override, so post-compaction
correctness rose 0.944→1.000. The literal pre-registered bar (answers IDENTICAL) was NOT met — but only because it
couldn't distinguish "changed for worse" from "changed for better"; the right metric (correctness vs ground truth)
shows a strict improvement. Recorded as-is, bar not moved (cf. JEP-328 lesson: measure the outcome that matters —
correctness — not a coincident-identity proxy). Established log-compaction/GC, named as such. No transformer.

