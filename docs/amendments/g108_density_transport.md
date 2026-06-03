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
_(pending run)_
