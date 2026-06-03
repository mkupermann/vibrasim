# G97 — Spatial channel capacity of the quiet substrate (real-time, no persistence)

## Motivation
The memory (storage) programme is a closed negative (G88–G96). The substrate's robust POSITIVES are
real-time: the quiet substrate reads input perfectly (G83, single-input 1.00) and the proto-cell is a
tunable analog filter/demodulator. The deep goal — communicate/transduce without an LLM — does not
require persistence if it lives in this real-time regime. G97 measures the substrate AS A COMMUNICATION
LINE: how many INDEPENDENT spatial channels can it carry crosstalk-free, read out by a LINEAR decoder
in the same tick?

This is a linear MIMO channel — an established concept, named as such. The contribution is the
quantitative MEASUREMENT on this substrate (its spatial channel pitch), not the method.

## Pre-registration (locked BEFORE run)
Quiet substrate (cull background, lambda_gen=0). Two input channels at x = centre ± d/2. Each trial,
independent random bits (a,b); inject_tight at a channel iff its bit is 1. Readout = fine free-vibration
grid along x. Train a separate ridge linear decoder per channel on a held-out split; report balanced
accuracy for each channel and CROSSTALK (channel-A decoder's accuracy at predicting bit b, and vice
versa — should be ~chance if channels are independent). Sweep separation d in {12, 8, 5, 3} (box=30).

**Bars (locked):**
- G97a sanity (wide, d=12): both channels bal-acc >= 0.85 AND crosstalk <= 0.60 (both seeds)
- G97b capacity: report the MINIMUM separation d at which both channels still meet
  (bal-acc >= 0.85 AND crosstalk <= 0.60) on both seeds. This min-d is the descriptive result.
PASS (as a demonstrated primitive) = G97a holds. The capacity sweep (G97b) is reported descriptively;
no threshold is attached to it (avoids post-hoc tuning). NULL if even d=12 fails (substrate is not a
clean parallel channel).

## Result
_(pending run)_
