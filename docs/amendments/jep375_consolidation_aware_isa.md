# JEP-375 — Consolidation-aware is-a: skip the BFS walk when the closure is materialized

## Motivation
JEP-374 showed the post-consolidation negative-probe false-positives are STRUCTURAL, not cleanup noise. The JEP-375
diagnostic pinned the exact cause: `BrainQuery.is_a` answers via a recursive BFS over is-a edges (`_ancestors`), and on
a consolidated store that walk **expands spurious borderline edges**, producing ~15% false-positives (neg 0.85). But a
**direct single-hop membership** test (`z ∈ query_all(x,"isa")`) gives deep 1.0 AND negatives **1.0/1.0** — because
after closure materialization every true ancestor is a DIRECT edge, so the BFS is unnecessary and only adds error.
Measured true-edge sim (mean ~0.06, min ~0.022) vs false-pair sim (p95 ~0.02–0.024) are separable; the BFS chaining is
what crosses the gate. Fix: when a relation's closure is materialized, answer is-a by direct membership, skipping the
walk. No transformer.

## Method
- Mark consolidated relations on the store: `consolidate_closure` records them in `SubstrateMemory.closed_relations`
  (persisted through save/load).
- `BrainQuery.is_a`: if "isa" ∈ `closed_relations`, return direct membership (`y ∈ query_all(x,"isa",gate)`) and skip
  the BFS; otherwise keep the existing multi-hop walk (needed for un-consolidated stores).
- Re-run the JEP-372/373 end-to-end harness (deep + negative is-a via `Conversation.say()`), and confirm a
  NON-consolidated store still answers deep multi-hop is-a via the walk (no regression).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: consolidation-aware is-a gives deep ≥0.95 AND negatives ≥0.95 on both seeds (the diagnostic showed
direct-membership = 1.0 deep / 1.0 neg), exceptions respected, persistence holds, multi-hop on un-consolidated stores
still works, suite green.

- **J375a (negatives fixed):** negative is-a via `say()` ≥0.95, BOTH seeds (0, 7).
- **J375b (deep still reliable):** deep is-a via `say()` ≥0.95, BOTH seeds.
- **J375c (no regression):** (i) a NON-consolidated store still answers a deep multi-hop is-a chain correctly (the BFS
  path is intact); (ii) exceptions respected + save/load preserves both deep and negative accuracy; (iii)
  `pytest -m "not slow" tests/test_conversation.py tests/test_substrate_memory.py` passes.

If negatives still miss, the direct-membership gate itself overlaps true/false (a deeper VSA limit) — report it. The
diagnostic predicts a clean PASS. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PARTIAL** (negatives FIXED + persistence bug fixed; deep recall now the borderline gap)
- **J375a (negatives fixed): PASS** — skipping the BFS on a consolidated store makes negative is-a probes via `say()`
  **1.0 / 1.0** (was 0.85 with the walk). The structural diagnosis was correct: the recursive walk was the false-
  positive source. Both seeds.
- **J375b (deep still reliable): NOT met (borderline)** — deep is-a via `say()` = **0.933 (seed 0) / 0.967 (seed 7)**,
  just under 0.95 on seed 0. Direct single-hop membership occasionally MISSES the faintest true ancestor edge whose
  cleanup similarity dips below the gate (true-edge sim min ~0.022 vs gate ~0.027 — a small distribution overlap). The
  BFS used to recover those by chaining, at the cost of the false-positives we just removed.
- **J375c (no regression): PARTIAL** — non-consolidated multi-hop is-a is **intact** (BFS path preserved: poodle→
  organism True, poodle→rock False); exceptions respected; `closed_relations` now **persists across save/load** (the
  `compact()` bug that dropped it is fixed); suite **23 passed**. The only miss is reload deep (0.9/0.967), the same
  faint-edge issue as J375b.

## Verdict: **PARTIAL — the structural fix is right (negatives solved); a small faint-edge recall gap remains**
Consolidation-aware is-a (direct membership when the closure is materialized, BFS otherwise) is the correct structural
fix: it eliminates the negative false-positives that brute-force dimension could not (JEP-374), preserves multi-hop on
un-consolidated stores, respects exceptions, and persists. It also exposed the complementary limit: a small overlap
between the faintest TRUE single-hop edge and the gate means ~3–7% of the deepest is-a queries miss (deep 0.93–0.97).
This is a genuine VSA cleanup-overlap effect, not a logic error. The fix is to **reinforce closure edges** during
consolidation (store each materialized edge with extra weight so faint deep edges rise above the gate, while negatives
keep their headroom) — pre-registered as JEP-376. Two bugs fixed (compact-drops-flag; BFS false-positives); one small
recall gap remains. Bars not moved. No transformer.
