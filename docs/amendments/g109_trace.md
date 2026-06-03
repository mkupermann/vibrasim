# G109 — Trace a moving packet: what actually removes the carrier? (diagnostic)

## Motivation
G108 refuted my "freeze into an atom" mechanism and left the real cause UNIDENTIFIED: a moving packet
neither reaches the far end nor forms atoms. Rather than guess again, G109 traces the EXACT injected
slots tick-by-tick (alive count, mean/max x, atoms formed) to see what happens.

## Expectations (pre-registered, diagnostic — no pass/fail)
Distinguish three hypotheses by the trajectory:
- **H1 velocity not applied:** mean_x stays ≈4 across ticks (the injected vel is overwritten/ignored).
- **H2 moves then dies:** mean_x rises (packet travels) but alive→0 before reaching the far bins.
- **H3 removed at source:** alive→0 at t=1 with mean_x≈4 (consumed/locked immediately).
Report which the data shows; that is the corrected mechanism for the transport closure.

## Result
Representative trace (inject x=4, vx=6, dt=0.5 → a CONSERVED velocity would advance x by 3.0/tick):
```
seed 42 n=14:  t=1 alive=14 mean_x=4.0   ...   t=8 alive=14 mean_x=4.7   atoms=0 throughout
seed 42 n=2 :  t=1 alive= 2 mean_x=3.7   ...   t=8 alive= 2 mean_x=4.4   atoms=0 throughout
```
Both seeds, both densities: alive count is CONSTANT (no deaths), atoms_formed stays 0, and mean_x drifts
only ~0.1/tick (3.7→4.4 over 8 ticks) — versus the 3.0/tick a conserved vx=6 would give.

## Finding — the carrier is QUASI-STATIONARY (diffusive), not ballistic: velocity is not conserved
The packet neither dies (H3 wrong) nor travels-then-dies (H2 wrong): it STAYS ALIVE and barely moves
(H1). An injected directional velocity of 6 yields ~0.1 units/tick of net drift — ~97% of the velocity is
gone each tick. Free vibrations do not propagate ballistically; they jitter near the injection site
(thermal/diffusive motion — the vibration dynamics do not conserve an injected momentum). Over the few
ticks before readout they move <1 unit, far short of the 14–18 units to the far region — so nothing
arrives, at any density.

**This is the MEASURED mechanism behind the whole transport closure (G105–G108), replacing both earlier
guesses:** not "absorbed en route", not "condenses into an atom" (G107, retracted), not "removed at the
source" — the carrier simply does not travel, because the medium does not sustain directional motion of a
free vibration. It also explains why the co-located codec works: a symbol read at its injection site
(G104) is read exactly where it stays. To transport, one would need a carrier the medium DOES move
coherently — a propagating bound structure (bridge/charge front along a built conduit), which G106 showed
the bare bridge graph does not provide. Transport closed; mechanism now identified and measured.
