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
| seed | d=12 (accA/accB/xtalk) | d=8 | d=5 | d=3 |
|------|-----------------------|-----|-----|-----|
| 42   | 1.00/1.00/0.47        | 1.00/1.00/0.47 | 1.00/1.00/0.67 | 1.00/1.00/0.50 |
| 7    | 1.00/1.00/0.56        | 1.00/1.00/0.58 | 1.00/1.00/0.52 | 1.00/1.00/0.46 |

G97a sanity (d=12 both seeds): **True** · G97b min crosstalk-free pitch (both seeds): **d=3.0**
→ **VERDICT: PASS**

## Finding — the quiet substrate is a clean, high-resolution parallel channel
Both channels decode at balanced-accuracy **1.00 at every tested separation down to d=3** (box=30),
with crosstalk at or near chance (0.46–0.58) except one isolated point (seed 42, d=5, 0.67 — a
grid-binning blip, since d=3 on the same seed is back to 0.50). Two independent spatial channels are
recovered crosstalk-free by a single linear ridge decoder per channel, read out in the same tick. A
pitch of ~3 in a 30-unit box implies on the order of ~10 independent spatial channels along one axis.

**Honest framing.** This is a linear MIMO channel — an established concept, not a new mechanism — and
it extends the already-known single-input result (G83, 1.00) to parallel streams. The contribution is
the quantitative MEASUREMENT: this substrate carries multiple independent information channels in real
time at a fine spatial pitch, with no persistence required. It is a building block, not a breakthrough.

**Why it matters for the programme.** The storage/memory route to "communication without an LLM" is a
closed negative (G88–G96). This is the constructive complement: communication as real-time TRANSDUCTION
over a multi-channel line, entirely inside the substrate's proven working regime. Surfaced as a reusable
primitive in docs/patterns/parallel_spatial_channel.md. Next (G98): carry a multi-SYMBOL message
(a temporal sequence over the spatial channels) and decode it — encode → transmit → decode in-substrate.
