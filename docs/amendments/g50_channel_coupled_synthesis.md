# G50 — Channel-coupled synthesis: does uptake increase interior structure assembly?

Pre-registered: 2026-06-02 (BEFORE the run). G45 found interior chemistry exists (~16 atoms) but
is channel-INDEPENDENT (plain channel: ON/OFF=1.00). G49 found the uptake trap does not raise
FREE nutrient concentration — likely because trapped compatible species are CONSUMED by binding.
The right test: does the uptake trap, by concentrating bindable material, increase interior
STRUCTURE (bound atoms)? That would be channel-coupled synthesis — turning the G45c boundary into
a positive via the uptake mechanism. This is the decisive test for the proto-cell's metabolic
potential (and for whether the structural thread continues or consolidates).

## Method
G30 membrane + atom-proximity channel, continuous ambient pressure. Count interior bound atoms
(level ≥ 4, r < 0.6R) over the last third. Arms: uptake (trap compatible) vs plain (G32) vs
channel-off. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G50a | Membrane forms | largest bridged component ≥ 50 (both seeds) |
| G50b | Uptake increases interior assembly | uptake interior atom count ≥ 1.5× plain (both seeds) |

PASS = G50a–b → the uptake channel concentrates bindable nutrient and drives MORE interior
structure: channel-coupled synthesis (a metabolic precursor function), resolving the G45c
boundary via active uptake. NULL: if G50b fails interior assembly is saturated / supply-
independent (the channel cannot drive synthesis) — an honest ceiling, and the signal to
consolidate the proto-cell thread. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — interior assembly is supply-independent (no channel-coupled metabolism)

| seed | component | uptake | plain | off | uptake/plain |
|------|-----------|--------|-------|-----|--------------|
| 42 | 112 | 16.0 | 16.0 | 16.0 | 1.00 |
| 7 | 110 | 16.9 | 16.9 | 16.9 | 1.00 |

G50b ✗ → **NULL.** Interior bound-atom count is IDENTICAL (16.0 / 16.9) across uptake, plain,
and channel-off — the channel/uptake has no effect on interior assembly. The ~16-atom interior
chemistry is fixed by local geometry and binding, NOT driven by nutrient supply. **There is no
channel-coupled metabolism:** the proto-cell regulates its environment (G43/G44) but its interior
synthesis is an autonomous, saturated background process the membrane does not control.

**Consolidation signal.** G45–G50 (six experiments probing interior-synthesis coupling, self-
repair, uptake, metabolism) are ALL NULL. The proto-cell's core positives (G30–G44: forms, seals,
regulates) are solid; its extensions hit a consistent ceiling — the membrane is a persistent,
self-regulating, but STATIC and NON-METABOLIC compartment. The structural thread is consolidated
(see PROTOCELL_SUMMARY); membrane-channel extensions are closed.
