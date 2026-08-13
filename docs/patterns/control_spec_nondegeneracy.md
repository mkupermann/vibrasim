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
- **G173, degeneration #3:** a decoy that differs in CONTENT but in no
  PHYSICALLY COUPLED variable is structurally inert (centered chains:
  span-preserving permutations leave ends — and thus all cross rests —
  identical). The domain check must walk the MEASUREMENT COUPLING, not just
  combinatorial existence: in which physical variable does the decoy differ,
  and is the measurement coupled to it?

## Metric non-degeneracy (Trap #6, from the BP-C6 v1 review)

The coupling walk checks whether the CONTROL couples to the measurement.
One step later, the same failure hides in the MEASUREMENT itself: after the
coupling walk, evaluate the metric formula at EVERY design cell before
sign-off. A cell where the metric is undefined (0/0 self-normalization at
the congruent cell) or trivially satisfied (an outcome guaranteed by
construction — Hooke, not hypothesis) is a degeneration of the same class
as an inert decoy. BP-C6 v1 had both in one formula: a self-normalized
following quotient whose congruent cell was 0/0 and whose incongruent cell
was the pattern-independent constant k_p/(k+k_p). Where possible, register
the ANALYTIC point prediction of the metric per cell; a design whose cells
all predict the same value measures nothing.

## Symmetry walk (Trap #6 one level up, from the BP-C6 v2 review)

When a bar rests on a symmetry argument ("these two cells must agree under
null physics"), evaluate that argument under the ACTUAL physical
transformation connecting the cells — not the algebraic relation between
their descriptors. BP-C6 v2 related two cells by mismatch-vector negation
(sign flip: a linear-only symmetry) but the chosen alternating pattern made
them SPATIAL MIRRORS of each other, and mirror symmetry survives local
nonlinearity of any order — the axis was blind to its own target signal.
Same review, same class: at k_p = k the two cells collapsed onto one
uniform endpoint geometry (complement targets sum to a constant), blinding
the endpoint metric. Rule: enumerate the transformations (mirror,
translation, relabeling, parameter coincidences) that map design cells onto
each other, and verify by explicit inequality that none of them forces the
claimed discriminator to zero.
