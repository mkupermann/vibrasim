"""Run report — natural-language narrative + PDF rendering.

A "report" describes one simulation run in plain English: the setup, the
sequence of events that emerged, the molecule species observed, what the
run did *not* reach, and how the evidence relates to acceptance criteria.

Output paths:
    build_report(run_id) -> dict
    render_markdown(report) -> str   (for Streamlit)
    render_pdf(report) -> bytes      (for download)
"""
from __future__ import annotations
import io
import json
from datetime import datetime
from typing import Any

from app.db import (
    get_run, get_observations, get_species, get_session,
    list_acceptance_criteria, list_notes,
)


# ---------------------------------------------------------------- analysis ---

# Threshold for "the structure has appeared" — a single observation is noise.
EMERGENCE_THRESHOLD = 1


def _first_t_above(rows: list[dict], col: str, threshold: int = EMERGENCE_THRESHOLD) -> float | None:
    """Find the first simulated_t at which `col` is greater than the threshold."""
    for r in rows:
        v = r.get(col)
        if v is not None and v > threshold:
            return float(r["simulated_t"])
    return None


def _max_value(rows: list[dict], col: str) -> tuple[float, int] | None:
    """Return (t_at_max, max_value) for `col`, or None if the column is empty."""
    best = None
    for r in rows:
        v = r.get(col)
        if v is None:
            continue
        if best is None or v > best[1]:
            best = (float(r["simulated_t"]), int(v))
    if best and best[1] <= 0:
        return None
    return best


def _last_value(rows: list[dict], col: str) -> int | None:
    if not rows:
        return None
    for r in reversed(rows):
        v = r.get(col)
        if v is not None:
            return int(v)
    return None


def _phase_reached(observations: list[dict]) -> int:
    """Return the highest phase the run produced evidence for (1-3)."""
    if not observations:
        return 0
    if any((r.get("n_molecule_l5") or 0) > 0 for r in observations):
        return 3  # molecules present (Phase 2/3 territory; treat as 3 if l6+ also)
    if any((r.get("n_atoms") or 0) > 0 for r in observations):
        return 2  # atoms but no molecules
    if any((r.get("n_pairs") or 0) > 0 or (r.get("n_triads") or 0) > 0 for r in observations):
        return 1
    return 0


# ---------------------------------------------------------------- builder ---

def build_report(run_id: str) -> dict[str, Any]:
    """Pull all data for a run and produce a structured report dict."""
    run = get_run(run_id)
    if not run:
        raise ValueError(f"run {run_id} not found")

    session = get_session(str(run["session_id"]))
    observations = get_observations(run_id)
    species = get_species(run_id)
    acceptance = list_acceptance_criteria()
    session_notes = list_notes(str(run["session_id"]))

    params = run.get("config_params") or {}
    if isinstance(params, str):
        params = json.loads(params)

    # Milestones in the timeseries
    milestones: list[dict] = []
    if observations:
        for label, col in [
            ("first electron pair", "n_pairs"),
            ("first triad", "n_triads"),
            ("first atom", "n_atoms"),
            ("first level-5 molecule", "n_molecule_l5"),
            ("first level-6 molecule", "n_molecule_l6"),
            ("first level-7 molecule", "n_molecule_l7"),
            ("first level-8 molecule", "n_molecule_l8"),
        ]:
            t = _first_t_above(observations, col, EMERGENCE_THRESHOLD)
            if t is not None:
                milestones.append({"label": label, "t": t, "column": col})

    # Peak counts
    peaks: dict[str, dict] = {}
    if observations:
        for col, label in [
            ("n_vibrations_alive", "vibrations alive"),
            ("n_atoms", "atoms"),
            ("n_molecule_l5", "level-5 molecules"),
            ("n_molecule_l6", "level-6 molecules"),
            ("n_molecule_l7", "level-7 molecules"),
            ("n_molecule_l8", "level-8 molecules"),
            ("n_molecule_higher", "higher-order molecules"),
        ]:
            p = _max_value(observations, col)
            if p:
                peaks[col] = {"label": label, "t": p[0], "value": p[1]}

    # Final state — what was alive at run end
    final_state = {}
    if observations:
        for col in ["n_vibrations_alive", "n_atoms", "n_molecule_l5",
                    "n_molecule_l6", "n_molecule_l7", "n_molecule_l8",
                    "n_molecule_higher"]:
            v = _last_value(observations, col)
            if v is not None:
                final_state[col] = v

    phase = _phase_reached(observations)

    # Phase relevance for acceptance comparison
    relevant_criteria = [c for c in acceptance if c["phase"] in (1, 2, 3) and phase >= c["phase"]]

    # Compose narrative
    narrative = _compose_narrative(
        run=run, session=session, params=params,
        observations=observations, species=species,
        milestones=milestones, peaks=peaks, final_state=final_state,
        phase=phase,
    )

    return {
        "run": run,
        "session": session,
        "params": params,
        "observations": observations,
        "species": species,
        "milestones": milestones,
        "peaks": peaks,
        "final_state": final_state,
        "phase_reached": phase,
        "relevant_criteria": relevant_criteria,
        "session_notes": session_notes,
        "narrative": narrative,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------- narrative ---

def _fmt_time(t: float) -> str:
    if t < 1.0:
        return f"{t * 1000:.0f} ms"
    if t < 60:
        return f"{t:.2f} s"
    return f"{t / 60:.2f} min"


def _compose_narrative(*, run, session, params, observations, species,
                       milestones, peaks, final_state, phase) -> dict[str, str]:
    """Return a dict of named prose paragraphs."""
    n = run.get("rng_seed")
    duration = run.get("duration_s")
    wall = run.get("wall_s")
    config_name = run.get("config_name") or "an unnamed config"
    box = params.get("box_size") or [params.get("box_size_x"), params.get("box_size_y"), params.get("box_size_z")]
    box_str = "×".join(str(int(b)) for b in box if b) if box else "default"
    n_init = params.get("n_initial_vibrations", "the configured number of")
    lambda_gen = params.get("lambda_gen")
    lambda_dec = params.get("lambda_dec")

    # ----- Setup paragraph
    setup_lines = [
        f"This run executed configuration **{config_name}** with random seed **{n}** "
        f"for **{duration:g} simulated seconds** of physical time."
    ]
    if wall:
        setup_lines.append(f"Wall-clock execution took {wall:.1f} s.")
    setup_lines.append(
        f"The simulation began with {n_init} vibrations distributed across a "
        f"{box_str} periodic-boundary cube."
    )
    if lambda_gen is not None or lambda_dec is not None:
        setup_lines.append(
            f"The ambient regeneration channel ran with "
            f"lambda_gen = {lambda_gen} and lambda_dec = {lambda_dec}, "
            "balancing spontaneous vibration generation against passive decay."
        )
    setup = " ".join(setup_lines)

    # ----- Emergence paragraph
    if not observations:
        emergence = (
            "No snapshot data was recorded for this run, so the chronology of structure "
            "formation cannot be reconstructed from the database alone."
        )
    elif not milestones:
        emergence = (
            "Across the full simulated duration, no electron pair, triad, atom or molecule "
            "passed the emergence threshold. The substrate remained at the level of "
            "free-flying vibrations."
        )
    else:
        # Build a chronological narrative
        ms_sorted = sorted(milestones, key=lambda m: m["t"])
        parts = []
        for i, m in enumerate(ms_sorted):
            if i == 0:
                parts.append(
                    f"The {m['label']} appeared at t = {_fmt_time(m['t'])}"
                )
            else:
                parts.append(
                    f"the {m['label']} followed at t = {_fmt_time(m['t'])}"
                )
        chrono = "; ".join(parts) + "."
        emergence = (
            f"Chronology of structure formation: {chrono} "
            "Each transition required a sustained alignment of frequency-matched vibrations "
            "before the next level of structure could bind."
        )

    # ----- Peak counts paragraph
    if peaks:
        peak_lines = []
        for col, p in peaks.items():
            if p["value"] <= 0:
                continue
            peak_lines.append(
                f"{p['label']} peaked at **{p['value']}** around t = {_fmt_time(p['t'])}"
            )
        peaks_p = "; ".join(peak_lines) + "."
        peaks_p = (
            "Peak populations across the run: " + peaks_p[0].lower() + peaks_p[1:]
        )
    else:
        peaks_p = "No structural populations were recorded."

    # ----- Species paragraph
    if not species:
        species_p = "No molecule species were identified."
    else:
        sp_sorted = sorted(species, key=lambda s: s["first_seen_t"])
        if len(sp_sorted) == 1:
            s = sp_sorted[0]
            species_p = (
                f"A single molecule species was identified: **{s['species_fingerprint']}** "
                f"(first seen at t = {_fmt_time(s['first_seen_t'])}, "
                f"peak count {s['max_count']})."
            )
        else:
            top = sp_sorted[:8]
            head = ", ".join(
                f"{s['species_fingerprint']} (t={_fmt_time(s['first_seen_t'])}, "
                f"max {s['max_count']})"
                for s in top
            )
            tail = ""
            if len(sp_sorted) > 8:
                tail = f" and {len(sp_sorted) - 8} further species."
            species_p = (
                f"**{len(sp_sorted)}** distinct molecule species emerged. "
                f"In order of first appearance: {head}.{tail}"
            )

    # ----- Phase + acceptance paragraph
    phase_descriptions = {
        0: "no structure formed; the run stayed in the free-vibration regime",
        1: "the run reached Phase 1 — pairs and triads bound, but no atom-level closure was observed",
        2: "the run reached Phase 1 (atoms): the four-fold closure expected of an atom is present in the snapshots",
        3: "the run reached Phase 2 (molecules): atoms further bound into level-5+ structures, providing the substrate molecules require",
    }
    phase_p = (
        f"In CONCEPT.md terms, {phase_descriptions[phase]}. "
        "Higher phases (membranes, neurons, plasticity, networks, attention) were not "
        "exercised by this configuration and remain open work."
    )

    # ----- Notes paragraph
    notes = run.get("notes") or ""
    if session and session.get("question"):
        question_p = (
            f"This run sat under session #{session['session_number']} — "
            f"*{session['title']}* — whose research question was: "
            f"\"{session['question']}\""
        )
    else:
        question_p = ""

    closing = (
        "Read alongside the snapshot timeseries below, this report should be enough to "
        "reproduce the run's substrate behaviour and judge whether the configuration is "
        "ready to advance to the next phase."
    )

    return {
        "setup": setup,
        "emergence": emergence,
        "peaks": peaks_p,
        "species": species_p,
        "phase": phase_p,
        "context": question_p,
        "operator_notes": notes,
        "closing": closing,
    }


# ---------------------------------------------------------------- markdown ---

def render_markdown(report: dict) -> str:
    """Render the report as Markdown for Streamlit display."""
    run = report["run"]
    session = report["session"]
    n = report["narrative"]

    parts: list[str] = []
    parts.append(f"## Run report — {str(run['id'])[:8]}")
    parts.append("")
    parts.append(
        f"_Generated {report['generated_at']} · session "
        f"#{session['session_number']} · config **{run.get('config_name')}** · "
        f"seed **{run.get('rng_seed')}** · duration **{run.get('duration_s'):g} s**_"
    )
    parts.append("")

    if n["context"]:
        parts.append(n["context"])
        parts.append("")

    parts.append("### Setup")
    parts.append(n["setup"])
    parts.append("")

    parts.append("### Emergence")
    parts.append(n["emergence"])
    parts.append("")

    parts.append("### Peak populations")
    parts.append(n["peaks"])
    parts.append("")

    parts.append("### Species")
    parts.append(n["species"])
    parts.append("")

    parts.append("### Phase reached")
    parts.append(n["phase"])
    parts.append("")

    if n["operator_notes"]:
        parts.append("### Operator notes")
        parts.append(n["operator_notes"])
        parts.append("")

    if report["relevant_criteria"]:
        parts.append("### Acceptance criteria touched by this run")
        for c in report["relevant_criteria"]:
            parts.append(
                f"- **Phase {c['phase']} — {c['criterion_key']}** "
                f"(currently *{c['status']}*): {c['description']}"
            )
        parts.append("")

    parts.append("### Reading guide")
    parts.append(n["closing"])
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------- PDF ---

def render_pdf(report: dict) -> bytes:
    """Render the report as a PDF using ReportLab Platypus."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    from reportlab.lib.enums import TA_LEFT
    import re

    BLUE = colors.HexColor("#2563eb")
    GREY_900 = colors.HexColor("#1f2937")
    GREY_500 = colors.HexColor("#6b7280")
    GREY_200 = colors.HexColor("#e5e7eb")

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Heading1"], fontSize=20, leading=24,
            textColor=GREY_900, spaceAfter=4, alignment=TA_LEFT,
        ),
        "meta": ParagraphStyle(
            "meta", parent=base["Normal"], fontSize=9, leading=12,
            textColor=GREY_500, spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=13, leading=16,
            textColor=BLUE, spaceBefore=12, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontSize=10.5, leading=15,
            textColor=GREY_900, spaceAfter=8,
        ),
        "muted": ParagraphStyle(
            "muted", parent=base["BodyText"], fontSize=9, leading=12,
            textColor=GREY_500, spaceAfter=8,
        ),
    }

    def md_to_paragraph_text(s: str) -> str:
        """Light Markdown → ReportLab inline tags.

        We deliberately *do not* convert `_..._` to italics — identifiers like
        `lambda_gen` and `atom_forms_reproducibly` would lose their underscores.
        Use `*..*` for italics in narrative text, never underscores.
        """
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", s)
        s = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", s)
        return s

    def P(text: str, style="body"):
        return Paragraph(md_to_paragraph_text(text), styles[style])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=22 * mm, bottomMargin=22 * mm,
        title="vibrasim run report",
        author="vibrasim research dashboard",
    )

    story = []
    run = report["run"]
    session = report["session"]
    n = report["narrative"]

    story.append(P(f"Run report — {str(run['id'])[:8]}", "title"))
    story.append(P(
        f"Generated {report['generated_at']} · session #{session['session_number']} · "
        f"config <b>{run.get('config_name')}</b> · seed <b>{run.get('rng_seed')}</b> · "
        f"duration <b>{run.get('duration_s'):g} s</b>",
        "meta",
    ))

    if n["context"]:
        story.append(P(n["context"]))

    story.append(P("Setup", "h2"))
    story.append(P(n["setup"]))

    story.append(P("Emergence", "h2"))
    story.append(P(n["emergence"]))

    story.append(P("Peak populations", "h2"))
    story.append(P(n["peaks"]))

    story.append(P("Species", "h2"))
    story.append(P(n["species"]))

    # Species table
    if report["species"]:
        story.append(Spacer(1, 6))
        sp_data = [["Species", "First seen (s)", "Max count"]]
        for s in sorted(report["species"], key=lambda x: x["first_seen_t"])[:25]:
            sp_data.append([
                s["species_fingerprint"],
                f"{s['first_seen_t']:.2f}",
                str(s["max_count"]),
            ])
        sp_tbl = Table(sp_data, colWidths=[60 * mm, 40 * mm, 40 * mm])
        sp_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), GREY_900),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, GREY_200),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
        ]))
        story.append(sp_tbl)

    story.append(P("Phase reached", "h2"))
    story.append(P(n["phase"]))

    if n["operator_notes"]:
        story.append(P("Operator notes", "h2"))
        story.append(P(n["operator_notes"]))

    if report["relevant_criteria"]:
        story.append(P("Acceptance criteria touched by this run", "h2"))
        for c in report["relevant_criteria"]:
            story.append(P(
                f"<b>Phase {c['phase']} — {c['criterion_key']}</b> "
                f"(currently <i>{c['status']}</i>): {c['description']}"
            ))

    # Configuration table on its own page
    story.append(PageBreak())
    story.append(P("Configuration", "h2"))
    if report["params"]:
        cfg_rows = [["Parameter", "Value"]]
        for k in sorted(report["params"].keys()):
            v = report["params"][k]
            cfg_rows.append([str(k), str(v)])
        cfg_tbl = Table(cfg_rows, colWidths=[60 * mm, 100 * mm])
        cfg_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, GREY_200),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(cfg_tbl)
    else:
        story.append(P("No parameters recorded.", "muted"))

    story.append(P("Reading guide", "h2"))
    story.append(P(n["closing"]))

    doc.build(story)
    return buf.getvalue()
