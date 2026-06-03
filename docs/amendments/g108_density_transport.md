# G108 — Dose-response: does injection DENSITY decide propagate-vs-freeze? (direct test of G107's mechanism)

## Motivation
G107 inferred that a symbol-strength packet fails to transport because it CONDENSES into a stationary
atom at the source ("to send is to freeze"). That was inference from far_energy=0. G108 tests it
directly with a dose-response: launch n moving vibrations into clear space and sweep n. Prediction from
the mechanism: LOW n (below the binding density) propagates and arrives at the far end; HIGH n binds into
atoms at the source and far energy collapses. This is the empirical backbone of the "no controllable
middle regime" unification (too dense → freezes).

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0; cull all free vibrations and clear all atoms (empty space) so the only dynamics are
the injected packet. Inject n moving vibrations (vel +x = 6) at x=4, y=z=centre; propagate D=6 ticks with
NO culling; then measure (a) far-region (x>18) free-vibration energy and (b) atoms formed at the source
(k_count after vs before). Sweep n in {2, 6, 14, 28}. One arm (no seeds-vs-arms cross): both seeds.

**Bars (locked):**
- G108a dose-response present: far energy at n=2 STRICTLY GREATER than at n=28 (both seeds) — density
  suppresses propagation.
- G108b mechanism is binding: atoms_formed at n=28 > atoms_formed at n=2 (both seeds) — the lost packets
  became matter at the source.
PASS = G108a AND G108b → "to send is to freeze" confirmed by dose-response. NULL otherwise.

## Result
| seed | n=2 (far/atoms) | n=6 | n=14 | n=28 |
|------|-----------------|-----|------|------|
| 42   | 0.00 / 0.03 | 0.00 / 0.03 | 0.00 / 0.03 | 0.00 / 0.03 |
| 7    | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |

G108a (far n=2 > far n=28): **False** · G108b (atoms n=28 > n=2): **False** → **VERDICT: NULL**

## Finding — REFUTES my G107 mechanism ("freeze into an atom"); transport closure stands, mechanism does not
The predicted dose-response did not appear. Far-region energy is 0 at EVERY density — even n=2 sparse
packets fail to traverse — and atoms_formed is ≈0 at every density. So the specific G107 mechanism I
proposed ("a dense, symbol-strength packet CONDENSES into a stationary ATOM at the source") is WRONG:
no atoms form, and density makes no difference. I retract "to send is to freeze (into an atom)."

What remains ROBUST (G105/G106/G107/G108): the substrate moves NOTHING a symbol's worth across ~14–18
units — free vibrations and charge both fail, at every density tested, even in cleared space. The carrier
is removed within a few ticks of the source by a mechanism I have NOT identified (not level-4 atom
formation; possibly sub-atomic locking or a free-vibration decay path I did not trace). `move_vibrations`
integrates velocity correctly, so a SURVIVING free packet would reach the far bins — therefore the
packets do not survive; they neither arrive nor become countable atoms.

Honest status: the TRANSPORT CLOSURE is solid and multiply-confirmed; the MECHANISM is open, and my
earlier causal story was over-confident. The co-located spatial codec (G104) is unaffected — it reads at
the source within a tick, before the carrier is lost. This is the session's second self-correction
(after retracting the "transmission" overclaim): an elegant inference, tested directly, refuted by the
data.
