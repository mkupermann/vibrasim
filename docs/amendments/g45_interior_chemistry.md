# G45 — Interior chemistry: does the protected environment assemble its own bound structure?

Pre-registered: 2026-06-02 (BEFORE the run). G43/G44 showed the proto-cell maintains and
regulates a foreign-depleted interior. The next cell-precursor property is whether that
protected interior is a REACTION CHAMBER: does bound structure (atoms, level ≥ 4) assemble
INSIDE the membrane (r < 0.6R, distinct from the shell), and is this enabled by the channel's
protection (more interior assembly with the channel than without)?

## Method
G30 membrane + G32 channel. Continuous ambient regeneration. Count interior bound atoms
(level ≥ 4, alive, r < 0.6R — the shell sits at r≈R, so this excludes it) over the last third
of the run, as a concentration (count / interior volume). Arms: channel ON vs OFF. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G45a | Membrane forms | largest bridged component ≥ 50 atoms (both seeds) |
| G45b | Interior assembles structure (ON) | interior bound-atom count ≥ 5 (mean over last third), channel ON |
| G45c | Channel enables interior assembly | interior atom concentration ON ≥ 1.5× OFF (mean over last third) |

PASS = G45a–c → the protected interior assembles its own bound structure, and the channel's
protection enables it: the proto-cell is a reaction chamber, not just a sealed environment.
A further cell-precursor function. NULL: if G45b fails the interior does not assemble structure
(the proto-cell regulates its environment but is not yet a reaction chamber — an honest
boundary); if G45c fails the channel does not affect interior assembly (assembly is
channel-independent). Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — interior chemistry EXISTS but is channel-independent

| seed | component | interior atoms (ON) | interior atoms (OFF) | ON/OFF |
|------|-----------|---------------------|----------------------|--------|
| 42 | 112 | 16.0 (conc 0.0138) | 16.0 (conc 0.0138) | 1.00 |
| 7 | 110 | 16.9 (conc 0.0136) | 16.9 (conc 0.0136) | 1.00 |

G45a ✓, G45b ✓ (16–17 interior atoms assemble), G45c ✗ (ON/OFF = 1.00). **Verdict: NULL/partial
— and it correctly bounds the proto-cell claim.**

1. **The interior IS a reaction chamber (G45b ✓).** ~16 bound atoms assemble inside r<0.6R
   (distinct from the ~110-atom shell), both seeds. The protected environment hosts its own
   chemistry.
2. **But assembly is channel-INDEPENDENT (G45c ✗, ratio exactly 1.00).** Interior atoms form
   from COMPATIBLE species (the ones that bind); compatible species pass the channel freely
   either way, and foreign species do not bind regardless — so excluding them (channel ON) vs
   not (OFF) leaves interior assembly unchanged.

**Honest decoupling:** the selective channel's role is environmental REGULATION (foreign
exclusion / homeostasis, G43/G44), NOT enabling interior synthesis. The proto-cell both
regulates its interior composition AND hosts an interior chemistry — but these are two
independent functions, not one driving the other. This prevents overclaiming the channel as a
"metabolism enabler"; it is a homeostatic barrier, and the interior chemistry is autonomous.

## Proto-cell, fully characterized (G30→G45)
forms (G30) · seals selectively (G32) · maintains an interior gradient (G43) · regulates back to
set-point after perturbation (G44) · hosts an autonomous interior chemistry (G45b). Next
structural test: membrane SELF-REPAIR (G46) — the structural analog of G44's functional recovery.
