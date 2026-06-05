# JEP-435 — Affect → cognition (JEP-434 with SNR-controlled noise)

## Motivation
JEP-434 was NULL because σ=1.0 per-component noise (norm ≈ 64) swamped the unit-normalized cloud
(norm 1) — the instrument had no signal. JEP-435 fixes the noise scale: corrupt the probe at a
controlled signal-to-noise ratio so the bright/dark twins are genuinely confusable but signal
remains, then re-ask the JEP-434 question with the SAME acceptance bars: does the energy model's
learned valence give the substrate a disambiguation channel raw VSA similarity lacks?

## Method (`tools/run_jep435_affect_recall_snr.py`)
Identical to JEP-434 except probe noise is scaled: `probe = normalize(cloud + n)` where `n` is
Gaussian rescaled so `||n|| = r · ||cloud||`. **Primary r = 0.5 (fixed pre-run);** r ∈ {0.3, 0.7}
reported descriptively. Confusable twins (share K=6 semantic features, differ in 1 polarity feature),
energy model trained on 300 clean train pairs, tested on 100 fresh pairs. semantics-only vs
affect-augmented vs shuffled-energy control. Seeds 0 and 7.

## Pre-registered PREDICTION + bars (BEFORE the run; evaluated at r=0.5)
- **J435a (confusion is real but signal present):** semantics-only accuracy in [0.55, 0.85] — the
  noisy twins partly confuse raw similarity, not total obliteration, both seeds.
- **J435b (affect helps cognition):** affect-augmented ≥ semantics-only + 0.10 AND ≥ 0.80, both seeds.
- **J435c (it is the LEARNED valence):** shuffled-energy control ≤ semantics-only + 0.05, both seeds.

Predicted PASS: at a real SNR the learned valence recovers the polarity distinction that noisy
cosine loses, while a shuffled valence channel does not. NULL if J435a out of band (still wrong
noise level — report and stop), or J435b fails (the energy model cannot read valence through noise
→ affect does not help recall; honest). Bars locked; r fixed pre-run; no retuning. No transformer.

## RESULT (2026-06-05): NULL — and it exposes a CONCEPTUAL flaw, not a tuning one

| r | seed | semantics-only | affect-augmented | shuffled control |
|---|------|----------------|------------------|------------------|
| 0.5 | 0 | 1.000 | 1.000 | 0.500 |
| 0.5 | 7 | 1.000 | 1.000 | 0.530 |
| 0.3 | 0/7 | 1.000 | 1.000 | 0.52/0.53 |
| 0.7 | 0/7 | 1.000 | 1.000 | 0.45/0.56 |

J435a ✗ (semantics-only = 1.000, not in [0.55,0.85]), J435b ✗ (no headroom — ceiling), J435c ✓
→ **NULL.** Between JEP-434 (r≈64, total obliteration → chance) and JEP-435 (r≤0.7, **no confusion
at all** → 1.000) there is no useful middle: the discriminating polarity feature is a clean
orthogonal direction in D=4096 that cosine reads perfectly until noise overwhelms *everything* at
once. The transition is a cliff, not a ramp.

**The real (conceptual) finding — affect-as-cloud-feature is REDUNDANT with similarity.** The flaw
is not the noise level; it is the premise. I built valence as a deterministic function of a feature
that is *itself part of the cloud*, so the cosine readout and the energy model draw on the **same
information**. Affect can therefore never be an *orthogonal* channel that recall "lacks" — wherever
the energy model can read valence, cosine can already see the feature. For affect to ADD value to
recall, valence would have to carry **exogenous** information not present in the concept's own
similarity structure (e.g., valence learned from external context/experience, decoupled from
intrinsic features).

**Decision (discipline): close the affect-recall line.** Two NULLs (434 instrument, 435 premise);
a third recall variant would be the "10th variant" anti-pattern. The energy model's genuine
cognitive payoff is **affective GENERALIZATION to the unseen** (JEP-433: predict good/bad for
concepts never labelled) — an approach/avoid capability, not a recall-disambiguation one. The
valuable next step is to integrate that generalization into the live substrate (`substrate_memory`
currently only returns *taught* valence) so the brain can predict the affect of untaught concepts —
pre-registered as JEP-436.
