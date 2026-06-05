# JEP-157 — END-TO-END learn-from-prose -> multi-hop UNDERSTANDING (the learn-from-sources capstone)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine fed Hearst-extracted taxonomy from encyclopedic prose answers CROSS-SENTENCE multi-hop is-a
  questions FAR above a bag-of-words/retrieval baseline (chance on facts no sentence states), BUT multi-hop accuracy
  DEGRADES with hop-DEPTH because extraction errors COMPOUND through the closure (the universal compounding insight
  manifest in learn-from-sources), and REDUNDANT prose (restating links) error-corrects via aggregation.
  MOST-LIKELY MISS: extraction clean enough that no compounding shows; or bag-of-words doing well via lexical overlap.

## Acceptance (characterization)
- Report multi-hop is-a accuracy by hop-depth for: engine-over-extracted-taxonomy vs bag-of-words baseline; and the
  same with REDUNDANT prose. The end-to-end real-prose -> understanding demonstration + the compounding/redundancy
  manifestation is the finding. Established (Hearst, transitive closure, the compounding insight); named; no novelty.

## Result — END-TO-END PASS; compounding sub-prediction MISS (157) then HIT under noise (157b)
### JEP-157 (clean extraction): the capstone demonstration WORKS
| hop-depth | engine | bag-of-words |
|-----------|--------|--------------|
| 1 | 1.00 | 1.00 |
| 2 | 1.00 | 0.00 |
| 3 | 1.00 | 0.00 |
| 4 | 1.00 | 0.00 |
(negatives correct-rejection: engine 1.00, bow 1.00). The engine, fed Hearst-extracted taxonomy from encyclopedic
prose, answers CROSS-SENTENCE multi-hop is-a (e.g. 'a poodle is an organism' — depth-4, stated in NO single
sentence) via transitive closure; bag-of-words retrieval gets only co-occurring (depth-1) pairs. END-TO-END
learn-from-prose -> understanding, no transformer — the positive capstone of the learn-from-sources thread.
COMPOUNDING SUB-PREDICTION MISS: I predicted multi-hop would degrade with depth from extraction errors; it stayed
1.00 because I used a TIGHT pattern on CLEAN hand-written prose (~1.00 extraction precision) — nothing to compound.
I conflated this with JEP-156's noisy 0.87 regime. DURABLE LESSON: match the TEST REGIME to the predicted MECHANISM
— a noise-dependent effect cannot show in a noise-free experiment. (tally: 157 MISS, 51/72.)

### JEP-157b (injected extraction noise): the compounding insight manifests + redundancy corrects
| condition | d1 | d2 | d3 | d4 |
|-----------|----|----|----|----|
| noise 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| noise 0.13 | 0.88 | 0.78 | 0.71 | 0.68 |
| noise 0.25 | 0.79 | 0.63 | 0.55 | 0.51 |
| noise 0.25, redundancy x2 | 0.95 | 0.92 | 0.93 | 0.92 |
| noise 0.25, redundancy x3 | 0.99 | 0.98 | 0.98 | 0.97 |
| noise 0.25, redundancy x4 | 1.00 | 0.99 | 0.99 | 1.00 |

Under extraction noise, multi-hop is-a DEGRADES with hop-DEPTH (compounding: depth-k fact needs all k extracted
edges correct ~ (1-p)^k); REDUNDANCY (restating each link -> multiple extraction chances) ERROR-CORRECTS, restoring
deep accuracy to ~1.00 (aggregation). The compounding sub-prediction was right IN SPIRIT — it needed the noisy
regime. (tally: 157b HIT, 52/73.) THE THIRD MANIFESTATION: the universal compounding/aggregation insight now spans
(1) structure LEARNING, (2) multi-hop REASONING, (3) learn-from-PROSE extraction->inference — one principle, same
cure (redundancy/aggregation) everywhere. Established (Hearst, transitive closure, robust extraction); named; no novelty.
