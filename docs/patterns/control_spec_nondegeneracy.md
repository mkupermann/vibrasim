# Pattern: prove control-spec non-degeneracy over the FULL domain, before implementing

## Source
G172 FAIL (2026-08-13): the span-matched decoy spec was logically impossible
for 1-bit chains (weight determines arrangement — no decoy exists); the
implementation silently degenerated to decoy = truth and the specificity
gate fired against the whole run. Authored, implemented and approved by
three parties — nobody walked the edge cases.

## The rule
Every control/decoy definition in a pre-registration must be accompanied by
a DOMAIN CHECK, written before implementation: for every parameter value the
protocol can reach, either (a) exhibit a valid instance of the control, or
(b) declare that parameter value NON-CERTIFIABLE by construction — in the
amendment text, before any run. A control that silently collapses onto the
treatment is worse than no control: it converts into a false gate.

## Worked consequences (G173)
- Arrangement decoys (same span, different bit order) exist iff a chain has
  mixed weight; uniform-weight chains have none.
- At bits_per = 1, content ≡ span: NO span-neutral content decoy exists at
  all — such arms serve as sensitivity anchors only and carry the
  non-certifiability label upfront.
- Pairing derangements need m ≥ 2 and are strain-visible unless restricted
  to equal-span classes — where they may coincide with content preservation
  (check per geometry).
