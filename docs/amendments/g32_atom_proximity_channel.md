# G32 — Atom-proximity membrane channel (mechanism fix for G31's leak)

Pre-registered: 2026-06-02 (BEFORE the run). G31 integrated a selective-permeability
channel into the engine and got 4/5 bars: strongly selective (gap +0.65), shell-stable,
but leaky (incompatible reached interior 0.35 > the 0.20 seal bar). Diagnosed cause: the
**fitted-sphere reflector** sits at the mean radius R≈11 and drifts between recomputes,
while the real shell is thick (σ_r≈3, atoms span r≈8–14). Incompatible probes register
inside the *fixed metric* radius in the annulus between the (smaller, drifting) reflector
surface and the metric surface before they are ever reflected.

## Mechanism change (NOT a threshold change)
Replace the smooth fitted-sphere reflector with an **atom-proximity reflector**, selected
by a new `membrane_channel_mode` config field (default `'sphere'` = G31 behaviour, so all
prior runs are byte-identical). In `'atom'` mode `apply_membrane_channel`:
1. Every `membrane_channel_recompute` ticks: re-derive the membrane atom set (largest
   bridged component) and cache the atom **indices** + the fitted **centre** + `f_mem`.
2. Each tick: read the CURRENT positions of those atoms (tracks the breathing shell), and
   for every alive free vibration compute its minimum-image distance to the nearest
   membrane atom. A vibration is reflected when ALL hold: (a) within binding range `r_2`
   of some membrane atom, (b) moving inward (radial velocity toward the cached centre
   < 0), (c) frequency-INCOMPATIBLE with `f_mem` under the substrate's binding band
   `ratio = |f−f_mem|/min(f,f_mem) ∈ [freq_ratio−tol, freq_ratio+tol]`.
   Reflection mirrors velocity about the outward radial normal and reverts position.

Because the real shell's outer atoms sit at r up to ≈14 — OUTSIDE the mean radius — the
atom-proximity reflector guards the full shell thickness, so probes are turned back
before they reach the interior. The metric is UNCHANGED from G31 (fraction reaching the
fixed injection-time radius R0). Same locked bars.

## Bars (locked — identical to G31)
| ID | Criterion | Bar |
|----|-----------|-----|
| G32a | Control transparent | channel OFF: both bands' inward-crossing fraction > 0.5 and \|diff\| < 0.20 |
| G32b | Channel blocks incompatible | channel ON: incompatible inward-crossing fraction < 0.20 |
| G32c | Channel passes compatible | channel ON: compatible inward-crossing fraction > 0.60 |
| G32d | Selective on the REAL shell | channel ON: compatible − incompatible ≥ 0.40 |
| G32e | Shell survives the channel | channel ON: final largest component ≥ 0.6 × channel-OFF final |

PASS = G32a–e. PASS means the atom-proximity reflector seals the emergent shell while
staying selective and non-destabilising — selective permeability is then a real, robust
engine capability on spontaneously-formed membranes. NULL would mean even tracking the
actual atoms cannot seal the irregular shell (e.g. genuine gaps in the lattice let
incompatible probes through, or proximity-reflecting free vibrations shakes atoms loose).
NULL remains a valid finding. No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — all five bars, clean seal

| arm | compatible crossed-in | incompatible crossed-in | final component |
|-----|------------------------|--------------------------|-----------------|
| control (OFF), seed 42 / 7 | 1.000 / 1.000 | 1.000 / 1.000 | 112 / 110 |
| channel ON (atom), seed 42 | 1.000 | **0.000** | 112 |
| channel ON (atom), seed 7  | 1.000 | **0.000** | 110 |

| ID | bar | result | verdict |
|----|-----|--------|---------|
| G32a | control transparent | c=1.000, i=1.000 | ✓ |
| G32b | incompatible < 0.20 | **0.000** | ✓ |
| G32c | compatible > 0.60 | 1.000 | ✓ |
| G32d | selective gap ≥ 0.40 | **+1.000** | ✓ |
| G32e | shell survives (≥0.6× OFF) | 112/110 unchanged | ✓ |

**5/5 bars → PASS.** The atom-proximity reflector turns the emergent ~110-atom shell into
a **cleanly selective** membrane: compatible probes pass completely, incompatible probes
are fully contained (leak 0.000, vs G31's 0.35 fitted-sphere leak), gap +1.000, and the
lattice is untouched (final = peak, identical to the channel-OFF control). The G31→G32
step confirms the diagnosis was correct: the leak was the smooth fitted sphere failing to
cover the thick (σ_r≈3), breathing real shell; reflecting off the actual atoms within r_2
guards the full thickness and seals it.

**Honest scope.** This is an ADDED engine rule (CONCEPT §6.5/§9.4 methodology — naming and
testing the rule a level needs), config-gated and no-op by default, validated against the
spontaneously-formed membrane (not an idealised sphere). The gate reuses the substrate's
OWN frequency-binding band as the selectivity criterion — no new selectivity mechanism.
The chain now: widen the rule (G27) → rich substrate → element ceiling lifts (G28) →
large closed membrane composes (G30) → **the membrane is selectively permeable in the
engine (G32)**. Phase-3 structure + function (containment/selectivity) is closed on the
real substrate. Reusable mechanism surfaced as docs/patterns/atom_proximity_reflector.md.
Next open frontier: memory/recall function on this large lattice (the bridge
firing-coincidence mechanism that was element-count-starved at ~25 atoms).
