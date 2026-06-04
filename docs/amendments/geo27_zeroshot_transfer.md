# GEO-27 — Geometry's irreducible edge: zero-shot transfer of a learned relation to UNSEEN entities

## Motivation
GEO-24 showed LLM-init is data-efficient for semantic-aligned structure. The strongest honest version:
does the LLM prior let a learned relation generalize to entities NEVER seen in any training pair (zero-shot
transfer)? Random-init cannot — unseen entities have random vectors. If LLM-init generalizes a learned
"bigger_than" ordering to held-out animals, that is geometry's IRREDUCIBLE capability: the semantic prior
positions new entities so a learned linear relation transfers with zero examples of them. This is the
clean, defensible "geometry enables understanding" claim.

## Pre-registration (locked BEFORE run)
- 16 animal words with real-world size order. Split: 11 SEEN (appear in training pairs), 5 UNSEEN (never in
  any training pair).
- Learn a scalar size-score (linear projection of the embedding) from pairs among SEEN entities only.
- Test ordering accuracy on pairs where AT LEAST ONE entity is UNSEEN (zero-shot), and on UNSEEN-vs-UNSEEN.
- Compare LLM-init vs random-init. 3 seeds.
- Bars: LLM-init zero-shot (>=1 unseen) accuracy >= 0.70 AND >= random-init + 0.20. Random-init expected
  ~chance on unseen (no information). PASS isolates the irreducible transfer.

PASS if LLM-init transfers to unseen entities and random-init cannot. NULL if LLM-init also fails to transfer.
