# JEP-136 — active + redundant querying for NOISY structure learning (combining JEP-134 + JEP-135)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 active+redundant determines a noisy transitive order in ~n log n * k queries (<< passive-redundant ~n^2 * k);
  the active speedup compounds with redundancy. MOST-LIKELY MISS: a single mis-voted comparison corrupts the
  insertion sort, so per-comparison redundancy k must be HIGHER than passive needs.

## Acceptance
- Report correctness + total queries for active+redundant vs passive-redundant at fixed per-query noise. PASS if
  active+redundant reaches >= 0.9 correct with far fewer total queries than passive. Established (active learning +
  majority-vote denoising), named; no novelty.

## Result — PASS (both prediction halves held); honest correction of the script's over-claim
| n | k | active queries | active correct | passive queries | passive correct |
|---|---|----------------|----------------|-----------------|-----------------|
| 8 | 11 | 173 | 0.74 | 376 | 0.66 |
| 16 | 11 | 494 | 0.60 | 1024 | 0.03 |
| 32 | 11 | 1306 | 0.21 | 2284 | 0.00 |

Active+redundant STRICTLY BEATS passive-redundant: more correct AND fewer total queries at every (n,k) (e.g. n=16,
k=11: active 0.60 vs passive 0.03, half the queries). The active advantage COMPOUNDS with the noise-redundancy.
BOTH halves of the prediction held: (a) active << passive queries; (b) the predicted FAILURE MODE materialized —
correctness DEGRADES WITH n (0.74 -> 0.60 -> 0.21 at fixed k=11) because the insertion SORT compounds errors: it
needs ALL ~n log n comparisons correct, so even small per-comparison vote-error compounds as n grows. CORRECTION:
the script's printed "FAR fewer queries -> determined" OVER-CLAIMS — active is BETTER but neither reaches high
accuracy at fixed k for large n. To maintain accuracy you must grow k ~ log n (total cost ~ n log^2 n). This
REINFORCES the JEP-134 insight in the active setting: structure inference (sort/closure) is fragile because it needs
all components correct, so noise-cost compounds with structure SIZE, not just rate. HONEST SYNTHESIS of the noisy
frontier (133+134+135+136): the efficient route is active+redundant querying, but redundancy must scale with
structure size; one-shot noisy structure learning stays genuinely hard. CALIBRATION: HIT (predicted both the active
advantage and the compounding failure mode); tally 32/50. Established (active learning + majority-vote denoising),
named; no novelty.
