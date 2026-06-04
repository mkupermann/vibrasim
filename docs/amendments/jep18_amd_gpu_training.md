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
