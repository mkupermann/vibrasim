# GEO-51 — Symbolic numeric comparison operator (closes the GEO-20 gap)

## Motivation
GEO-20: pure geometry is BELOW chance (0.29) on numeric comparison ("who earns more, X or Y?"). The
architecture says: geometry resolves the entities, the SYMBOLIC layer compares the numbers. GEO-51 builds
and tests that operator end-to-end — the last routed operator (GEO-48) not yet validated end-to-end.

## Pre-registration (locked BEFORE run)
- 10 people each with numeric salary + age in the store meta.
- Queries: "Who earns more, X or Y?" and "Is X older than Y?" (12 pairs each, mixed outcomes).
- Operator: extract the two entities, resolve their numeric attribute (from meta), compare symbolically.
- Baseline: pure-geometric (embed the question, pick the name whose embedding is closer — GEO-20 style).
- Metric: accuracy. Bars: symbolic >= 0.9 AND >> geometric baseline (which ~chance). PASS confirms the
  comparison operator works; geometry-alone fails (consistent with GEO-20).

## Result — PASS
| operator | accuracy |
|----------|----------|
| symbolic numeric comparison | **1.00** |
| pure-geometric baseline | 0.42 (GEO-20: 0.29) |

**VERDICT: PASS.** The symbolic comparison operator (geometry resolves entities -> symbolic numeric compare)
answers "who earns more / is X older than Y" at 1.00, where pure geometry is near chance (0.42). Closes the
GEO-20 gap. **Operator coverage now complete:** every operation the symbolic router dispatches to —
factoid (retrieve), count (GEO-18), temporal (GEO-47), join (GEO-42), comparison (GEO-51), contradiction
(GEO-41) — is built and validated end-to-end, each an instance of the principle: geometry RESOLVES, the
symbolic layer OPERATES. The neuro-symbolic reasoning system is operator-complete for standard structured
queries.
