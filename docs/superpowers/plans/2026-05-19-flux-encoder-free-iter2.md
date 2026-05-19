# Encoder-Free Audio — Iteration 2 (R-13 / R-14 / R-LR-8)

> **Origin:** R-LR-1 (2026-05-19) showed substrate forms emergent topology from raw audio (1358 nodes, 3188 bridges) but the F2 synthesis-bank baseline dominates output regardless of substrate state. Test framework asked the wrong question of the wrong observable.
>
> **User mandate 2026-05-19 04:25:** "Was können wir verbessern?" Answer: not cube size (synthesis is the bottleneck, not compute). Three pre-registered items address the actual diagnosis.

## R-13 — Bridge-Weight Spectrum: Substrate-Internal Observable

Goal: bypass the synthesis layer entirely. Measure substrate's learning directly via its **internal topology**: the joint distribution of (node-frequency, bridge-weight) across the alive bridges.

**Rationale:** R-LR-1 produced 3188 alive bridges in the trained substrate vs 0 in the no-input control. The bridges *exist* and have weights — what they encode is the question. If they encode audio statistics, their distribution should differ from a substrate exposed to a different (e.g., random-amplitude) input stream. The synthesis layer is irrelevant to this measurement.

**Pre-registered acceptance for R-13** (locked thresholds, no retuning):

- `tests/flux/test_bridge_spectrum.py::test_bridge_spectrum_observable_constructs PASSES` — NEW: load substrate state from R-LR-1's saved snapshot (or a synthetic equivalent), extract `(freq, weight)` pairs for all alive bridges, assert the histogram has at least 32 bins populated and that the distribution is normalised.
- `tests/flux/test_bridge_spectrum.py::test_bridge_spectrum_zero_on_empty_substrate PASSES` — NEW: on a substrate with 0 nodes, the spectrum function returns an empty distribution (not NaN, not error).
- `tests/flux/test_bridge_spectrum.py::test_bridge_spectrum_differs_under_different_audio PASSES` — NEW: run two short (50k-tick) encoder-free substrates, one on English audio Stage 1, one on white-noise audio of matched RMS. Assert KL divergence between their bridge-weight spectra > 0.1 (distinguishing structure formed). 50k ticks fits in postflight's 30-min cap.
- `tests/flux/test_conservation.py PASSES` — T1 robust.
- `tests/flux/test_crystallization_robustness.py PASSES` — T3 robust.

Time budget: 4 hours.

## R-14 — Synthesis Sensitivity Sweep

Goal: characterise how F2 synthesis output depends on substrate state, parametrised over (Q, gain). Pre-register thresholds at which synthesis becomes sensitive enough that babble from a 1358-node substrate is statistically distinguishable from babble from an empty substrate.

**Rationale:** R-LR-1 showed both trained (1358 nodes) and empty (0 nodes) substrates produced babble that was KL-indistinguishable (0.000001). This means synthesis is dominated by its own intrinsic resonator-bank response, not by substrate firings. Lower-Q resonators decay faster; higher gain makes firing impulses dominate baseline.

**Pre-registered acceptance for R-14:**

- `tests/flux/test_synthesis_sensitivity.py::test_synthesis_baseline_with_empty_substrate_has_low_energy PASSES` — NEW: at the chosen (Q, gain) combo, the empty-substrate synthesis output RMS is < 0.1× the trained-substrate synthesis output RMS.
- `tests/flux/test_synthesis_sensitivity.py::test_synthesis_with_firings_dominates_baseline PASSES` — NEW: at the chosen (Q, gain) combo, synthesis driven by 100 firings/sec produces output whose dominant FFT peak is at the firing-pattern frequency (within ±20%), not at the resonator-bank's natural resonance.
- The R-14 session locks ONE (Q, gain) combination from the sweep `[Q ∈ {3, 5, 10, 30}, gain ∈ {1, 5, 25, 100}]` — 16 combos. Pick the smallest Q and gain that pass both tests above. Document the choice in phase-log.
- `tests/flux/test_synthesis.py PASSES` — F2 baseline synthesis unit tests (the original R-3 ones) still pass for the existing Q=10 gain=1 default. The new combo is an ADDITIONAL config, not a replacement.

Time budget: 4 hours.

## R-LR-8 — Encoder-Free Long-Run with Both New Observables

Goal: re-run R-LR-1 but evaluate via R-13's bridge-spectrum AND R-14's tuned synthesis. PASS verdict if EITHER observable shows learning.

**Setup:** encoder-free raw injection, 1.8M ticks, English corpus from R-7. Same as R-LR-1 except:
- Substrate state snapshotted to disk every 100k ticks so R-13 spectrum can be computed offline
- Synthesis run with R-14's tuned (Q, gain) instead of defaults
- TWO control substrates run alongside: matched-wallclock no-input, AND matched-wallclock white-noise input (so we have two baselines)

**Pre-registered acceptance for R-LR-8 (locked thresholds, no retuning):**

- `tests/flux/test_R_LR_8_acceptance.py::test_bridge_spectrum_audio_vs_white_noise PASSES` — NEW: KL divergence between (trained on English) bridge-weight-spectrum and (trained on matched-RMS white noise) bridge-weight-spectrum > 0.5. (Bigger threshold than R-13's 0.1 because we have 1.8M-tick scale, not 50k.)
- `tests/flux/test_R_LR_8_acceptance.py::test_synthesis_audio_vs_no_input PASSES` — NEW: with R-14's tuned synthesis, KL between (trained on English) babble MFCC and (no-input control) babble MFCC > 0.001. (Much weaker threshold than R-11 because the synthesis-baseline is finally a fair baseline at this Q/gain.)
- LOGBOOK entry with both KL numbers and the (Q, gain) used. Cross-reference R-LR-1's KL=0.000001 to show the improvement.

R-LR-8 PASS condition: EITHER of the two tests above PASS (OR semantics, not AND). The two observables address different question — internal topology vs external babble — and either is publishable independently.

Time budget: 24 hours.

## Why this is more honest than further parameter scaling

- **Cube enlargement** (160×80×20): 8× compute cost, addresses substrate-density, but the synthesis bottleneck remains. Not the bottleneck.
- **Longer ticks** (10M): R-LR-1 had 3188 alive bridges already; more ticks → more bridges, but diminishing return, and synthesis still dominates.
- **R-13 + R-14** address the actual diagnosed bottleneck (synthesis sensitivity + observable choice). Cheap iterations (~4h each), high information value.

## Dependencies

R-13 and R-14 can run in either order (independent). R-LR-8 depends on both (uses R-13's spectrum function + R-14's tuned synthesis).

R-LR-2 / R-LR-3 / R-LR-4 from iter-1 continue running in parallel as long-run datapoints; their results will inform whether the issue is truly synthesis-only or something deeper.
