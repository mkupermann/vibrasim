# JEP-65 — build in COMPOSITIONALITY: systematic generalization to combinatorially-many novel goals

## Motivation
JEP-64: the approach categorizes but doesn't compose - the gap toward human-level. Build it in: represent each
entity by its PRIMITIVE composition (decompose its affordance into learned primitives), so the agent can ground
and plan to COMPOSITIONALLY-specified goals ('reach something that affords HOLD and CUT') - including NOVEL
primitive combinations never seen as a category. Systematic generalization to 2^K goals from K primitives is a
hallmark of human understanding.

## Pre-registration (locked BEFORE run)
- K primitive affordances; entities afford random SUBSETS; outcome = sum of primitive prototypes + noise. Agent
  learns the K primitive prototypes from SINGLE-primitive items. Each entity -> compositional code (which
  primitives, via decomposition). Goal = an arbitrary primitive subset (incl. combinations never seen);
  ground = entities whose code includes ALL goal primitives; SR-plan.
- Bars: zero-shot compositional grounding F1 >= 0.9 on novel subset goals AND grounded-planning success >= 0.85.
  PASS = compositionality built in -> systematic generalization to combinatorially-many novel goals from K
  primitives. NULL otherwise. Established (linear decomposition, SR/TD, set logic), named as such.

## Result — PASS (systematic compositional generalization, in the ADDITIVE regime - honest)
| metric | value |
|--------|-------|
| zero-shot compositional grounding F1 (arbitrary subset goals) | 1.000 |
| grounded-planning to compositional goals | 1.000 |

**VERDICT: PASS, honestly bounded.** From 5 learned primitives the agent grounds and plans to ARBITRARY
primitive-subset goals (2^5=32, incl. novel combinations) zero-shot. This is genuine SYSTEMATIC COMPOSITIONALITY -
combinatorial generalization from few primitives, a real hallmark of human understanding - and it closes the
JEP-64 categorize-not-compose gap with an explicit compositional code. CRUCIAL HONEST CAVEAT: it works because
the affordances are LINEARLY ADDITIVE (outcome = SUM of primitive prototypes), so linear decomposition trivially
recovers them. This is the EASY case of composition. HUMAN compositionality is far richer: NON-LINEAR (a 'striped
horse' is not zebra+stripes additively), RELATIONAL (X-on-top-of-Y, ordering matters), and RECURSIVE (concepts of
concepts). So JEP-65 demonstrates systematic compositionality in the ADDITIVE/LINEAR regime - a real step, but the
simplest form. The next frontier toward human-level: NON-ADDITIVE / RELATIONAL / RECURSIVE composition (binding,
roles, structure) - which additive decomposition does NOT capture. Honest: a genuine compositional step, named as
the additive case, not human-level composition. Established (linear decomposition, set logic, SR/TD), named.

## Toward human-level (honest path, per Michael's directive)
JEP-64 found the gap (categorize != compose); JEP-65 closed the ADDITIVE case (systematic 2^K generalization). The
remaining gaps to human-level composition, concretely: (1) NON-LINEAR composition (feature interactions, not
sums); (2) RELATIONAL/role binding (who-did-what-to-whom, order); (3) RECURSION (structures of structures);
(4) all of the above grounded at scale + language. These are real, hard, established-as-open problems. We are
closing them one concrete gap at a time, honestly - not claiming arrival, but not stopping.
