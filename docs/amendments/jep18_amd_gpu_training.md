# JEP-18 — REAL training on the AMD GPU (CUDA-like PyTorch, not NVIDIA) via torch-directml

## Motivation (Michael's request)
"Can we develop code for my GPU. CUDA-like PyTorch, but not NVIDIA? There must be a way." Yes. Earlier
torch-directml failed ONLY because the repo had Python 3.13 (unsupported). Fix: installed Python 3.11 (winget) +
venv `.venv-dml311` + torch-directml. DirectML (Microsoft, DX12) is a hardware-agnostic GPU backend; torch-
directml exposes it as a PyTorch device. Write normal PyTorch, move to a `dml` device instead of `cuda`.

## Pre-registration (locked BEFORE run)
- Train a 784-1024-256-10 MLP (Adam + backprop) on MNIST ON the AMD GPU (RX 7700S) via torch-directml.
- Bars: training RUNS on the dml device, loss decreases, test acc >= 0.95. PASS = real GPU TRAINING on AMD works
  (not just inference). Report GPU vs CPU wall-clock. Full option map: docs/AMD_GPU_COMPUTE.md. DirectML /
  torch-directml established - named as such.

## Result — PASS (training works on AMD GPU) with an honest speed caveat
| device | MLP test acc | 5-epoch time |
|--------|--------------|--------------|
| AMD RX 7700S (torch-directml) | 0.9807 | 36.9s |
| CPU (16 threads) | 0.9803 | 7.1s |

**VERDICT: PASS.** REAL backprop training runs on the AMD GPU via torch-directml (both AMD GPUs visible: RX
7700S + 780M). Same code as CUDA, just `torch_directml.device()` instead of `cuda`. Loss decreased, 0.9807 acc -
the GPU did the training. HONEST CAVEAT: for THIS small MLP the GPU (37s) was SLOWER than the 16-thread CPU
(7s) - DirectML per-op launch overhead + occasional CPU fallbacks dominate at small scale, and the Ryzen 9 is
strong. GPUs pay off at LARGER model/batch sizes -> JEP-18b finds that regime. So the answer to Michael is YES
(CUDA-like PyTorch on AMD works), with the honest note that DirectML is slower than CUDA-on-NVIDIA and only
beats this CPU on bigger workloads.

## JEP-18b — the GPU-win regime (honest benchmark)
| workload | GPU RX 7700S | CPU 16-thread | speedup |
|----------|--------------|---------------|---------|
| matmul 1024^3 | 838 GFLOP/s | 394 | x2.13 |
| matmul 2048^3 | 1701 GFLOP/s | 504 | x3.37 |
| matmul 4096^3 | 2317 GFLOP/s | 488 | x4.75 |
| matmul 8192^3 | 2805 GFLOP/s | 470 | x5.96 |
| large MLP (3x4096) training, 3 epochs | 15.1s | 38.6s | x2.56 |

**FINDING.** The AMD RX 7700S via torch-directml BEATS the 16-thread CPU on large compute-bound work: up to
x5.96 on big matmuls and x2.56 training a large MLP. It LOSES on small models (JEP-18: small MLP 37s vs 7s) due
to per-op launch overhead. Practical rule: GPU for big nets / big batches / big matmuls; CPU for small models
(the Ryzen 9 is strong). Complete answer to Michael: YES - CUDA-like PyTorch training on your AMD GPU works
(torch-directml, Python 3.11, `.venv-dml311`), it accelerates large workloads 2.5-6x, with honest caveats
(slower than CUDA-on-NVIDIA, partial op coverage, small-model overhead). Full option map: docs/AMD_GPU_COMPUTE.md.
