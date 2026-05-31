# BET-102 — The Scale Test: Adequate Separation + Integration Time

Pre-registered: 2026-05-31 (BEFORE any run). Directly tests the falsifiable
consolidated claim of BET-099→101: clean long-horizon selective recall fails
because write (emission reaching bridged neighbours) and leak (emission reaching
control) are geometrically inseparable when neighbour-distance ≈ control-distance
and charge decays in ~1 step.

## Hypothesis

If the substrate gives (1) enough spatial room that control-distance ≫
neighbour-distance AND (2) a long enough charge-integration window that SLOW
emission can still write to near neighbours, then local emission separates write
from leak and the selective persistent memory passes. If it still fails, the
limit is deeper than scale.

## Regime (coherent, pre-committed)

- **Bigger box: 50³** (was 30³). Stim/control at 0.25/0.75 → x=12.5 / 37.5,
  periodic separation 25 (≫ r_2=10). Neighbours stay within r_2≈10; control is
  25 away.
- **Longer integration: tau_membrane = 2.0 s** (4 steps, was 0.5). Charge
  persists long enough that slow emission can accumulate at a neighbour and
  co-fire.
- **Moderate local emission: emit_speed = 6.0** (3 units/step). Reaches a ≤10-unit
  neighbour within the 4-step window; the 25-unit control needs ~8 steps →
  vibration consumed/charge decayed before it can latch control.
- More vibrations to fill the bigger box: n_initial 1800, soft_cap 2000,
  n_vibrations_max 8192. Persistence (fusion_bond_block=3), anchoring,
  correlation plasticity, neuron_dynamics all as BET-099. n_emit=8.

## Acceptance bars (locked pre-run — BET-100/101 metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| T102a | Selective firing (gate) | stim firings >= 3× control during STIM |
| T102b | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| T102c | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| T102d | Negative control FAILS | uniform arm: fraction of those POST checkpoints selective < 0.25 |

PASS = T102a–c hold AND T102d. PASS → scale/geometry WAS the limit; the
correlation-memory mechanism is sound given adequate separation + integration.
NULL → the limit is deeper than scale; record as the programme's end-state.

This is the LAST regime experiment of the memory programme either way — PASS
confirms the mechanism, NULL confirms the deeper limit; no further tuning.

## RESULT (2026-05-31): NULL — and the limit is DEEPER than scale: network percolation

Run 1 hit wall budget mid-STIM (POST never reached; big box ~3× slower than
estimated). Re-run with shorter phases (WARMUP 3000, STIM 3000) reached POST.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T102a selective firing | ✓ | fire ratio 577. |
| T102b selective potentiation | ✓ | stim-frac 0.67 — bigger box made the WRITE cleaner (stim pinned 5–6, control lower during STIM). |
| T102c persistent recall | ✗ | POST: stim ~5.5 AND control ~4–5 (>mid). Control latched too. post-frac 0.00. |
| T102d control fails | ✓ | (uniform arm also non-selective.) |

### The deeper finding — percolation, not scale

Adequate spatial separation (25 units ≫ r_2) + longer integration did NOT contain
the memory. During STIM control was lower (2.8–3.8); by POST it had climbed to
~5. The memory SPREAD into control over the stimulation period. Cause: the
substrate is a **connected lattice**, and firing/co-firing **percolates** —
a stim atom fires, co-activates a neighbour, which co-activates ITS neighbour,
and the cascade hops atom-to-atom across the 25-unit gap over thousands of steps.
Spatial distance only DELAYS percolation in a connected graph; it does not
contain it. Bigger box ⇒ cleaner write but the same eventual spread.

So the limit on clean PERSISTENT selective recall is not box size, element count,
drive form, or emission range — it is **connectivity**. A homogeneous, fully
connected substrate cannot hold a spatially-local selective memory at ANY scale;
activity percolates to homogenise it.

### Resolution points at the charter's own architecture

Containment requires **engineered modular compartments** — weakly-coupled
clusters that localise activity — i.e. exactly CONCEPT §4.8's engineered port
topology, which the charter already designates as ENGINEERED (not emergent),
while internals emerge. The memory programme thus converges on the project's
founding design principle: selective memory needs engineered modularity; it will
not emerge from a homogeneous substrate.

### End-state (per pre-registration: no more regime tuning)

This closes the spontaneous-substrate memory programme (BET-089→102) with a
consolidated, defensible finding. See docs/amendments/MEMORY_PROGRAMME_SUMMARY.md.
The honest next direction is architectural (engineered modular compartments /
ports), not another regime knob — a strategic decision, surfaced to Michael.
