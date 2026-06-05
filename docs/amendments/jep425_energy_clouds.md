# JEP-425 — Energy clouds: affective valence + experience strengthening (Michael's model)

## Motivation
Michael's vision: concepts are "energy clouds" with valence (good=bright, bad=dark, color) — the "molecules that
remember" — and "connections become stronger with experience." Build a first concrete version on the substrate's
distributed VSA energy clouds. Honest framing: these are ESTABLISHED concepts (affect/somatic-marker — Damasio;
Hebbian strengthening — Hebb 1949), named as such — NOT new science — but a real, brain-like extension. No transformer.

## Method
- **Valence:** an affect lexicon (positive/negative words); when an affective word is asserted of an entity, tag the
  entity with a +bright / -dark charge (`sm.valence`). Query "is X good/bad?", "what is the energy of X?".
- **Strengthening:** `sm.strength[fact]` counts experiences; re-asserting a fact increments it AND adds energy to the
  existing trace (Hebbian) without duplicating the fact. Carried through consolidation/compaction and persisted.

## Pre-registered bars
- **J425a (valence):** "A hero is good. A villain is evil." → "is a hero good?" yes, "is a villain bad?" yes, "what is
  the energy of a hero?" → bright; both seeds (0, 7).
- **J425b (experience strengthens):** re-asserting a fact 5× gives strength ≥ 5; both seeds.
- **J425c (persists + no regression):** valence survives save/load; suite passes; both seeds.

## Result: **PASS** (both seeds) — valence (hero→bright, villain→dark) queryable; strength reaches 5 after 5
experiences; persists; 23 cognition tests pass.

## Verdict: **PASS — a first build of the energy-cloud model**
Concepts now carry an affective valence (bright/dark cloud), queryable as "energy", and connections strengthen with
repeated experience (Hebbian count + added energy to the trace). Built on the substrate's distributed VSA clouds — the
distributed-energy part of Michael's model was already the architecture; valence and experience-strengthening are the
new, established-concept extensions (affect/somatic-marker; Hebb) — honestly NOT new science. No transformer.
