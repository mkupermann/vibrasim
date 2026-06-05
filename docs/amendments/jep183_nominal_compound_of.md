# JEP-183 — extract tight 'X of Y' nominal compounds (the JEP-182 recall gap)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 allowing exactly-3-token 'X of Y' NPs recovers 'form of government' (democracy->political system chains),
  document recall holds, Boole increases only modestly (still ~0 genuine). RISK: re-admitting Boole 'of'-fragments.

## Result — PASS (HIT)
Relaxed the bare-NP guard to allow a TIGHT nominal compound 'X of Y' (exactly 3 tokens, 'of' in the middle, both
outer tokens bare nouns) while still rejecting longer prepositional fragments. Results:
- 'Democracy is a form of government. A form of government is a political system.' -> is_a(democracy, form of
  government) True, is_a(democracy, political system) True (chains through the X-of-Y concept). 'Ice is a state of
  matter' -> is_a(ice, state of matter) True.
- DOCUMENT test (JEP-175) recall UNCHANGED at 0.93, precision PERFECT (0 spurious) — no regression.
- BOOLE (JEP-181): is_a 24->27, part_of 27->28 (modest +4, the new 'X of Y' fragments like 'law of thought' — still
  ~0 GENUINE natural-kind taxonomy, the genre gate holds).
- Longer prepositional fragments still rejected ('admissibility of things which' -> bare_np False), precision preserved.
59/59 regression tests green (+1). A real recall gain on a common ENCYCLOPEDIC construction (form of government,
state of matter, point of view, branch of science) at no precision cost on the target genre. Prediction HIT; tally
72/99. Established (NP chunking, nominal compounds); named; no novelty.
