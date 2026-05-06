# DB Migrations

Numbered SQL migrations for the vibrasim research database. Apply them in order; each file is idempotent where possible.

## Sequence

| File | Purpose |
|---|---|
| `0001_initial_schema.sql` | Creates all tables, indexes, and views. Verbatim copy of `db/schema.sql`. |
| `0002_seed_amendments_and_acceptance.sql` | Seeds amendment rows and acceptance criteria. Verbatim copy of `db/seed.sql`. Uses `ON CONFLICT … DO NOTHING` — safe to re-run. |
| `0003_mark_planA_amendments_pending.sql` | No-op placeholder — reserves the slot for Plan A's merge marker. |
| `0004_mark_planA_implemented.sql` | Marks R1, R2, PHASE3-R1 as `implemented`. Run via `make db-migrate-planA-mark-implemented MERGE_SHA=<sha>` after Plan A merges to main. |

## How to apply

```bash
# First-time setup (creates schema + seeds data):
make db-migrate

# After Plan A merges to main, record the merge SHA:
make db-migrate-planA-mark-implemented MERGE_SHA=$(git rev-parse main)
```

The `make db-migrate` target applies migrations 0001–0003 in order. Migration 0004 is intentionally excluded from the default target because it requires a real merge SHA.

**Customised passwords.** The Makefile and Docker Compose default both use `vibrasim` as the password. If you changed `POSTGRES_PASSWORD` in `docker-compose.yml`, pass it explicitly: `PGPASSWORD=<your-password> make db-migrate`.

## Relationship to db/schema.sql and db/seed.sql

`db/schema.sql` and `db/seed.sql` are the **Docker init path** — mounted via `docker-compose.yml` as init scripts for the Postgres container on first start. They continue to work as before.

The `db/migrations/` directory is the **checked-in mutation path** — used when the container is already running and you need to apply incremental changes or record implementation status. The two paths are complementary: Docker init bootstraps a fresh container, migrations handle subsequent changes and audit the amendment lifecycle.

Do not remove `db/schema.sql` or `db/seed.sql`.
