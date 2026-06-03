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
| seed | m=0 | m=4 | m=8 | m=14 |
|------|-----|-----|-----|------|
| 42   | 1.00 | 1.00 | 1.00 | 1.00 |
| 7    | 1.00 | 1.00 | 1.00 | 1.00 |
(K=8, WIN=4, chance 0.125; m = interferer injections/symbol, ratio to signal 0–1.0)

G101a sanity (m=0 transfer both seeds): **True** · G101b max interferer at >= 0.90: **m=14 (ratio 1.0)**
→ **VERDICT: PASS**

## Finding — robust to random-location interference (with an honest caveat)
A decoder calibrated on clean traffic decodes at 1.00 even when each symbol is hit by an interferer as
strong as the signal itself (m=14), both seeds. The argmax decoder is robust because the true symbol is
a CONCENTRATED spatial peak at a known channel location, while the interferer is at a uniformly RANDOM x
each tick — diffuse, uncorrelated energy that rarely aligns with and never consistently dominates the
true channel bin.

**Caveat (honest):** this is robustness to RANDOM-LOCATION noise specifically. Structured interference
placed AT a competing channel location would be a harder, adversarial case and is NOT tested here; the
m=14 tolerance should not be read as a general SNR margin. As characterised, the channel handles diffuse
background noise gracefully — sufficient for the "communication without an LLM" demonstration, which does
not assume an adversary.

This completes the communication characterisation (G97 spatial · G99 alphabet · G100 rate · G101 noise),
all PASS, with the G98 boundary (active reset required). See COMMUNICATION_SUMMARY.md.
