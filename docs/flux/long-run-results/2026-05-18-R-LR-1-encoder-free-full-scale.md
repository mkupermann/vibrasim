# R-LR-1 — Encoder-Free Full-Scale Training Run (1.8M ticks)

**Date:** 2026-05-18T01:54:36 → 2026-05-19T03:53:42  
**Wall-clock:** 26h 18min 05s  
**Substrate config:** 80 × 40 × 10 voxels, encoder-free raw audio injection (`freq = log(SR/2)` constant, `energy = abs(sample)`), F1c thermal + R-1b pressure-gradient + R-1d-T3-bis ceiling scaffold + F2 synthesis (read-out only) + R-4 F3 monotone-flux plasticity.  
**Audio corpus:** R-7 English curriculum (Stage 1 LibriVox audiobook + Stage 2 single-speaker YouTube + Stage 4 substitute, ~6 h total, looped to fill 1.8M ticks).  
**Pre-registered acceptance:** R-11 thresholds (locked, no retuning).  
**Verdict:** NULL on both acceptance tests.

## Substantive measurements

```
trained substrate (encoder-free, exposed to ~6h English audio):
    bridges_alive  = 3188
    nodes_alive    = 1358
    quanta_peak    = 535
    
no-input control substrate (matched-wallclock, no audio):
    bridges_alive  = 0
    nodes_alive    = 0
    quanta_peak    = (negligible — nothing injected)

trained-vs-control babble distinguishability:
    KL_mean(trained-MFCC, control-MFCC)   = 0.000001
    KL_std (100-bootstrap)                = 0.000001
    2σ acceptance threshold               = 0.000003
    → not distinguishable → test 1 NULL

no-input control vs white-noise baseline:
    KS statistic     = 0.6758
    p-value          = 5.67e-277
    p ≥ 0.05 required
    → control significantly differs from white-noise → test 2 NULL
    (control is not an honest baseline)
```

## What this means

### Positive (newly-demonstrated)
- **Substrate forms emergent topology from raw audio**: 1358 atom-nodes + 3188 bridges
  developed across 1.8M ticks from purely amplitude-modulated quantum injection
  (no frequency information, no DSP frontend). This is the substantive new finding
  of the long-run — emergence is happening at production scale on encoder-free input.
- **Negative control is properly empty**: the matched-wallclock no-input substrate
  developed zero structure (0/0), so any structure trained develops cannot be
  attributed to the substrate's own dynamics in absence of audio.

### Negative (failure modes documented)
- **Synthesis layer baseline is not white-noise**: when reading from an empty
  substrate (0 nodes, 0 bridges), the F2 resonator-bank synthesis still produces
  output that is highly distinguishable from white noise (KS=0.68, p<1e-200).
  The resonator bank has its own characteristic spectral signature from numerical
  artifacts (probably initial-state ringing, floor-Q damping pole, etc.).
- **Trained substrate's emergent topology doesn't manifest in synthesis output**:
  even with 1358 nodes and 3188 bridges built from audio exposure, the resulting
  babble MFCC distribution is statistically indistinguishable from the empty-substrate
  control synthesis. Either (a) the bridges encode audio statistics in a form that
  the synthesis layer cannot read out, (b) the trained babble is dominated by the
  same synthesis-layer baseline noise that the control exhibits, or (c) the audio
  statistics simply aren't represented in the topology.

### Test framework defect identified
The pre-registered R-11 control design assumed no-input substrate babble would be
indistinguishable from white noise. Empirically (test 2), this is false — synthesis
has its own signature. A corrected control must compare trained-substrate babble
against synthesis-layer-baseline babble *directly*, not against the abstract
white-noise distribution. R-LR-7 (queued post-R-LR-1) will use a corrected design.

## Falsifiability note

Per the user's CLAUDE.md ("post-hoc threshold tuning is forbidden by protocol"),
R-LR-1's NULL verdict stands. R-LR-7 is a NEW pre-registered item with a different
test framework, NOT a re-run of R-LR-1 with a relaxed threshold. The R-LR-1 result
remains a record of "the original encoder-free hypothesis as pre-registered, run at
production scale, did not pass acceptance".
