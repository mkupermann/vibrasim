# JEP-75 — LEARN the relations from data (TransE), not hand-specify them

## Motivation (the honest gap #5)
Across JEP-66..73b the relational structure (ABOVE role, analogy operator) was HAND-SPECIFIED as fixed random
vectors. Human-level understanding LEARNS relations from experience. Standard, named method: knowledge-graph
embedding (TransE, Bordes et al. 2013) learns entity AND relation embeddings from (head, relation, tail) triples
such that head + relation ~ tail, then predicts UNSEEN facts (link prediction). This replaces hand-assignment
with learning-from-data.

## Pre-registration (locked BEFORE run)
- Synthetic KG: N=60 entities with latent structure, R relations as consistent latent offsets; triples = (h, r,
  nearest entity to latent_h + offset_r). Hold out 20% of triples. Learn E (entities) and R (relations) by TransE
  (margin-ranking loss, negative sampling, entity-norm constraint) on TRAIN ONLY.
- Metric: on held-out triples, rank the true tail among all N entities (filtered). Report Hits@10 and MRR.
- BAR (PASS): held-out Hits@10 >= 0.80 AND MRR >= 0.50, vs a random-embedding control at ~chance (10/60 = 0.17).
  PASS => the relations the structured system uses CAN BE LEARNED from triples (and generalize to unseen facts),
  not hand-specified — closing gap #5 in the toy regime.
- Honest bound stated up front: this is the LEARNABLE regime (relations with consistent structure); TransE's known
  weakness is symmetric / 1-to-N / N-to-N relations. Established (TransE), named as such; NO novelty claimed.

## Result — PASS
- Control (random init): Hits@10=0.146, MRR=0.058 (~chance 0.167).
- Trained TransE: held-out **Hits@10=0.854 (>=0.80), MRR=0.568 (>=0.50)**.
- Per-relation Hits@10: R0 0.90, R1 0.82, R2 1.00, R3 0.70 (all well above chance).

**VERDICT: PASS.** The relational structure the system composes over CAN BE LEARNED from (h,r,t) triples (TransE)
and generalizes to UNSEEN facts — it need not be hand-specified. Closes gap #5 in the toy regime. Honest bound:
learnable regime (relations with consistent offset); TransE's known weakness is symmetric/1-to-N/N-to-N relations;
supervised triples still required; toy scale. Established (TransE, Bordes 2013), named; NO novelty.
