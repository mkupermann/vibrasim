# G105 — Is it transmission over DISTANCE, or just co-located readout? (honesty check)

## Motivation
The G97–G104 channel injects symbols and reads the free-vibration grid at the SAME location, right after
injection. Calling that "transmission" / "transported by the substrate" (G104) may overclaim: it could be
local inject-and-read, not propagation across distance. This experiment tests genuine transmission:
encode the symbol across channels arranged along Y, inject at the LEFT edge with a +x velocity, let the
vibrations PROPAGATE across the box, and decode at the far RIGHT end. If far-end decode works, it is a
real transmission line; if only co-located decode works, the docs must be corrected to "local spatial
readout," not transmission.

## Pre-registration (locked BEFORE run)
K=4 channels along Y at y = linspace(8,22,4), injected at x=4 with velocity (+emit_speed,0,0). After
injection, propagate D=4 ticks (no reset) so vibrations travel in +x. Read the Y-binned vibration grid
of ONLY the far region x>18 (downstream of injection). Decoder (multiclass linear, per-symbol reset
after readout) calibrated on random traffic, held-out test. Compare to a CO-LOCATED control that reads
the whole box immediately (the G97-style readout).

**Bars (locked):**
- G105a transmission over distance: far-region (x>18) decode >= 0.85 both seeds → genuine transmission.
- G105b control: co-located full-box decode >= 0.85 both seeds (sanity that the symbol is encoded).
If G105a holds → "transmission" language is justified. If only G105b holds → CORRECT the G104/summary
wording to "co-located spatial readout," not transmission over distance. Chance = 0.25.

## Result
| seed | far-end (x>16) | co-located (full box) |
|------|----------------|-----------------------|
| 42   | 0.24 (chance)  | 1.00 |
| 7    | 0.29 (chance)  | 1.00 |
(K=4, chance 0.25, n=240)

G105a (transmission over distance): **False** · G105b (co-located sanity): **True** → **VERDICT: PARTIAL**

## Finding — it is CO-LOCATED spatial readout, NOT transmission over distance (correcting my own wording)
The symbol is perfectly encoded and recovered at the injection site (co-located 1.00) but the far region
decodes at CHANCE (0.24, 0.29). Even with a +x launch velocity, the free vibrations do not arrive
downstream carrying the symbol — they are absorbed into atoms / damped locally within a few ticks rather
than propagating ballistically across the box. The substrate does NOT transport a signal across distance.

**Honest correction to the communication claim.** The G97–G104 "channel" is a SPATIALLY-MULTIPLEXED,
CO-LOCATED input/output interface: a symbol written as a localized excitation is recoverable in the same
tick at the SAME site by a linear decoder. The verbatim-text result (G104) stands — you can encode text
as substrate states and read it back exactly — but it is encode-and-read-back at one place, NOT
transmission/transport over a distance. Wording like "transmitted through / transported by the substrate"
overclaims and is corrected to "co-located spatial codec / addressable spatial I/O" in g104,
COMMUNICATION_SUMMARY, SYNTHESIS, and the pattern. This is the kind of claim the honesty discipline exists
to catch: the demonstration is real but smaller than "transmission" implied.
