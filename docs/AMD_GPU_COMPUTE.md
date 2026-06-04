# Running GPU compute on this machine (AMD, not NVIDIA) — the honest options

Michael asked: "Can we develop code for my GPU. CUDA-like PyTorch, but not NVIDIA? There must be a way." Yes.
This machine has 2x AMD GPUs (RX 7700S 8GB discrete + 780M iGPU). CUDA is NVIDIA-only, but several routes give
GPU compute on AMD. Ranked by practicality for THIS machine (Windows 11, was Python 3.13):

## 1. torch-directml (CHOSEN) — PyTorch-like training on AMD via DirectML
- DirectML is Microsoft's hardware-agnostic GPU API (DirectX 12). `torch-directml` is a PyTorch backend on top of
  it: you write NORMAL PyTorch and move tensors/models to a `dml` device instead of `cuda`. Works on AMD/Intel/
  NVIDIA on Windows.
- CONSTRAINT (the only reason it failed before): it supports Python <= 3.10/3.11 and pins torch 2.4.x. The repo
  had only Python 3.13/3.12. FIX: installed Python 3.11 (winget) + a dedicated venv `.venv-dml311`.
- Usage: `import torch_directml; dev = torch_directml.device(); model.to(dev); x = x.to(dev)`. Training (backprop)
  runs ON the GPU. See tools/run_jep18_amd_gpu_train.py.
- Caveats: partial op coverage (most common ops work; exotic ones fall back/err), generally slower than CUDA on
  NVIDIA, fp64 limited. Fine for MLP/CNN training at small-mid scale.

## 2. onnxruntime-directml — GPU INFERENCE (already working, JEP-10c)
- For deploying trained models: export to ONNX, run with DmlExecutionProvider. x3.5 vs CPU at large batch. Works
  on Python 3.13. Inference only (no training).

## 3. ZLUDA — a CUDA implementation for AMD ("CUDA but not NVIDIA", literally)
- ZLUDA intercepts CUDA calls and runs them on AMD (HIP/ROCm under the hood). Lets some unmodified CUDA apps and
  CUDA-PyTorch run on AMD. Status is volatile (AMD funded then withdrew; now community/open-source; RDNA3 / RX
  7700S support is partial and Windows support is rough). High-effort, fragile - NOT chosen, but it is the most
  literal answer to "CUDA on AMD".

## 4. Vendor-neutral GPU compute kernels (for custom hot paths)
- pyopencl (OpenCL), wgpu-py (WebGPU compute shaders), kompute/pyvulkan (Vulkan compute): write GPU kernels that
  run on AMD. General-purpose but lower-level (you write the kernels), no autograd. Good for substrate physics
  hot paths if we ever want GPU there.
- tensorflow-directml-plugin: TF training on DirectML/AMD (like option 1 for TensorFlow); similar Python-version
  constraints.

## 5. ROCm (AMD's CUDA equivalent) — Linux only
- The "real" high-performance AMD path (HIP, rocBLAS, PyTorch-ROCm). RDNA3 (RX 7700S) is supported, but PyTorch-
  ROCm wheels are LINUX-ONLY. Route: dual-boot or WSL2 + ROCm. Best performance, biggest setup cost. Not done
  here (staying on Windows), logged as the upgrade path if GPU training becomes a bottleneck.

## Bottom line
For "CUDA-like PyTorch training on your AMD GPU on Windows now": torch-directml on Python 3.11 (option 1).
Demonstrated in JEP-18. For max performance later: WSL2 + ROCm (option 5).
