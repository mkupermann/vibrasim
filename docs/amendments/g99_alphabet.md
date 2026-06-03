# G99 — Message transmission WITH active reset; alphabet-size (symbol) sweep

## Motivation
G98 (NULL) showed the substrate cannot carry a message free-running: without re-quieting between symbols,
residual accumulates (ISI) and decode falls to chance. G97 reached 1.00 precisely because it re-quieted
between trials. G99 is the constructive complement: re-quiet (cull) after each symbol's readout — the
cheap active reset — and measure how large an ALPHABET the channel resolves (how many distinct symbols
it can carry per window). This is the substrate's per-symbol information capacity.

## Pre-registration (locked BEFORE run)
K symbols map one-hot to K spatial channels evenly spaced across x in [6,24] (box=30). A random N-symbol
message; each symbol injects at its channel for WIN ticks, readout the free-vibration x-grid (24 bins),
then `cull_free_vibrations` (active reset). Multiclass linear decoder (one-vs-rest ridge, argmax) on a
held-out 70/30 split. Sweep alphabet K in {4, 8, 16}.

**Bars (locked):**
- G99a sanity (K=4): held-out symbol accuracy >= 0.90 (both seeds). Chance = 0.25.
- G99b capacity: report accuracy vs K and the MAXIMUM alphabet K still reaching >= 0.90 on both seeds
  (descriptive; no threshold tuned).
PASS (as a demonstrated primitive) = G99a → with active reset the substrate transmits messages.
NULL if even K=4 fails.

## Result
_(pending run)_
