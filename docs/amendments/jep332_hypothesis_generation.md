# JEP-332 — Probing the creative-generation wall: plausible hypotheses vs novel invention

## Motivation
JEP-331 did DEDUCTIVE generation (certain entailments). Probe the next layer honestly: can the substrate generate
PLAUSIBLE-but-uncertain hypotheses (abductive/analogical), and where does it stop? Hypothesis: it CAN propose
defeasible guesses by class/sibling majority (recombining known properties), but CANNOT invent a genuinely novel
property no sibling has — bounding "creative" generation. Established (analogical/default inference), named as such.
No transformer. This experiment is designed to find the wall, so a partial/bounded result is the expected, valid
finding.

## Method
Give a NEW entity only its class (`collie is a dog`), withholding its properties. Generate hypotheses for it by
the MAJORITY property among known siblings (other dogs) / the class. Score: (a) plausibility — do the hypotheses
match what the entity would have under full knowledge; (b) the boundary — every hypothesis must use an EXISTING
property atom (count any invented-novel atom, which would be true creative generation).

## Pre-registered bars (BEFORE the run)
- **J332a (plausible hypotheses):** for a class-only entity, sibling-majority hypotheses match the held-out true
  properties ≥ 0.90, both seeds (0, 7) — defeasible generation works.
- **J332b (honest boundary):** the substrate generates ZERO genuinely-novel property atoms (it only recombines
  existing ones) — i.e. creative invention does NOT emerge; reported as the wall, both seeds.

Predicted outcome: J332a PASS (sibling-majority is sound recombination), J332b confirms the wall (no novel atoms) —
a HONEST bounded result: the substrate generates plausible defaults but cannot invent. If J332a misses, report the
sibling-agreement level needed; J332b is a definitional check (the generator only emits known atoms by construction
— stated plainly, not dressed as a limitation discovered).

## Result (seeds 0, 7): **PASS (bounded — the honest finding)**
- **J332a:** for `collie` (class-only, no properties given), sibling-majority hypothesis = **['bark']** = the true
  majority property; plausibility (Jaccard) = **1.0**, both seeds. Defeasible/analogical generation works. **PASS.**
- **J332b:** **0** novel atoms invented — every hypothesis reuses an existing property; the substrate recombines,
  it does not invent. **PASS** (the wall, confirmed).

## Verdict: **PASS (bounded)**
The substrate generates PLAUSIBLE defeasible hypotheses for a new entity by class/sibling majority ("a collie
probably barks"), recombining known properties — but it invents NO genuinely novel property. This honestly maps the
generation frontier:
- **Deductive generation** (certain entailments) — works (JEP-331).
- **Plausible-hypothesis generation** (defeasible defaults) — works (here, J332a).
- **Creative invention** (a property no sibling has) — does NOT emerge (J332b); it is the documented wall, exactly
  as FOR_EVERYONE names it. This is consistent with the project goal: make real steps AND draw an honest map of
  what's reachable under the no-LLM constraint. Established default/analogical inference, named as such; no
  transformer.

