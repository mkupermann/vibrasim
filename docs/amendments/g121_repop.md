# G121 — Repopulation source (diagnostic for G120's maintenance requirement)

## Question (diagnostic — no pass/fail)
G120 showed empty cells repopulate without active band-clearing. WHERE do those atoms come from — NEW
formation (intrinsic churn) or PRE-EXISTING atoms DRIFTING into the cleared band? If drift-dominated, a
passive structural barrier could replace the active clearing; if formation-dominated, the maintenance is
fundamental churn.

## Result (seed 42; in-band non-carrier atom count over a scaffold-free POST)
| tick | total | NEW (formed after write) | OLD (drifted in) |
|------|-------|--------------------------|-------------------|
| 200  | 11    | 3                        | 8                 |
| 400  | 22    | 4                        | 18                |
| 600  | 33    | 11                       | 22                |
| 800  | 57    | 25                       | 32                |

## Finding — repopulation is a MIX (drift-in + formation), so maintenance is genuinely needed
Both mechanisms contribute. Early it is DRIFT-dominated (8 vs 3, 18 vs 4): the write-time band-clearing
leaves the band emptier than its surroundings, so pre-existing atoms diffuse DOWN that gradient into the
band. Later NEW formation grows (25 of 57 by t=800): vibrations keep binding into fresh atoms inside the
band (intrinsic churn). Net ~56% drift-in, ~44% formation over the window.

Implication for a passive (static) memory: a structural y-barrier around the empty cells could block the
DRIFT-IN half, but NOT the formation churn — so a fully passive static variant is not trivially reachable;
some active suppression (or formation inhibition) remains necessary. This mechanistically confirms the
G120 bound: the matter memory is a MAINTAINED store. The maintenance is irreducible-ish (churn), but
SELECTIVE and NON-DESTRUCTIVE (it never disturbs the written carriers), which is the real break from the
activity deadlock. Logged as the mechanistic close of the matter-memory maintenance question.
