# Pattern: backprop-free local learning that scales (predictive coding)

Predictive coding (local error nodes + inference relaxation, no backprop) is a viable substrate-compatible
trainer, validated across EQMOD-4:
- Matches backprop on a well-posed iid task (JEP-6d: 0.97 vs 0.98).
- Matches backprop on MNIST AND Fashion-MNIST at 1- AND 2-hidden depth under a MATCHED comparison (same MSE+tanh
  +plain-SGD, differ only in credit assignment) - JEP-19b/19c.
- The substrate's EBM half: local Hebbian storage + relaxation inference (Hopfield) - JEP-4 (recall 0.905,
  energy monotone, capacity ~0.14N).

## Pitfalls (each cost a NULL)
- Multi-layer PC is finicky: a buggy hand-rolled version collapsed to chance (JEP-19) - VALIDATE on easy MNIST
  before claiming depth effects.
- Fair comparison requires MATCHED optimizers (Adam-vs-plain-SGD confounded JEP-19/10).
- Plain SGD on MSE diverges at high lr; standardize inputs + modest lr (JEP-19c).
- PC's inference loop is compute-heavy (many small ops) - slow on CPU AND on DirectML GPU (launch overhead).

## Hardware (this machine: AMD, Windows, no NVIDIA)
GPU training works via torch-directml on Python 3.11 (.venv-dml311) - normal PyTorch, `torch_directml.device()`
instead of `cuda`. Beats 16-thread CPU x2.1-6.0 on big matmuls, x2.56 large-MLP; loses on small models. GPU
inference also via onnxruntime-directml (Py3.13). Best-perf upgrade path: WSL2 + ROCm. See docs/AMD_GPU_COMPUTE.md.
