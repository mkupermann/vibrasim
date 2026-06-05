# NSH-02 — New-Science Hunt step 2: is the characteristic structure size a sharp "magic number"?

## Motivation
NSH-01 found the substrate forms a structure of a characteristic, density-independent size (~100–150
atoms). The native-science question: is that size a SHARP preferred value (a "magic number" — discrete
quantization like fullerene C60 or nuclear shell closures, which WOULD be a striking native law), or
just a broad distribution? A peaked/quantized distribution that we did not design in would be a real
phenomenon to characterize. Honest open search; the analysis (histogram/CV) is standard, the system
and any law are ours.

## Method (`tools/run_nsh02_magic_number.py`)
Fix density at the G43 default (n=300) and run the settling dynamics across MANY seeds (30), recording
the largest bridged structure size each time. Analyze the distribution: mean, std, coefficient of
variation (CV = std/mean), and whether the histogram is unimodal-peaked or broad/multimodal.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **NSH02a (characteristic, not random):** CV ≤ 0.30 across 30 seeds — the size is a characteristic
  value, not broadly scattered.
- **NSH02b (a clear preferred size):** a single dominant mode/peak holds ≥ 40% of runs within ±10% of
  the modal size (a peak, not a flat spread).
- **NSH02c (sharpness ≠ trivial):** report the histogram; flag whether it looks quantized (one sharp
  peak / discrete peaks) vs a smooth broad hump.

PASS = the structure size is a sharply-preferred characteristic value (a candidate native
quantization). NULL = broad/scattered (no magic number — the ~110 was coincidence; honest, look
elsewhere). This is an honest measurement of OUR system; bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** — a reproducible characteristic size (modestly novel)

30 runs (n=300): sizes 98–161, **mean 138.7, std 15.1, CV = 0.109**; modal bin ~135 holds 60% within
±10%. Histogram: a single broad peak over 130–160. NSH02a ✓ (CV ≤ 0.30), NSH02b ✓ (≥40% at the mode)
→ **PASS.**

## Verdict: a native characteristic size — real, but honestly only modestly novel
The substrate forms a closed structure of a **reproducible, density-independent characteristic size
(~140 ± 15 atoms)** — confirmed peaked (CV 0.11), not random. This is a genuine quantitative property
of our own system (no one has studied it). **Honest limits on the novelty:** CV 0.11 is a
*characteristic* size with ±11% spread, NOT a razor-sharp "magic number" (a true quantization would
be CV ~ 0.01 with discrete sub-peaks; the histogram shows one broad hump, no discrete shells). And the
size is mechanistically attributable to **valence-saturated closed shells** — atoms bond up to
`atom_valence` then the shell closes — which follows from binding rules we set, so it is explainable,
not a mysterious new law. So: a real native regularity, characterized from scratch, but it does not
clear the bar for "new science we did not put in." The hunt continues elsewhere (PR-01, the
Neuron-2026-motivated paced-reactivation attack on the actual open problem). No transformer.
