# vibrasim research database

PostgreSQL schema and seed data for the vibrasim research dashboard.

## Schema overview

| Table | Purpose |
|---|---|
| `sessions` | A coherent block of research work (one question, one outcome). |
| `configs` | A `WorldConfig` snapshot. JSONB params so the schema doesn't follow code. |
| `runs` | A single simulation execution against a config. |
| `observations` | Per-snapshot counts and metrics for a run. |
| `species_observations` | Molecule species fingerprints per snapshot. |
| `firing_events` | Phase 4+ neuron firing events. |
| `synapse_measurements` | Phase 5 plasticity metrics per pre/post pair. |
| `amendments` | Substrate amendments to `CONCEPT.md` and their decisions. |
| `acceptance_criteria` | Per-phase acceptance status. |
| `session_notes` | Free-form notes attached to a session. |

Two convenience views: `v_session_summary`, `v_acceptance_dashboard`.

## Setup — Docker (recommended)

From the repo root:

```bash
docker compose up -d postgres
```

The compose file runs `schema.sql` and `seed.sql` automatically on first
container start (via `docker-entrypoint-initdb.d`).

To reset the database:

```bash
docker compose down -v
docker compose up -d postgres
```

## Setup — local PostgreSQL

```bash
psql postgres -c "CREATE DATABASE vibrasim;"
psql postgres -c "CREATE USER vibrasim WITH PASSWORD 'vibrasim';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE vibrasim TO vibrasim;"

psql -U vibrasim -d vibrasim -f db/schema.sql
psql -U vibrasim -d vibrasim -f db/seed.sql
```

## Connection string

The dashboard and helpers read `VIBRASIM_DSN`. Default:

```
host=localhost port=5433 dbname=vibrasim user=vibrasim password=vibrasim
```

(Port `5433` keeps the docker-managed Postgres from colliding with any
locally-installed Postgres on `5432`. If you don't run a host Postgres,
edit `docker-compose.yml` and `app/db.py` to use `5432`.)

Override via environment variable for non-default deployments.

## Running the Streamlit dashboard

```bash
docker compose up -d
# open http://localhost:8502
```

Or locally:

```bash
pip install "streamlit>=1.40" "psycopg[binary]>=3.2" "pandas>=2.2"
streamlit run app/main.py --server.port 8502
```

(Port `8502` keeps the dashboard from colliding with any other Streamlit
already running on the default `8501`.)

## Re-seeding amendments and criteria

`seed.sql` uses plain `INSERT` (no `ON CONFLICT`). To re-run it on an existing
database, truncate first:

```bash
psql -U vibrasim -d vibrasim -c "TRUNCATE amendments, acceptance_criteria CASCADE;"
psql -U vibrasim -d vibrasim -f db/seed.sql
```

Sessions, runs, and observations are not affected.
