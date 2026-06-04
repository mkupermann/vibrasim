# JEP-70 — UNSUPERVISED relation discovery from unlabeled sequences

## Motivation
JEP-69 noted the open gap: UNSUPERVISED relation discovery (no labels). Test the cleanest case: a relation
observed ONLY as unlabeled SEQUENCES (transitions a->b on a structured graph). Can a consistent relational
structure be DISCOVERED from the co-occurrence statistics alone (like word2vec analogies emerging unsupervised),
and predict the relation for held-out entities?

## Pre-registration (locked BEFORE run)
- Structured latent graph (a ring: 'next' relation i->i+1). Generate UNLABELED random-walk sequences. Learn
  embeddings from co-occurrence (SVD of the windowed co-occurrence / SR). Discover the 'next' relation as the
  mean OFFSET (emb[next]-emb[i]) over a FEW seed pairs; predict next for HELD-OUT entities via offset+cleanup.
- Bars: held-out next-prediction hits@1 >= 0.7 (relation discovered unsupervised + generalizes). PASS =
  unsupervised relation discovery works for sequence-observed relations. NULL otherwise. Established (co-occurrence
  embeddings / word2vec-style offsets), named as such.

## Result — PARTIAL/NULL (confirms unsupervised relation discovery is genuinely hard)
discovered-'next' held-out hits@1 = 0.418 (chance ~0.017, bar 0.7). NULL because the offset method's assumptions
do not match the structure:
1. SYMMETRIC co-occurrence (I bundled both directions) loses DIRECTION - 'next' vs 'prev' confounded.
2. On a RING, 'next' is NOT a constant offset - it is a ROTATION (tangent), position-dependent - so a single mean
   offset (word2vec-style) does not apply globally.
**VERDICT: PARTIAL/NULL - honest confirmation that the gap is real and hard.** Generic unsupervised relation
discovery via constant-offset works only for FLAT/LINEAR structures with DIRECTED statistics; it fails on cyclic/
curved structure. Fixing it (directed co-occurrence + a rotation operator) would require BUILDING IN knowledge of
the ring - the opposite of unsupervised discovery. So: unsupervised discovery of ARBITRARY relational structure
(matching the operator to an unknown structure) is a GENUINE OPEN PROBLEM, not solved by simple methods. This
confirms the honest gap to human-level: relations are learnable WITH supervision (GEO-66) and SOME structure
emerges unsupervised in the right regime, but general unsupervised structure learning - which humans do - remains
open. Consistent with the honest overall assessment. Established (co-occurrence embeddings; offset analogies),
named as such. NOT engineering it to a forced PASS.
