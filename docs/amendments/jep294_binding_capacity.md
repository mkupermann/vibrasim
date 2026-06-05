# JEP-294 — How many instance-distinct facts does the binding store hold? (VSA bundle capacity)

## Motivation
JEP show_binding proved the substrate keeps "German politics" ≠ "Hungarian politics" via role-filler **binding**
(world/vsa, Hadamard) and stores both in ONE bundle vector. The open question Michael's example raises: **how
many** such instance-facts fit in one bundle before it blacks out, and does capacity **scale** with vector size?
This is the established VSA/HRR heteroassociative-capacity measurement (Plate/Kanerva) — named as such, not novel.

Store K facts as `mem = bundle_k( bind(entity_k ⊗ role, value_k) )`; query by `cleanup(unbind(mem, entity_k⊗role))`.

## Pre-registered bars (BEFORE the run)
- **J294a (instance-distinct retrieval works):** at K=8 facts, D=4096, per-fact value recovery ≥ 0.90 AND every
  query returns the value bound to THAT entity (no cross-talk), both seeds (0, 7).
- **J294b (capacity scales ~linearly with D):** sweep K to find K* = max facts with recovery ≥ 0.90, at
  D ∈ {2048, 4096, 8192}. Pre-registered prediction: K* roughly **doubles** as D doubles (linear capacity law);
  bar = K*(8192) ≥ 1.5 × K*(2048). NULL if K* does not grow with D.
- **J294c (no hallucination):** an UNtaught entity's best cleanup similarity is separable below taught-entity
  similarity (mean gap > 0, both seeds) — so untaught queries can be rejected, not confabulated.

Predicted most-likely failure: the bundle's crosstalk noise (~√K/√D) could make J294a's 0.90 require D>4096 at
K=8; if so J294a FAILS at D=4096 and I report the honest K*-vs-D curve instead (no post-hoc bar move).

## Result (seeds 0, 7)
- **J294a:** recovery@(K=8, D=4096) = **1.000** both seeds. **PASS.**
- **J294b:** K* (max facts at ≥0.90 recovery) = **64 → 128 → 256** for D = 2048 → 4096 → 8192 — capacity
  **doubles as D doubles** (clean linear law; ceiling raised to 512 to avoid scan-censoring). **PASS.**
- **J294c:** taught-entity sim ≈ 0.275 vs untaught ≈ 0.025, gap ≈ **+0.25** both seeds — untaught queries
  clearly separable. **PASS.**

## Verdict: **PASS**
One bundle vector holds hundreds of instance-distinct facts (≈ D/32), separable by which key you unbind, with
untaught queries rejectable — and the capacity is a clean linear function of vector size. This is the established
VSA/HRR capacity law (Plate/Kanerva), confirmed in the substrate's own primitive. Honest note: caught and removed
a scan-censoring artifact (K* for 4096/8192 first both read 128 = the scan ceiling) before claiming scaling.

