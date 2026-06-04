# JEP-67 — RECURSIVE composition (structures of structures) via VSA, and its depth limit

## Motivation
The third compositional gap after additive (JEP-65) and relational (JEP-66): RECURSION - structures whose fillers
are themselves structures (a stack: above(X1, above(X2, ... Xd))). VSA supports this by binding a structure-vector
as a filler. But each bind/unbind adds crosstalk noise, so RECURSION HAS A DEPTH LIMIT (a real VSA property, and
arguably cognitively plausible - humans also fail on deep center-embedding). Test: encode nested structures of
increasing depth, traverse to recover each element, characterize the depth limit.

## Pre-registration (locked BEFORE run)
- VSA (D=2048). Stack of d objects: S_d = TOP*X_1 + BOTTOM*S_{d-1}, base S_1=X_d (circular convolution binding,
  sum bundling). Query element at level i by unbinding BOTTOM (i-1) times then TOP, cleanup to nearest object.
- Sweep depth d in {2,3,4,5,6}; measure per-element recovery accuracy.
- CHARACTERIZATION: report accuracy vs depth. Expectation: high at shallow depth, degrading as noise accumulates
  -> the honest depth limit of VSA recursion. PASS-criterion: works (>=0.9) at depth<=3. Established (VSA/HRR,
  Plate 1995), named as such.

## Result — recursion works to a DEPTH LIMIT (~4-5 at D=2048), cognitively plausible
| depth | per-element recovery accuracy |
|-------|-------------------------------|
| 2 | 1.000 |
| 3 | 1.000 |
| 4 | 1.000 |
| 5 | 0.927 |
| 6 | 0.699 |

**VERDICT: PASS (recursion works to a depth limit).** Recursive VSA structures recover deep elements perfectly to
depth 4, degrading at 5-6 as crosstalk noise overwhelms cleanup. The depth limit (more dims -> deeper) is honest,
and PARALLELS HUMAN working-memory limits on deep center-embedding (humans fail at depth ~3+ too) - cognitively
plausible. Recursion is the 3rd compositional capability after additive (JEP-65) and relational (JEP-66).

## Compositional progression (JEP-64/65/66/67) - synthesis toward human-level structured cognition
- JEP-64: located the gap (the grounded approach categorizes, does not compose).
- JEP-65: SET composition (X AND Y) - systematic zero-shot to 2^K goals from K primitives (F1 1.00). Additive/linear.
- JEP-66: RELATIONAL composition (X-on-Y != Y-on-X) via VSA role-binding (1.00) - where additive is blind.
- JEP-67: RECURSIVE composition (structures of structures) - works to depth ~4-5, a cognitively-plausible limit.
These ARE genuine hallmarks of human-like STRUCTURED thought, demonstrated via ESTABLISHED methods (linear
decomposition; vector-symbolic architectures / HRR, Plate 1995 - NOT novel, named as such). HONEST gap to
human-level: these are demonstrated as CAPABILITIES in TOY isolation; a human-level system would INTEGRATE all
three WITH grounded learning, language, and unbounded generativity - the open frontier (which large language
models partly achieve, but are forbidden here per CLAUDE.md). Genuine progress on real structural gaps, honestly
bounded, no novelty claimed.
