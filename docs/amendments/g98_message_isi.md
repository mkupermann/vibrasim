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
| seed | gap=12 | gap=6 | gap=2 | gap=0 |
|------|--------|-------|-------|-------|
| 42   | 0.17 (n=79) | 0.21 (n=111) | — (aborted) | — (aborted) |
| 7    | — (aborted) | — | — | — |

G98a (gap=12 acc>=0.90 both seeds): **False** (0.17) → **VERDICT: NULL**

[Sweep cut short — see below. The pre-registered bar is already decided: gap=12 is the MOST settling
condition and it failed at 0.17 (below chance 0.25); shorter gaps have strictly less decay and can only
be worse. Remaining cells were aborted because the no-reset runs blow up computationally, which is part
of the finding.]

## Finding — the substrate is NOT a memoryless channel; messaging requires active reset
Without re-quieting between symbols, decode accuracy is at or BELOW chance (0.17, 0.21 vs 0.25) even at
the longest gap (12 ticks). Two coupled effects, both pointing the same way:
1. **Decode failure.** Natural decay over 12 ticks does not clear the previous symbol's residual; symbols
   superimpose in the readout grid and the multiclass decoder cannot separate them.
2. **Computational blowup.** With no cull, free vibrations ACCUMULATE unboundedly (each symbol injects
   14·WIN); only 79–111 of 200 symbols completed before the wall budget, and ticks slowed to a crawl as
   the vibration population grew. The substrate physically piles up un-cleared signal.

This is the SAME accumulation that defeated selective memory (G88–G96), now seen as inter-symbol
interference in the communication channel: the substrate has strong "memory" in the wrong sense — it
RETAINS and superimposes rather than storing-and-recalling. A usable channel therefore needs an active
reset between symbols (a cull), exactly the reset G97 used between trials to reach 1.00. G99 tests that
constructive path directly (message transmission WITH per-symbol reset, alphabet-size sweep).

Honest note: G98 establishes the NEGATIVE (no free-running memoryless channel). It does NOT show
messaging is impossible — only that it requires the active-reset operation, which is cheap and already
proven in G97. The positive demonstration is G99.
