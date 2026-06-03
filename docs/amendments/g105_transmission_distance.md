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
_(pending run)_
