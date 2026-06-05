# JEP-368 — Where do mistakes begin INSIDE a taught domain? (the real "no mistakes" test)

## Motivation
JEP-367 showed 1.0 on a small hand-picked taught domain. But Michael's requirement is "no mistakes" — so the honest
question is where mistakes begin *even inside a taught domain*, as it scales and as questions get harder. If error-free
Q&A only holds for ~30 facts and shallow chains, the reachable gate is far smaller than claimed. This stress-tests the
within-domain error onset: scale (hundreds of facts), depth (long is-a chains), distractors (siblings/near-misses),
and adversarial composition. Honest aim: find the failure point, not confirm a comfortable one. No transformer.

## Method (the real deployed brain at scale)
Generate a large synthetic taxonomy + property/exception/causal knowledge base (hundreds of facts across multiple
auto-grown modules), then test held-out derived questions of increasing difficulty:
- **D1 deep is-a chains** (depth up to ~8): is X a Z across the full chain.
- **D2 inheritance + exceptions at depth**: a property defined high in the chain, with an exception inserted at a
  deep node — most-specific-wins must hold under distractors.
- **D3 negative/distractor probes**: is X a Y where Y is a SIBLING/cousin (must answer False), and X is-a non-ancestor.
- **D4 adversarial composition**: multi-hop is-a AND inherited property AND an exception in the SAME query set.
Report accuracy per difficulty and the fact-count at which any error first appears.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: within-domain accuracy stays high (≥0.95) up to several hundred facts and depth ~6–8 BECAUSE module-aware
routing (JEP-307) and most-specific-wins (JEP-305) were already shown to scale — but I flag genuine risk that deep
chains + distractors at scale erode accuracy (cleanup-similarity dilution across modules). The finding is the curve and
the onset point, whichever way it falls.

- **D1 deep chains:** accuracy ≥ 0.95 at 300+ facts, both seeds (0, 7).
- **D2 inheritance+exception at depth:** accuracy ≥ 0.90, both seeds.
- **D3 distractor/negative probes:** accuracy ≥ 0.95 (must NOT false-positive on siblings), both seeds.
- **D4 adversarial composition:** accuracy ≥ 0.85, both seeds.
- **Onset report:** the smallest fact-count (if any, within tested range) at which accuracy drops below 0.95, per
  difficulty — recorded honestly whether or not a bar is missed.

If any bar misses, that is the honest within-domain ceiling — report it plainly; do NOT retune. A miss tells Michael
exactly how large/deep a "no mistakes" domain can be. No transformer.

## Result (seeds 0, 7): **PARTIAL / honest NEGATIVE — mistakes begin INSIDE the taught domain**
Per-difficulty accuracy by scale (both seeds):

| facts | D1 deep is-a | D2 inherit+exc | D3 distractor | D4 adversarial compose |
|------:|:---:|:---:|:---:|:---:|
| ~95   | 0.95–1.0 | 1.0 | 0.975–1.0 | 1.0 |
| ~178  | 0.95 | 0.97–1.0 | 0.93–1.0 | 0.875–1.0 |
| ~278  | 0.925–0.95 | 1.0 | 0.875–0.925 | 0.75–1.0 |
| ~378  | 0.95–0.975 | 1.0 | 0.90–1.0 | **0.375–0.5** |

- **D1 (deep is-a chains): misses the 0.95 bar** — drops to ~0.925 at ~278 facts. Long chains compound per-hop
  cleanup error: each hop is routed and cleaned with small similarity noise, and at depth ~8 across 3+ auto-grown
  modules a single mis-step breaks the chain.
- **D2 (inheritance + exception): PASS (≥0.90)** — most-specific-wins is robust; the property logic itself holds.
- **D3 (distractor/negative): misses 0.95** — down to ~0.875: cleanup occasionally false-positives a sibling/cousin
  as an ancestor at scale.
- **D4 (adversarial composition): COLLAPSES** — 0.375–0.5 at ~378 facts. The conjunction (full-chain is-a AND
  exception AND distractor-rejection) compounds the individual error rates, so accuracy falls off a cliff.
- **Error onset: ~96 facts** — the first size where any difficulty dips below 0.95.

## Verdict: **PARTIAL — the honest within-domain ceiling, and it is SMALL**
The comfortable JEP-367 result (1.0) held only for a *small* domain. Stress-tested, the substrate is **not** error-free
within a taught domain once it scales: deep multi-hop chains and adversarial conjunctions degrade, and the collapse of
D4 (adversarial composition) to ~0.4 at a few hundred facts is the headline. The mechanism is the **same cleanup-
similarity dilution across auto-grown modules** that earlier capped the memory thread — small per-hop/per-probe errors
compound over depth and conjunction.

Honest consequence for Michael's gate: "no mistakes" holds only for a **small, shallow** taught domain (≲~100 facts,
shallow chains); it does NOT hold at scale/depth/adversarial composition as currently built. This is a real engineering
ceiling, not a tuning artifact (bars pre-registered, not moved). The natural next lever is **dimension** (JEP-315
showed D is the cleanup-noise lever) and/or hardened readout — tested next (JEP-369). Reported as found. No transformer.
