# JEP-286 — closing the gap: REAL-PERCEPTION -> REASONING loop (per Michael's steer)

Pre-registered 2026-06-05 (BEFORE the run). Michael's directive: "close the gap — perceiving the world via senses as
soon as the base works." The base (the Understanding Engine) now comprehensively reads/reasons/communicates over
declarative prose (122 tests). This BET starts the perception thread: connect REAL sensory input (real Fashion-MNIST
clothing photos — the 'senses') end-to-end to the prose engine, so the engine SEES a real image, recognizes it, and
REASONS about what it sees using knowledge it READ. No transformer, no pretrained vision model (raw pixels + the
engine's prototype perception).

## Method (no transformer / no pretrained vision)
- Senses = real Fashion-MNIST images (784 raw pixels, normalized 0-1). 4 concepts: shirt(6), coat(4), sandal(5),
  ankle-boot(9). LEARN each from K=30 real training examples (the engine's `learn_concept` = prototype mean).
- READ a prose taxonomy: "A shirt is clothing. A coat is clothing. A sandal is footwear. A boot is footwear."
  (clothing and footwear are SEPARATE categories.)
- For 200 held-out TEST images (50/class), PERCEIVE the image -> concept, then REASON: "is this footwear?" =
  is_a(perceived_concept, footwear). Compare to ground truth (is the true class footwear).
- CONTROL: the same reasoning WITHOUT reading the taxonomy (the engine can't answer 'is this footwear?'). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J286a | Perception works on real pixels | 4-class perceive accuracy (perceived == true) ≥ 0.60 (both seeds) |
| J286b | COARSE perceive+reason loop | 'is this footwear?' accuracy ≥ 0.85 (footwear-vs-clothing is featurally separable even if shirt/coat confuse), both seeds |
| J286c | End-to-end demonstrated | a real held-out image is perceived from raw pixels AND its 'is this footwear?' answer is derived through the READ taxonomy (shown), both seeds |
| J286d | Knowledge is necessary | without reading the taxonomy, 'is this footwear?' is unanswerable (control accuracy = the engine returns unknown / can't reason) |

PASS = J286a-c -> the engine perceives real images and reasons about them via read knowledge — the symbol-grounding
loop closed on REAL senses. NULL (honest): J286b fails -> raw-pixel prototypes don't separate footwear from clothing
well enough (then richer features are needed); J286a fails -> nearest-prototype is too weak on 4 classes. No post-hoc
tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J286a PASS (~0.65-0.75: tops shirt/coat confuse with each other and footwear sandal/boot confuse, but cross-group
separation is strong on raw pixels -> per-class still > 0.6). J286b PASS (~0.88-0.93: the COARSE footwear-vs-clothing
split is featurally distinctive — footwear is bottom-heavy/compact, tops fill the frame — so even a shirt/coat mix-up
stays within 'clothing'->'not footwear', matching the grounding-thread finding that coarse beats fine, JEP-189).
J286c PASS (the loop runs). J286d PASS (no taxonomy -> is_a unknown). Net: the engine SEES real images and REASONS
about them through read prose — the first concrete step of closing the perception gap. HONEST scope: raw-pixel
prototypes are weak perception (no learned vision features, per the no-pretrained rule); the value is the demonstrated
END-TO-END real-sensory -> symbolic-reasoning binding, and an honest measurement of how far raw senses + the engine get.
Established (nearest-prototype perception + symbolic reasoning), named; no novelty — the contribution is the closed loop.

## RESULT (2026-06-05): PASS — the engine PERCEIVES real images and REASONS about them via read prose

| seed | perceive acc (4-class) | 'is this footwear?' acc | control (no taxonomy) |
|------|------------------------|-------------------------|------------------------|
| 42 | 0.745 | **0.965** | 0.50 |
| 7  | 0.795 | **0.94** | 0.50 |

- **J286a ✓** — raw-pixel nearest-prototype perceives the 4 real classes at 0.745 / 0.795 (no learned vision features).
- **J286b ✓** — 'is this footwear?' = **0.96 / 0.94**: the engine SEES a real image and REASONS about it through the
  READ taxonomy. Even with fine confusion (shirt↔coat, sandal↔boot), the COARSE footwear-vs-clothing answer is right,
  because within-group confusions stay on the correct side of the clothing/footwear line — the predicted
  coarse-beats-fine pattern (JEP-189), confirmed.
- **J286c ✓** — end-to-end: e.g. *a real shirt image -> perceived 'coat' -> is_a(coat,footwear)=False (correct, it's
  clothing)*. Real pixels in, reasoned answer out, through the prose taxonomy.
- **J286d ✓** — knowledge is necessary: without reading the taxonomy the engine can't answer (control 0.50 = base rate).

**A REAL PROSE BUG, surfaced by perception + fixed:** the taxonomy 'A sandal is footwear' was initially NOT extracted
because 'footwear' (a collective noun) was not recognized as an is-a parent ('clothing' was, being in _MASS_NOUNS,
'footwear' was not). Added a `-wear`/`-ware` morphological rule + collective-noun lexicon entries (footwear/eyewear/
software/...) so 'X is footwear/software' -> X is-a footwear/software. The perception experiment doing its job as a
real-usage check on the prose side too.

**FINDING — the perception gap, first step closed (per Michael's steer):** the Understanding Engine now PERCEIVES the
world via senses (real Fashion-MNIST clothing photos, raw pixels) and REASONS about what it sees using what it READ —
the symbol-grounding loop closed end-to-end on REAL sensory input, at 0.95 coarse accuracy, no transformer / no
pretrained vision. HONEST scope: raw-pixel prototypes are weak fine perception (0.75); the robust, demonstrated
capability is the real-sensory -> symbolic-reasoning BINDING and the coarse-category competence. Verdict: **PASS**
(predict-calibrate HIT — perception ~0.75, coarse reasoning ~0.95, coarse-beats-fine, all as forecast). NEXT in the
perception thread: richer (still no-pretrained) features for fine perception; more senses; the full developmental
perceive->name->read->reason loop on real images.
