# JEP-10c — using the AMD GPU: inference via onnxruntime-directml (Michael's scaling directive)

## Result — PASS
| path | test acc | 10k-batch | 200k-batch throughput |
|------|----------|-----------|------------------------|
| GPU (DirectML, AMD RX 7700S) | 0.9652 (exact match) | 34.1ms | 985k img/s |
| CPU (16 threads) | 0.9652 | 32.7ms | 281k img/s |
| **GPU speedup @200k** | — | — | **x3.51** |

**VERDICT: PASS.** The trained MLP runs on the AMD RX 7700S via onnxruntime-directml, matching the numpy
reference EXACTLY (0.9652). The GPU delivers x3.51 throughput vs 16-thread CPU at large batch (at small batch,
launch overhead makes them even). So on this machine the GPU IS usable - for INFERENCE. Established tooling
(ONNX, DirectML EP), named as such.

## Honest hardware envelope (the scaling reality on this machine)
- GPUs: 2x AMD (RX 7700S 8GB discrete + 780M integrated). NOT NVIDIA.
- TRAINING on GPU: NOT available here. CUDA is NVIDIA-only; ROCm is Linux-only; torch-directml does not support
  Python 3.13 (only <=3.10/3.11; the machine has 3.13 + 3.12). No PyTorch-GPU training path.
- INFERENCE on GPU: YES via onnxruntime-directml (DmlExecutionProvider) - x3.51 at 200k batch (JEP-10c).
- TRAINING practical max: Ryzen 9 7940HS (8c/16t) + 62GB RAM, multithreaded BLAS (OMP/OPENBLAS=16). Used in
  JEP-10/10b: predictive coding scales to full MNIST at parity with backprop (0.947 vs 0.968).
- To unlock GPU TRAINING later: (a) dual-boot/WSL2 Linux + ROCm (RDNA3 supported), or (b) a Python 3.10/3.11
  venv + torch-directml (slower, partial op coverage), or (c) an NVIDIA GPU. None required for the current
  programme; logged for transparency.
