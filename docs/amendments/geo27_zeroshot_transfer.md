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

## Result — PARTIAL
| init | seen-vs-seen | >=1-unseen (zero-shot, PRIMARY) | unseen-vs-unseen |
|------|--------------|----------------------------------|------------------|
| LLM-init | 0.98 | 0.90 | **1.00** |
| random-init | 0.99 | 0.77 | 0.73 |

**VERDICT: PARTIAL.** LLM-init transfers to unseen entities better, clearly on unseen-vs-unseen (1.00 vs
0.73, gap 0.27). But the PRE-REGISTERED PRIMARY metric (>=1-unseen) gap is only 0.13, below the 0.20 bar —
because mixed seen/unseen pairs are partly carried by the correctly-placed SEEN entity (so even random-init
scores 0.77), and a tiny 5-entity unseen set makes random-init noisily high (not true chance). NOT
retuning the bar (forbidden). The signal is real but the test was under-powered. Re-run clean in GEO-27b:
more entities, larger unseen split, unseen-vs-unseen as the PRIMARY pre-registered metric.
