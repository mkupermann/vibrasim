# JEP-180 — the developmental loop's perceptual boundary (where discovery, and the whole loop, degrade)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the loop holds while noise < separation, then degrades SHARPLY as clusters merge; the bottleneck is the
  discovery/perception step (reasoning exact given correct perception). RISK: perception is the weak link, not binding.

## Result — HIT on mechanism (perception is the bottleneck); degradation GENTLER than predicted; + a test-design self-correction
Per-dim noise sweep of the full developmental loop (cluster -> name -> read -> reason):
| noise | cluster-purity | downstream (discriminating 'is it a mammal?') |
|-------|----------------|-----------------------------------------------|
| 0.3-1.2 | 1.00 / 0.99 | 1.00 |
| 1.5 | 0.97 | 0.98 |
| 2.0 | 0.88 | 0.93 |
The downstream DISCRIMINATING reasoning TRACKS the clustering purity -> the DISCOVERY/PERCEPTION step is the
bottleneck; reasoning is EXACT given correct perception; the loop inherits perception's limits (JEP-91/113), not a
limit of the binding or reasoning. HONEST NUANCES: (1) degradation is GENTLE not SHARP (I over-predicted sharpness —
high-D ward clustering separates well even at per-dim noise 2.0, only 0.88 purity). (2) TEST-DESIGN SELF-CORRECTION:
my FIRST metric ('is it an animal?') was INSENSITIVE because BOTH discovered concepts are animals, so cross-cluster
confusion didn't change the answer (a non-discriminating probe — the JEP-87 confound family). Switched to a
DISCRIMINATING question ('is it a mammal?', only one cluster) to actually measure the boundary. LESSON: a downstream
metric must DISCRIMINATE the failure mode it claims to measure. Prediction HIT (mechanism); tally 70/96. Established
(clustering separability, prototype perception); named; no novelty.
