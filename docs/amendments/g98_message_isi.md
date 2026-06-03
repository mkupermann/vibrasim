# G98 — Multi-symbol message transmission & inter-symbol interference (ISI)

## Motivation
G97 established the quiet substrate as a clean parallel spatial channel (PASS). The forward step toward
"communication in writing" is to send a MESSAGE: a temporal sequence of symbols, decoded one per window.
The real question is INTER-SYMBOL INTERFERENCE — does the substrate's own decay clear the previous
symbol's residual before the next, or is explicit re-quieting required? The answer is the channel's
temporal capacity (max symbol rate), the standard complement to G97's spatial capacity. Established
comm-engineering measurement; applied in-substrate.

## Pre-registration (locked BEFORE run)
K=4 symbols mapped one-hot to 4 spatial channels at x = 9,13,17,21 (pitch 4, inside G97's crosstalk-free
regime). A random message of N symbols in {0,1,2,3}; each symbol injects at its channel for WIN ticks,
then GAP ticks of NO injection and NO culling — the substrate must clear residual by its own decay.
Read the free-vibration x-grid at the end of each symbol's WIN; decode with a multiclass linear readout
(one-vs-rest ridge, argmax) on a held-out 70/30 split. Sweep GAP in {12, 6, 2, 0}.

**Bars (locked):**
- G98a sanity (GAP=12, most settling): held-out symbol accuracy >= 0.90 (both seeds) → clean message
  transmission works.
- G98b temporal capacity: report symbol accuracy vs GAP and the MINIMUM GAP that still reaches >= 0.90
  on both seeds (descriptive; no threshold tuned). Chance = 0.25.
PASS (as a demonstrated primitive) = G98a. NULL if even GAP=12 fails (substrate cannot carry a message
without explicit re-quieting between every symbol).

## Result
_(pending run)_
