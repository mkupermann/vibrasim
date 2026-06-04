# JEP-34 — abstract-goal planning: concept reasoner grounds a conceptual goal, world-model navigates

## Motivation
Integrate the two EQMOD-4 threads into ONE agent: given an ABSTRACT/conceptual goal ("reach a carnivore"), the
concept reasoner (IS-A, JEP-28) grounds it into concrete entities, and the world-model SR planner (JEP-11)
navigates to the nearest one. Tests whether conceptual knowledge + planning compose into understanding-informed
behaviour.

## Pre-registration (locked BEFORE run)
- Looped grid maze; 14 leaf entities (cat/dog/oak/rose/...) placed at random cells. Concept reasoner on the
  taxonomy; SR learned by local TD. Abstract goal = a random category (carnivore/mammal/plant/...).
- Agent: ground goal via is_a(entity, category) -> navigate to the nearest grounded entity via SR-value.
- Success = the entity the agent ENDS on is TRULY a descendant of the category (ground truth).
- Bars: reached-correct-category >= 0.85 AND >> random-entity baseline (+0.3). PASS = integrated conceptual+
  planning agent acts correctly on abstract goals. NULL otherwise. Established methods (SR/TD, Poincare), named.

## Result — PASS
| metric | value |
|--------|-------|
| agent reached a CORRECT-category entity | 1.00 |
| random-entity baseline | 0.38 |

**VERDICT: PASS.** The integrated agent acts correctly on ABSTRACT conceptual goals: the concept reasoner grounds
"reach a <category>" into concrete entities via IS-A, and the world-model SR planner navigates to the nearest
grounded entity, reaching a truly correct-category entity 1.00 of the time (random 0.38). This composes the two
EQMOD-4 threads - conceptual reasoning (JEP-28) + world-model planning (JEP-11) - into understanding-informed
behaviour. Works cleanly because entity->category IS-A is the RELIABLE regime (true ancestor relations, not the
sibling residual of JEP-33). A genuine integration step: knowledge informs action. Established methods (SR/TD,
Poincare embeddings), named as such. Honest scope: small curated world + taxonomy, structured not open.
