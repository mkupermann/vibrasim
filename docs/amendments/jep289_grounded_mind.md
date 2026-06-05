# JEP-289 — the BRIDGE: teacher-grounded PERCEPTION -> prose REASONING (a "GroundedMind")

Pre-registered 2026-06-05 (BEFORE the run). Unifies the perception thread per Michael's steers: a GroundedMind =
ActiveLearner (perceives the world, grounds concepts from a TEACHER, asks only when UNSURE — JEP-287) +
UnderstandingEngine (reasons over what it READ). It SEES real Fashion-MNIST images, grounds the clothing concepts
from a teacher, READs a taxonomy, then for held-out images PERCEIVES -> reasons 'is this footwear?'. No transformer.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J289a | perceive -> reason works | 'is this footwear?' accuracy >= 0.85 (both seeds) |
| J289b | teacher-grounded yet efficient | teacher queried on <= 70% of the stream (ask-when-unsure) (both seeds) |
| J289c | end-to-end demonstrated | a real held-out image is perceived (teacher-grounded prototype) AND reasoned about through the READ taxonomy (shown) |

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS: perception (teacher-grounded prototypes, JEP-287) + reasoning (prose is_a, JEP-286) compose -> 'is this
footwear?' ~0.9 coarse (within-group confusions stay on the right clothing/footwear side); the ask-when-unsure gate
keeps teacher labels well under labeling-everything. The engine PERCEIVES the world and REASONS about it via read
prose -- perception + understanding unified. Established (prototype perception + symbolic reasoning + active learning).

## RESULT (2026-06-05): PASS — perception and understanding unified
| seed | 'is this footwear?' acc | teacher asked | ask fraction |
|------|-------------------------|---------------|--------------|
| 42 | 0.98 | 20 / 240 | 8% |
| 7  | 0.935 | 140 / 240 | 58% |

- **J289a ✓** — the GroundedMind perceives real images and reasons 'is this footwear?' at 0.94-0.98 via the read taxonomy.
- **J289b ✓** — teacher-grounded yet label-efficient (asks 8-58% of the stream; the harder seed asks more, still <=70%).
- **J289c ✓** — end-to-end: a real image -> teacher-grounded perception -> symbol -> reasoned through read prose.

**FINDING (the perception thread, capped per Michael's steers):** JEP-286 (perceive real images + reason) + JEP-287
(slow, ask-when-unsure TEACHER loop + GUI) + JEP-288 (hear<->write cross-modal) + JEP-289 (the BRIDGE) together give a
GroundedMind that PERCEIVES the world via senses (sight + sound), GROUNDS concepts from a human teacher (querying only
when unsure), and REASONS about what it perceives using what it READ -- perception and understanding unified, no
transformer / no pretrained model. The symbol-grounding gap (a long-mapped honest frontier) now has a working,
demonstrated end-to-end loop. HONEST scope: prototype perception on raw pixels / synthesized audio is coarse (fine
classes confuse), and the audio is synthesized (no microphone yet); the contribution is the demonstrated grounded
loop with a teacher, ready to scale with richer (still no-pretrained) features and real audio input. predict-calibrate
HIT (tally 168/204). Established (prototype perception, active learning, symbolic reasoning), named; no novelty -- the
value is the unified perceive->understand loop with a teacher in it.
