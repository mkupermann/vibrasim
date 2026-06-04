# JEP-72 — do LEARNED grounded concepts integrate with VSA structured composition?

## Motivation
Two threads: grounded concept formation (learned, CORRELATED concept vectors) and VSA structured composition
(needs quasi-ORTHOGONAL vectors for clean unbinding). Integration question: do LEARNED concept vectors (real,
correlated - shirt/pullover/coat look alike) actually plug into VSA relational binding/query, or does correlation
break cleanup? Tests whether the grounding and structure threads UNIFY.

## Pre-registration (locked BEFORE run)
- Fashion-MNIST class-mean vectors as concepts (real, correlated). Build relational structures (X above Y via
  a(x)(ABOVE(x)b)), query 'what is above Y', cleanup to nearest concept. Compare: RAW learned vectors vs WHITENED
  (decorrelated) learned vectors vs RANDOM (clean baseline).
- Bars: raw-learned relational-query accuracy reported; if < 0.8 -> correlation breaks VSA (integration challenge);
  whitening should recover toward random's ~1.0. CHARACTERIZATION: where does integration work / fail.
  Established (VSA/HRR, whitening), named as such.

## Result — PARTIAL: grounding<->structure integration REQUIRES a decorrelation interface
| concept vectors | mean off-diag cosine | relational-query accuracy |
|-----------------|----------------------|---------------------------|
| random (clean) | ~0 | 1.000 |
| learned raw | 0.769 | 0.133 (correlation breaks cleanup) |
| learned whitened | ~0 | 1.000 |

**VERDICT: PARTIAL - a concrete integration finding.** LEARNED grounded concepts are HIGHLY CORRELATED (0.769
cosine - real concepts look alike: shirt/pullover/coat), which BREAKS VSA structured composition (0.13, below
chance - cleanup confuses similar concepts). WHITENING (decorrelating) the learned concepts RECOVERS VSA perfectly
(1.00). So the grounding thread (correlated, similarity-structured representations) and the structure thread (VSA,
needs orthogonal representations) UNIFY ONLY through a DECORRELATION INTERFACE. This is a real architectural
TENSION - and its resolution: grounded representations must be orthogonalized to plug into symbolic composition.
It mirrors the known CONNECTIONIST-SYMBOLIC binding tension (continuous similarity-based reps vs discrete
compositional symbols). A concrete, honest step on the INTEGRATION gap: the two halves of the system (learned
grounding + structured composition) require a decorrelation bridge to work together. Established methods (VSA/HRR,
PCA-whitening), named as such - the INSIGHT (decorrelation interface) is the contribution, not a new method.
