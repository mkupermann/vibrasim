# JEP-126 — scale validation: correctness + performance on a large knowledge base

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 correct (matches a reference closure) and fast (sub-millisecond is_a queries) at 1000 concepts / depth ~10.
  MOST-LIKELY MISS: a deep-hierarchy correctness edge or a performance surprise.

## Acceptance
- PASS: is_a matches reference over a sample at 1000 concepts AND mean query time < 5ms. Established, named; no novelty.

## Result — PASS (HIT)
1000 concepts built in 0.02s; max sampled ancestor-set size 535 (deep). Correctness 1999/1999 match the reference
closure; mean is_a query 0.048 ms. Prediction HIT; tally 25/40. The core reasoning scales to real-size knowledge
bases (correct + sub-ms). With JEP-124 (sound) and JEP-125 (robust), the engine is validated SOUND, ROBUST, and
SCALABLE. Established (graph reasoning at scale), named; no novelty.
