# JEP-150 — mereology (part-whole reasoning), distinct from IS-A

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: part_of is transitive (finger part-of hand, hand part-of body => finger part-of body) AND DISTINCT from
  is_a (finger is part-of body but is NOT a body; the two graphs don't leak). MOST-LIKELY MISS: leakage between
  the part-of and is-a graphs.

## Acceptance
- PASS: mereology battery = 100% (transitive part-of + non-leakage with is-a). Established (mereology / part-whole
  calculi), named; no novelty. HONEST: transitive part-of only (no part-of/is-a interaction axioms like 'a part of
  a dog is a part of an animal', which need careful treatment).

## Result — PASS (HIT)
Mereology battery 8/8: part_of transitive (finger->hand->arm->body), asymmetric (body NOT part-of finger), and
DISTINCT from is-a — finger is part-of body but is NOT a body, finger is part-of hand but NOT a hand; the graphs
don't leak (finger is-a thing via the is-a graph but is NOT part-of thing). Prediction HIT; tally 45/64; 40 tests
gated green. A fundamental distinct cognitive relation (mereology / part-whole) correctly kept separate from is-a
(subsumption) — the part-of != type-of distinction is the cognitive point. The engine now reasons over the major
DISTINCT relation types each with correct separate semantics: subsumption (is-a), ordering (comparison), causal,
spatial (+ frames of reference), and part-whole (mereology). Established (mereology / part-whole calculi), named;
no novelty. HONEST: transitive part-of only; no part-of/is-a interaction axioms (e.g. 'a part of a dog is a part of
an animal'), which need careful, non-trivial treatment.
