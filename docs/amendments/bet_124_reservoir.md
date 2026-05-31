# BET-124 — Emergent Generalization via Substrate Reservoir + Online Learning

Pre-registered: 2026-05-31. Goal (Michael): the substrate must GENERALIZE BY
ITSELF and LEARN ONLINE (every answer updates it), no transformer, new substrate
math. Radical substrate-native method: the substrate's random modular connectivity
+ nonlinear activation IS a random nonlinear feature map phi(x)=tanh(Rx); a LINEAR
readout on phi generalizes to unseen inputs and trains ONLINE via recursive least
squares. Generalization emerges from the substrate's own projection — nothing is
hand-designed (contrast BET-122's hand-built VSA).

## Task (held-out compositional generalization)
A 10x10 grid of discrete inputs (a,b), value-coded to [-1,1], target a smooth
nonlinear COMPOSITIONAL function y=f(a,b). Train on a random 60% of the (a,b)
CELLS, ONE AT A TIME (online); test on the held-out 40% (novel combinations).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T124a | Reservoir generalizes | held-out R^2 >= 0.85 on UNSEEN (a,b) combinations |
| T124b | Linear cannot | linear-readout baseline held-out R^2 < 0.40 |
| T124c | Online learning | training MSE decreases markedly from first to last example |
| T124d | Clear gap | reservoir held-out R^2 - linear held-out R^2 >= 0.4 |

PASS = T124a-d. PASS = generalization to novel combinations EMERGES from the
substrate's own nonlinear features (not hand-design), learned ONLINE — the radical
substrate-native step toward a self-generalizing, continually-learning system.
Honest scope: this is interpolative/functional generalization; systematic symbolic
generalization is the next frontier (BET-125+).

## RESULT (2026-05-31): PASS

| metric | value |
|--------|-------|
| reservoir held-out R^2 (novel (a,b) combos) | **0.999** |
| linear-readout held-out R^2 | 0.312 |
| online MSE first -> last example | 0.077 -> 0.0002 |
| T124a (reservoir R^2>=0.85) | PASS |
| T124b (linear R^2<0.40) | PASS |
| T124c (online MSE drops >=2x) | PASS |
| T124d (gap >=0.4) | PASS (0.687) |

The substrate's own random modular projection + nonlinear activation
phi(x)=tanh(Rx) turns un-generalizable raw inputs into features on which a
LINEAR readout generalizes to 40 (a,b) combinations it NEVER saw — and it was
learned strictly ONLINE, one example at a time, via recursive least squares
(every example updates Wout and P in O(D^2), no replay, no backprop, no
transformer). The matched linear baseline (same online RLS, raw features)
MEMORIZES and FAILS the held-out cells (R^2=0.312). Generalization is the
substrate's projection, not the readout's.

**Honest scope.** This is INTERPOLATIVE / functional generalization on a smooth
target: random features tile the input space, so unseen *interpolated* points are
covered. It is NOT yet systematic/symbolic generalization (recombining known parts
into structurally-novel wholes the way language needs). That is the next frontier
— BET-125+: feed the reservoir COMPOSED codes (VSA-bound role-filler pairs from
world/vsa.py) so the nonlinear features see structure, and test held-out *symbol
combinations*, not held-out *interpolation points*. Banked here: the substrate now
has a native, online, self-generalizing readout — the engine the language layer
sits on.
