# JEP-188 — ground a spatial RELATION from perception (grounding beyond objects)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 perceived geometry (object positions) grounds spatial relations ('A above B' from y-coordinates), which compose
  with the spatial faculty (transitive, perspective) — extending grounding from objects to RELATIONS. RISK: trivial
  perception (coordinate comparison), but grounding a relation (not just an object) is the new step.

## Result — PASS (HIT)
From perceived object positions (cup/plate/fork at descending y), the engine grounds DIRECT spatial relations
(cup above plate, plate above fork) from geometry, then the spatial faculty (JEP-149) reasons over them:
- cup above plate (direct, grounded) -> True
- cup above fork (TRANSITIVE, never directly perceived) -> True
- fork below cup (INVERSE) -> True
- cup above fork from the OPPOSITE viewpoint (above/below invariant under perspective) -> True
- and it composes with PROSE-learned taxonomy: 'is a cup an object?' -> True (cup is-a container is-a object, read
  from prose, on a spatially-grounded object).
So grounding extends from OBJECTS (perceive an instance -> concept, JEP-178) to RELATIONS (perceive a geometric
arrangement -> spatial relation), and the grounded relations compose with the full spatial reasoning faculty AND
with prose-learned structure. The 'perception' here is geometric (coordinate comparison) — legitimate for SPATIAL
perception specifically, though still toy. HONEST SCOPE: this grounds the SPATIAL relation type, which has a direct
geometric signature; grounding NON-geometric relations from perception (causal from observing interactions, JEP-62)
needs interaction data and remains the open frontier. Prediction HIT; tally 77/104. Established (geometric spatial
extraction + the spatial reasoning faculty); named; no novelty.
