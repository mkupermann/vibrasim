# G95 — Structural memory: read the largest CONNECTED engram component, not bridge counts

## Pre-registration (locked BEFORE run)
G94 showed bridge consolidation is non-selective by COUNT — control carries 2–18 persistent strong
bridges in every arm. But a count is blind to topology. The spatially-tight stim injection
(inject_tight, small sigma) clusters atoms that bridge into ONE connected mesh, whereas control
contamination arrives via drifted/diffuse vibrations that should form SCATTERED isolated bridges.
Read STRUCTURE: the size (atom count) of the largest connected component of STRONG bridges
(strength>=5) within each region, tracked into POST.

Same write as G91/G94: quiet + disconnected (boundary=15) + refractory (0.5) + consolidation (4.0),
n=6 write at the stim centre. No POST maintenance (G94 showed it doesn't help and worsens control).

**Bars (locked):**
- G95a stim forms a connected engram : stim largest-component >= 4 atoms at STIM_END (both seeds)
- G95b engram persists                : stim largest-component >= 3 atoms at horizon (both seeds)
- G95c selective by topology          : control largest-component <= 2 at horizon AND
                                         (stim_horizon − control_horizon) >= 2 (both seeds)
PASS = G95a AND G95b AND G95c → structural memory is selective + persistent where synaptic-count is not.
Else NULL/PARTIAL.

## Result
_(pending run)_
