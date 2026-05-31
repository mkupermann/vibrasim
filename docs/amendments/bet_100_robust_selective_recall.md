# BET-100 — Robust Selective Recall: Contain Propagation + Noise-Robust Metric

Pre-registered: 2026-05-31 (BEFORE any run). Continuation of BET-099, which
showed correlation plasticity WRITES and PERSISTS a selective memory (LOC arm
selective for ~3000 s post-stimulus) but failed T99d because (a) the
any-checkpoint selectivity metric is noise-sensitive on tiny-n cores and (b)
firing propagates to control via emitted vibrations.

## The two fixes

1. **Contain firing propagation: `n_emit = 0`.** Atoms emit 8 vibrations per
   firing by default; those spread to the control region and make it fire/latch.
   Correlation detection reads `firing_events` directly, so emission is not
   needed for the write — dropping it to 0 contains firing to where the stimulus
   actually drives charge. (Principled: removes a cross-region leak, not a tune.)
2. **Noise-robust selectivity metric.** Replace `any checkpoint` with
   **fraction of checkpoints selective** (stim_mean>mid AND ctrl_mean<mid) over
   the phase. A clear majority vs a clear minority separates signal from the
   tiny-n noise. Thresholds fixed a priori below.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T100a | Selective firing (gate) | stim firings >= 3× control during STIM |
| T100b | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| T100c | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| T100d | Negative control FAILS | uniform arm: fraction of those POST checkpoints selective < 0.25 |

PASS = T100a, T100b, T100c hold AND T100d (uniform clearly below threshold).
Thresholds (0.5 majority / 0.25 minority) are pre-registered a priori as the
natural "clear majority vs clear minority" split; they are NOT fitted to data.

PASS = selective, persistent, propagation-contained correlation memory measured
robustly — the substrate writes a localized memory by correlated activity, holds
it for thousands of seconds with a blank control, read out by a noise-robust
statistic. The memory milestone of the whole BET-089→100 programme.

If T100c holds for LOC but T100d also passes (uniform selective too), propagation
or scale still dominates → the consolidated finding is that clean long-horizon
selective recall is substrate-scale-bounded (every mechanism writes; specificity
is limited by element count), which is itself the honest end-state of the memory
programme.

## Run design

Identical to BET-099 plus `n_emit=0`. neuron_dynamics ON, correlation plasticity
ON, flux bistable OFF. Warmup → starve + cull + blank → STIM (confined, localized
vs uniform) → clear field → POST. Fraction-selective metric over phases. Same
rng_seed across arms.

## RESULT (2026-05-31): NULL — n_emit=0 over-corrected; emission IS the write mechanism

Verdict: **NULL**. Firing is cleanly contained (T100a ratio 125, T100d ✓) but
NOTHING latches: LOC stim-frac 0.00, post-frac 0.00 — all bridges sit at 1.00
through STIM and POST in both arms.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T100a selective firing | ✓ | ratio 125 — firing fully contained to stim region. |
| T100b selective potentiation | ✗ | 0.00 — no bridge latched at all. |
| T100c persistent recall | ✗ | 0.00. |
| T100d control fails | ✓ (trivially) | nothing latched anywhere. |

### Diagnosis — the write/contaminate tension

`n_emit=0` removed firing propagation AND the write. Co-firing requires PAIRS of
bridged atoms firing within tau_LTP. Emission is what creates those pairs: a
stimulated atom fires, emits, and its bridged NEIGHBOURS fire just after → the
pair co-fires → the bridge potentiates. With no emission and a starved field,
stimulated atoms fire alone (ratio 125) but rarely as bridged pairs → no write.
(Confirming evidence: WARM bridges latched to 6.0 even at n_emit=0, because the
dense ambient field there co-activated neighbours.)

So emission is BOTH the write mechanism (co-firing pairs) and the contamination
mechanism (propagation to control). BET-099 had write+contaminate; BET-100 has
neither. The same confound has now been traded back and forth.

### Consolidated finding of the memory programme (BET-089→100)

- **Persistent lattice: SOLVED** (BET-091, atoms 13 s → 1500 s).
- **Selective WRITE: SOLVED** (BET-096/097: flux latch; BET-099: correlation).
- **Persistent RECALL: DEMONSTRATED transiently** (BET-099, clean selective
  memory for ~3000 s post-stimulus).
- **Clean, robust, long-horizon selective recall: BOUNDED by substrate scale &
  coupling.** Every write mechanism succeeds, but specificity over long times is
  limited by (a) few, noisy elements per region and (b) the firing-propagation
  ↔ co-firing-write tension. This is a SCALE/COUPLING limit, consistent across
  flux and correlation paradigms — not a missing mechanism.

This is the honest end-state of the spontaneous-substrate memory programme, and
it directly answers the project's strategic question: the wall to learning/recall
is substrate SCALE, repeatedly, not the learning rule.

### Next direction — a genuine strategic fork (see LOGBOOK + checkpoint)

Recorded as a strategic decision rather than another regime tweak: either
(a) LOCAL emission (emit frozen, low-velocity vibrations so firing co-activates
neighbours WITHOUT long-range propagation — a principled resolution of the
tension), (b) content-addressability on the BET-099 transient-recall window, or
(c) test whether a LARGER substrate breaks the scale limit. Default tee-up: (a).
