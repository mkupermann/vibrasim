# G77 — Substrate as a reservoir: temporal XOR (learning without writable memory)

Pre-registered: 2026-06-03 (BEFORE the run). The memory deadlock is fundamental, but RESERVOIR
COMPUTING needs no writable internal memory: a fixed nonlinear dynamical system transforms inputs
into a high-dimensional state that a simple LINEAR readout can classify. The substrate is a proven
nonlinear dynamical system (G74/G75). Decisive test: temporal XOR — encode 2 input bits as
presence/absence of foreign-influx bursts in two time windows, read the interior concentration
trajectory as features, fit a LINEAR readout to the XOR label. XOR is NOT linearly separable in the
inputs, so a linear readout can only solve it if the substrate's NONLINEARITY built the needed
representation. If it does, the substrate is a usable reservoir — a real path to a responsive/learning
system on the physics, sidestepping write=leak. (Honest: reservoir computing is established — Jaeger/
Maass; the novelty would only be using THIS physics substrate as the reservoir.)

## Method
Proto-cell (channel ON). 4 patterns (00,01,10,11); bit=1 → inject a burst in that window. Sample the
interior concentration over the readout window → feature vector. Least-squares linear readout to XOR
labels; check it classifies all 4 correctly. Control: verify XOR is NOT separable from the raw 2-bit
inputs (sanity that the task needs nonlinearity). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G77a | Reservoir solves XOR | linear readout on the substrate state classifies all 4 patterns correctly, both seeds |
| G77b | Task needs nonlinearity (control) | XOR is NOT linearly separable from the raw 2-bit inputs, both seeds |

PASS = G77a–b → the substrate's nonlinear dynamics make a non-linearly-separable task linearly
readable: it is a usable RESERVOIR. Learning lives in an external linear readout; the substrate
supplies the nonlinear feature map — NO writable internal memory needed. A genuine path to a
responsive/learning system on the physics, bypassing the memory deadlock. NULL = the readout cannot
solve XOR (the substrate state does not encode the input interaction separably). Honest either way.
No post-hoc threshold tuning.

## RESULT (2026-06-03): INVALID — overfitting artifact, NOT a real result

preds=[-0.5,0.5,0.5,-0.5], margin 0.5, both seeds — a SUSPICIOUSLY perfect XOR fit. The reason: the
readout used ~12 trajectory features but only 4 data points (the 4 XOR patterns). With more features
than points, least-squares perfectly interpolates ANY labeling — even from random/meaningless
features. So this "PASS" demonstrates nothing about reservoir capability; it is a textbook
over-parameterization artifact. **Recorded as INVALID (caught in self-review).**

A valid reservoir test needs #samples >> #features AND a HELD-OUT train/test split so the readout
must GENERALIZE. Redone as G78: a long random bit stream, a higher-dimensional reservoir state read
from multiple spatial sub-regions, temporal-XOR/parity target, ridge readout trained on the first
portion and evaluated on a held-out tail. Test accuracy >> chance = a genuine reservoir.
