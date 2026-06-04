# JEP-21 — structural transfer / factorization: apply a learned relational STRUCTURE to NEW entities (zero-shot)

## Motivation
The deepest "understanding" probe in this thread: factorize STRUCTURE from CONTENT (Whittington et al.,
Tolman-Eichenbaum Machine 2020). Learn an abstract relational STRUCTURE (e.g., a 2D grid of relations) once;
then for a NEW set of entities arranged in the SAME structure, observe only a FEW relations and infer the rest
ZERO-SHOT by mapping new entities onto the learned structural code. If the structural code (SR/grid-cell basis)
is content-independent, it transfers - the hallmark of relational abstraction / understanding.

## Pre-registration (locked BEFORE run)
- STRUCTURE = a rectangular grid graph (relations = N/S/E/W). Learn the structural code = SR eigenbasis (grid
  cells) on the abstract structure (JEP-20b). This code is ENTITY-AGNOSTIC.
- NEW domain: a fresh set of entities bound to grid nodes by a RANDOM permutation (content). Observe a few
  ANCHOR bindings (entity<->structural-position) + local adjacency among new entities. Infer the structural
  position of ALL new entities, then answer relational queries (relative direction) on NON-adjacent NEW pairs.
- Baseline: WITHOUT the learned structure (only the few observed adjacencies) - should be at chance on
  non-adjacent pairs.
- Bars: with-structure relational inference on new entities >= 0.9 AND >> no-structure baseline. PASS =
  structural code transfers to new content (zero-shot relational generalization). NULL otherwise. TEM /
  structure-content factorization (Whittington 2020) established - named as such.

## Result — PARTIAL (numbers strong, but the implementation does NOT test the strong claim — honest downgrade)
| measure | value |
|---------|-------|
| transferred-coord corr (new entities) x / y | 0.975 / 0.976 |
| zero-shot relational inference new pairs east / north | 0.957 / 0.972 |
| baseline | 0.5 |

**VERDICT: PARTIAL — self-corrected downgrade from the script's "PASS".** The numbers are real but I must be
honest about what the implementation actually did: it built the FULL adjacency of the new entities and re-ran
the SR from scratch (re-deriving the 2D structure exactly as JEP-20b does), then used the prior structural code
ONLY for AXIS ALIGNMENT via the anchors. So this does NOT demonstrate the core TEM factorization claim - that a
prior structure lets you GENERALIZE FROM FEW observations. With full adjacency, structure is simply re-derived;
the "transfer" reduces to aligning axes. The strong claim (prior structure REDUCES the observations needed on
new content) is UNTESTED here. Honest status: structure can be re-recovered on new content and aligned to a
prior frame (real but modest); genuine factorization (sparse-observation generalization via a structural prior)
remains the open test (JEP-21b would give only a SPARSE subset of new relations and check the prior fills gaps a
no-prior baseline cannot). Not overclaiming. TEM (Whittington 2020) established - named as such. Bars locked.
