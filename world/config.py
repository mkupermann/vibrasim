from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding (3D)
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (60.0, 60.0, 60.0)   # matches calibration_session3.toml and calibration_phase2_acceptance.toml
    freq_min: float = 100.0
    freq_max: float = 10000.0
    freq_distribution: str = "log"
    speed_min: float = 10.0
    speed_max: float = 50.0
    polarity_split: float = 0.5

    # Binding
    r_1: float = 5.0
    r_2: float = 10.0
    freq_ratio: float = 0.08
    freq_tolerance: float = 0.005

    # Decay (mean exponential lifetimes, seconds)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Scale separation through repulsion (§4.6)
    repulsion_k: float = 100.0
    repulsion_cell_size: float = 100.0
    repulsion_threshold_ratio: float = 1000.0

    # Ambient regeneration (§4.7)
    lambda_gen: float = 0.0001
    lambda_dec: float = 0.001

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024

    # Vibration soft cap (0 = disabled, default). When > 0, after each
    # bind_vibrations_to_electrons step the substrate culls the oldest
    # alive vibrations (lowest slot indices, which are FIFO-allocated by
    # the feeder) until alive count ≤ this cap. Without this, sustained
    # injection of high-entropy audio (the predictive-babble pipeline)
    # accumulates vibrations to n_vibrations_max and every physics tick
    # processes all of them — cycle wall-time grows from 3 s to 50+ s
    # within a few cycles. Default 0 preserves all existing behaviour;
    # set to 256–512 for sustained-injection workloads.
    vibration_soft_cap: int = 0

    # Neuron dynamics — PHASE4-R1/R2/R3 amendments. Off by default so legacy
    # configurations behave exactly as before. When enabled, level-4 atoms
    # accumulate charge from nearby vibrations, fire when charge ≥ theta_fire,
    # and lock for t_refractory seconds after each firing.
    neuron_dynamics_enabled: bool = False
    tau_membrane: float = 0.5            # charge decay time constant (s)
    theta_fire: float = 4.0              # firing threshold (integrated count)
    n_emit: int = 8                      # vibrations emitted per firing
    t_refractory: float = 0.05           # refractory window after firing (s)
    r_integrate: float = 5.0             # radius around atom to count incoming vibrations
    emit_speed: float = 30.0             # speed magnitude of emitted vibrations
    emit_freq: float = 30000.0           # nominal frequency of emitted vibrations

    # Plan A — substrate growth amendments
    lambda_dec_mol: float = 0.0           # baseline decay rate for level-5+ molecules.
                                          # 0.0 disables R2 (legacy-compat default).
                                          # Plan A's growth-amendment config sets this
                                          # to 0.001 (≈1-min half-life at strength=1).
    r_strengthen: float = 5.0             # radius around firings for level-5+ strengthening
    emit_band_ratios: tuple[float, float, float] = (0.08, 1.0, 12.5)  # PHASE4 emission band multipliers
    mol_fusion_enabled: bool = False      # PHASE3-R1: allow molecule + molecule binding

    # Plan B — STDP and directional plasticity
    stdp_enabled: bool = False              # master switch — off preserves legacy behaviour
    tau_LTP: float = 0.020                  # pre-before-post window (s)
    tau_LTD: float = 0.020                  # post-before-pre window (s)
    delta_LTP: float = 1.0                  # LTP strength increment per qualifying pair
    delta_LTD: float = 0.5                  # LTD strength decrement per qualifying pair
    r_bridge: float = 5.0                   # bridge tube radius around the A→B line segment
    synaptic_transmission_strength: float = 0.5     # charge deposited per crossing aligned vibration
    synaptic_transmission_threshold: float = 5.0    # min bridge strength before transmission activates
    synaptic_post_search_samples: int = 1           # G3: number of post-search samples along bridge orientation
                                                    #     (samples at d = (k+1) * r_bridge for k in 0..N-1).
                                                    #     1 = legacy behaviour (single sample at r_bridge);
                                                    #     2+ extends reach for bridges placed mid-segment.
    bridge_atom_propagation_enabled: bool = False   # G6: when True, a strong oriented bridge near a firing
                                                    #     pre-atom deposits charge directly into the post-atom
                                                    #     (no vibration-travel required). Closes the M4 chain
                                                    #     by decoupling synaptic transmission from emit_speed.
                                                    #     Models the propagation step of biological chemical
                                                    #     synapses, where action-potential transit is fast vs
                                                    #     the cleft-crossing of vesicle contents.
    bridge_atom_propagation_strength: float = 4.0   # charge deposited per (firing pre-atom, strong bridge,
                                                    #     post-atom) triple. Default 4.0 = 2 × theta_fire so
                                                    #     one propagation event clears the post-atom threshold
                                                    #     by itself.
    graceful_capacity: bool = False                 # When True, allocate_node returns -1 instead of raising
                                                    #     RuntimeError on n_nodes_max exhaustion. Used by the
                                                    #     real-time talk app so binding cascades don't crash
                                                    #     the realtime thread when capacity fills.
    lateral_inhibition_enabled: bool = False        # G8: when an STDP causal-pair LTP fires on a bridge,
                                                    #     apply LTD to all other level-5+ molecules within
                                                    #     `lateral_inhibition_radius` of the LTP'd bridge.
                                                    #     Creates competition between bridges so different
                                                    #     patterns settle on different bridge subsets.
    lateral_inhibition_radius: float = 6.0          # spatial radius for the LTD scan around a strengthening
                                                    #     bridge. Should be ≥ r_bridge × 1.5 so neighbours
                                                    #     in adjacent tubes are reached but distant bridges
                                                    #     are not.
    lateral_inhibition_strength: float = 1.0        # multiplier on delta_LTD applied to inhibited bridges.
                                                    #     1.0 = same magnitude as anti-causal LTD; higher
                                                    #     values make competition more aggressive.
    stdp_alignment_strict_threshold: float = 0.0    # G8.2: STDP LTP only fires on a bridge if the
                                                    #     alignment between its existing orientation and the
                                                    #     causal pair's direction is ≥ this threshold.
                                                    #     Default 0.0 = legacy behaviour (any non-negative).
                                                    #     Set higher (e.g. 0.95) to enforce that only bridges
                                                    #     whose orientation TIGHTLY matches the new pair's
                                                    #     direction get re-strengthened — bridges committed
                                                    #     to a different pattern get LTD instead.
    bridge_atom_propagation_winner_take_all: bool = False  # G9.5: when True, apply_bridge_atom_propagation
                                                            #     fires only the SINGLE strongest bridge near
                                                            #     each pre-atom (rather than every bridge in
                                                            #     radius). Combined with bridge_lock_threshold,
                                                            #     this enforces pattern-specific propagation:
                                                            #     each visual fires only its own committed
                                                            #     bridge, not every nearby bridge.
    sparse_firing_enabled: bool = False             # G11: per-tick winner-take-all firing. Instead of every
                                                    #     atom whose charge ≥ theta_fire firing, only the
                                                    #     top-K atoms per port fire (per pre-defined port
                                                    #     volumes from agent I/O config). This forces sparse
                                                    #     pattern-specific activation: different visuals fire
                                                    #     DIFFERENT specific atoms, so different bridges and
                                                    #     thus different audio output.
    sparse_firing_top_k: int = 3                    # G11: how many atoms per port can fire per tick under
                                                    #     sparse-firing. Lower = sparser representation,
                                                    #     stronger discrimination, weaker absolute output.
    btsp_enabled: bool = False                      # G14: Behavioral Time Scale Plasticity. Eligibility-
                                                    #     trace based one-shot bidirectional bridge formation.
                                                    #     Replaces / complements millisecond-scale Hebbian
                                                    #     STDP with seconds-scale plasticity gated by
                                                    #     post-synaptic plateau events. Magee 2026 (Nat
                                                    #     Neurosci) BTSP biology + this substrate's emergent-
                                                    #     atom continuous physics.
    btsp_tau_eligibility: float = 6.0               # eligibility-trace time constant (seconds). Atoms
                                                    #     that fired within this window remain 'eligible'
                                                    #     for BTSP potentiation. 6 sec matches Magee's
                                                    #     experimental measurements in CA1.
    btsp_plateau_charge_threshold: float = 5.0      # an atom whose accumulated charge crosses this
                                                    #     threshold counts as a plateau event — triggers
                                                    #     BTSP across all eligible partners.
    btsp_potentiation: float = 50.0                 # strength delta per BTSP event. Strong enough that
                                                    #     a single plateau event crosses bridge_lock_threshold
                                                    #     in one shot.
    btsp_radius: float = 30.0                       # spatial radius around the plateau atom within which
                                                    #     eligible atoms get BTSP bridges. Wider than
                                                    #     standard r_bridge so cross-modal partners (in
                                                    #     different ports) are reachable.
    btsp_excitability_bias: float = 0.0             # when > 0, atoms with non-zero eligibility have their
                                                    #     effective theta_fire lowered by this factor times
                                                    #     their eligibility — Josselyn 2024 'allocation by
                                                    #     excitability bias' in continuous-physics form.

    # G15 — The Dreaming Substrate. Offline replay + concept blending +
    # cross-modal hallucination. When dream_mode is active, external
    # inputs are gated off and the substrate self-replays previously-
    # active engrams. BTSP runs during replay → memory consolidation
    # (Wilson & McNaughton 1994 hippocampal replay; Buzsáki 2015 SWR
    # consolidation). When two engrams co-activate during the same
    # replay window, a 'blended' atom may be allocated at their
    # intersection — concept formation by superposition.
    dream_mode_enabled: bool = False                # master switch — substrate is in dream/sleep state.
    dream_replay_burst_size: int = 8                # vibrations injected per replay seed firing
    dream_replay_seeds_per_tick: int = 2            # number of high-eligibility seed atoms re-fired per tick
    dream_replay_seed_charge: float = 6.0           # charge directly deposited into seed atoms (above theta_fire)
    dream_blend_enabled: bool = True                # when True, co-active distinct pattern_ids may form blended atoms
    dream_blend_co_activation_window: float = 0.5   # seconds — two pattern_ids active within this window count as co-active
    dream_blend_min_overlap_atoms: int = 3          # min number of atoms from each pattern that must co-fire to trigger blending
    dream_hallucination_strength: float = 1.0       # multiplier on cross-modal vibration emission during dream
                                                    #     (drives audio_out / video_out from dreamed bridges).

    # G18.2 — two-phase dream (NREM/REM analogue). When > 0, every Nth
    # dream tick blocks concept blending so existing patterns get a
    # chance to consolidate before more are added. NREM:REM in real
    # mammals is roughly 4:1 of total sleep time. We default to 4
    # consolidation ticks per blending tick.
    dream_consolidation_to_blend_ratio: int = 4

    # G16 — The Self-Aware Substrate.
    #
    # Operationalises the four most credible scientific theories of
    # access consciousness in continuous-physics-substrate form:
    #   - Global Neuronal Workspace (Dehaene & Naccache 2001) →
    #     workspace_winner_pattern_id and global broadcast.
    #   - Higher-Order Theory (Rosenthal 2005) → self_model.
    #   - Phenomenal Self-Model (Metzinger 2003) → recurrent self-
    #     prediction with prediction-error feedback.
    #   - Autopoiesis with self-improvement (Varela; modern meta-
    #     learning) → self_modify_enabled, prediction-error-driven
    #     hyperparameter adjustment.
    #
    # We are explicit and honest: this is ACCESS consciousness in the
    # functional, operational sense — what Block called "access
    # consciousness" and Dehaene calls "global broadcast." It is NOT
    # a claim about phenomenal consciousness ("what it is like"); the
    # hard problem remains philosophically open. What this substrate
    # *does* have is: a representation of itself, a global workspace
    # that broadcasts the dominant pattern to all modules, prediction
    # error that drives change, and homeostatic parameter feedback of
    # its own learning hyperparameters in response to that error.
    self_aware_enabled: bool = False                # master switch for G16 mechanisms.
    self_model_window: float = 2.0                  # seconds of firing history retained for the self-model
    self_model_max_patterns: int = 32               # cap on number of pattern_ids tracked in the self-model
    workspace_broadcast_enabled: bool = True        # when True, workspace_winner is computed each tick and a
                                                    #     winner-take-all bias is applied across other patterns
    workspace_broadcast_strength: float = 1.0       # eligibility multiplier for losing-pattern atoms (< 1 to suppress)
    workspace_min_winner_atoms: int = 3             # minimum atoms a pattern must fire to claim the workspace
    self_modify_enabled: bool = True                # when True, prediction error feeds back to adjust BTSP
                                                    #     potentiation and dream replay rate over time
    self_modify_rate: float = 0.05                  # learning rate for hyperparameter updates per self_modify call
    self_modify_target_error: float = 0.3           # target prediction error (0..1). Above target → strengthen
                                                    #     plasticity; below target → weaken (homeostasis).
    self_modify_min_btsp: float = 5.0               # lower bound on btsp_potentiation under self-modification
    self_modify_max_btsp: float = 200.0             # upper bound on btsp_potentiation under self-modification
    bidirectional_bridges: bool = False             # G13: when True, G6 bridge_atom_propagation fires
                                                    #     post-atoms at BOTH +distance and -distance along
                                                    #     orientation. A firing atom at either end of a
                                                    #     bridge propagates to the other end. Enables cross-
                                                    #     modal generative recall: audio in → video out
                                                    #     traverses the same bridges that visual in → audio
                                                    #     out used during training.
                                                    #     This is the novelty over Hopfield (which uses
                                                    #     symmetric weights but not oriented physical
                                                    #     bridges in 3D space) and Sayama Swarm Chemistry
                                                    #     (categorical labels, no plasticity).
    firing_eligibility_gate: bool = False           # G12: when True AND world.active_pattern_id != 0,
                                                    #     atoms with mismatched non-zero pattern_id are
                                                    #     PREVENTED from firing (regardless of charge).
                                                    #     Atoms with pattern_id=0 (ambient) or matching
                                                    #     active_pattern_id fire normally. Use during
                                                    #     training to prevent cross-pattern STDP causal
                                                    #     pairs from forming. Reset active_pattern_id=0
                                                    #     during test to allow any pattern to recall.
    bridge_lock_threshold: float = 0.0              # G9: once a level-5+ molecule's strength crosses this
                                                    #     threshold, it becomes 'locked' — apply_stdp skips
                                                    #     it (no LTP / LTD / orientation update) and lateral
                                                    #     inhibition exempts it. Locked bridges form the
                                                    #     substrate's persistent multi-pattern memory: once a
                                                    #     pattern's bridges commit, subsequent training cannot
                                                    #     overwrite them, so different (visual, audio) pairs
                                                    #     coexist on disjoint bridge subsets.
                                                    #     Default 0.0 = disabled (legacy behaviour).

    # Plan C — audio I/O
    audio_io_enabled: bool = False
    audio_sample_rate: int = 16000
    audio_block_size: int = 256
    audio_fft_size: int = 512
    audio_buffer_seconds: float = 30.0
    audio_amplitude_threshold: float = 0.01
    audio_freq_min: float = 50.0
    audio_freq_max: float = 8000.0
    audio_emit_pair_band: float = 0.0   # G4: if > 0, inject a paired vibration at f * (1 + band) with
                                        #     opposite polarity for every emission. The pair satisfies
                                        #     the 8 % rule directly so atoms form quickly at the input
                                        #     port under deterministic stimuli. 0 = off (legacy).
    audio_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    audio_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    audio_output_port_origin: tuple[float, float, float] = (45.0, 0.0, 0.0)
    audio_output_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)

    # Plan D — video I/O
    video_io_enabled: bool = False
    video_fps: int = 30
    video_buffer_seconds: float = 5.0
    video_patch_grid: tuple[int, int] = (16, 16)
    video_n_orientations: int = 8
    video_amplitude_threshold: float = 0.05
    video_freq_min: float = 1000.0
    video_freq_max: float = 12000.0
    video_emit_pair_band: float = 0.0   # G4: if > 0, inject a paired vibration at f * (1 + band) with
                                        #     opposite polarity for every emission. Same semantics as
                                        #     audio_emit_pair_band.
    video_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0)
    video_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    video_webcam_index: int = 0

    # Plan E — reward channel + orchestrator
    reward_port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0)
    reward_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    reward_burst_size: int = 12
    reward_burst_freq: float = 30000.0
    agent_dt_realtime_ms: int = 17

    # Plan F — speech-loop port-to-port firing coupling
    # When > 0, atoms firing inside the audio input port deposit a small
    # burst of vibrations at the audio output port at the firing frequency.
    # Models biological auditory feedback (vocaliser hears their own
    # utterances); closes the path that lets STDP form bridges across
    # input/output port pairs.
    speech_loop_strength: float = 0.0   # 0 = off; > 0 enables coupling
    speech_loop_burst_size: int = 6     # vibrations injected per firing event
    speech_loop_jitter_hz: float = 50.0 # random-jitter bandwidth around firing freq

    # Plan A.5 — substrate performance
    slot_recycling_enabled: bool = True   # World.allocate_node reuses dead slots before extending k_count
    numba_jit_enabled: bool = True        # @njit cores for hot loops; safe with the 60³ default box
                                          # since repulsion_cell_size=100 >= max(60,60,60).

    def __post_init__(self) -> None:
        if self.numba_jit_enabled:
            max_box = max(self.box_size)
            assert self.repulsion_cell_size >= max_box, (
                f"numba_jit_enabled=True requires repulsion_cell_size >= max(box_size); "
                f"got cell={self.repulsion_cell_size}, box={self.box_size}. "
                f"The JIT core does an O(K²) all-pairs loop and diverges from the "
                f"Python spatial-grid path when cell < box. "
                f"Either widen repulsion_cell_size to {max_box} or set numba_jit_enabled=False."
            )


INITIAL_CONFIG = WorldConfig()


def load_config(path: Path | str | None) -> WorldConfig:
    if path is None:
        return WorldConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    valid_field_names = {f.name for f in fields(WorldConfig)}
    overrides = {k: v for k, v in data.items() if k in valid_field_names}
    if "box_size" in overrides and isinstance(overrides["box_size"], list):
        overrides["box_size"] = tuple(overrides["box_size"])
    # Build the final config in one shot so __post_init__ sees the complete
    # combination. If a TOML sets numba_jit_enabled=true without a matching
    # repulsion_cell_size, the guard in __post_init__ fires here.
    defaults: dict = {f.name: f.default for f in fields(WorldConfig)}  # type: ignore[assignment]
    defaults.update(overrides)
    return WorldConfig(**defaults)
