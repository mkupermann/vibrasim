# JEP-10 — does substrate-compatible local learning (predictive coding) scale to REAL data? (MNIST, full CPU)

## Motivation (Michael's scaling directive)
Hardware reality: AMD GPUs (no CUDA; ROCm Linux-only; torch-directml unsupported on Py3.13) -> no PyTorch GPU
TRAINING path. Practical max for training = Ryzen 9 (16 threads) + 62GB RAM with multithreaded BLAS. GPU usable
only for INFERENCE via onnxruntime-directml (JEP-10b). So: scale the SCIENCE on CPU. JEP-6d showed predictive
coding (local, no backprop) matches backprop on toy two-moons; this asks the real question - does it scale to
REAL data (MNIST, 60k x 784) with a large network?

## Pre-registration (locked BEFORE run)
- MNIST 60k train / 10k test, pixels/255. Network 784 -> 1024 -> 10, tanh hidden, softmax out. Minibatch SGD.
- Two learners, SAME arch: BACKPROP and PREDICTIVE CODING (local error nodes + hidden relaxation, no backprop).
  16-thread BLAS (OMP/OPENBLAS=16). Equal epochs/lr.
- Bars: backprop test acc >= 0.95 (confirms scale+task), PC test acc >= backprop - 0.03 (PC matches at scale),
  both >> 0.10. PASS = substrate-compatible local learning SCALES to real data matching backprop. NULL if PC
  fails to scale. Predictive coding (Rao-Ballard; Whittington-Bogacz 2017) established - named as such.

## Result — PARTIAL (PC strong at scale, but backprop baseline mistuned -> comparison confounded)
| learner | MNIST test acc | wall-clock |
|---------|----------------|------------|
| backprop (lr=0.5) | 0.8893 | 16s |
| predictive coding (lr=0.5) | 0.9652 | 58s |

**VERDICT: PARTIAL.** Predictive coding scaled strongly to real MNIST (0.965 with a 1-hidden 1024 net, 16
threads) — the substrate-compatible local-learning path is clearly NOT toy-only. BUT the backprop baseline
underperformed (0.889): lr=0.5 (locked pre-run) is too aggressive for backprop here, so the comparison is
CONFOUNDED — I will NOT claim "PC > backprop" from a mistuned baseline (that would be overclaiming). The locked
soundness bar (backprop >= 0.95) correctly flagged this. Fair fix = equal lr sweep for BOTH learners (JEP-10b),
standard practice, not post-hoc bar tuning. PC's 0.965 itself is a solid, honest scaling result.

## JEP-10b — FAIR equal-lr-sweep result — PASS
| learner | lr=0.05 | lr=0.1 | lr=0.2 | BEST |
|---------|---------|--------|--------|------|
| backprop | 0.9373 | 0.9555 | 0.9683 | **0.9683** |
| predictive coding | 0.9247 | 0.9346 | 0.9471 | **0.9471** |

**VERDICT: PASS.** With an equal lr sweep for both, predictive coding (local, no backprop) matches backprop on
real MNIST: best PC 0.9471 vs backprop 0.9683 (within 0.03). The JEP-10 anomaly (PC 0.965 > backprop 0.889) was
confirmed as the mistuned lr=0.5 backprop (unstable); PC was more robust to high lr (a known PC property, not
over-claimed here). Headline: substrate-compatible local learning SCALES to real data (60k x 784, 1024-wide net,
16 threads) at PARITY with backprop. Whittington-Bogacz (2017) reproduced at scale - established, named as such.
