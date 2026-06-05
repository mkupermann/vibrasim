# JEP-304 — Acquiring arbitrary (open) relation types into the durable substrate

## Motivation
JEP-300 bridged four FIXED relations (is-a, part-of, causal, property). But the Understanding Engine also learns
OPEN relations from prose — any verb seen ≥2× (eats, spins, lays, produces …) lands in `e.facts` as (s, verb, o).
Show the substrate acquires these relation types it was never pre-programmed for: bridge each verb as its own role
vector, persist, and after reload answer "does s VERB o?" and "what does s VERB?" matching the engine. No
transformer — the verb role vector is just another `atom_vector(name)`.

## Pre-registered bars (BEFORE the run)
- **J304a (open-relation recall + truth):** for every learned (s, verb, o) fact, the RELOADED substrate gives
  `query(s, verb)[0] == o` AND `relation_holds`-style truth matches the engine; accuracy ≥ 0.95, both seeds (0, 7).
- **J304b (no hallucinated relations):** on a balanced set of true facts + false (s, verb, o′) triples,
  `contains(s, verb, o, gate)` matches the engine's `relation_holds` ≥ 0.90, both seeds.
- **J304c (persists):** answers identical after a fresh reload, both seeds.
- **No-regression:** JEP-300 (the four fixed relations) still PASS under the same store.

Predicted most-likely failure: many distinct verb roles + objects raise total load; if a verb's object falls below
the gate, J304a drops — report the #relations/load at which open-relation recall degrades (a capacity finding,
not a gate tweak). Multi-object verbs (a subject VERB-ing several things) would need `query_all`; the test uses
single-object facts and notes this.

## Result (seeds 0, 7): **PASS**
- **J304a:** object recall = **1.000**, truth-vs-engine = **1.000** across 6 learned relations / 12 facts,
  both seeds. **PASS.**
- **J304b:** balanced true/false vs engine `relation_holds` = **1.000** (spider spins web True, silk False),
  both seeds. **PASS.**
- **J304c:** identical after reload. **PASS.** **No-regression:** JEP-300 fixed relations still PASS. **PASS.**
- Demo (from reloaded store): learned relations = {builds, eats, lays, makes, produces, spins};
  "what does a carnivore eat?" → meat; "what does a factory produce?" → car.

## Verdict: **PASS**
The substrate is not limited to its four pre-programmed relations — ANY relation the engine learns from prose
(a verb seen ≥2×) bridges in as its own role vector, is stored durably, and is answered after reload, matching the
engine. So new relation *types* are acquired from reading, not hand-coded. Honest scope: single-object facts here;
a subject doing one verb to several objects would use `query_all` (JEP-303) — a mechanical extension.

