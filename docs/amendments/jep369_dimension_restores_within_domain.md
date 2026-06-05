# JEP-369 — Is dimension the lever to restore within-domain "no mistakes" at scale?

## Motivation
JEP-368 found within-domain accuracy collapses at scale (deep is-a 0.925, adversarial composition 0.375–0.5 at ~378
facts), via cleanup-similarity dilution across auto-grown modules. JEP-315 established that DIMENSION D is the lever
for cleanup noise; and a larger D also raises per-module capacity (module_cap ∝ K* ≈ D/32), so the SAME ~360 facts
occupy FEWER modules — less cross-module argmax interference and lower per-hop error that compounds favorably over deep
chains and conjunctions. Test whether raising D restores error-free within-domain Q&A at the scale where 368 failed.
No transformer.

## Method
Re-run the JEP-368 stress at the largest size (~360 facts) for D ∈ {4096, 8192, 16384}, focusing on the difficulties
that failed: D1 (deep is-a chains), D3 (distractors), D4 (adversarial composition). Report accuracy vs D, both seeds.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: accuracy rises monotonically with D and is RESTORED at D=16384 — because ~360 facts then fit in ≈1–2
modules (cap ≈ 512 at D=16384), collapsing the cross-module interference, and per-hop cleanup error shrinks so deep
chains and conjunctions stop compounding. If higher D does NOT restore it, the ceiling is structural (not noise) — an
important harder finding.

- **J369a (deep is-a restored):** D1 accuracy at ~360 facts is ≥0.95 at D=16384, and higher than at D=4096, both seeds.
- **J369b (adversarial composition restored):** D4 accuracy at ~360 facts is ≥0.85 at D=16384, and markedly higher
  than the ~0.4 at D=4096, both seeds.
- **J369c (monotonic lever):** for D1 and D4, accuracy is non-decreasing across D=4096→8192→16384 (the lever works in
  the predicted direction), both seeds.

If restored: the reachable "no mistakes" taught domain is much larger than 368 implied — bounded by D (a tunable
engineering knob), not a hard wall. If not: the within-domain ceiling is structural. Either is the finding; bars fixed.
No transformer.

## Result (seeds 0, 7): **NULL — dimension is NOT the lever; the failure is structural (per-hop compounding)**

| D | modules (~378 facts) | D1 deep is-a | D3 distractor | D4 adversarial |
|--:|:--:|:--:|:--:|:--:|
| 4096  | 4 | 0.95–0.975 | 0.9–1.0 | 0.375–0.5 |
| 8192  | 2 | 0.925–0.95 | 1.0 | 0.625–0.875 |
| 16384 | 1 | **0.85–0.925** | 0.975–1.0 | 0.625 |

- **J369a (deep is-a restored): FALSE** — at D=16384, D1 is 0.85–0.925, NOT ≥0.95; for seed 7 it even *dropped* to
  0.85. A single module (no cross-module interference at all) still fails deep chains.
- **J369b (adversarial restored): FALSE** — D4 reached only 0.625 at D=16384, well below 0.85.
- **J369c (monotonic in D): FALSE** — not monotonic; D1 got worse at the largest D for one seed.
- **What DID improve:** D3 distractors (single-hop probes) rose to ~1.0 — consistent with the diagnosis below.

### Diagnosis (the important part)
Raising D collapses the module count (4→1) and fixes the **single-hop** difficulty (D3 → 1.0), confirming cleanup
noise IS reduced. But **deep is-a (D1) and adversarial composition (D4) do NOT recover** — because they are not
single lookups. `is_a` over a depth-8 chain walks the taxonomy **hop by hop** (`_ancestors` iterates), and even a
per-hop accuracy of ~0.98 compounds to 0.98^8 ≈ 0.85 — exactly the seed-7 D=16384 number. Higher D shrinks per-hop
error only as ~√(load/D) (diminishing), so it cannot beat the multiplicative compounding. The bottleneck is the
**sequential hop count**, not cleanup noise or module routing.

## Verdict: **NULL — correctly falsifies the dimension hypothesis, and points to the real lever**
Dimension is not the fix for within-domain deep reasoning. The ceiling is structural: iterative multi-hop chains
compound per-hop error. The proper, substrate-legal lever is therefore to **remove the hops** — materialize the
transitive closure (store every ancestor edge directly, via consolidation, like dream consolidation G15/G18), turning
deep is-a into a SINGLE-hop lookup that does not compound. That is the next experiment (JEP-370), and this NULL is what
motivates it. Honest negative result; bars pre-registered and not moved. No transformer.
