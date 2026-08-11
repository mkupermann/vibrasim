# G162 — the rest-length register: geometry-coded bits under PRIM14

**Status: SIGNED OFF 2026-08-11, no conditions — committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> If a carrier chain STORES its bit pattern in per-bond rest lengths
> (short = 4 → bit 0, long = 8 → bit 1) — i.e. in non-equilibrium geometry that
> only PRIM14 can hold — can the substrate's own tension dynamics re-express the
> full pattern from a scrambled state (uniform spacing 6 = the global
> equilibrium = maximum ignorance), read back as spacings, at ≥ 0.90 bit
> accuracy — while the same protocol under the global rule decodes at chance?

Honesty framing (D5): the write is DRIVEN engineering (the chain is held at the
encoded geometry during consolidation; PRIM14 freezes the rests). The claim is
retrieval: the pattern restores ITSELF from its bonds after scrambling. This is
geometry-register retrieval with a single position anchor — NOT G154-style
cue-half-the-bits association (that stays NEGATIVE per G154+G161), and NOT an
efficiency claim (closed per G154).

Why this design: G161 showed (i) PRIM14 is orthogonal to any register whose
stored geometry equals the global equilibrium, and (ii) displace-14 probes leave
the basin. G162 makes the stored geometry THE information carrier (4/8 vs global
6) and scrambles only 2 units per bond — inside the D2-verified basin.

## 2. Protocol

Chain of K+1 = 7 level-4 carriers along x from X0 = 15, y = 30, z = 30.
Pattern = 6 bits (random, ≥1 one and ≥1 zero), bond k spacing 4 (bit 0) or
8 (bit 1). Both spacings are inside the empirical bond-formation window
(D0/D1: 4 and 8 form, 12 does not) and i↔i+2 distances (≥ 12) cannot bond —
the chain stays linear. Valence 2; interior carriers saturated, chain ends
have a free slot → recall-phase bridge-formation freeze (harness-enforced,
census-verified, kill count reported; same mechanism as G161).

Phases per pattern:
1. **Write (driven):** hold all carriers at encoded positions, 8 consolidation
   ticks → bonds form with rest = encoded spacings. Census: exactly 6 bonds,
   consecutive pairs, rests ≈ pattern (else run INVALID, engineering stop).
2. **Scramble:** reposition carriers to uniform spacing 6 (carrier 0 fixed at
   X0), zero all velocities.
3. **Retrieve:** pin carrier 0 only; free relaxation 800 ticks under tension
   (k = 8.0, damping 0.95 — the D1-stable cell; window 800 not 400: chain
   normal modes are slower than the single-bond D2 system; fixed here, not
   tuned later).
4. **Read:** bit k = 1 if dist(carrier k, carrier k+1) > 6.0 else 0.

Arms:
- **ARM-P:** per_bond_rest_enabled = True.
- **ARM-OLDREST:** flag off (global r_eq = 6) — all spacings relax to 6;
  decode must be ~chance. Attribution control.
- **NEG:** bonds deleted after scrambling — chain frozen at uniform 6, decode
  all-0 (accuracy = share of 0-bits, ~0.5 in expectation).

8 random patterns × seeds {42, 7, 13} (pattern draw seeded per seed).

## 3. Pre-registered bars (fixed before any data; D3)

- **PASS:** ARM-P mean bit accuracy ≥ 0.90 on ≥ 2/3 seeds AND ARM-OLDREST
  mean ≤ 0.6 AND NEG mean ≤ 0.6 AND all censuses clean.
- **PARTIAL:** ARM-P 0.75 ≤ mean < 0.90 on ≥ 2/3 seeds, controls clean.
- **NULL:** ARM-P < 0.75, controls clean (rest lengths do not re-express the
  pattern at this regime).
- **FAIL:** ARM-OLDREST ≥ 0.75 (information is NOT in the per-bond rests —
  attribution broken), or any census violated, or NEG > 0.6 (readout
  artifact).

## 4. Predictions (calibration, before data)

- Census clean everywhere: 85%.
- ARM-P ≥ 0.90: 70% — a free-boundary spring chain's unique equilibrium is
  every bond at its own rest length; D2 verified single-bond point precision.
  Risk: 7-node chain normal modes not settled in 800 ticks, or cumulative
  positional drift mis-decoding interior bonds.
- ARM-OLDREST ≤ 0.6: 85% (uniform-6 relaxation decodes all-0 → ~share of
  zeros ≈ 0.5).
- Verdict distribution: PASS 60%, PARTIAL 20%, NULL 10%, FAIL 10%.
- Most-likely failure mode: unsettled chain oscillation at k=8 leaves interior
  spacings between 4/6/8 at read time → misdecodes → PARTIAL.

## 5. Budget (hybrid, §5)

Harness (write/scramble/retrieve/read + census + 3 arms): 45 min. Runs:
minutes. Verdict + LOGBOOK + FRONTIER (D10): 30 min.
**Realistic 1.5 h → hard cap 3 h.**

## 6. Out of scope

Cue-based association (G154/G161 territory), capacity beyond 6 bits × 8 × 3,
retention over long idle, interference between registers, adaptive rests,
efficiency claims, flux port.
