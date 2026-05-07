-- vibrasim research database
-- Run after creating an empty database (e.g. CREATE DATABASE vibrasim;)
-- See db/README.md for setup.

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- ----------------------------------------------------------------------------
-- sessions: a research session is a coherent block of work
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_number  INTEGER NOT NULL UNIQUE,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    researcher      TEXT NOT NULL,
    title           TEXT NOT NULL,
    question        TEXT,                   -- the research question
    hypothesis      TEXT,                   -- what we expected
    outcome         TEXT,                   -- what we found
    status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'paused', 'completed', 'abandoned')),
    parent_session  UUID REFERENCES sessions(id),
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS sessions_started_idx ON sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS sessions_status_idx ON sessions(status);

-- ----------------------------------------------------------------------------
-- configs: a WorldConfig snapshot. Stored as JSONB so the schema doesn't
-- have to change when WorldConfig fields change.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,           -- human label, e.g. 'session3b_molecules'
    params          JSONB NOT NULL,          -- all WorldConfig fields
    toml_path       TEXT,                    -- if persisted, the path
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS configs_session_idx ON configs(session_id);
CREATE INDEX IF NOT EXISTS configs_name_idx ON configs(name);

-- ----------------------------------------------------------------------------
-- runs: a single simulation execution
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    config_id       UUID NOT NULL REFERENCES configs(id),
    rng_seed        INTEGER NOT NULL,
    duration_s      DOUBLE PRECISION NOT NULL,    -- simulated seconds
    snapshot_every  DOUBLE PRECISION,             -- simulated seconds between snapshots
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    wall_s          DOUBLE PRECISION,             -- real seconds elapsed
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    snapshot_dir    TEXT,                         -- absolute path
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS runs_session_idx ON runs(session_id);
CREATE INDEX IF NOT EXISTS runs_config_idx ON runs(config_id);
CREATE INDEX IF NOT EXISTS runs_started_idx ON runs(started_at DESC);

-- ----------------------------------------------------------------------------
-- observations: per-snapshot counts and metrics
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS observations (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    simulated_t     DOUBLE PRECISION NOT NULL,
    n_vibrations_alive  INTEGER,
    n_electrons     INTEGER,
    n_pairs         INTEGER,
    n_triads        INTEGER,
    n_atoms         INTEGER,
    n_molecule_l5   INTEGER,
    n_molecule_l6   INTEGER,
    n_molecule_l7   INTEGER,
    n_molecule_l8   INTEGER,
    n_molecule_higher INTEGER,
    total_vibrations INTEGER,
    ambient_density DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS observations_run_idx ON observations(run_id);
CREATE INDEX IF NOT EXISTS observations_run_t_idx ON observations(run_id, simulated_t);

-- ----------------------------------------------------------------------------
-- species_observations: molecule-species fingerprints per run snapshot
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS species_observations (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    simulated_t     DOUBLE PRECISION NOT NULL,
    species_fingerprint TEXT NOT NULL,           -- e.g. 'A33', 'A3344'
    count           INTEGER NOT NULL,
    first_seen      BOOLEAN DEFAULT FALSE        -- this is the first occurrence in the run
);

CREATE INDEX IF NOT EXISTS species_run_idx ON species_observations(run_id);
CREATE INDEX IF NOT EXISTS species_fp_idx ON species_observations(species_fingerprint);

-- ----------------------------------------------------------------------------
-- firing_events: Phase 4+ neuron firing events
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS firing_events (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    neuron_id       INTEGER NOT NULL,            -- index in the run's neuron_definitions
    start_t         DOUBLE PRECISION NOT NULL,
    peak_t          DOUBLE PRECISION NOT NULL,
    peak_count      INTEGER NOT NULL,
    duration_s      DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS firing_run_idx ON firing_events(run_id);

-- ----------------------------------------------------------------------------
-- synapse_measurements: Phase 5 plasticity metrics per run
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS synapse_measurements (
    id                    BIGSERIAL PRIMARY KEY,
    run_id                UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    pre_neuron_id         INTEGER NOT NULL,
    post_neuron_id        INTEGER NOT NULL,
    growth_rate_active    DOUBLE PRECISION,
    growth_rate_inactive  DOUBLE PRECISION,
    hebbian_signal        DOUBLE PRECISION,
    n_co_active_intervals INTEGER,
    n_inactive_intervals  INTEGER,
    notes                 TEXT
);

CREATE INDEX IF NOT EXISTS synapse_run_idx ON synapse_measurements(run_id);

-- ----------------------------------------------------------------------------
-- amendments: substrate amendments to CONCEPT.md
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS amendments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    number          TEXT NOT NULL UNIQUE,        -- e.g. 'R1', 'R2', §4.8'
    title           TEXT NOT NULL,
    spec_section    TEXT,                        -- e.g. '§4.7 ambient regeneration'
    description     TEXT NOT NULL,
    motivation      TEXT,                        -- the empirical reason
    proposed_session UUID REFERENCES sessions(id),
    proposed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          TEXT NOT NULL DEFAULT 'proposed'
                        CHECK (status IN ('proposed', 'in_progress', 'implemented', 'rejected', 'deferred')),
    decided_session UUID REFERENCES sessions(id),
    decided_at      TIMESTAMPTZ,
    impl_commit     TEXT,                        -- git SHA when implemented
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS amendments_status_idx ON amendments(status);
CREATE INDEX IF NOT EXISTS amendments_number_idx ON amendments(number);

-- ----------------------------------------------------------------------------
-- acceptance_criteria: per-phase acceptance status
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS acceptance_criteria (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase           INTEGER NOT NULL,            -- 1..8
    criterion_key   TEXT NOT NULL,               -- e.g. 'atom_forms', 'five_species'
    description     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'partially_met', 'met', 'not_reachable')),
    evidence_run_id UUID REFERENCES runs(id),
    evidence_notes  TEXT,
    last_updated    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (phase, criterion_key)
);

CREATE INDEX IF NOT EXISTS acceptance_phase_idx ON acceptance_criteria(phase);

-- ----------------------------------------------------------------------------
-- session_notes: free-form notes attached to a session
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS session_notes (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    body            TEXT NOT NULL,
    tag             TEXT                         -- 'observation', 'decision', 'todo'
);

CREATE INDEX IF NOT EXISTS notes_session_idx ON session_notes(session_id);

-- ----------------------------------------------------------------------------
-- Convenience views
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    s.id,
    s.session_number,
    s.title,
    s.researcher,
    s.status,
    s.started_at,
    s.ended_at,
    COUNT(DISTINCT c.id) AS n_configs,
    COUNT(DISTINCT r.id) AS n_runs,
    COUNT(DISTINCT n.id) AS n_notes
FROM sessions s
LEFT JOIN configs c ON c.session_id = s.id
LEFT JOIN runs r ON r.session_id = s.id
LEFT JOIN session_notes n ON n.session_id = s.id
GROUP BY s.id;

CREATE OR REPLACE VIEW v_acceptance_dashboard AS
SELECT
    phase,
    COUNT(*) AS n_total,
    COUNT(*) FILTER (WHERE status = 'met') AS n_met,
    COUNT(*) FILTER (WHERE status = 'partially_met') AS n_partial,
    COUNT(*) FILTER (WHERE status = 'pending') AS n_pending,
    COUNT(*) FILTER (WHERE status = 'not_reachable') AS n_blocked
FROM acceptance_criteria
GROUP BY phase
ORDER BY phase;
