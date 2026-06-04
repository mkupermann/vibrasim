# GEO-28 — Compositional zero-shot: two learned attributes, composed on UNSEEN entities

## Motivation
GEO-27b: a single learned relation transfers zero-shot to unseen entities. The deeper understanding test is
COMPOSITIONAL zero-shot: learn TWO independent attribute relations (size, predator-status) on seen
entities, then answer a COMPOSED query ("large AND predator?") on entities never seen in training. Systematic
composition + zero-shot transfer together is a strong hallmark of understanding (vs memorization). Honest
interpretation either way: success = compositional understanding via geometry; failure = a boundary (second
attribute not cleanly encoded, or composition breaks).

## Pre-registration (locked BEFORE run)
- 20 animals, each labelled size-rank (real-world) and predator (1/0, real-world).
- Learn size-score and predator-score (two linear projections) from SEEN animals only (12 seen / 8 unseen).
- On UNSEEN animals, compositional decision: classify "large AND predator" (size-score > median AND
  predator-score > 0) vs ground truth. Balanced accuracy on the 8 unseen.
- Compare LLM-init vs random-init. 5 splits.
- Bars: LLM compositional balanced-acc on unseen >= 0.70 AND >= random + 0.20. PASS = compositional zero-shot
  understanding; NULL = honest boundary. Report per-attribute unseen accuracy too (localize any failure).

## Result — NULL/PARTIAL (honest boundary)
| init | composite bal-acc (unseen) | size (unseen) | predator (unseen) |
|------|----------------------------|---------------|-------------------|
| LLM-init | **0.53** | 0.75 | 0.78 |
| random-init | 0.51 | 0.53 | 0.57 |

**VERDICT: NULL/PARTIAL.** The INDIVIDUAL attributes transfer zero-shot to unseen animals (LLM size 0.75,
predator 0.78, vs random at chance — confirms GEO-27b for two attributes), but their CONJUNCTION ("large AND
predator") collapses to 0.53 (~chance). Two ~0.77 noisy zero-shot classifiers AND-composed on a rare
conjunction class compound their errors, and balanced accuracy on the rare positive degrades to chance.

**Honest boundary:** geometric zero-shot transfer is reliable for a SINGLE learned relation (GEO-27b) but
does NOT compose robustly — multi-attribute conjunctions over noisy zero-shot scores break down. This is a
concrete gap from human-level understanding (which composes attributes reliably) and bounds the
"compositional understanding" claim: composition works on CLEAN trained structure (GEO-7/12) but not on
noisy zero-shot-transferred attributes. Add per-attribute calibration / more training entities to recover it
(untested). Recorded as the limit, not retuned.
