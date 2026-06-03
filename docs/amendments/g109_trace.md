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
_(pending run)_
