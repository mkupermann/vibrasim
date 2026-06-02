# G52 — Fluid membrane probe: does atom mobility enable self-repair without dissolving the shell?

Pre-registered: 2026-06-02 (BEFORE the run). The capstone (FINDINGS_SUMMARY) names positional
RIGIDITY as the blocker for repair/metabolism/division, and a FLUID membrane as the needle-mover.
The substrate's rigidity has two sources (verified in code): bonds are PERMANENT (decay_bridges
only removes a bridge when an atom dies — no spontaneous breaking) and membrane atoms are
STATIONARY (node_thermal_speed=0 in the G30 config). This BET probes the cheapest fluidity knob —
atom MOBILITY (node_thermal_speed>0) — to test whether mobility alone lets a wound heal while the
membrane stays intact, or whether bond-turnover is also required.

## Method
G30/G46 protocol. Arms: node_thermal_speed ∈ {0.5 (mobile), 0.0 (rigid, = G46)} × {wounded,
unwounded}. Wounded: form → wound → repair window → healing (component regrowth). Unwounded:
form → observe → persistence (final/peak). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G52a | Mobile membrane stays intact | mobile unwounded: final/peak ≥ 0.7 (both seeds) — fluidity doesn't dissolve it |
| G52b | Mobility heals the wound | mobile wounded: healed (recovered−post)/(N0−post) ≥ 0.3 (both seeds) |
| G52c | Rigid control does NOT heal | rigid wounded: healed < 0.1 (both seeds; reconfirms G46) |

PASS = G52a–c → atom mobility gives a fluid membrane that self-repairs while staying intact:
the rigidity ceiling is broken by mobility alone. NULL: if G52b fails, mobility is insufficient
(atoms are tethered by permanent bonds, so they vibrate but cannot flow into a wound) → fluidity
requires BOND TURNOVER, not just mobility — narrowing the needle-mover to a specific new mechanism.
If G52a fails, mobility dissolves the membrane (fluidity/stability trade-off). Honest either way.
No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — mobility is insufficient; rigidity = PERMANENT BONDS

| seed | mobile wounded heal | mobile unwound persist | rigid wounded heal |
|------|---------------------|------------------------|--------------------|
| 42 | 0.00 | 1.00 | 0.00 |
| 7 | 0.00 | 1.00 | 0.00 |

G52a ✓, G52b ✗, G52c ✓ → **NULL.** Atom mobility (node_thermal_speed=0.5) does NOT heal the
wound (0.00) and does not dissolve the membrane (persist 1.00) — it changes nothing, because the
atoms are TETHERED by permanent bonds. They vibrate in place but cannot flow into a wound.

**Precise localization of the needle-mover:** the membrane's rigidity is PERMANENT BONDS
(decay_bridges removes a bridge only when an atom dies; there is no spontaneous breaking), NOT
stationarity. A fluid, self-healing membrane therefore requires BOND TURNOVER — a mechanism for
bonds to break and reform so the network can remodel and atoms can flow into a wound. That is a
specific new substrate primitive, the defined strategic next step (G53).
