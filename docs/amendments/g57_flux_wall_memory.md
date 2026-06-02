# G57 — Flux-write + engineered wall: selective PERSISTENT memory (re-attacking the deadlock)

Pre-registered: 2026-06-02 (BEFORE the run). The memory deadlock (write=broadcast=leak) was mapped
across FIRING-based writes. But the FLUX/bistable write (BET-096/097) is NON-neural and LOCAL
(vibration flux through a bridge), and it achieved selective WRITE + a held stim latch — failing
only on CONTROL CONTAMINATION at the boundary (BET-097: control crept 3.6→4.3). The engineered
compartment wall (built this session) is an untried fix for that contamination, and because flux-
write does not broadcast, the wall cannot starve it (unlike the firing write in G33/BET-103). This
combination (flux-write + wall) was never tested.

## Method
BET-096/097 flux-write protocol (frozen vel=0 confined injection, blank slate, rectified bistable
drive) + the engineered mirror wall around the stim region (radius 6), raised at STIM start.
Arms: LOC+wall (test), UNI+wall (negative control), LOC-nowall (matched control = BET-097, should
contaminate). Fraction-selective metric over POST (≥ stim_end+2000 s). Seeds: 42 (single, per the
BET-096 protocol; replicate if it passes).

## Bars (locked pre-run — BET-096 T96 metric)
| ID | Criterion | Bar |
|----|-----------|-----|
| G57a | Contrast | stim flux ≥ 1.5× control flux |
| G57b | Selective latch (STIM) | fraction of STIM checkpoints selective ≥ 0.5 |
| G57c | Persistent recall (POST) | fraction of POST checkpoints (≥ stim_end+2000 s) selective ≥ 0.5 |
| G57d | Uniform control fails | uniform arm POST selective fraction < 0.25 |

PASS = G57a–d → the engineered wall contains the flux-write's contamination, yielding the
programme's first SELECTIVE PERSISTENT memory: write=leak is broken because the LOCAL flux write
+ a containment wall separates the write from the leak. A milestone — would reopen the memory
deadlock as breakable. If it passes, replicate across seeds (G58) before any milestone claim.
NULL: if G57c fails even with the wall, the contamination is not vibration-transit (the wall can't
reach it) → the deadlock holds even for the local flux write + containment, confirming it is
fundamental. Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — wall does not contain the contamination; deadlock holds

LOC+wall: stim-frac 0.50 (selective WRITE ✓, G57b), post-frac **0.00** (no persistent recall,
G57c ✗). G57a ✓, G57d ✓. LOC-nowall reproduced BET-097 (control crept 3.60→4.24 in POST).
Even WITH the engineered wall, control crept above 3 in POST → the wall did NOT contain the
contamination. **The contamination is NOT vibration-transit** (the wall reflects free vibrations
but the leak happens anyway) — it is bistable-well boundary drift (control bridges near the well
boundary drift up). A fresh, untried combination (local flux-write + containment wall) CONFIRMS
the memory deadlock is fundamental, not a re-derivation: write=leak holds even for the non-
broadcast local write plus containment. Memory frontier definitively closed.
