# JEP-88 — structure (VSA role-binding) breaks the bag-of-words comprehension ceiling

## Why
JEP-87: bag-of-words scores same-bag true/false statements IDENTICALLY (5/5 ties) — it encodes vocabulary, not
meaning. The substrate's own primitive for making ROLE/BINDING matter is VSA role-filler binding (HRR, Plate 1995;
used in JEP-66). Test whether binding distinguishes the very pairs bag-of-words tied — locating the mechanism that
gets past the comprehension ceiling.

## Setup
- Represent a fact (subject, relation, object) with HRR: fact = cconv(SUBJ,s) + cconv(REL,r) + cconv(OBJ,o).
- Build a TRUE-fact memory from Boole's actual claims (one=universe, zero=nothing, product=common-class, ...).
- Score a statement (parsed to its (s,r,o) facts) by mean max-cosine to the true-fact memory.
- Same-bag true/false pairs from JEP-87 (false = subject/object swapped — identical word multiset).
- BASELINE: bag-of-words (sum of word vectors, no binding) — expected to TIE (reproating JEP-87).

## Pre-registration (locked BEFORE run)
- PASS: BINDING separates true>false in >= 0.90 of pairs AND bag-of-words baseline ~0.50 (ties). Shows STRUCTURE
  (role-binding), a substrate primitive, breaks the ceiling that vocabulary-only encoding hits.
- HONEST BOUND up front: this assumes a PARSE into (s,r,o) roles (the JEP-85 bottleneck) and verifies against a
  CURATED true-fact memory — it is structured verification of known facts, NOT understanding of novel prose.
  Established (HRR/VSA), named; no novelty. The point is to locate the mechanism, with its dependencies named.

## Result — PASS
| pair | bind(true) | bind(false) | bow(true) | bow(false) |
|------|-----------|-------------|-----------|------------|
| 1 | 1.000 | 0.689 | 1.000 | 0.672 |
| 2 | 1.000 | 0.329 | 1.000 | 1.000 |
| 3 | 1.000 | 0.387 | 1.000 | 1.000 |
| 4 | 1.000 | 0.333 | 1.000 | 1.000 |
| 5 | 1.000 | 0.323 | 1.000 | 1.000 |

BINDING true>false: **5/5 (1.00)**; bag-of-words true>false: 1/5 (4 exact ties).

**VERDICT: PASS.** VSA role-binding separates the same-bag true/false pairs that bag-of-words ties. STRUCTURE — a
substrate primitive (HRR/VSA, JEP-66) — is the mechanism that breaks the comprehension ceiling: who-plays-which-
role is encoded, so swapping subject/object changes the representation. HONEST BOUND: assumes a PARSE into (s,r,o)
roles (the JEP-85 bottleneck) and a CURATED true-fact memory — structured verification of KNOWN facts, NOT
understanding of novel prose. This locates the MECHANISM, not a full system. Established (HRR, Plate 1995), named;
no novelty. The honest ladder is now complete: retrieval = vocabulary geometry (JEP-83/86); bag-of-words ties truth
(JEP-87); role-binding separates it (this); the open gate is the parse (JEP-85) + learning the structure (JEP-69/70).
