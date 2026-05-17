"""Flux Substrate — agent layer (cochlea, synthesis, audio I/O).

Filled in F2 with the cochlea + synthesis adapters around the F0-F1c
substrate. Attention reallocate (§5.8) remains deferred to F4+.

See spec §5.6 (cochlea), §5.7 (synthesis), §6 (tick integration).
"""
from __future__ import annotations

from agent.flux.cochlea import (
    Cochlea,
    CochleaConfig,
    Resonator,
    cochlea_inject,
    step_resonator,
    step_resonators,
)
from agent.flux.synthesis import (
    Synthesizer,
    SynthesisConfig,
    drive_resonator_impulse,
    read_output_samples,
    route_node_firings,
    route_node_firings_explicit,
)
from agent.flux.audio_in import (
    DEFAULT_SR_HZ,
    iter_sample_chunks,
    read_wav_mono_16k,
)
from agent.flux.audio_out import (
    WavWriter,
    write_wav_mono_16k,
)
from agent.flux.audio_raw import (
    inject_raw_audio_chunk,
    inject_raw_audio_sample,
    position_hash,
)
from agent.flux.encoder_free_training import (
    EncoderFreeTrainingConfig,
    EncoderFreeTrainingResult,
    bootstrap_kl,
    bootstrap_kl_stats,
    compute_mfcc_per_frame,
    mfcc_histogram_from_per_frame,
    mfcc_of_white_noise,
    run_encoder_free_training,
)

__all__ = [
    # cochlea
    "Cochlea",
    "CochleaConfig",
    "Resonator",
    "cochlea_inject",
    "step_resonator",
    "step_resonators",
    # synthesis
    "Synthesizer",
    "SynthesisConfig",
    "drive_resonator_impulse",
    "read_output_samples",
    "route_node_firings",
    "route_node_firings_explicit",
    # audio io
    "DEFAULT_SR_HZ",
    "iter_sample_chunks",
    "read_wav_mono_16k",
    "WavWriter",
    "write_wav_mono_16k",
    # encoder-free audio injection (R-10)
    "inject_raw_audio_chunk",
    "inject_raw_audio_sample",
    "position_hash",
    # encoder-free training + readout (R-11)
    "EncoderFreeTrainingConfig",
    "EncoderFreeTrainingResult",
    "bootstrap_kl",
    "bootstrap_kl_stats",
    "compute_mfcc_per_frame",
    "mfcc_histogram_from_per_frame",
    "mfcc_of_white_noise",
    "run_encoder_free_training",
]
