# JEP-328 — Lexicon cleanup recovers noisy words (stress the variable JEP-327 left idle)

## Motivation
JEP-327 PASSed but raw letter recognition was so good (1.0) that edit-distance cleanup was a no-op — the cleanup
mechanism was never exercised (calibration #5: stress the variable into the effect's regime). Here, add glyph noise
until raw word recognition degrades, and show lexicon cleanup recovers the word (the JEP-290 redundancy cure), then
find where even cleanup fails. No transformer.

## Method
Render word glyphs with extra Gaussian noise σ; recognize letters → raw word; snap to nearest lexicon word by edit
distance. Sweep σ; report raw word-accuracy and cleaned word-accuracy at each σ.

## Pre-registered bars (BEFORE the run)
- **J328a (cleanup demonstrably helps):** there EXISTS a noise level where raw word-accuracy < 0.70 while cleaned
  word-accuracy ≥ 0.90 — i.e. cleanup recovers words single-letter errors would otherwise break, both seeds (0, 7).
- **J328b (characterize the failure):** report the σ at which cleaned accuracy first drops below 0.90 (where too
  many letters are wrong for edit-distance to recover) — a capacity-of-the-cure finding, not tuned.

Predicted most-likely failure: if no σ produces the raw<0.70 / cleaned≥0.90 window (cleanup either never needed or
never enough), J328a fails — report the raw/cleaned curves and that the vocabulary's edit-distance separation sets
how much cleanup can absorb. Near-neighbor words (cat/cot-style) would cap it; this vocab is checked for separation.

## Result (seeds 0, 7): **PARTIAL** — cleanup demonstrably helps, but the literal both-seeds window wasn't met
Raw vs cleaned word-accuracy by glyph noise σ (after extending the sweep — at σ≤0.5 the recognizer is fully robust,
raw=1.0, so cleanup is idle):

| σ | seed0 raw→clean | seed7 raw→clean |
|---|-----------------|------------------|
| 1.0 | 0.80 → **1.00** | 0.90 → **1.00** |
| 1.5 | 0.05 → 0.80 | 0.40 → **0.95** |
| 2.0 | 0.025 → 0.35 | 0.175 → **0.875** |
| 2.5 | 0.0 → 0.175 | 0.10 → 0.65 |

- **J328a (literal bar — raw<0.70 AND cleaned≥0.90, BOTH seeds): NOT met.** seed7 hits it (σ=1.5: raw 0.40,
  cleaned 0.95), but seed0's recognition collapses too sharply (1.0→0.80→0.05), skipping the sparse-error regime —
  so no single σ has both seeds in the window.
- **BUT cleanup clearly helps:** the raw→cleaned GAP is large and positive across the transition — σ=1.0 lifts
  0.80→1.00 / 0.90→1.00; σ=2.0 (seed7) lifts 0.175→0.875 (+0.70). The cure recovers words that single-letter errors
  would break, exactly the JEP-290 mechanism.
- **J328b (characterize):** cleaned first <0.90 at σ≈1.5 (seed0) / 2.0 (seed7) — once the glyph is mostly noise and
  ≥2-3 letters are wrong, edit-distance can't recover. The cure has a capacity, set by per-letter error rate × word
  length vs vocabulary edit-separation.

## Verdict: **PARTIAL** (honest)
The cleanup mechanism IS exercised and demonstrably recovers noisy words (large positive raw→cleaned gaps at
σ=1.0–2.0) — closing the "cleanup was idle" gap JEP-327 left. But the literal pre-registered window (both seeds,
one σ) was NOT satisfied because the exemplar recognizer transitions sharply from robust to mostly-noise, leaving a
thin sparse-error band that one seed skipped. Honest lesson: the bar should have measured the raw→cleaned GAP
(clearly ≥0.3) rather than a coincident both-seeds window; recorded as-is, not moved. The recognizer's noise
robustness (σ≤0.5 untouched) is itself the JEP-293 strength resurfacing.

