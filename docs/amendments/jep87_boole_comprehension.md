# JEP-87 — does the Boole-trained substrate UNDERSTAND? true-vs-false comprehension probe

## Why (Michael: "human-level power of understanding")
JEP-86 trained the substrate on Boole and showed retrieval. The honest test of UNDERSTANDING (not retrieval):
can it tell TRUE statements about Boole's logic from FALSE ones that use the SAME vocabulary? Retrieval scores by
word overlap; truth requires entailment vs contradiction — which bag-of-words similarity cannot see. Probed
directly, with the expectation this exposes the gap.

## Setup
- 10 matched (true, false) statement pairs about Boole's actual content (x as a class; x*x=x idempotency; 1=
  universe; 0=nothing; logic as an algebra of symbols ...). Each pair shares vocabulary; only the CLAIM differs.
- Score each statement by its best compatibility with the ingested corpus (max retrieval score). Accuracy =
  fraction of pairs where the TRUE statement scores higher than its FALSE partner.

## Pre-registration (locked BEFORE run)
- If true>false separation >= 0.80: a weak comprehension signal (the geometry tracks truth somewhat).
- If ~0.5 (chance): retrieval does NOT equal comprehension — the substrate matches VOCABULARY, not TRUTH; the
  understanding gap on the real text is confirmed. This is the EXPECTED, honest outcome and a valid finding.
- Established (distributional retrieval), named; no novelty. The point is to locate understanding honestly, not to
  manufacture a PASS.

## Result — NULL (with a self-correction that flips an apparent PASS)
First pass (confounded): true>false in 9/10 (0.90), BUT mean gap only +0.025. On inspection the "false" statements
drifted to NON-Boole vocabulary ("greater than ten", "geometry", "heavy or light") — so they scored lower from
WORD RARITY, not falsehood. The 0.90 is a TEST-CONSTRUCTION ARTIFACT, not comprehension.

Corrected (vocabulary-matched, SAME-BAG pairs — true and false built from IDENTICAL words, only the binding
swapped):
| pair | score(true) | score(false) | diff |
|------|-------------|--------------|------|
| 1 | 0.78234 | 0.78234 | 0.000000 |
| 2 | 0.89817 | 0.89817 | 0.000000 |
| 3 | 0.93146 | 0.93146 | 0.000000 |
| 4 | 0.87968 | 0.87968 | 0.000000 |
| 5 | 0.81617 | 0.81617 | 0.000000 |
**5/5 EXACT ties.**

**VERDICT: NULL.** With identical word-bags the Boole-trained substrate scores true and false statements
IDENTICALLY — it encodes VOCABULARY, not MEANING. Retrieval != comprehension, decisively, on the real text. The
first-pass 0.90 was a confound (false items used rarer words); corrected, the understanding signal is exactly zero.
This is the honest line: training on Boole gives word-geometry + retrieval, NOT understanding. Judging truth needs
entailment/contradiction over MEANING (structure + inference), which bag-of-words lacks. Bridging it without a
transformer is the open frontier. Established (distributional retrieval), named; no novelty. SELF-CORRECTION
recorded in full (apparent PASS -> NULL on a fair control), per pre-registration discipline.
