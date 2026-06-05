# NSH-01 — New-Science Hunt, step 1: is there a native phase transition in the substrate's own dynamics?

## Reframe (Michael's directive: "new math and science — don't work with known")
Stop importing known algorithms (VSA, reservoir) to do cognition. Instead STUDY OUR OWN novel system
— the EQMOD substrate physics (vibrations → electrons → atoms → bridges, under rules we wrote) — as an
unstudied universe, and hunt step by step for a NATIVE quantitative law we did not build in. New
science begins with a phenomenon existing theory does not predict, in a system no one has studied.
This is an open-ended SEARCH, honestly labelled — not a guaranteed discovery, and the analysis tools
(percolation/criticality) are known even though the SYSTEM and any law it yields are not.

## Hunt step 1 — structure-formation transition vs density
Sweep one control parameter (the initial vibration density / `n_initial_vibrations`) and measure an
emergent observable (the largest bridged structure after a fixed settling time). Question: does the
substrate show a SHARP transition — a critical density where a "giant" structure suddenly appears —
rather than a smooth/linear rise? A sharp transition with a definite critical point is the first sign
of a native law worth characterizing (its exponent, in a later step, is where novelty could live).

## Method (`tools/run_nsh01_density_transition.py`)
Base config = the G43 proto-cell cfg (known to form structure), seeds 42 & 7. Sweep
`n_initial_vibrations` ∈ {50,100,150,200,250,300,400,500,600}; settle SETTLE ticks; record the
largest bridged component size S(ρ). Report S vs density and the location/sharpness of any jump.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **NSH01a (a transition exists):** S(ρ) is NON-linear with a sharp rise — the ratio of the largest
  single-step jump in S to the mean step is ≥ 3× (a knee, not a ramp), both seeds.
- **NSH01b (a definite critical density):** the jump localizes to one density interval consistently
  across seeds (the critical ρ* is reproducible, not seed-noise).
- **NSH01c (saturation):** above ρ*, S saturates (capacity/excluded-volume limited), giving an
  S-curve rather than unbounded growth.

PASS = a reproducible sharp structure-formation transition exists in the substrate's own dynamics —
the first native phenomenon to then characterize (step 2: its critical exponent / universality, where
genuine novelty could appear). NULL = S(ρ) is smooth/linear (no transition — the substrate has no
critical density here; honest, and we look elsewhere). This is step 1 of an open search; bars locked;
no retuning. No transformer.

## RESULT (2026-06-05): NULL for the transition — but found a density-INDEPENDENT characteristic size

| density ρ | 50 | 100 | 150 | 200 | 250 | 300 | 400 | 500 | 600 |
|-----------|----|----|----|----|----|----|----|----|----|
| S (seed 42) | 141 | 140 | 76 | 142 | 101 | 112 | 152 | 76 | 106 |
| S (seed 7)  | 136 | 129 | 133 | 142 | 142 | 110 | 139 | 146 | 165 |

NSH01a ✗ (sharpness 1.6–2.2, < 3), NSH01b ✗ (no reproducible ρ*), NSH01c ✗ → **NULL for a density
transition.**

**But the NULL is informative — a native observation.** The largest structure size is **essentially
independent of initial density** (~100–150 atoms whether you start with 50 or 600 vibrations). There
is no percolation/giant-component transition; instead the substrate forms a structure of a
**characteristic, self-limiting size** set by its binding RULES (valence/capacity/selectivity), not by
how much material you supply. Adding more vibrations does not build a bigger structure — they cap.

**This redirects the hunt (the process working).** The open native question becomes: is that
characteristic size a SHARP "magic number" (a preferred size, like nuclear shell closure or a
fullerene C60 — which WOULD be a striking native quantization law) or a broad distribution? The
proto-cell thread independently saw ~110-atom closed membranes (G30), hinting at a preferred size.
Pursued in NSH-02 (distribution of structure sizes across many seeds at fixed density — peaked vs
broad). Step 1 done honestly: no transition, but a concrete next question. No transformer.
