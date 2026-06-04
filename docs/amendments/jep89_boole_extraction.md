# JEP-89 — the parse gate on REAL prose: relation extraction from Boole's actual text

## Why
JEP-88 showed structure+binding breaks the comprehension ceiling, GIVEN a parse into (s,r,o). JEP-85 showed the
parse is the bottleneck on a toy corpus. This rung confronts it on the REAL Boole text (5447 sentences) — how much
usable structure does classic non-ML extraction actually recover from dense Victorian mathematical prose?

## Setup
- Apply definitional/Hearst patterns over Boole's sentences, including Boole's own definitional verbs (denote,
  represent, signify, is/are called, let X denote Y, by X we mean Y, X is a Y).
- Extract (subject, relation, object) triples; report count, a plausibility sample, and how many chain (2-hop).

## Pre-registration (locked BEFORE run)
- PASS: >= 50 plausible definitional/IS-A triples AND >= 5 forming 2-hop chains (enough structure to support
  inference like JEP-84/88 on real content).
- NULL/PARTIAL: sparse or noisy extraction (Boole's prose is argumentative/mathematical, not definitional) — an
  honest measure of how far real-text understanding is. Established (pattern extraction), named; no novelty.
  Characterization rung: report the actual yield, no post-hoc bar tuning.

## Result — NULL/PARTIAL (the parse gate is severe on real prose)
- 5447 sentences -> 66 raw triples -> **46 unique**, only **3 two-hop chains**.
- Most extractions are NOISE: predicate adjectives captured as objects (matter->necessary x13, sign->arbitrary,
  snow->white, cause->intelligent). A few plausible (water->fluid, language->instrument, signs->things).

**VERDICT: NULL/PARTIAL.** Classic non-ML extraction recovers almost no usable structure from Boole's dense
argumentative/mathematical prose. The parse gate is real and severe on real text. The honest synthesis of the arc:
the MECHANISMS of understanding work given structure (binding JEP-88, inference JEP-84), but you cannot GET reliable
structure from this prose with classic extraction — and the no-transformer constraint forbids the learned extractors
modern NLP uses for exactly this. This quantifies the distance to real-text understanding: it is gated by robust
parsing / unsupervised structure learning (JEP-69/70 NULL), the open frontier. Established (pattern extraction),
named; characterization rung, no bar tuning.
