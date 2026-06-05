# JEP-245 — is the substrate relational store MEMORY or GENERALIZATION? (the honest boundary)

Pre-registered 2026-06-05 (BEFORE the run). Closes the substrate-relational arc's honest boundary-mapping by placing
the store on the programme's retrieval-vs-understanding line (JEP-83/84): does the energy-substrate relational store
MEMORIZE (reproduce stated facts + their deductive closure) or GENERALIZE (infer UNSTATED edges)? With random
orthogonal concept codes the prediction is the former; the latter needs structured/learned codes (JEP-176/177).

## Method (no transformer)
- JEP-232 store, is-a chain c0→…→cn, RANDOM ±1 codes. Three probes:
  - **STORED multi-hop**: store all edges; query is_a(c0, c4) (a 4-hop transitive pair, in no single edge) — tests
    deductive closure via chaining.
  - **HELD-OUT BRIDGE**: remove ONE middle edge (c2→c3), keep the rest; query is_a(c0, c4) — tests whether the store
    can INFER across the hole (inductive generalization to the unstated edge).
  - **HELD-OUT DIRECT**: never store c1→c2 but store c1→(other), c2→…; query is_a(c1, c2) — tests pure unstated-edge
    inference.
- Energy-gated chains (JEP-244). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J245a | Deductive closure WORKS | stored multi-hop is_a(c0,c4) = True via chaining (both seeds) |
| J245b | Held-out BRIDGE breaks the chain | with c2→c3 removed, is_a(c0,c4) = False (chain stops at the hole; can't infer) (both seeds) |
| J245c | Held-out DIRECT edge unrecoverable | is_a for a never-stored edge = False / chance (both seeds) |
| J245d | The boundary is the CODES, not the substrate | the same store with COMPOSITIONAL codes (child bundles parent) answers is_a(c0,c4) by code-overlap even with the bridge removed — i.e. structure in the codes restores it (both seeds) |

PASS = J245a–d → the substrate store is MEMORY + deductive closure over STORED edges (chaining), NOT inductive
generalization to unstated edges with random codes; generalization is a property of the CODES (structured/learned),
not the store — exactly the retrieval-vs-understanding + JEP-176/177 redundancy/structure lesson, in the substrate.
NULL/finding: if J245b "holds" (random codes somehow bridge the hole) that would be a surprise; if J245d fails,
compositional codes don't encode subsumption here. No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J245a PASS (chaining = deductive closure, the JEP-233 result). J245b PASS — random codes are orthogonal, carrying
NO similarity to infer the missing c2→c3; the energy-gated chain STOPS at c2 (no stored edge) → is_a(c0,c4) False.
J245c PASS (a never-stored edge is unrecoverable; the store is memory). J245d PASS — compositional codes (c_i =
sig_i ⊕ parent_code, bundled) put every ancestor's signature INTO a child's code, so is_a by code-overlap answers
c0→c4 from the geometry alone, bridge or no bridge (established VSA subsumption-by-bundling, Plate/HRR). NET: the
substrate store is MEMORY+deduction with random codes; GENERALIZATION lives in the representation (structured codes),
not the attractor store — the honest close to the arc. RISK (in-rung): J245d's overlap threshold must separate
ancestors from non-ancestors — check a non-ancestor scores low. Established (transitive closure, orthogonal-code
memory, VSA bundling), named; no novelty — the value is the honest memory-vs-generalization boundary for the substrate.

## RESULT (2026-06-05): PARTIAL — the MEMORY boundary is confirmed (a/b/c); naive codes DON'T generalize (d, as corrected)

| seed | (a) stored multi-hop | (b) held-out bridge breaks | (c) held-out direct unrecoverable | (d) compositional codes generalize |
|------|----------------------|----------------------------|-----------------------------------|-------------------------------------|
| 42 | True | True | True | False (anc overlap 0.10) |
| 7  | True | True | True | False (anc overlap 0.12) |

- **J245a/b/c ✓ — the core characterization, clean:** the substrate ATTRACTOR store is **MEMORY + DEDUCTIVE CLOSURE**.
  Stored multi-hop is_a(c0,c4) works via chaining (deductive closure over stored edges, JEP-233); but removing ONE
  bridge edge (c2→c3) makes the energy-gated chain STOP at the hole → is_a(c0,c4) False (it cannot INFER the missing
  edge), and a never-stored direct edge is unrecoverable. With random orthogonal codes the store reproduces stated
  facts + their transitive closure, NOT unstated edges. This is the retrieval-vs-understanding line (JEP-83/84) for
  the substrate: chaining = deduction, NOT induction.
- **J245d ✗ (prediction corrected):** naive COMPOSITIONAL codes do NOT cleanly encode multi-level subsumption. I
  predicted child-bundles-parent codes would answer is_a by overlap; with SIGN-bundling ancestor overlap was ~0.10
  (≈ chance), and a clarifying ANALOG-bundling check was no better (c0's overlap with ancestors c1..c4 = 0.35/0.51/
  0.04/0.19 — NON-monotone, deep ancestors c3/c4 WASHED OUT, overlapping the non-ancestor 0.05). RECURSIVE bundling
  DILUTES deep levels (a VSA capacity limit; the sign-bundle is even lossier — the cognition-programme lesson
  "[[cognition-programme-state]]: sign() bundle caps generalization, analog restores it" — but here even analog is
  insufficient for DEPTH).

**FINDING (the honest close to the arc's boundary-mapping):** the substrate attractor store is MEMORY + deduction;
INDUCTIVE generalization to unstated subsumption is a property of the REPRESENTATION, and naive VSA bundling is NOT a
sufficient representation for deep hierarchies — that needs the PROPER geometric embeddings already built in the
GEOMETRY thread (hyperbolic / order embeddings, JEP-23..27, which fit tree/subsumption structure) or learned
embeddings (JEP-176/177). So: substrate store = memory+deduction; generalization = a separate structured-embedding
problem with a known good answer (hyperbolic), NOT the attractor store and NOT naive bundling. CALIBRATION: my J245d
prediction (bundling encodes subsumption) was wrong — recursive bundling washes out depth (I under-counted the
capacity cost of nesting). Verdict: **PARTIAL** (a/b/c PASS — the boundary confirmed; d the corrected sub-claim).
predict-calibrate: a/b/c HIT, d MISS. This completes the substrate-relational arc (JEP-232..245): the substrate is the
engine's robust relational MEMORY + DEDUCTIVE-INFERENCE engine, with the generalization boundary honestly drawn.
