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
| seed | K=4  | K=8  | K=16 |
|------|------|------|------|
| 42   | 1.00 | 1.00 | 0.97 |
| 7    | 1.00 | 1.00 | 0.94 |
(chance: K=4 0.25, K=8 0.125, K=16 0.0625; n=240 each)

G99a sanity (K=4 both seeds): **True** · G99b max alphabet >= 0.90 (both): **K=16**
→ **VERDICT: PASS**

## Finding — with active reset the substrate is a working message channel (~4 bits/symbol)
The only change from G98 (NULL) is the active reset (`cull_free_vibrations`) after each symbol's readout
— and the result flips from sub-chance to near-perfect. K=4 and K=8 decode at 1.00; K=16 at 0.94–0.97,
all far above chance, both seeds. The substrate carries a 16-symbol alphabet (4 bits/symbol) reliably.

This closes the G97→G98→G99 arc honestly:
- G97: clean PARALLEL spatial channel (pitch ~3, ~10 channels/axis).
- G98: free-running FAILS — accumulation (ISI) drowns symbols; the substrate retains-and-superimposes.
- G99: with a per-symbol RESET, message transmission works at alphabet 16.

The reset is the operational substitute for the persistence the substrate cannot do selectively: rather
than storing each symbol, the channel transmits it in real time and clears. This is standard digital
communication over a linear channel (named as such — not a new mechanism); the substrate-specific data
are the spatial pitch (G97), the ISI/accumulation failure mode (G98), and the 4-bit symbol alphabet
under reset (G99). Together they are the constructive complement to the closed memory deadlock:
"communication without an LLM" is reachable as real-time transduction, not storage.
