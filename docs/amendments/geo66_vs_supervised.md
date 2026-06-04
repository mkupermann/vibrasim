# GEO-66 — Does the geometric framing beat a plain supervised baseline on embeddings?

## Motivation
The programme frames relation learning geometrically (offset/ranking/TransE). Honest deflation risk: maybe a
PLAIN supervised model (logistic regression / linear probe) on the same embeddings does just as well, in
which case "geometric" adds nothing over standard ML. GEO-66 compares head-to-head on (a) few-shot relation
learning and (b) zero-shot transfer to unseen entities — the cases where geometry should have an edge.

## Pre-registration (locked BEFORE run)
- (a) Few-shot ordinal (animal size): geometric ranking-offset vs logistic-regression pairwise classifier
  (trained on (emb_i - emb_j) -> sign), at k=4/8 training pairs. Held-out pair accuracy.
- (b) Zero-shot transfer to UNSEEN entities (GEO-27b setup): geometric ranking-projection vs the same
  logistic pairwise classifier, on unseen-vs-unseen pairs.
- Metric: accuracy, geometric vs supervised. Bars (honest, descriptive): report both. If supervised >=
  geometric on both, the geometric framing is NOT necessary (deflation). If geometric >= supervised
  (esp. few-shot/zero-shot), the framing earns its place. NULL/PASS/deflation all valid.

## Result — HONEST DEFLATION (geometric framing not necessary for LEARNING)
| task | geometric | supervised-logistic |
|------|-----------|---------------------|
| few-shot k=4 | 0.65 | 0.65 |
| few-shot k=8 | 0.70 | 0.71 |
| zero-shot transfer (unseen) | 0.82 | 0.82 |

**VERDICT: DEFLATION (significant, honest).** The geometric ranking-offset relation learner is IDENTICAL to a
plain logistic-regression pairwise classifier on the same embeddings — same few-shot, same zero-shot. So the
"geometric" framing (TransE / offset / ranking) for LEARNING relations adds NOTHING over a standard linear
probe; both learn essentially the same linear direction. **The genuine value is the LLM EMBEDDINGS + a LINEAR
READOUT** — calling it "geometric" vs "logistic regression" is immaterial.

## What this corrects, and what survives as genuinely geometric
- DEFLATED: "geometric relation learning" (GEO-6/24/27b results stand, but the framing is not special — a
  linear probe does identically). Zero-shot transfer is a property of the EMBEDDINGS, not the geometric method.
- SURVIVES as genuinely geometric (distinct from supervised ML, NO training): training-free VECTOR ARITHMETIC
  — analogy by offset (GEO-5), retrieval/grounding (GEO-15/23), multi-hop COMPOSITION by chaining (GEO-16/31),
  semantic resolution of descriptions (GEO-25b). These use the embedding geometry directly; a logistic
  regression cannot do retrieval or composition. THAT is the irreducible geometric contribution.
- Refined honest claim: the system is "EMBEDDINGS + linear readouts + symbolic operators." The embedding
  GEOMETRY genuinely powers training-free retrieval/analogy/composition; the LEARNED-relation parts are just
  ordinary linear ML on those embeddings (no geometric magic). 13th self-correction.
