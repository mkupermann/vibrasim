# Pattern: how distinct relation types INTERACT with taxonomy (JEP-169/170/186)

Human-like understanding requires not just reasoning WITHIN a relation (transitive closure) but reasoning across HOW
relation types COMBINE with the is-a hierarchy — and each combines under DIFFERENT, correct rules. Getting these
right (and guarding the invalid ones) is a hallmark of structured understanding; getting them wrong silently
produces false inferences. The complete, measured matrix:

## The matrix (taxonomy × each transitive relation)
| relation R(x,y) | UP the whole/effect/bigger-side | subtype inheritance | INVALID (must NOT fire) |
|-----------------|----------------------------------|----------------------|--------------------------|
| **part-of** (JEP-169) | x part-of y, y is-a Z ⟹ x part-of Z (a dog's heart is part of an animal) | Z is-a y ⟹ x part-of Z (a poodle, being a dog, has a heart) | — both directions valid (parts distribute) |
| **causal** (JEP-170) | x causes y, y is-a Z ⟹ x causes Z (causes cancer, cancer is-a disease ⟹ causes a disease) | z is-a x ⟹ z causes y (a poodle inherits a dog's causal powers) | effect-SUBtype NOT entailed (causes cancer ≠ causes every cancer kind) |
| **comparison** (JEP-186) | — | subtype inherits its kind's position (elephant > dog, poodle is-a dog ⟹ elephant > poodle) | sibling does NOT inherit (elephant > dog ⇏ elephant > a mammal that isn't a dog) |

## The deep ASYMMETRY (why one rule does not fit all)
- **Parts DISTRIBUTE over subtypes** (every dog has a heart ⟹ every poodle, being a dog, has a heart) — so a whole's
  subtype inherits the part.
- **Effects do NOT distribute over effect-subtypes** ("causes cancer" is kind/existential, not "causes every kind of
  cancer") — so an effect's subtype is NOT entailed.
- **Comparison is generic between KINDS** and a subtype inherits its kind's comparative position, but a SIBLING does
  not (being a different subtype of a common ancestor says nothing about the comparison).
The lesson: do NOT apply one relation's interaction rule to another by analogy — the distributive vs existential
character of the relation determines which interactions are valid. MEASURE each.

## The implementation invariant (the leak guard)
Apply each interaction to nodes reachable in R's own graph, expanded by is-a in the VALID direction(s) only, WITHOUT
chaining up-then-down across unrelated branches. Concretely (the shape used for all three): seed the search from x
and its is-a ancestors (subtype-of-the-source inheritance); satisfy the target z if z is in the reached set, or z
is-a a reached node (subtype-of-the-target). NEVER add the is-a-expanded targets back into R's graph as new sources —
that is what would leak a dog's heart into being part of a cat (both are animals). Property-verified sound across
400 random taxonomies (JEP-171). Established (mereological/causal/order inference, kind-level vs distributive
semantics); named; no novelty. The reusable wisdom is the MATRIX + the asymmetry + the leak-guard shape.
