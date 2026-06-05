# PR-01 — Paced reactivation (Neuron 2026) vs the memory deadlock

## Incorporating Michael's research (Neuron 2026, Oxford slow-oscillation paper)
The paper Michael gave: brief slow-oscillation BURSTS pace and COORDINATE offline reactivation, and
reactivation strength predicts retention. Our substrate's memory deadlock is "maintenance =
contamination": continuous re-activation keeps the engram alive but the same charge cascade
contaminates the control region (G94/G96). I earlier dismissed pacing as inert — wrongly, because the
seal I tested acted on the VIBRATION channel, whereas reactivation/replay runs on the CHARGE channel,
which IS the contamination channel. PR-01 tests the paper's actual mechanism on that channel: reactivate
the engram in BRIEF BURSTS separated by quiet GAPS, and ask whether the gaps let the charge cascade
DISSIPATE before it contaminates control — giving selective persistent memory where continuous
reactivation could not. This both honors the research and is a genuinely new attempt at our open
problem; the analysis is standard, the mechanism-result for our system would be new.

## Method (`tools/run_pr01_paced_reactivation.py`)
Reuse the G94 quiet-substrate engram protocol (WARMUP cull+blank → STIM writes a localized engram →
capture engram atom indices). POST phase, three arms, NO control culling (let contamination happen):
- **none:** no reactivation (engram decays — reactivation is necessary).
- **continuous:** every POST tick inject a small charge into the engram atoms.
- **paced:** inject the SAME total charge but in bursts — `BURST` ticks on, `GAP` ticks off (a slow
  rhythm), so each burst re-pins the engram and each gap lets the cascade settle.
Readout (G94 set-based): engram strong-bridge persistence vs control strong-bridge count. Seeds 42 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **PR01a (reactivation is necessary):** 'none' engram bridge-persist < 0.30, both seeds.
- **PR01b (paced gives SELECTIVE persistence):** paced engram bridge-persist ≥ 0.40 AND paced control
  strong-bridge count ≤ 2, both seeds.
- **PR01c (pacing beats continuous on selectivity):** paced control count ≤ continuous control count − 2
  (the quiet gaps reduce contamination), both seeds.

PASS = paced reactivation yields the selective persistent memory that continuous reactivation cannot —
the first crack in the deadlock, motivated by the Neuron paper. NULL if PR01b fails (paced also
contaminates or the engram still decays — pacing does not separate write from leak on the charge
channel either). Honest either way. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL — the deadlock survives the paper's mechanism too

| seed | mode | engram persist | control bridges |
|------|------|----------------|-----------------|
| 42 | none / continuous / paced | 0.17 / 0.17 / 0.17 | 3 / 5 / 5 |
| 7  | none / continuous / paced | 0.10 / 0.20 / 0.20 | 13 / 17 / 14 |

PR01a ✓ (none decays — reactivation necessary), **PR01b ✗ (paced persist 0.17–0.20 < 0.40, control
5–14 > 2), PR01c ✗ (paced ≈ continuous on contamination) → NULL.**

**Honest finding — pacing does not separate write from leak on the charge channel either.** Faithfully
implementing the Neuron-2026 mechanism (brief reactivation bursts + quiet gaps) on the engram does NOT
crack our deadlock: (1) the engram still decays to 0.17–0.20 in every arm — re-firing the engram atoms
does NOT stop their EROSION (G93: the atoms lose members in the quiet substrate; firing ≠ feeding their
survival), and (2) the quiet gaps do not meaningfully reduce contamination (control 5/14 ≈ continuous
5/17 — inconsistent, within noise) — the charge cascade reaches control even from brief bursts.

**What this means (incorporating Michael's research honestly).** The Neuron-2026 slow-oscillation
finding is real and our substrate even reproduces its premise (reactivation is necessary — 'none'
decays). But the biological mechanism does NOT transfer to our deadlock, because our block is
**structural (atom erosion + charge-cascade coupling)**, not a reactivation-COORDINATION problem that
pacing fixes. Pacing coordinates *which* memories replay together; it does not feed eroding atoms or
decouple the shared charge channel. So the paper vindicates our replay design but is not the key to
this deadlock — recorded honestly, not forced. Bars held; no retuning. No transformer.
