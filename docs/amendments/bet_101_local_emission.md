# BET-101 — Local Emission: Resolve the Write/Contaminate Tension by Locality

Pre-registered: 2026-05-31 (BEFORE any run). The orthogonal fix prescribed by
Pattern 02 (docs/patterns/02). BET-099: emission (n_emit=8) wrote selective
memory but propagated to control. BET-100: n_emit=0 stopped propagation AND the
write. The coupling (emission) is over-loaded — reshape its LOCALITY, not its
gain.

## The lever (root cause found)

`cfg.emit_speed = 30.0` by default — emitted vibrations travel ~15 units/step
(dt=0.5) and cross the entire 30-box instantly. That is the propagation. Reduce
emit_speed so emission reaches bridged NEIGHBOURS (within ~r_2=10) and
co-activates them (creating the co-firing pairs that write the memory) but is
consumed before traversing the ~15-unit gap to the control region.

## Mechanism under test

Identical to BET-099 (firing-coincidence bridge plasticity, neuron_dynamics ON,
n_emit=8 so co-firing pairs still form) EXCEPT **emit_speed = 2.0** (was 30.0).
Local emission → local co-firing → selective write, without long-range leak.

## Acceptance bars (locked pre-run — BET-100's noise-robust metric)

| ID | Criterion | Bar |
|----|-----------|-----|
| T101a | Selective firing (gate) | stim firings >= 3× control during STIM |
| T101b | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| T101c | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| T101d | Negative control FAILS | uniform arm: fraction of those POST checkpoints selective < 0.25 |

PASS = T101a, T101b, T101c hold AND T101d. Thresholds (0.5 / 0.25) carried over
verbatim from BET-100 (pre-registered, not refitted).

PASS = the memory milestone: selective, persistent, propagation-contained
correlation memory, read out by a noise-robust statistic. Confirms Pattern 02
(locality resolves the write/contaminate tension).

If T101b passes but T101d fails (control still selective), emit_speed=2.0 is
still too fast → the locality lever is correct in direction but the substrate's
gap/consumption can't separate write from leak at this scale → reinforces the
consolidated scale-limit finding. No further gain-tuning either way.

## Run design

Identical to BET-099 + emit_speed=2.0. Localized vs uniform arms, same rng_seed.

## RESULT (2026-05-31): NULL — no Goldilocks window at this scale; geometry, not mechanism

Verdict: **NULL**. emit_speed=2.0 (with n_emit=8) gave fire ratio 125 (contained)
but LOC stim-frac 0.00 — no potentiation, same failure as n_emit=0.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T101a selective firing | ✓ | ratio 125. |
| T101b selective potentiation | ✗ | 0.00 — slow emission never reaches neighbours within the charge-decay window, so no co-firing pairs form. |
| T101c persistent recall | ✗ | 0.00. |
| T101d control fails | ✓ (trivially) | nothing latched. |

### The decisive finding — write/contaminate is geometrically inseparable HERE

For emission to WRITE, it must deliver charge to a bridged neighbour within
~tau_membrane (0.5 s ≈ 1 step) so the pair co-fires. Neighbours sit ~5–10 units
away; the control region ~15 units. These distances are COMPARABLE, and charge
decays in ~1 step, so:
- emit_speed=30 (BET-099): reaches neighbours AND control in one step → writes
  AND contaminates.
- emit_speed=2.0 (here) / n_emit=0 (BET-100): reaches neither in time → no write.

There is no emission speed that reaches 5–10 units but not 15 within one decay
window. **Pattern 02's locality fix is correct in principle but cannot be applied
at this scale** — neighbour-distance ≈ control-distance. The separation the fix
needs does not exist in a 30-box with this charge-decay timescale.

### Consolidated finding — confirmed from three angles

Selective WRITE solved; persistent RECALL demonstrated transiently; clean robust
long-horizon selective recall is **bounded by substrate scale/geometry**, now
shown from the coupling angle (write and leak are geometrically inseparable when
neighbour ≈ target distance). This is a falsifiable claim: **give the box enough
room that neighbour-distance ≪ control-distance, and local emission should
separate write from leak.**

### Next direction (BET-102) — test the scale hypothesis directly

Larger substrate: bigger box (e.g. 50³), more vibrations/atoms, stim and control
regions far apart (≫ r_2), moderate local emission (emit_speed ~5–10). If the
selective persistent memory now passes, scale/geometry WAS the limit and the
mechanism is sound. If it still fails, the limit is deeper. Either way: no more
same-scale emission-knob tuning.
