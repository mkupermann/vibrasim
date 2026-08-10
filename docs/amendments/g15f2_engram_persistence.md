# G15F-2 — Under which regime do tagged flux engrams persist at all?

**Status: SIGNED OFF 2026-08-10 (one condition applied: C4 wording clarified) —
committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> Across a FIXED, pre-registered matrix of training/decay regimes, does any condition
> produce tagged node populations that (i) form at all (trainability, the gate G15F-1
> missed) and (ii) survive a 60 s rest phase — measured with no replay, no noise,
> nothing (ARM-R only)?

Context: G15F-1 (docs/amendments/g15f_dream_consolidation.md) closed **NULL-T** —
under its regime, tagged engrams did not survive the training phase itself
(N_T = {1, 0} vs bar ≥20, 3/3 seeds). Mechanism reading: flux nodes are
formation-minus-decay flux, not a persistent store. G15F-2 maps the precondition
space. This is a **characterization** (engineering measurement, named as such per
D5), NOT an effect claim: there is no treatment/control contrast to protect here —
the pre-registered condition matrix guards against post-hoc regime cherry-picking,
which is the relevant failure mode. Any later consolidation claim (a G15F-3) still
needs the full G15F-1-style control set (energy-matched arm + no-engram NC).

## 2. Fixed condition matrix (no adaptive search; changes = new ID per D3)

World and protocol identical to G15F-1 §3 (grid 80×40×10, n_quanta 10000, dt 1/60,
30 s training with the labeled A/B stimulus, 60 s rest with nothing, seeds {42,43,44})
EXCEPT the one registered factor per condition:

| Cond | Factor changed vs G15F-1 | Value |
|------|--------------------------|-------|
| C0 | none (anchor = the NULL-T regime) | — |
| C1 | window length | 2 s → 5 s |
| C2 | decay threshold `DecayConfig.T_decay_crit` | 0.02 → 0.05 |
| C3 | decay gain `DecayConfig.gamma` | 100 → 20 |
| C4 | no alternation — maximal-stimulus configuration for ONE pattern: pattern A receives the full 30 s of training (upper bound on per-pattern stimulus; pattern B untrained by design and excluded from C4's bars) | 30 s pattern A only |
| C5 | C1 + C2 combined | 5 s windows, T_decay_crit 0.05 |

6 conditions × 3 seeds = 18 runs of (30 s T + 60 s R). Auditor at 1e-9 in every run
(gate G-E as in G15F-1; violation → run invalid, engineering FAIL). Headless (D7).
No smoke needed — the harness is proven (G15F-1); the C0 anchor doubles as the
technical continuity check (its N_T must reproduce the G15F-1 order of magnitude).

## 3. Pre-registered bars (fixed before any data)

Per condition (judged on ≥2/3 seeds):
- **TRAINABLE:** N_p(T) ≥ 20 for both patterns (C4: for pattern A alone).
- **PERSISTENT:** TRAINABLE **and** S_p(60 s rest) ≥ 0.5 for the same patterns,
  where S_p = N_p(end R)/N_p(T).

Overall verdict:
- **PASS:** ≥1 condition PERSISTENT.
- **PARTIAL:** ≥1 condition TRAINABLE, none PERSISTENT (formation is fixable,
  persistence is not — in this matrix).
- **NULL:** no condition TRAINABLE (the precondition space of this matrix is empty;
  a wider matrix would be a new ID).
- **FAIL:** C0 anchor produces N_p(T) ≥ 20 (would contradict G15F-1's data —
  reproduction failure, engineering investigation before anything else).

## 4. Predictions (calibration, before data)

- C0 reproduces NULL-T-scale N_T: 90%.
- ≥1 condition TRAINABLE: 55% (C2/C5 most likely — decay threshold is the
  direct lever on the observed mechanism; C4 next).
- ≥1 condition PERSISTENT (→ PASS): 30%.
- Verdict distribution: PASS 30%, PARTIAL 25%, NULL 40%, FAIL 5%.
- Single most-likely failure mode: decay is not the binding constraint — tagged
  populations stay small because windowed mono-frequency injection feeds too few
  coherent pairs, in which case C1/C4 (more stimulus per pattern) beat C2/C3 and
  persistence still fails → PARTIAL or NULL.

## 5. Budget (hybrid, §5)

Harness extension (condition loop + config overrides): 0.5 h. Runs: ~15 min
(18 × ~30 s wall). Analysis + LOGBOOK + FRONTIER commit (D10): 0.75 h.
**Realistic 1.5 h → hard cap 3 h.** Overrun → FAILED post-mortem, no extension.

## 6. Out of scope

Dream/replay (any arm beyond ARM-R), blending, G16, bridge-pid segregation,
any adaptive/optimizing search over regimes (that would be parameter fitting,
not a pre-registered map).
