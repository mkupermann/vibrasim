# GEO-61 — Multi-passage context recovers document generation (top-k, not top-1)

## Motivation
GEO-60's main failure was retrieval picking the WRONG single sentence (then confident-wrong generation). The
standard RAG fix: give the generator the TOP-K retrieved sentences as context, so the right sentence is
present even if not ranked #1. GEO-61 tests whether top-3 multi-passage context recovers document generation.

## Pre-registration (locked BEFORE run)
- Same octopus paragraph + 6 answerable questions + 2 unanswerable (GEO-60).
- Pipeline: retrieve TOP-3 sentences -> concatenate as context -> 0.5B LLM generates with faithfulness
  prompt; abstain if top-1 sim < tau.
- Answer match: fair — accept numeric synonyms (8==eight, 3==three) since those are the same answer.
- Metric: (a) answerable correct >= 0.7; (b) unanswerable abstain. Compare to GEO-60 single-passage (0.17).
  PASS if multi-passage >= 0.7. Report the lift.

## Result — PARTIAL (large improvement: 0.17 -> 0.67)
| method | answerable correct |
|--------|--------------------|
| GEO-60 single-passage (top-1) | 0.17 |
| GEO-61 multi-passage (top-3) | **0.67** |
| unanswerable abstain | 1.00 |

**VERDICT: PARTIAL (4x improvement).** Multi-passage context lifts document generation from 0.17 to 0.67,
confirming the GEO-60 diagnosis: the bottleneck was retrieval picking the WRONG single sentence; giving the
generator the top-3 sentences puts the right one in context, and it answers correctly. Just below the 0.7 bar
(NOT retuned). The residual reflects the genuine prose-QA ceiling on a 0.5B model + abstention sensitivity.
**Honest conclusion on document QA (GEO-56/60/61):** retrieval over prose is the limiter; mitigate with
multi-passage context (0.17->0.67) and re-ranking (0.67->0.83 retrieval, GEO-56b). Structured generation
(GEO-34/35, 1.00) stays far more reliable because structured retrieval is exact. For documents: use
multi-passage + re-rank, expect ~0.7-0.8, and abstention keeps it honest (no silent hallucination, 1.00).
