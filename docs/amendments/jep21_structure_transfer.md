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
