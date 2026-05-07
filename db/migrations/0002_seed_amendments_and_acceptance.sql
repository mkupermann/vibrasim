-- Seed data: existing amendments + acceptance criteria as of session 4.

-- ----------------------------------------------------------------------------
-- Amendments (substrate-level proposals from session-4 teammate findings)
-- ----------------------------------------------------------------------------

INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES
    ('R1', 'Vibration injection that doesn''t no-op',
     '§4.7+',
     'Either enlarge n_vibrations_max to ~16000 with a calibrated lambda_gen, or implement a displace injection that moves a far-field alive vibration to the target zone.',
     'Phase 5 calibration agent observed that lambda_gen=0.0002 in 200³ box with n_vibrations_max=512 saturates the buffer in milliseconds; subsequent injection finds zero dead slots.',
     'proposed'),
    ('R2', 'Decay channel for level-5+ nodes',
     '§4.7',
     'Add per-tick decay probability lambda_dec_mol * dt for level-5+ nodes, reviving constituent level-4 atoms. Mirrors the existing levels 2-3 decay path.',
     'Currently molecules are permanent; ambient_regeneration only handles levels 1-3. The "inactive synapses weaken" half of §6.3 cannot occur without molecule mortality.',
     'proposed'),
    ('R3', 'Local capture / assembly rule',
     '§6.3',
     'When vibration density near a region exceeds a threshold (or when a level-4 atom is within r_2 of an active region), assemble a new level-5 store molecule at that location.',
     'CONCEPT.md §6.3 commits to "local capture from ambient" as the Hebbian strengthening mechanism but no rule operationalises it. Without this, plasticity cannot grow synapse structures.',
     'proposed'),
    ('R4', 'Activity detector for synapse-region events',
     '§6 + tools/measure_neuron_activity.py',
     'Either track level-5 count changes near outlet/inlet directly, or shrink n_vibrations_max so vibrations accumulate locally and the existing detection logic can see them.',
     'Phase 5 agent: vibrations dwell within r_io=1.8 for 0.04-0.18s, shorter than the 0.5s snapshot interval. Activity detection misses transient stimuli.',
     'proposed'),
    ('PHASE4-R1', 'k_charge[K] per-atom accumulator',
     '§4.x (new)',
     'Add a charge field per atom with exponential decay (membrane time constant τ_m). Charge accumulates from incoming vibration binding events.',
     'Phase 4 agent: substrate has no integration mechanism. Stimulation is pass-through, not summation.',
     'proposed'),
    ('PHASE4-R2', 'Threshold rule in tick()',
     '§4.x (new)',
     'When any inlet atom''s charge >= theta_fire, emit N_out vibrations at the outlet and reset charge.',
     'Phase 4 agent: substrate has no firing mechanism.',
     'proposed'),
    ('PHASE4-R3', 'Refractory rule',
     '§4.x (new)',
     'Lock charge accumulation for T_r seconds after each emission.',
     'Phase 4 acceptance criterion includes refractory period.',
     'proposed'),
    ('PHASE3-R1', 'Allow molecule + molecule binding',
     '§4.5',
     'Append (5,5)→6, (5,6)→7, etc. entries to _UPGRADE_TARGET. Currently only atoms can be added to molecules; molecules cannot fuse.',
     'Phase 3 agent: spontaneous shells need ≥12 molecules. Current calibration caps at 17. Molecule fusion would unlock condensation pathway.',
     'proposed')
ON CONFLICT (number) DO NOTHING;

-- ----------------------------------------------------------------------------
-- Acceptance criteria (one row per CONCEPT.md v2 §5 criterion)
-- ----------------------------------------------------------------------------

INSERT INTO acceptance_criteria (phase, criterion_key, description, status)
VALUES
    -- Phase 1
    (1, 'atom_forms_reproducibly',
     'Atoms form reproducibly with the calibrated TOML across multiple rng seeds',
     'partially_met'),
    (1, 'h2_spatial_sorting',
     'H2: nodes spanning multiple frequency decades show spatial sorting via §4.6 repulsion',
     'pending'),
    (1, 'ambient_density_stable',
     'Ambient density holds within ±20% with non-zero lambda_gen',
     'pending'),

    -- Phase 2
    (2, 'five_species',
     'At least 5 distinct molecule species reproducible',
     'met'),
    (2, 'small_mobile_molecules',
     'Small mobile molecules (potential neurotransmitters) and large structural molecules both observed',
     'pending'),

    -- Phase 3
    (3, 'closed_shell_forms',
     'A closed shell of bound nodes around a 3D pocket forms (constructed or spontaneous)',
     'partially_met'),
    (3, 'spontaneous_shell',
     'Spontaneous shell formation observed under simulation',
     'pending'),
    (3, 'permeability_points',
     'Selectively permeable channel points identified',
     'pending'),

    -- Phase 4
    (4, 'cluster_integrates',
     'Constructed neuron cluster shows input integration over time',
     'pending'),
    (4, 'threshold_firing',
     'Cluster fires when integrated activity exceeds a threshold',
     'pending'),
    (4, 'refractory_period',
     'Cluster has measurable refractory period after firing',
     'pending'),

    -- Phase 5
    (5, 'positive_hebbian_signal',
     'Co-active synapses develop measurably stronger connections than random pairs',
     'pending'),
    (5, 'inactivity_decay',
     'Inactive synapses weaken on minute-to-hour timescale',
     'pending'),
    (5, 'thermodynamic_stability',
     'Ambient density holds bounded fluctuation under realistic activity patterns (§6.5)',
     'pending'),

    -- Phase 6
    (6, 'pattern_recognition',
     'A 5-50 neuron network reliably maps input patterns to consistent output patterns',
     'pending'),
    (6, 'hopfield_memory',
     'Network completes partial cues to stored memories (Hopfield-style associative recall)',
     'pending'),
    (6, 'simple_learning',
     'Network response modifies under repeated stimulation',
     'pending'),

    -- Phase 7
    (7, 'carrier_selectivity',
     'Global carrier frequency selectively determines which neurons synchronise',
     'pending'),
    (7, 'lateral_inhibition',
     'Non-resonating clusters are inhibited',
     'pending'),

    -- Phase 8 (open)
    (8, 'specialised_modules',
     'Hierarchies of networks and specialised modules emerge',
     'pending')
ON CONFLICT (phase, criterion_key) DO NOTHING;
