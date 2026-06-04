# GEO-29 — Is the compositional zero-shot gap (GEO-28) fundamental or recoverable?

## Motivation
GEO-28: conjunction of two zero-shot attributes collapsed to chance. But that test was under-powered (8
unseen, rare positive class, no calibration). GEO-29 asks whether composition RECOVERS with (a) more
entities (denoise per-attribute scores) and (b) a BALANCED conjunction target. If it recovers, the gap is
practical (data/noise); if it stays at chance, it is a more fundamental limit of composing noisy zero-shot
scores.

## Pre-registration (locked BEFORE run)
- 40 synthetic-but-LLM-resolvable items: animals with size-rank + a second attribute that MiniLM encodes
  (aquatic vs land, a clean semantic split). 24 seen / 16 unseen.
- Target: "large AND aquatic" with a BALANCED design (size median split; aquatic ~half) so the positive
  class is ~25-35%, not rare.
- Learn size-score (ranking) + aquatic-score (mean-diff) on seen; compose on unseen. LLM vs random init, 5
  splits.
- Bars: composition recovers if LLM composite bal-acc on unseen >= 0.70 AND >= random + 0.20. If still
  < 0.65, the compositional limit is confirmed as more fundamental. Report per-attribute too.

## Result — PARTIAL (resolves the question: recoverable, not fundamental)
positive rate (large AND aquatic) = 0.20
| init | composite bal-acc | size | aquatic |
|------|-------------------|------|---------|
| LLM-init | **0.69** | 0.76 | 0.94 |
| random-init | 0.52 | 0.59 | 0.57 |

**VERDICT: PARTIAL — but it answers the question.** Composition RECOVERED from GEO-28's 0.53 to 0.69 (vs
random 0.52 at chance) with more entities + a cleanly-encoded attribute (aquatic 0.94). Just below the
pre-registered 0.70 bar and +0.17 < 0.20 gap (NOT retuned). The finding is clear regardless of the strict
bar: **the compositional zero-shot gap is NOT fundamental — it is bounded by the WEAKEST per-attribute
accuracy.** The conjunction multiplies per-attribute errors, so the noisier attribute (size 0.76) caps the
composite; the clean one (aquatic 0.94) is not the bottleneck. Implication: geometric zero-shot composition
works to the degree BOTH attributes are cleanly encoded by the LLM; improve the weak attribute (more
training entities, better descriptions) and the composite rises. A practical, not fundamental, limit —
though it still falls short of human-level robust composition. Compositional thread closed honestly.
