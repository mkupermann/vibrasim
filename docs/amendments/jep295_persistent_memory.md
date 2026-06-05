# JEP-295 — Persistent, growing substrate memory (don't die when the program closes)

## Motivation (Michael)
"I will lose the memory once the program is closed? That can't be. The substrate will be dead. We need to find a
way to store the substrate and let it grow like a brain." Correct — until now the memory (VSA bundle + cleanup
dict + taught percept exemplars) lived only in RAM. This makes it **durable on disk** and **growable across
sessions** (lifelong learning): teach today, close, reopen tomorrow, the knowledge is still there AND you can add
more without erasing the old. No transformer, no pretrained model — just saving/loading the substrate's own arrays.

## Design
`world/substrate_memory.py :: SubstrateMemory` — wraps the relational VSA store (facts as bound bundle + cleanup
memory + entity/role registry) and the perceptual `ActiveLearner` (taught exemplars). `save(dir)` writes a real
**folder of files** (`vectors.npz`, `meta.json`, `exemplars.npz`); `load(dir)` reconstructs the exact state.
Growth = `add_fact` / `teach_percept` then `save` again; capacity beyond K*≈D/32 (JEP-294) is added by widening D
or adding modules (linear capacity), noted not hidden.

## Pre-registered bars (BEFORE the run)
- **J295a (persistence):** teach K=12 facts + 8 letters, `save`, `load` into a FRESH object (no shared RAM);
  fact recovery ≥ 0.95 and letter recognition ≥ 0.90 — identical to pre-save, both seeds (0, 7).
- **J295b (grow without forgetting):** 3 save/load cycles, each adds new facts+letters; after the final load ALL
  accumulated facts recover ≥ 0.90 and ALL accumulated letters ≥ 0.90 (old knowledge not lost when new added).
- **J295c (real cross-process persistence):** a SEPARATE python subprocess that reads only the saved folder
  recovers facts ≥ 0.95 — proving it's the FILE, not lingering RAM.

Predicted most-likely failure: float dtype/round-trip mismatch on npz reload silently degrades vectors → recovery
drops; mitigated by saving float64 and asserting array-equality on reload. If J295b drops below 0.90 it means the
growth exceeded bundle capacity K* — report the honest cliff, don't move the bar.

## Result (seeds 0, 7)
- **J295a (persistence):** teach 12 facts + 8 letters → save → load into a FRESH object → facts **1.00**,
  letters **1.00**, identical to pre-save. **PASS.**
- **J295b (grow without forgetting):** 3 save/load cycles adding facts+letters (→ 17 facts, 13 letters); after
  the final load ALL recall facts **1.00**, letters **1.00**. **PASS.**
- **J295c (real cross-process):** a separate python subprocess reading only the folder recovers facts **1.00**
  — it is genuinely the file, not lingering RAM. **PASS.**

## Verdict: **PASS**
The substrate's memory is now a **durable folder of files** (`vectors.npz` + `meta.json`) that survives
close+reopen, grows across sessions without forgetting the old, and is reconstructable by any process. Directly
answers Michael: the substrate no longer dies when the program closes. Key correctness detail: atom vectors are
hashlib-seeded (cross-process stable) — Python's builtin `hash()` is per-process salted and would have silently
broken J295c. Honest scope: growth is bounded by VSA bundle capacity K*≈D/32 (JEP-294); past that, widen D or add
a module (linear capacity) — the file format already stores D, so a wider brain is a re-encode, not a redesign.

