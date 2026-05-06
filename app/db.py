"""Database connection + query helpers for the vibrasim research dashboard.

Uses psycopg3 directly (no ORM). Connection details come from environment
variables matching libpq conventions.
"""
from __future__ import annotations
import json
import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row


def get_dsn() -> str:
    """Return the PostgreSQL DSN from environment variables."""
    return os.environ.get(
        "VIBRASIM_DSN",
        "host=localhost port=5433 dbname=vibrasim user=vibrasim password=vibrasim",
    )


@contextmanager
def get_conn() -> Iterator[Connection]:
    """Yield a connection. Caller must commit or rollback."""
    conn = psycopg.connect(get_dsn(), row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------- sessions ---

def list_sessions(limit: int = 100) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM v_session_summary
            ORDER BY started_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
        return list(rows)


def get_session(session_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM sessions WHERE id = %s",
            (session_id,),
        ).fetchone()


def create_session(researcher: str, title: str, question: str | None = None,
                   hypothesis: str | None = None, parent_session: str | None = None) -> str:
    """Create a new session. Returns the new session's UUID."""
    with get_conn() as conn:
        # Determine next session_number
        n = conn.execute(
            "SELECT COALESCE(MAX(session_number), 0) + 1 AS next FROM sessions"
        ).fetchone()["next"]
        row = conn.execute(
            """
            INSERT INTO sessions (session_number, researcher, title, question, hypothesis, parent_session)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (n, researcher, title, question, hypothesis, parent_session),
        ).fetchone()
        conn.commit()
        return str(row["id"])


def update_session(session_id: str, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [session_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE sessions SET {cols} WHERE id = %s", values)
        conn.commit()


def add_note(session_id: str, body: str, tag: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO session_notes (session_id, body, tag) VALUES (%s, %s, %s)",
            (session_id, body, tag),
        )
        conn.commit()


def list_notes(session_id: str) -> list[dict]:
    with get_conn() as conn:
        return list(conn.execute(
            "SELECT * FROM session_notes WHERE session_id = %s ORDER BY created_at DESC",
            (session_id,),
        ).fetchall())


# ---------------------------------------------------------------- configs ---

def list_configs(session_id: str | None = None) -> list[dict]:
    with get_conn() as conn:
        if session_id:
            return list(conn.execute(
                "SELECT * FROM configs WHERE session_id = %s ORDER BY created_at DESC",
                (session_id,),
            ).fetchall())
        return list(conn.execute(
            "SELECT * FROM configs ORDER BY created_at DESC LIMIT 100"
        ).fetchall())


def save_config(session_id: str, name: str, params: dict,
                toml_path: str | None = None, notes: str | None = None) -> str:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO configs (session_id, name, params, toml_path, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (session_id, name, json.dumps(params), toml_path, notes),
        ).fetchone()
        conn.commit()
        return str(row["id"])


def get_config(config_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM configs WHERE id = %s", (config_id,)).fetchone()


# ---------------------------------------------------------------- runs ---

def create_run(session_id: str, config_id: str, rng_seed: int, duration_s: float,
               snapshot_every: float | None = None,
               snapshot_dir: str | None = None) -> str:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO runs (session_id, config_id, rng_seed, duration_s,
                              snapshot_every, snapshot_dir, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id
            """,
            (session_id, config_id, rng_seed, duration_s, snapshot_every, snapshot_dir),
        ).fetchone()
        conn.commit()
        return str(row["id"])


def update_run_status(run_id: str, status: str, wall_s: float | None = None,
                      ended_at_now: bool = False, notes: str | None = None) -> None:
    sets = ["status = %s"]
    values: list[Any] = [status]
    if wall_s is not None:
        sets.append("wall_s = %s")
        values.append(wall_s)
    if ended_at_now:
        sets.append("ended_at = NOW()")
    if notes is not None:
        sets.append("notes = %s")
        values.append(notes)
    values.append(run_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE runs SET {', '.join(sets)} WHERE id = %s", values)
        conn.commit()


def list_runs(session_id: str | None = None, limit: int = 100) -> list[dict]:
    with get_conn() as conn:
        if session_id:
            return list(conn.execute(
                """
                SELECT r.*, c.name AS config_name
                FROM runs r JOIN configs c ON c.id = r.config_id
                WHERE r.session_id = %s
                ORDER BY r.started_at DESC LIMIT %s
                """,
                (session_id, limit),
            ).fetchall())
        return list(conn.execute(
            """
            SELECT r.*, c.name AS config_name
            FROM runs r JOIN configs c ON c.id = r.config_id
            ORDER BY r.started_at DESC LIMIT %s
            """,
            (limit,),
        ).fetchall())


def get_run(run_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT r.*, c.name AS config_name, c.params AS config_params
            FROM runs r JOIN configs c ON c.id = r.config_id
            WHERE r.id = %s
            """,
            (run_id,),
        ).fetchone()


# ----------------------------------------------------------- observations ---

def insert_observation(run_id: str, simulated_t: float, **counts) -> None:
    cols = ["run_id", "simulated_t"] + list(counts.keys())
    vals = [run_id, simulated_t] + list(counts.values())
    placeholders = ", ".join(["%s"] * len(cols))
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO observations ({', '.join(cols)}) VALUES ({placeholders})",
            vals,
        )
        conn.commit()


def get_observations(run_id: str) -> list[dict]:
    with get_conn() as conn:
        return list(conn.execute(
            "SELECT * FROM observations WHERE run_id = %s ORDER BY simulated_t",
            (run_id,),
        ).fetchall())


def delete_observations(run_id: str) -> int:
    """Delete all observations + species for a run. Returns number removed."""
    with get_conn() as conn:
        n = conn.execute(
            "DELETE FROM observations WHERE run_id = %s", (run_id,)
        ).rowcount
        conn.execute(
            "DELETE FROM species_observations WHERE run_id = %s", (run_id,)
        )
        conn.commit()
        return int(n or 0)


def insert_species_observations(run_id: str, simulated_t: float,
                                species_counts: dict[str, int],
                                first_seen: set[str] | None = None) -> None:
    first_seen = first_seen or set()
    rows = [
        (run_id, simulated_t, fp, count, fp in first_seen)
        for fp, count in species_counts.items()
    ]
    if not rows:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO species_observations
                    (run_id, simulated_t, species_fingerprint, count, first_seen)
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows,
            )
        conn.commit()


def get_species(run_id: str) -> list[dict]:
    with get_conn() as conn:
        return list(conn.execute(
            """
            SELECT species_fingerprint, MAX(count) AS max_count,
                   MIN(simulated_t) AS first_seen_t
            FROM species_observations WHERE run_id = %s
            GROUP BY species_fingerprint
            ORDER BY first_seen_t
            """,
            (run_id,),
        ).fetchall())


# ---------------------------------------------------------------- amendments ---

def list_amendments(status: str | None = None) -> list[dict]:
    with get_conn() as conn:
        if status:
            return list(conn.execute(
                "SELECT * FROM amendments WHERE status = %s ORDER BY proposed_at DESC",
                (status,),
            ).fetchall())
        return list(conn.execute(
            "SELECT * FROM amendments ORDER BY proposed_at DESC"
        ).fetchall())


def get_amendment(amendment_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM amendments WHERE id = %s",
            (amendment_id,),
        ).fetchone()


def create_amendment(number: str, title: str, description: str,
                     spec_section: str | None = None, motivation: str | None = None,
                     proposed_session: str | None = None) -> str:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO amendments (number, title, description, spec_section, motivation, proposed_session)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (number, title, description, spec_section, motivation, proposed_session),
        ).fetchone()
        conn.commit()
        return str(row["id"])


def update_amendment_status(amendment_id: str, status: str,
                            decided_session: str | None = None,
                            impl_commit: str | None = None,
                            notes: str | None = None) -> None:
    sets = ["status = %s"]
    vals: list[Any] = [status]
    if status in ("implemented", "rejected", "deferred"):
        sets.append("decided_at = NOW()")
        if decided_session:
            sets.append("decided_session = %s")
            vals.append(decided_session)
    if impl_commit:
        sets.append("impl_commit = %s")
        vals.append(impl_commit)
    if notes is not None:
        sets.append("notes = %s")
        vals.append(notes)
    vals.append(amendment_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE amendments SET {', '.join(sets)} WHERE id = %s", vals)
        conn.commit()


# --------------------------------------------------- acceptance criteria ---

def list_acceptance_criteria(phase: int | None = None) -> list[dict]:
    with get_conn() as conn:
        if phase is not None:
            return list(conn.execute(
                "SELECT * FROM acceptance_criteria WHERE phase = %s ORDER BY criterion_key",
                (phase,),
            ).fetchall())
        return list(conn.execute(
            "SELECT * FROM acceptance_criteria ORDER BY phase, criterion_key"
        ).fetchall())


def get_acceptance_dashboard() -> list[dict]:
    with get_conn() as conn:
        return list(conn.execute("SELECT * FROM v_acceptance_dashboard").fetchall())


def update_acceptance(criterion_id: str, status: str, evidence_run_id: str | None = None,
                     evidence_notes: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE acceptance_criteria
            SET status = %s, evidence_run_id = %s, evidence_notes = %s, last_updated = NOW()
            WHERE id = %s
            """,
            (status, evidence_run_id, evidence_notes, criterion_id),
        )
        conn.commit()


# ---------------------------------------------------------------- health ---

def health_check() -> tuple[bool, str]:
    """Return (ok, message)."""
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1").fetchone()
        return True, "connected"
    except Exception as e:
        return False, str(e)
