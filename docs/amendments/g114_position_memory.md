# G114 — Is MATTER POSITION a persistent store? (new angle on the memory deadlock)

## Motivation
The memory programme is a closed negative for ACTIVITY-based stores: every bridge/firing/charge write
spreads and leaks (write=leak), and quieting erodes the engram (maintenance=contamination). The
driven-matter discovery (G110-G113) suggests a different representation: an atom DRIVEN to a location and
then RELEASED should STAY there (G110: undriven velocity decays → the atom halts) and, being localized
matter rather than spreading activity, should not contaminate elsewhere. G114 tests whether matter
POSITION is a persistent store — a representation the activity-based deadlock never had.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. WRITE: drive the 4 leftmost atoms +x for DRIVE_T=220 ticks; record each written x.
RELEASE: set their k_vel=0. POST: run POST_T=3000 ticks with NO drive. Read final position.

**Bars (locked):**
- G114a survival: a majority of written atoms are still alive after the 3000-tick POST (both seeds).
- G114b position held: surviving atoms drift < 2 units from their written x over the POST (both seeds).
PASS = G114a AND G114b → matter-position is a persistent, stable store (a new, non-activity memory
representation). PARTIAL = survive but drift. NULL = written atoms decay.

## Result (INCONCLUSIVE — methodological flaw; not counted as PASS/NULL)
| seed | written_x | post_x | "drift" |
|------|-----------|--------|---------|
| 42 | 0.1, 0.1, 0.2, 0.8 | 1.5, 1.5, 19.9, 2.6 | 1.4, 1.4, 19.7, 1.8 |
| 7  | 0.2, 0.5, 0.5, 0.6 | 1.5, 1.4, 21.3, 3.2 | 1.4, 0.9, 20.8, 2.6 |

The script printed "PARTIAL", but that verdict is INVALID and I am not counting it. Two confounds:
1. **Periodic-wrap during WRITE.** At ~0.13 units/tick the 220-tick drive moved each atom ~30 units — a
   FULL LAP of the 30-unit box — so `written_x` landed back near the origin (0.1–0.8), not at a far target.
   The whole premise (atom driven TO a distinct location) failed: it returned to start. The "drift" metric
   (written_x vs post_x) is therefore meaningless.
2. **No identity tracking over 3000 ticks.** Atom slots can be reused as atoms die/form, so a tracked
   index may not follow the same atom across the long POST.

**What IS robust here:** during the no-drive POST, most atoms moved only ~1–2 units over 3000 ticks
(0.1→1.5, 0.2→1.5, 0.8→2.6, …) — i.e. RELEASED atoms are quasi-stationary and hold position, consistent
with G110/G111. That is SUGGESTIVE that matter-position could persist, but this run does NOT establish it:
the write never placed atoms at distinguishable locations (it lapped), and identity wasn't tracked.

**Verdict: INCONCLUSIVE (invalid design).** Clean redo (G115, queued): drive a SHORT sub-box distance
(e.g. 8 units, no wrap), track atoms by k_birth identity, write one location and leave a control location
empty in a CLEARED region, then POST and read presence-by-location. Honest status: matter-position memory
is plausible (released atoms hold position) but UNDEMONSTRATED. Logged rather than over-claimed.
