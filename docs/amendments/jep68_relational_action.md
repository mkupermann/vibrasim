# JEP-68 — relational goal-directed action: VSA relational reasoning drives planning

## Motivation
The compositional trio (JEP-65/66/67) are capabilities in isolation. Integrate RELATIONAL reasoning (JEP-66 VSA)
with PLANNING (SR): the agent encodes object configurations (A on B) via VSA, resolves a RELATIONAL goal ('go to
the object on top of a container') by unbinding, and navigates to it. A step beyond set-logic goals (JEP-35)
toward STRUCTURED understanding-informed action.

## Pre-registration (locked BEFORE run)
- Scene: objects with types (container/tool/...) placed on a grid; pairwise ON-TOP relations encoded in a VSA
  scene-vector (TOP*upper + BOTTOM*lower, bundled over pairs). Relational goal = 'the object on top of a <type>':
  resolve by finding the <type> object, unbinding the scene to get what's on top of it, cleanup -> target; SR-plan.
- Bars: relational-goal resolution accuracy >= 0.9 (correct target identified) AND planning success >= 0.85
  (reaches it). PASS = relational reasoning drives correct action. NULL otherwise. Established (VSA/HRR, SR/TD),
  named as such.

## Result — NULL (encoding bug: separate role-binding loses pairing)
resolution 0.39, planning 0.39. My encoding (TOP*a + BOTTOM*b, summed over pairs) BUNDLES all tops and all
bottoms but does NOT bind WHICH top goes with WHICH bottom - the pairing is lost, so 'what is on top of Y' is
unrecoverable (crosstalk -> 0.39). FIX: bind the pair so it is queryable: above(a,b) = a (x) (ABOVE (x) b); then
querying with (ABOVE (x) b) recovers a. JEP-68b. The relational CAPABILITY is fine (JEP-66); my SCENE encoding
was wrong. Bars locked.

## JEP-68b — correct pair binding — PASS
| metric | value |
|--------|-------|
| relational-goal resolution ('what is on top of Y') | 1.000 |
| relational goal-directed planning success | 1.000 |

**VERDICT: PASS.** With the correct relational encoding (above(a,b) = a (x) (ABOVE (x) b)), the agent encodes
ON-TOP relations, resolves the relational goal by unbinding with (ABOVE (x) Y) -> the on-top object (1.00), and
navigates to it (1.00). RELATIONAL reasoning drives correct ACTION - structured understanding-informed behaviour
beyond set-logic goals (JEP-35). JEP-68's NULL was the encoding (separate role-binding lost pairing), not the
capability. Integrates VSA relational composition (JEP-66) with SR planning. Established (VSA/HRR, SR/TD), named.

## Structural-cognition progression (JEP-64..68) toward human-level
located the compositionality gap (64) -> SET composition (65) -> RELATIONAL composition (66) -> RECURSIVE
composition (67) -> RELATIONAL reasoning DRIVES ACTION (68b). Each a genuine building block of human-like
structured cognition, via ESTABLISHED methods (decomposition, VSA/HRR, SR) - NO novelty claimed. The honest
remaining gap to human-level: a UNIFIED system that LEARNS these structures from grounded experience and uses
them GENERATIVELY at scale (partly what large language models achieve - forbidden here per CLAUDE.md). Genuine,
measured progress on the structural gaps; not arrival.
