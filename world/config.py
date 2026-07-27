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
    resonance_coupling: float = 0.0       # Kuramoto coupling for node freq synchronization (0=off)
    node_thermal_speed: float = 0.0       # Brownian speed for nodes (0=stationary). Actual speed = thermal/sqrt(level).
    atom_valence: int = 0                 # Max bindings per atom (0=unlimited). 2=linear chains, 3=branched, 4=tetrahedral.
    bridge_cooldown: float = 0.0          # Seconds after bridging before atom can bridge again (0=instant).
    bond_turnover_rate: float = 0.0       # G53: per-bridge per-second probability of spontaneous break (frees valence). >0 makes the membrane FLUID (bonds break + reform -> remodeling, healing). 0=off (rigid).
    node_freq_binding: bool = True        # Apply 8% rule to node→node binding. False = proximity-only (freq selectivity only at vibration→electron).
    atom_repulsion_k: float = 0.0         # Repulsion between non-bonded atoms. With bridge tension, produces minimal-surface membranes.
    edge_closure_k: float = 0.0           # Edge atoms (free valence) attract each other, curling sheets toward closed shells.
    curvature_k: float = 0.0              # Spontaneous curvature: push atoms away from bridge-neighbour centroid. Domes flat sheets into shells.
    # G31: selective permeability — a frequency-gated reflection barrier at the emergent shell surface.
    membrane_channel_k: float = 0.0       # 0=off (no-op). >0 enables apply_membrane_channel: reflect free vibrations crossing the shell unless frequency-compatible with the membrane.
    membrane_channel_recompute: int = 20  # Re-derive membrane geometry (centre, radius, f_mem) every N ticks.
    membrane_channel_width: float = 1.5   # Half-thickness (in length units) of the reflective shell surface band.
    membrane_channel_mode: str = "sphere" # 'sphere' = fitted-sphere reflector (G31). 'atom' = reflect off the nearest real membrane atom within r_2 (G32).
    membrane_channel_uptake: bool = False # G49: in 'atom' mode, ALSO reflect COMPATIBLE outbound vibrations (trap nutrient inside) -> active accumulation/uptake, not just exclusion.
    # G33: engineered compartment wall (CONCEPT §4.8 port topology) — reflect outbound free vibrations to keep a region's emissions local.
    compartment_k: float = 0.0            # 0=off (no-op). >0 enables apply_engineered_compartment.
    compartment_centre: tuple = (0.0, 0.0, 0.0)  # Sphere centre (engineered port boundary).
    compartment_radius: float = 0.0       # Sphere radius; outbound free vibrations are reflected back inside.
    compartment_mode: str = "clamp"       # 'clamp' (G33, snap to R*0.999) or 'soft' (G35, revert the overshoot only — avoids a dense boundary layer that suppresses the write).
    compartments: tuple = ()              # G40: multiple engineered compartments, each (cx,cy,cz,R). When set, overrides the single compartment_centre/radius.
    # PRIM1-D2: reflecting midplane slab (free vibrations cannot cross x = midplane_wall_x).
    midplane_wall_enabled: bool = False
    midplane_wall_x: float = 40.0
    # PRIM2: internal local write (no free-vibration inject). Defaults OFF.
    ilw_enabled: bool = False
    ilw_radius: float = 8.0
    ilw_delta_strength: float = 0.5
    # PRIM3: exponential leak of level≥4 k_strength toward 1.0.
    # 0.0 = off (legacy). Units: seconds (tau in s ← 1+(s-1)*exp(-dt/tau)).
    ilw_strength_decay_tau: float = 0.0
    # PRIM4: multi-slot ILW — allocate new L4 when nearest band differs.
    ilw_multislot_enabled: bool = False
    ilw_multislot_rel_freq: float = 0.35
    # PRIM5: exclusive bridge between the two atoms just dual-written.
    ilw_pair_link_enabled: bool = False
    ilw_pair_link_delta: float = 1.0
    # PRIM8: kill other bridges from each endpoint when forming a pair link.
    ilw_pair_replace_enabled: bool = False
    # PRIM6: latched activity from bridge charge prop (separate from membrane).
    # Default OFF. tau<=0 with enabled = no decay; tau>0 = exp decay seconds.
    charge_latch_enabled: bool = False
    charge_latch_tau: float = 0.0
    # PRIM7: kill free vibs on wrong side of midplane by frequency band.
    midplane_sideband_cull_enabled: bool = False
    midplane_gate_f_mid: float = 1581.1388300841897  # sqrt(500*5000)
    # PRIM9: bridge prop only if ≥2 distinct firers hit same target this tick.
    coincidence_and_enabled: bool = False
    # PRIM10: on fire, scale down charge of other L4 within radius (0=off).
    fire_inhibit_radius: float = 0.0
    fire_inhibit_frac: float = 0.5
    # PRIM11: on fire, zero k_latch of other L4 within radius (0=off).
    fire_zero_latch_radius: float = 0.0
    # PRIM12: on fire, kill bridges touching nodes within radius of emitter (0=off).
    fire_kill_bridge_radius: float = 0.0
    # PRIM13: on fire, scale b_strength of nearby bridges (0 radius=off).
    fire_weaken_bridge_radius: float = 0.0
    fire_weaken_bridge_frac: float = 1.0
    flux_plasticity_rate: float = 0.0     # Bridge strengthening rate from vibration flux (0=off). Plasticity from physics.
    flux_threshold: float = 2.0           # Flux above this potentiates a bridge, below depresses.
    flux_decay: float = 0.05              # Strength decay per second for low-flux bridges.
    flux_max_strength: float = 10.0       # Max bridge strength.
    # Bistable plasticity (BET-089): double-well bridge strength = memory latch.
    bistable_rate: float = 0.0            # Master rate (0=off).
    bistable_low: float = 1.0             # Weak stable state.
    bistable_mid: float = 3.0             # Unstable barrier.
    bistable_high: float = 6.0            # Strong stable state (latched).
    bistable_well_k: float = 0.02         # Double-well restoring strength.
    bistable_flux_gain: float = 0.02      # How hard flux pushes strength up.
    bistable_flux_ref: float = 30.0       # Flux reference (above this = drive up).
    # Structural anchoring (BET-090): freeze mature lattice sites so bridges
    # keep stable place-identity (the missing ingredient for selective memory).
    anchor_damping: float = 0.0           # Velocity multiplier for mature atoms (0=off, e.g. 0.7=stiffen).
    anchor_bond_min: int = 2              # Min bond count to count as a mature interior site.
    anchor_age: float = 50.0              # Sim-seconds at bond_min before a site freezes.
    # Valence commitment (BET-091): a bonded atom resists fusion, so the lattice
    # persists. Level-4 atoms with k_bond_count >= this are skipped as fusion
    # partners in bind_nodes_upward. 0 = off (atoms fuse freely, as before).
    fusion_bond_block: int = 0
    # BET-092: bistable drive reference. 'relative' = drive vs moving mean flux
    # (BET-089 v2); 'absolute' = drive vs fixed bistable_flux_ref, which latches
    # on a populated lattice where the moving mean washes out the stimulus.
    bistable_drive_mode: str = 'relative'
    # BET-097: rectify the drive (one-sided). When True, flux only drives strength
    # UP (write); the bistable well alone holds or decays it. Prevents zero-flux
    # from erasing a latched memory. Default False preserves prior behaviour.
    bistable_drive_rectified: bool = False
    # BET-099: firing-coincidence (Hebbian) bridge plasticity. When two bridged
    # atoms fire within tau_LTP, the bridge is driven over the bistable barrier;
    # the well holds it. A turnover-robust write signal (vs fragile flux state).
    corr_plasticity_rate: float = 0.0     # master rate (0 = off)
    corr_potentiation: float = 1.0        # co-firing drive magnitude (over-barrier push)
    # BET-103: engineered modular compartment. If > 0, an x-plane wall: atoms only
    # integrate charge from vibrations on their own side, and co-firing
    # potentiation cannot cross it. Contains activity percolation (CONCEPT 4.8
    # engineered modularity). 0 = off (homogeneous substrate).
    compartment_boundary: float = 0.0
    # BET-105: non-broadcast write — a firing atom deposits charge into its
    # bridged neighbours (gain × bridge strength), so co-activation travels along
    # the bridge graph instead of omnidirectional emission. 0 = off. Pair n_emit≈0.
    bridge_charge_prop_rate: float = 0.0
    # BET-107: graded propagation — only bridges with strength >= this carry the
    # bridge-charge write. Latched (written) bridges self-sustain recall; blank
    # bridges carry nothing, so unwritten regions stay silent. 0 = ungated.
    bridge_prop_min_strength: float = 0.0
    # BET-108: consolidation — once a bridge strength reaches this, lock it at the
    # strong well (immune to decay/turnover), so a written memory cannot fade in
    # recall. 0 = off. Control bridges never reach it, so are never locked.
    bridge_consolidate_threshold: float = 0.0

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
    global_wta_k: int = 0                           # G65: global k-winner-take-all lateral inhibition — only the top-K most-charged atoms fire each tick (0=off). Self-limiting write: only strongly-driven atoms fire.
    bridge_leak_rate: float = 0.0                   # G69: LEAKY write — continuous downward pull on bridge strength toward bistable_low, so a bridge stays high only while CONTINUOUSLY reinforced (0=off). Intermittent control co-firing decays; continuous stim co-firing holds + consolidates.
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
