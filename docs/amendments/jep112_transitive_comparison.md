# JEP-112 — transitive comparison relations (a second transitive relation type beyond IS-A)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: "X is bigger than Y" parses to an order relation; transitive closure answers "is dog bigger than mouse?"
  -> Yes across a chain; must NOT collide with IS-A. MOST-LIKELY MISS: the comparative form captured by _ISA first
  (routed the comparative BEFORE _ISA).

## Acceptance
- PASS: comparison battery = 100%. Established (transitive inference over an order relation; JEP-17), named; no
  novelty. HONEST: assumes the relation is transitive (true for size/age orderings); doesn't enforce antisymmetry
  or detect cycles - a later tier.

## Result — PASS (HIT)
Comparison battery 5/5: dog>cat (direct), dog>mouse (2-hop), elephant>mouse (3-hop) all Yes; mouse>dog -> "Not
that I can tell."; IS-A intact (the comparative "X is bigger than Y" routes BEFORE _ISA so it isn't misread as
'X is-a bigger'). Prediction HIT; tally 15/24; 23 tests gated green. The engine now reasons over TWO transitive
relation types: IS-A subsumption and comparison ordering. Established (transitive inference, JEP-17), named; no
novelty. HONEST: assumes transitivity (true for size/age); no antisymmetry/cycle checks - a later tier.
