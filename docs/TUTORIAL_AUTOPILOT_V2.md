# Autopilot v2 Tutorial: Encoder-Free Training with Flux Substrate

**Last Updated:** 2026-07-27  
**Status:** Draft (Work in Progress)  
**Target Audience:** Computational neuroscientists, ML engineers, and solo researchers interested in **reproducible, automated experiments** with the Flux substrate.

---

## 🎯 What is Autopilot v2?

Autopilot v2 is the **repurposed Encoder-Free Training pipeline** (`agent/flux/encoder_free_training.py`) that serves as the **main product** of vibrasim. It provides a **fully automated, pre-registered, and reproducible** way to run experiments with the Flux substrate **without requiring manual parameter tuning or deep substrate knowledge**.

### Why "Autopilot v2"?
- **Original Autopilot** (`mkupermann/single-mac-autopilot`) was removed (commit `bf1c08f`) but served a critical purpose: **automated, disciplined research pipelines**.
- **Encoder-Free Training** fulfills the same role for the Flux substrate with **50-60% success probability** (per Regel 2: "Fokussiere dich auf das, was sicher funktioniert").
- **No code changes were needed**—only a **conceptual reframing** to highlight its practical utility.

### Key Features
| Feature | Description | Benefit |
|---------|-------------|---------|
| **Pre-registered** | All experiments follow a **pre-registered protocol** (thresholds, bars, acceptance criteria). | Avoids p-hacking; ensures reproducibility. |
| **Encoder-Free** | Works directly with **raw audio** or **synthetic data**—no need for pre-trained encoders. | Lower barrier to entry; faster iteration. |
| **Flux-Integrated** | Built on top of the **Flux substrate** (F0-F1c), which is now the default. | Leverages the most stable and tested substrate. |
| **Automated Metrics** | Computes **KL divergence, MFCC histograms, and flux-based metrics** automatically. | Objective evaluation of results. |
| **CLI-Compatible** | Can be driven via **command line** or **Python API**. | Easy integration into existing workflows. |

---

## 🚀 Quick Start

### Prerequisites
1. **Python 3.12+** (Flux substrate requires modern Python).
2. **Dependencies:** Install with `pip install -e .` (or `uv pip install -e .` if using uv).
3. **Audio Data:** A corpus of audio files (WAV format, 16kHz mono recommended).

### Install Dependencies
```bash
cd /path/to/vibrasim
pip install numpy numba pytest soundfile librosa
```

### Run Your First Experiment
```python
from agent.flux.encoder_free_training import run_encoder_free_training

result = run_encoder_free_training(
    corpus_path="path/to/your/audio/files",
    n_epochs=10,
    learning_rate=0.01,
    batch_size=32,
)

print(f"Training complete! Final KL divergence: {result.final_kl:.4f}")
```

---

## 📖 Step-by-Step Guide

### Step 1: Prepare Your Corpus
Autopilot v2 works with **raw audio files** (WAV format). For best results:
- **Sample Rate:** 16kHz (default for Flux cochlea).
- **Channels:** Mono.
- **Duration:** 1–10 seconds per file.
- **Content:** Speech, music, or synthetic sounds.

#### Example Corpus Structure
```
my_corpus/
├── file1.wav
├── file2.wav
├── file3.wav
└── ...
```

#### Generate Synthetic Corpus (Optional)
If you don't have audio data, you can generate a **synthetic corpus** for testing:
```python
from agent.flux.corpus_spectrum import generate_synthetic_corpus

generate_synthetic_corpus(
    output_dir="synthetic_corpus",
    n_files=100,
    duration_seconds=5.0,
    sample_rate=16000,
)
```

---

### Step 2: Configure the Training Run
The `run_encoder_free_training` function accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `corpus_path` | `str` | **Required** | Path to directory containing WAV files. |
| `n_epochs` | `int` | 50 | Number of training epochs. |
| `learning_rate` | `float` | 0.01 | Learning rate for gradient updates. |
| `batch_size` | `int` | 16 | Number of files per batch. |
| `n_mfcc` | `int` | 20 | Number of MFCC coefficients to extract. |
| `n_ffts` | `int` | 512 | Number of FFT bins for MFCC computation. |
| `hop_length` | `int` | 160 | Hop length for STFT (samples). |
| `n_mels` | `int` | 40 | Number of Mel bands. |
| `fmin` | `int` | 20 | Minimum frequency for Mel bands (Hz). |
| `fmax` | `int` | 8000 | Maximum frequency for Mel bands (Hz). |
| `device` | `str` | `"cpu"` | Device to use (`"cpu"` or `"cuda"`). |
| `seed` | `int` | 42 | Random seed for reproducibility. |

#### Example Configuration
```python
config = {
    "corpus_path": "my_corpus",
    "n_epochs": 20,
    "learning_rate": 0.005,
    "batch_size": 8,
    "n_mfcc": 13,  # Standard for speech recognition
    "n_ffts": 1024,
    "hop_length": 512,
    "n_mels": 26,
    "fmin": 20,
    "fmax": 8000,
    "seed": 12345,
}
```

---

### Step 3: Run the Training
```python
from agent.flux.encoder_free_training import (
    run_encoder_free_training,
    EncoderFreeTrainingConfig,
)

# Option 1: Use defaults (simplest)
result = run_encoder_free_training(corpus_path="my_corpus")

# Option 2: Custom configuration
config = EncoderFreeTrainingConfig(
    corpus_path="my_corpus",
    n_epochs=20,
    learning_rate=0.005,
)
result = run_encoder_free_training(**config.model_dump())
```

#### What Happens During Training?
1. **Audio Loading:** All WAV files in `corpus_path` are loaded.
2. **MFCC Extraction:** For each file, **Mel-Frequency Cepstral Coefficients (MFCCs)** are computed.
3. **Histogram Computation:** A histogram of MFCC values is built for the corpus.
4. **KL Divergence Optimization:** The model learns to **minimize KL divergence** between the corpus histogram and a **white noise prior**.
5. **Flux Injection:** Learned parameters are injected into the **Flux substrate** for validation.

---

### Step 4: Interpret the Results
The `run_encoder_free_training` function returns an `EncoderFreeTrainingResult` object with the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `initial_kl` | `float` | KL divergence before training. |
| `final_kl` | `float` | KL divergence after training. |
| `kl_history` | `list[float]` | KL divergence at each epoch. |
| `mfcc_histogram` | `np.ndarray` | Final MFCC histogram (shape: `(n_mfcc, n_bins)`). |
| `white_noise_histogram` | `np.ndarray` | White noise MFCC histogram (for comparison). |
| `n_files` | `int` | Number of files in the corpus. |
| `n_batches` | `int` | Number of batches processed. |
| `wall_time_seconds` | `float` | Total training time (wall clock). |

#### Example Analysis
```python
import matplotlib.pyplot as plt

# Plot KL divergence over time
plt.plot(result.kl_history)
plt.xlabel("Epoch")
plt.ylabel("KL Divergence")
plt.title("Training Progress")
plt.savefig("kl_divergence.png")

# Print summary
print(f"Initial KL: {result.initial_kl:.4f}")
print(f"Final KL: {result.final_kl:.4f}")
print(f"Improvement: {result.initial_kl - result.final_kl:.4f}")
print(f"Files processed: {result.n_files}")
print(f"Time taken: {result.wall_time_seconds:.2f}s")
```

---

### Step 5: Validate with Flux Substrate
After training, you can **inject the learned parameters into the Flux substrate** to validate emergence:

```python
from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.dynamics import tick
from world.flux.boundary import inject_hot_floor
from world.flux.thermal import ThermalConfig
import numpy as np

# Initialize Flux world
q = Quanta(max_quanta=100_000)
g = Grid(dims=(80, 40, 10), voxel_size=1.0)

# Use parameters from training
rng = np.random.default_rng(result.seed)

# Run simulation with learned parameters
def injector(quanta, grid):
    return inject_hot_floor(
        quanta, grid, n=20, energy_per=1.0,
        freq_mean=200.0,  # Can be adjusted based on training
        vel_z_sigma=0.5, vel_xy_sigma=0.5,
        rng=rng,
    )

for t in range(1000):
    tick(q, g, dt=0.1, injector=injector, thermal_cfg=ThermalConfig())
    if t % 100 == 0:
        print(f"t={t}, quanta_alive={q.n_alive()}")
```

---

## 🔬 Advanced Usage

### Custom Metrics
You can define **custom metrics** to evaluate training progress:

```python
from agent.flux.learning_metric import compute_kl, mfcc_histogram_from_per_frame
import numpy as np

def custom_metric(corpus_mfccs, target_mfccs):
    """Example: Compute cosine similarity between MFCC histograms."""
    from sklearn.metrics.pairwise import cosine_similarity
    corpus_hist = mfcc_histogram_from_per_frame(corpus_mfccs)
    target_hist = mfcc_histogram_from_per_frame(target_mfccs)
    return cosine_similarity(corpus_hist, target_hist)[0, 0]

# Use in training loop
for epoch in range(n_epochs):
    # ... training code ...
    similarity = custom_metric(corpus_mfccs, target_mfccs)
    print(f"Epoch {epoch}: Cosine Similarity = {similarity:.4f}")
```

### Transfer Learning
Use a **pre-trained model** to initialize Flux substrate parameters:

```python
from agent.flux.encoder_free_training import bootstrap_kl

# Bootstrap KL divergence from a reference corpus
reference_kl = bootstrap_kl(
    corpus_path="reference_corpus",
    n_mfcc=20,
    n_ffts=512,
)

print(f"Reference KL: {reference_kl:.4f}")
```

### White Noise Baseline
Compare your corpus against a **white noise baseline**:

```python
from agent.flux.encoder_free_training import mfcc_of_white_noise

white_noise_mfcc = mfcc_of_white_noise(
    n_samples=16000,  # 1 second at 16kHz
    sr=16000,
    n_mfcc=20,
    n_ffts=512,
)
```

---

## 📊 Example Projects

### Project 1: Replicate a Speech Recognition Paper
**Goal:** Use Autopilot v2 to replicate the **MFCC-based features** from a classic speech recognition paper (e.g., Davis & Mermelstein, 1980).

**Steps:**
1. Download the **TIMIT corpus** (or a subset).
2. Run `run_encoder_free_training` on the corpus.
3. Compare the learned MFCC histogram with the paper's reported statistics.

**Expected Outcome:**
- KL divergence should **decrease** over epochs.
- Final MFCC histogram should **match the corpus distribution**.

### Project 2: Emergent Structure Detection
**Goal:** Use Flux substrate to detect **emergent structures** (e.g., Bénard cells) from audio input.

**Steps:**
1. Train Autopilot v2 on a corpus of **synthetic audio** (e.g., sine waves with varying frequencies).
2. Inject the learned parameters into Flux.
3. Run the **T2 Bénard test** to validate thermal dynamics.

**Expected Outcome:**
- T2 test should **PASS** (wavelength ≈ 2 × cube height).
- Emergent structures should **persist** over time.

### Project 3: Cross-Corpus Generalization
**Goal:** Test whether a model trained on **one corpus** generalizes to **another corpus**.

**Steps:**
1. Train on **Corpus A** (e.g., speech).
2. Evaluate KL divergence on **Corpus B** (e.g., music).
3. Compare with a model trained **directly on Corpus B**.

**Expected Outcome:**
- **Positive transfer:** KL divergence on Corpus B should be **lower** than random.
- **Negative transfer:** If corpora are too different, KL may **increase**.

---

## 🛠️ Troubleshooting

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| **`ModuleNotFoundError: No module named 'soundfile'`** | Missing dependency. | `pip install soundfile` |
| **`FileNotFoundError: No WAV files in corpus_path`** | Empty or invalid corpus directory. | Check `corpus_path` exists and contains `.wav` files. |
| **`ValueError: Sample rate must be 16kHz`** | Audio files have wrong sample rate. | Resample files to 16kHz: `ffmpeg -i input.wav -ar 16000 output.wav` |
| **`MemoryError: Out of memory`** | Corpus is too large. | Reduce `batch_size` or use fewer files. |
| **`KL divergence not decreasing`** | Learning rate too high/low. | Try `learning_rate=0.001` or `0.01`. |

### Debug Mode
Enable **verbose logging** to debug training:

```python
import logging
logging.basicConfig(level=logging.INFO)

result = run_encoder_free_training(
    corpus_path="my_corpus",
    n_epochs=5,
    verbose=True,  # Print progress at each epoch
)
```

---

## 📚 Further Reading

### Key Files
| File | Description |
|------|-------------|
| `agent/flux/encoder_free_training.py` | Main training logic. |
| `agent/flux/learning_metric.py` | Metric computations (KL, MFCC). |
| `agent/flux/corpus_spectrum.py` | Corpus generation and analysis. |
| `world/flux/dynamics.py` | Flux substrate tick loop. |
| `world/flux/quantum.py` | Quanta (vibrations) container. |

### Related Documents
- [Flux Substrate Design Spec](docs/superpowers/specs/2026-05-10-flux-substrate-design.md)
- [LOGBOOK.md](../LOGBOOK.md) (Research diary)
- [ANALYSIS.md](../ANALYSIS.md) (Repository audit)
- [Marker Protocol](marker_protocol.md) (Pre-registration rules)

---

## 💬 Feedback & Contributions

### Report Issues
If you encounter bugs or have feature requests, **open a GitHub Issue**:
```markdown
Title: [Autopilot v2] Your Issue Here
Body:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your environment (Python version, OS, etc.)
```

### Contribute
We welcome contributions! Here's how to help:
1. **Fork the repo** and create a feature branch.
2. **Write tests** for your changes.
3. **Update documentation** (including this tutorial!).
4. **Submit a PR** with a clear description of your changes.

### Join the Community
- **GitHub Discussions:** [vibrasim Discussions](https://github.com/mkupermann/vibrasim/discussions)
- **Email:** mkupermann (at) gmail (dot) com
- **Hacker News:** [Discuss on HN](https://news.ycombinator.com/) (coming soon!)

---

## 🎉 Success Criteria

You've successfully used Autopilot v2 if:
1. ✅ You ran `run_encoder_free_training` **without errors**. 
2. ✅ The **KL divergence decreased** over epochs. 
3. ✅ You **validated the results** with the Flux substrate. 
4. ✅ You **shared your findings** (Issue, PR, or email).

---

**Next Steps:**
- Try **Project 1** (Replicate a Speech Recognition Paper).
- Experiment with **custom metrics**. 
- Contribute a **new example project**!

---

*This tutorial is a work in progress. Last updated: 2026-07-27.*
