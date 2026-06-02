# G31 — Selective permeability INTEGRATED into the engine, tested on the real emergent membrane

Pre-registered: 2026-06-02 (BEFORE the run). G25 proved a local frequency-gated
reflection rule makes a *Fibonacci-sphere* membrane selectively permeable. The honest
open question (G25 doc, "NEXT"): does it compose with a **real, spontaneously-formed**
shell — the ~110-atom emergent membrane from G30 — when implemented as a config-gated
step inside `world/physics.py`, not a standalone toy?

## What is added (named per CONCEPT §6.5/§9.4 methodology)
`apply_membrane_channel(world, dt)` — a new tick step, **no-op when
`membrane_channel_k == 0`** (default), so all prior runs are unchanged. When enabled:
1. Every `membrane_channel_recompute` ticks, derive the membrane from the ACTUAL
   structure: largest bridged atom component → least-squares sphere fit → centre C,
   radius R; characteristic frequency `f_mem` = mean frequency of those atoms. Cache it.
2. Each tick, for every alive free vibration that crossed the shell surface |r−R|
   inward this step, reflect it (velocity mirrored about the radial normal, position
   reverted) UNLESS it is frequency-compatible with the membrane under the substrate's
   OWN binding band: `ratio = |f−f_mem|/min(f,f_mem) ∈ [freq_ratio−freq_tol,
   freq_ratio+freq_tol]`. Compatible vibrations pass; incompatible are contained.

This reuses the substrate's existing compatibility primitive as the gate — no new
selectivity mechanism, only a barrier that consults the binding rule at the shell.

## Protocol
Build the G30 rich substrate (broad band freq_ratio=0.05, tol=0.045; atom_valence=3,
fusion_bond_block=2, curvature_k=2.0, atom_repulsion_k=1.0), let the ~110-atom shell
form (200 ticks). Then inject two bands of tracer free vibrations launched inward from
outside the shell: COMPATIBLE (ratio to f_mem inside the band) and INCOMPATIBLE
(ratio far outside). Run 120 more ticks with the channel OFF (control) and ON, measuring
per band the fraction of tracers that achieve ≥1 inward crossing of the shell surface.
Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G31a | Control transparent | channel OFF: both bands' inward-crossing fraction > 0.5 and \|diff\| < 0.20 |
| G31b | Channel blocks incompatible | channel ON: incompatible inward-crossing fraction < 0.20 |
| G31c | Channel passes compatible | channel ON: compatible inward-crossing fraction > 0.60 |
| G31d | Selective on the REAL shell | channel ON: compatible − incompatible ≥ 0.40 |
| G31e | Shell survives the channel | channel ON: final largest component ≥ 0.6 × the channel-OFF final component |

PASS = G31a–e. PASS means selective permeability is now a real engine capability that
composes with the emergent membrane and does not destabilise it. NULL would mean the
rule that worked on the idealised sphere does NOT hold on the irregular emergent shell
(e.g. the rough surface makes "crossing" ill-defined, or reflection shakes the lattice
apart). NULL is a valid finding. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — strongly selective, not a tight seal

| arm | compatible crossed-in | incompatible crossed-in | final component |
|-----|------------------------|--------------------------|-----------------|
| control (channel OFF), seed 42 / 7 | 1.000 / 1.000 | 1.000 / 1.000 | 112 / 110 |
| channel ON, seed 42 | 1.000 | **0.255** | 112 |
| channel ON, seed 7  | 1.000 | **0.450** | 110 |

| ID | bar | result | verdict |
|----|-----|--------|---------|
| G31a | control transparent (both >0.5, \|diff\|<0.20) | c=1.000, i=1.000 | ✓ |
| G31b | incompatible < 0.20 | 0.353 (mean) | ✗ |
| G31c | compatible > 0.60 | 1.000 | ✓ |
| G31d | selective gap ≥ 0.40 | **+0.647** | ✓ |
| G31e | shell survives (≥0.6× OFF) | 112/110 unchanged | ✓ |

**4/5 bars. Verdict: NULL/partial.** The channel, implemented in the real engine
(`apply_membrane_channel`, no-op by default), makes the emergent shell **strongly
selective** — compatible probes pass completely, incompatible are reflected with a
+0.65 gap — and does **not** destabilise the lattice (G31e clean). But it is **not a
tight seal**: ~25–45 % of incompatible probes still reach the interior, missing the
locked <0.20 bar. Honest, per discipline: this is recorded as NULL, not retuned.

**Diagnosed leak mechanism (honest).** The reflector uses a single least-squares
**fitted-sphere radius** R, recomputed every 20 ticks. The emergent shell is not a rigid
object — it *breathes* (σ_r/R ≈ 0.27, so atoms span r ≈ 8–14 around the mean R ≈ 11, and
the fitted R itself drifts tick-to-tick). When R grows at a recompute, probes sitting in
the outer band (r ∈ (R+1.5, R+6)) are retroactively engulfed (r < R_new) without ever
triggering an inward *crossing*, so they are never reflected. The per-seed spread
(0.255 vs 0.450) tracks how much each shell's R wandered. The idealised-sphere rule
(G25, leak 0.000) does not transfer cleanly to the irregular, dynamic emergent geometry
— exactly the composition risk this BET was pre-registered to test.

**Next (G32, mechanism change — NOT threshold change):** replace the fitted-sphere
reflector with an **atom-proximity reflector** — an incompatible free vibration is
reflected when it comes within binding range (r_2) of any *actual* membrane atom, off
that atom's local outward normal. This tracks the real, breathing, irregular surface
instead of a smooth approximation, and removes the "R grew and swallowed the probe"
artifact. Same locked bars (G31a–e).
