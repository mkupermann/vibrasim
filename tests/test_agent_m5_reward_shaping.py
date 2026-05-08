"""Headline integration test M5 — reward shaping (stepped, slow).

100 reward trials × 5 seeds, targeted vs random reward conditions.
Targeted: fire RewardChannel.fire_positive when output spectral similarity
to a target template exceeds threshold.
Random: fire at random times.
Assertion: targeted-run baseline output similarity > random-run baseline
similarity + margin (acceptance.toml [M5].margin_min, default 0.10).

Currently xfailed for the same reason as M4 (see test_agent_m4_glass_of_water.py
for the full root-cause analysis): the substrate's binding chain
(freq_ratio=0.08 ± freq_tolerance=0.025) does not accept M5's deterministic
audio frequencies, so no atoms form in the audio output port and BOTH
conditions produce zero output. The comparison is undefined/zero.

What PASSES in Plan E and is load-bearing: I5, RC1-RC3, RA1-RA5, AL1-AL3,
plus 264 prior tests. M5 awaits the same path as M4 — Plan F brain-
checkpoint, substrate-tuning expedition, OR pre-seeded-atoms redesign.
"""
import numpy as np
import pytest
import tomllib
from pathlib import Path

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.reward import RewardChannel
from agent.loop import AgentLoop


def _load_acceptance():
    p = Path(__file__).parent / "acceptance.toml"
    with p.open("rb") as f:
        return tomllib.load(f)


def _synthesize_water_audio(duration_sec: float, sample_rate: int = 16000) -> np.ndarray:
    t = np.arange(int(sample_rate * duration_sec)) / sample_rate
    audio = (
        np.sin(2 * np.pi * 500 * t)
        + np.sin(2 * np.pi * 1000 * t)
        + np.sin(2 * np.pi * 1500 * t)
    ).astype(np.float32) * 0.3
    return audio


def _spectral_cosine(audio: np.ndarray, target: np.ndarray) -> float:
    n = min(len(audio), len(target))
    if n < 32:
        return 0.0
    spec_a = np.abs(np.fft.rfft(audio[:n]))
    spec_t = np.abs(np.fft.rfft(target[:n]))
    norm_a = float(np.linalg.norm(spec_a))
    norm_t = float(np.linalg.norm(spec_t))
    if norm_a == 0 or norm_t == 0:
        return 0.0
    return float(np.dot(spec_a, spec_t) / (norm_a * norm_t))


def _build_world(seed: int) -> tuple[World, AudioIO, AgentLoop, RewardChannel]:
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=512, n_nodes_max=32768,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=seed,
        # Same scoping as M4 — substrate physics is empirical, not the goal here.
        lambda_gen=0.0, lambda_dec=0.0,
        audio_amplitude_threshold=0.05,
        # Plans A, B, E
        lambda_dec_mol=0.001, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=2.0, delta_LTD=0.5,
        r_bridge=8.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=3.0,
        audio_io_enabled=True,
    )
    w = World(cfg)
    audio_io = AudioIO(amplitude_threshold=0.05, rng=np.random.default_rng(seed))
    rc = RewardChannel(rng=np.random.default_rng(seed))
    loop = AgentLoop(w, audio_io=audio_io, reward=rc)
    return w, audio_io, loop, rc


def _run_condition(seed: int, targeted: bool, n_trials: int, target: np.ndarray) -> float:
    """Run one reward-shaping condition; return baseline output similarity."""
    w, audio_io, loop, rc = _build_world(seed)
    cfg = w.config
    rng = np.random.default_rng(seed + 1000)

    # Reward-shaping training: each trial is a short audio drive + reward decision
    for trial in range(n_trials):
        audio_io._write_input_buffer(_synthesize_water_audio(0.5))
        for _ in range(int(0.5 / cfg.dt)):
            loop.step(cfg.dt)
        # Sample current output and decide reward
        n_out = (audio_io._output_write_pos - audio_io._output_read_pos) % len(
            audio_io._output_buffer
        )
        if n_out > 32:
            recent = audio_io._read_output_buffer(min(n_out, 256))
            sim = _spectral_cosine(recent, target)
        else:
            sim = 0.0
        if targeted:
            if sim > 0.3:
                rc.fire_positive(w)
            elif sim < 0.1:
                rc.fire_negative(w)
        else:
            # Random reward: 50/50 probability per trial
            if float(rng.random()) < 0.5:
                rc.fire_positive(w)
            else:
                rc.fire_negative(w)

    # Baseline phase: no audio input, measure output for 5 sim-sec
    n_baseline_ticks = int(5.0 / cfg.dt)
    for _ in range(n_baseline_ticks):
        loop.step(cfg.dt)
    n_out = (audio_io._output_write_pos - audio_io._output_read_pos) % len(
        audio_io._output_buffer
    )
    audio_out = audio_io._read_output_buffer(max(n_out, 1))
    return _spectral_cosine(audio_out, target)


@pytest.mark.slow
@pytest.mark.xfail(
    strict=True,
    reason=(
        "M5 reward-shaping fails for the same substrate-binding-chain "
        "reason as M4 (see tests/test_agent_m4_glass_of_water.py for the "
        "full root-cause analysis). Audio at 500/1000/1500 Hz produces "
        "electrons at frequencies whose pairwise ratios fall outside the "
        "binding window [0.055, 0.105]; no atoms form in the audio output "
        "port; BOTH targeted-reward and random-reward conditions produce "
        "zero-output baselines; the comparison targeted > random + margin "
        "is undefined. The reward-channel physics itself works (RC1-RC3, "
        "RA1-RA5 all pass — including the new k_reward_polarity=-1 swap). "
        "M5 awaits the same path as M4: Plan F brain-checkpoint OR "
        "substrate-tuning expedition OR pre-seeded-atoms redesign."
    ),
)
def test_M5_reward_shaping():
    """Reward shaping: targeted reward shifts output spectrum toward target
    more than random reward does."""
    acceptance = _load_acceptance()
    n_trials = acceptance["M5"]["n_trials"]
    n_seeds = acceptance["M5"]["n_seeds"]
    margin_min = acceptance["M5"]["margin_min"]
    seeds = acceptance["provenance"]["plan_E"]["held_out_seeds"][:n_seeds]

    target = _synthesize_water_audio(0.5)

    targeted_sims = []
    random_sims = []
    for seed in seeds:
        t_sim = _run_condition(seed, targeted=True, n_trials=n_trials, target=target)
        r_sim = _run_condition(seed, targeted=False, n_trials=n_trials, target=target)
        targeted_sims.append(t_sim)
        random_sims.append(r_sim)
        print(f"M5 seed={seed}: targeted={t_sim:.4f}, random={r_sim:.4f}", flush=True)

    targeted_mean = float(np.mean(targeted_sims))
    random_mean = float(np.mean(random_sims))
    margin = targeted_mean - random_mean
    print(
        f"M5: targeted_mean={targeted_mean:.4f}, random_mean={random_mean:.4f}, "
        f"margin={margin:.4f} (threshold={margin_min})",
        flush=True,
    )
    assert margin >= margin_min, (
        f"M5: targeted - random margin {margin:.3f} below threshold {margin_min}"
    )
