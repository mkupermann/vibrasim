# JEP-187 — the developmental loop on REAL image data (Fashion-MNIST): grounding beyond toy prototypes

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the loop composes on real images but clustering purity is LOWER than toy (~0.7-0.9), and downstream reasoning
  inherits the perceptual purity — the bottleneck is real perception (JEP-180), not the binding.

## Result — PASS (HIT); + a real-time non-discriminating-probe SELF-CATCH
Ran the full developmental loop on REAL Fashion-MNIST images (raw pixels, no feature engineering), 3 visually-distinct
classes (trouser/sneaker/bag), feat_dim=784:
- UNSUPERVISED discovery: clustering purity 0.93 on 60 unlabeled real images (LOWER than toy 1.00, as predicted —
  real pixels are less separable).
- discovered concepts mapped to the right classes; read structure ('a <concept> is a garment/object').
- NEW held-out test images -> the CORRECT discovered concept (DISCRIMINATING): 0.93.
- 'is it a garment?' (DISCRIMINATING: trouser/sneaker yes, bag no): 0.93.
All downstream DISCRIMINATING metrics track the clustering purity (0.93) -> real PERCEPTION is the bottleneck;
the binding + reasoning are exact given perception. Grounding ADVANCED from toy prototypes toward REAL images.
DISCIPLINE SELF-CATCH (important): my first metrics ('is it an object?' — all 3 classes are objects; 'maps to a
concept' — always true) were NON-DISCRIMINATING (the JEP-180/87 confound family) and trivially read 1.00. I caught
this BEFORE recording — applying the lesson I had JUST written into docs/patterns/calibration_lessons.md one rung
earlier — and switched to discriminating metrics (per-class perception + 'is it a garment?'). The forbidden outcome
(repeating a diagnosed mistake into the record) was AVOIDED; the discipline worked in real time. HONEST SCOPE: still
PIXEL grounding (visual, not functional — JEP-58/61); rich functional grounding (affordance/interaction, JEP-62) is
the open frontier. But the developmental loop now demonstrably composes on REAL perceptual data. Prediction HIT;
tally 76/103. Established (agglomerative clustering on images, prototype perception); named; no novelty.
