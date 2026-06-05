# JEP-392 — "What is not clear to you?": curiosity-driven gaps from real prose

## Motivation
Michael's vision includes the substrate reading a text and telling him what it doesn't understand ("what is not clear
to you?"), then learning from his answer. The gaps/curiosity machinery (JEP-346/361) was validated on synthetic facts;
this validates it on REAL prose read end-to-end: after reading an article that references concepts it never defines,
the substrate identifies exactly those genuine gaps, voices them, and closes them (unlocking new reasoning) when taught.
No transformer.

## Method
Read an article that defines some concepts (dog→mammal→animal, whale→mammal) but only REFERENCES others without
defining them (sparrow→bird but no "bird is ..."; salmon→fish but no "fish is ..."). Then:
- `gaps()` should list the genuinely-undefined referenced concepts (bird, fish), not the defined ones, not roots.
- `say("what is not clear to you?")` voices them.
- Teaching the gap ("A bird is an animal") closes it and unlocks new multi-hop ("is a sparrow an animal?" → yes).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the substrate identifies real-prose gaps correctly, voices them, and closing one unlocks new reasoning.

- **J392a (correct gaps):** after reading, `gaps()` == {bird, fish} (the referenced-but-undefined concepts) — contains
  neither defined concepts (dog, mammal, whale) nor the root (animal), both seeds (0, 7).
- **J392b (voices them):** `say("what is not clear to you?")` mentions "bird" and "fish", both seeds.
- **J392c (teaching closes + unlocks):** "is a sparrow an animal?" is **no/unknown BEFORE** (bird undefined); after
  teaching "A bird is an animal", bird is no longer in `gaps()` AND "is a sparrow an animal?" → **yes**, both seeds.

If a defined concept or a root shows up as a gap, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — curiosity works on real prose)
- **J392a (correct gaps): PASS** — after reading, `gaps()` == **{bird, fish}** exactly: the concepts referenced
  (sparrow→bird, salmon→fish) but never given their own parent. Defined concepts (dog, mammal, whale) and the root
  (animal) are correctly NOT gaps. Both seeds.
- **J392b (voices them): PASS** — `say("what is not clear to you?")` → "A few things aren't clear to me yet — what is a
  bird?; what is a fish?". Both seeds.
- **J392c (teaching closes + unlocks): PASS** — "is a sparrow an animal?" was **no/unknown before** (bird undefined);
  after teaching "A bird is an animal", **bird leaves `gaps()`** (→ {fish}) AND "is a sparrow an animal?" → **yes** (new
  multi-hop unlocked). Both seeds.

## Verdict: **PASS — "what is not clear to you?" works on real prose**
After reading a real article, the substrate identifies exactly the referenced-but-undefined concepts as its honest
knowledge gaps, voices them when asked, and — when the teacher answers one — closes that gap and unlocks new multi-hop
reasoning that failed before. This realizes Michael's curiosity-driven vision ("what is not clear to you?" → teach →
it learns and reasons further) on real read prose, composing the gap-detection (JEP-346), self-directed learning
(JEP-361), and consolidation machinery. No transformer.
