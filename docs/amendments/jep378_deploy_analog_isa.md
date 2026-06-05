# JEP-378 — Deploy analog is-a for closed relations: close the deep floor end-to-end

## Motivation
JEP-377 proved (controlled) that a magnitude-preserving (analog) readout separates true/false single-hop is-a where
sign cannot (min(deep,neg)=1.0 vs 0.95/0.975). This deploys it: `SubstrateMemory.edge_sim_analog` + an analog gate in
`BrainQuery`, used by `is_a` ONLY when the is-a closure is materialized (`closed_relations`). Everything else stays on
the sign readout. Verify the deep-recall floor closes in the live `Conversation.say()` path with negatives still
perfect, exceptions respected, persistence, multi-hop on un-consolidated stores intact, and the suite green. No
transformer.

## Method
Re-run the JEP-375 end-to-end harness (read ~300-node taxonomy via `read_text` → auto-consolidate; ask deep + negative
is-a via `Conversation.say()`; teach an exception; save/load; non-consolidated multi-hop regression; suite). The only
change is the library now answering closed-is-a via the analog readout.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: deep AND negative is-a via `say()` are BOTH ≥0.95 on both seeds (the analog readout closes the faint-edge
gap that left deep at 0.93 in JEP-375), exceptions respected, persistence holds, multi-hop intact, suite green.

- **J378a (deep closed):** deep is-a via `say()` ≥0.95, BOTH seeds (0, 7) — strictly better than JEP-375's 0.933.
- **J378b (negatives stay fixed):** negative is-a via `say()` ≥0.95, BOTH seeds.
- **J378c (persist + exceptions + multi-hop + suite):** reload deep AND neg ≥0.95; exceptions respected; non-
  consolidated multi-hop is-a intact (poodle→organism True, poodle→rock False); `pytest -m "not slow"
  tests/test_conversation.py tests/test_substrate_memory.py` passes.

If deep clears but negatives regress (analog raises false-positives too), report the honest trade-off. Predicted: both
clear. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — the floor is closed end-to-end)
- **J378a (deep closed): PASS** — deep is-a via `Conversation.say()` = **1.0 / 1.0** (was 0.933/0.967 with the sign
  readout in JEP-375). The analog readout lifts the faint deep edges clear of the gate. Both seeds.
- **J378b (negatives stay fixed): PASS** — negative is-a via `say()` = **1.0 / 1.0**. The analog readout did NOT
  reintroduce false-positives. Both seeds.
- **J378c (persist + exceptions + multi-hop + suite): PASS** — reload deep **1.0** + neg **1.0** (analog gate
  recalibrates on load); exceptions respected; non-consolidated multi-hop is-a intact (poodle→organism True,
  poodle→rock False, on the sign path); suite **23 passed**. Both seeds.

## Verdict: **PASS — within-domain deep reasoning is now reliable end-to-end (deep 1.0, negatives 1.0)**
The deep-recall floor is closed in the deployed brain. `is_a` over a materialized closure now uses the analog
(magnitude-preserving) readout with its own calibrated gate, answering deep is-a at **1.0** while keeping negatives at
**1.0** — through the normal `Conversation.say()` path, persisting across save/load, with exceptions respected and the
un-consolidated multi-hop path untouched. The change is surgical: only closed-relation is-a uses the analog readout;
every other operation stays on the sign readout, so the 23-test suite is green.

### The complete within-domain arc (JEP-367 → 378)
367 error-free in a small taught domain (abstains outside) → 368 breaks at scale (adversarial 0.4) → 369 dimension is
NOT the lever (per-hop compounding) → 370 closure materialization restores deep → 371 shipped to the store → 372 wired
into the live Conversation (deep 1.0, negatives 0.8) → 373 D-scaling partially helps negatives → 374 brute-force D NULL
(structural) → 375 skip-the-BFS fixes negatives, exposes a faint-edge deep gap → 376 reinforcement NULL (sign readout
discards weight) → 377 analog readout separates the overlap (1.0) → **378 deploy analog is-a → deep 1.0 AND negatives
1.0 end-to-end.** Net: consolidation + consolidation-aware analog is-a make within-domain deep reasoning error-free at
scale (hundreds of facts, depth 8) in the live talk loop. The open-domain knowledge-tail wall (JEP-362) is separate and
still stands. No transformer.
