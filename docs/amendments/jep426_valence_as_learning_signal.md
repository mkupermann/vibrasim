# JEP-426 — Frontier probe: can a valence/energy signal act as an unsupervised LEARNING signal?

## Motivation
Michael's directive: pursue the frontier ("perceive the environment's energies") via experiments, accepting NULL. A
sharp, testable hypothesis from his energy model + the somatic-marker idea (Damasio): can an affective VALENCE/energy
signal serve as a LEARNING signal — i.e., can the system, from the *energy* of experiences alone (good/bad), learn
which concepts MATTER and form stronger/correct associations, WITHOUT explicit labels? If yes, it is a step toward
unsupervised learning from environmental "energy". If no, we map precisely why (which open problem blocks it).

This is reinforcement/affect-driven association (ESTABLISHED: RL, somatic markers), tested in this substrate — NOT a
claim of new science. The genuinely-open part is whether such a scalar signal is SUFFICIENT to learn structure
unsupervised; I predict it is NOT (a scalar valence carries far too little information to induce relational structure —
the credit-assignment / sample-efficiency wall). No transformer.

## Method
Present a stream of experiences (entity + a valence ±1 from the "environment") with NO relational labels. Two regimes:
(a) entities whose valence is determined by a HIDDEN rule (e.g., "things with property P are good"); can the system,
from valence alone, RECOVER which property predicts good/bad (i.e., learn the rule unsupervised)? (b) control: random
valence. Measure whether valence-driven association recovers the hidden predictive property above chance.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction (honest, before running): a scalar valence signal is INSUFFICIENT to recover the hidden relational rule from
a modest stream — the system cannot, from "good/bad" alone, learn WHICH property causes it (that is exactly the
credit-assignment + sample-efficiency open problem). I predict NULL: recovery ≈ chance at realistic stream sizes, only
rising with implausibly many examples.

- **J426a (the honest wall):** with a hidden rule "property P → good", valence-driven association does NOT identify P as
  the predictive property above chance (its valence-correlation is within the noise band of non-predictive properties)
  at a modest stream (≤200 experiences), both seeds (0, 7).
- **J426b (scaling — where would it work?):** report the stream size (if any, up to 5000) at which P becomes
  distinguishable — quantifying how much "energy experience" a scalar signal needs to teach one rule.
- **J426c (positive control):** with an EXPLICIT label (supervised), the rule is recovered immediately — confirming the
  gap is the unsupervised/scalar signal, not the mechanism.

If valence alone recovers the rule cheaply, that is a genuinely interesting positive — report it with skepticism and
investigate. Predicted: NULL (scalar valence too weak) — mapping exactly the credit-assignment wall. Established methods
(correlation/RL), named; no claim of novelty. No transformer.

## Result (seeds 0, 7): **MISS (prediction WRONG) — instructive**
- **J426a (predicted the wall): FALSE** — I predicted scalar valence would FAIL, but it RECOVERED the hidden rule
  easily: property-0 mean-valence 0.835-0.873 vs best-other 0.075-0.101 (margin ~0.76) at just 200 experiences. Both
  seeds.
- **J426b: recovered at stream=200** (the smallest tested) — cheaply, not "lots of data".
- **J426c: supervised control trivially recovers** (as expected).

### Honest diagnosis (why I was wrong)
My "hidden rule" was a SINGLE linearly-separable feature (property 0 directly → good). Correlating each property's
average valence trivially recovers that — it is the perceptron-EASY case (linearly separable), solvable since 1958.
So scalar valence DOES act as a learning signal for LINEAR rules — my pessimism was misplaced for that case. The real
credit-assignment / sample-efficiency wall appears only for NON-LINEAR / COMPOSITIONAL rules (e.g., "good iff A XOR B"),
where per-feature correlation is exactly chance (Minsky-Papert). I tested the wrong (too-easy) regime.

## Verdict: **MISS — honest wrong prediction; corrected and sharpened**
Scalar valence learns LINEARLY-SEPARABLE rules cheaply (surprise — the easy case works). My prediction of NULL was
wrong because I tested a linear rule, not the hard non-linear case. Bar NOT moved; recorded as a miss. The finding
relocates the real wall to NON-LINEAR/compositional rules — tested next (JEP-427), where per-feature valence-correlation
must be at chance (the genuine credit-assignment wall). Established methods (correlation/perceptron/Minsky-Papert),
named; no claim of novelty. No transformer.
