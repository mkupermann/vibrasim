# G91 — Quiet + disconnected + refractory + consolidation (full combination)

## Pre-registration
Combine every mechanism that helped the memory chain: quiet substrate (cull free vibrations each
STIM tick), disconnected compartments (compartment_boundary=15), local emission (emit_speed=6),
refractory cap on the runaway cascade (t_refractory=0.5), and consolidation
(bridge_consolidate_threshold=4.0). Sweep stim injection n in {6, 10, 16}.
**Bar (locked before run):** a "working n" requires post-frac >= 0.5 (persistent selective recall)
with uni-post < 0.25 (control blank). PASS if any n meets it; else NULL.

## Result
| n  | stim-frac | post-frac | uni-post |
|----|-----------|-----------|----------|
| 6  | 0.83      | 0.44      | 0.00     |
| 10 | 0.17      | 0.00      | 0.10     |
| 16 | 0.00      | 0.00      | 0.00     |

**VERDICT: NULL** — no n meets the post-frac >= 0.5 bar.

## Finding
n=6 is the sweet spot: a STRONG selective write (stim-frac 0.83) with the control region CLEANLY
BLANK (uni-post 0.00) — the contamination that dogged the whole programme is fully solved by the
quiet+disconnected substrate. But recall lands on the **recurring 0.44 plateau** seen since G66/G70.
Higher n disrupts the write (n=10 -> 0.17, n=16 -> 0.00): more injected vibrations restart the
self-ignition cascade the refractory only partly caps, scrambling the local engram.

The 0.44 is now isolated to ONE cause: **stim-bridge persistence in POST**, not contamination
(control is blank) and not write strength (0.83). The region-mean readout reports <3 in ~56% of POST
checkpoints. G92 tests whether this is the G34 region-mean dilution artifact (engram permanent, mean
diluted by new weak bridges) or a genuine decay of the engram bridges.
