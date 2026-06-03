# G101 — Channel noise robustness (fixed decoder under interference)

## Motivation
G97–G100 characterised the clean channel (spatial pitch, alphabet, bit rate). A usable channel must
tolerate noise. G101 calibrates the decoder on CLEAN traffic, then transmits under interference (extra
random injections per symbol) and measures how accuracy degrades. This is the channel's interference
tolerance — a real failure mode (NULL is possible).

## Pre-registration (locked BEFORE run)
K=8, WIN=4, per-symbol active reset (the G99/G100 base). Train the multiclass linear decoder on a clean
message (no noise). Test on a SEPARATE message where each symbol, in addition to its true n=14 signal
injection, also receives `m` interferer vibrations at a uniformly random x in the channel span. Sweep
m in {0, 4, 8, 14} (interferer-to-signal ratio 0, 0.29, 0.57, 1.0). Held-out test accuracy per m.

**Bars (locked):**
- G101a sanity (m=0): fixed clean-trained decoder reaches >= 0.90 on the clean test message (both seeds).
- G101b tolerance: report accuracy vs m and the MAX interferer m still >= 0.90 on both seeds
  (descriptive; no threshold tuned). Chance = 0.125.
PASS (characterised) = G101a. NULL if even m=0 transfer fails.

## Result
_(pending run)_
