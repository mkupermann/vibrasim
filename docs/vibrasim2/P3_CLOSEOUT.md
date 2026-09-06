# P3 engineering closeout — PASS

On 2026-09-06 I tested a supplied six-site ring with open energy transport,
local capture and paid finite-lived bond renewal. This is a deliberately
constructed system. The P3 run label does not denote achievement of the
original charter's organisational-memory milestone.

The registration was committed as `74bf299f` before data; implementation and
tests as `df9b2027`. The single eleven-cell matrix completed in 144.325 seconds.
Registration-to-closeout work stayed within the 45-minute estimate and
90-minute ceiling. Raw step records occupy approximately 43 MB locally.

## Evidence

The readback verdict is **PASS**. Late mean live-bond counts over [100,120]
are 6 for full and damaged, 2 for no_feedback, and 0 for no_capture and
drive_off. The half-step runs have the same late means. The full repetition
has an identical raw-file hash, stronger than the required ordered-event
agreement. Maximum absolute energy residual across cells is about 2.51e-11,
below the frozen 1e-9 gate.

The damage intervention at t=40 coincides with scheduled expiry: the recorded
post-step state has one live bond, not simply four. Five live bonds are
restored at t=42.14 in the primary run, inside the t=60 deadline. This is paid
formation on supplied candidate edges; the rule does not consult a repair map.

Result and manifest:
`archive/run-logs/v2-p3/2026-09-06-observed-001/{result.json,run.json}`.
The result hashes every raw JSONL cell. A fresh assessment from those files
exactly matched the saved result excluding wall-clock duration.

Registration SHA-256:
`5a0be722c25cc24ac3a20f667d8166c0ca485e1a8e20d0a76e1e31bffb3c61bb`.
Implementation SHA-256:
`0c7669e1a38835ce86bda72d6c77c37d7a1c6cbe8aed23968ea30ba9d69fb1e0`.

## Observation and limits

The visible P3 window was inspected during the no_capture half-step cell and
again at COMPLETE PASS. Snapshots are flushed during solver iteration before
publication, unlike the older P2 runner's whole-trajectory buffering. The
display uses the existing P0-style wireframe renderer. Height means energy,
colour means reservoir level; geometry is not literal three-dimensional matter.
Display sampling/pacing is not a claim of real-time physical simulation.

This test supports engineered energy-dependent maintenance and recovery in
one small deterministic network. It does not establish robustness over a
parameter region, spontaneous topology, material replacement, memory, life or
consciousness. P0 NULL and P2 INCONCLUSIVE are unchanged.

The next useful question is whether maintenance remains when some supplied
scaffolding is removed. That requires a new pre-data contract; no additional
run or parameter tuning followed this result.

## Local use

From the repository root, replay existing data without recomputation:

```powershell
.venv\Scripts\python.exe -m vibrasim2.p3 --output archive/run-logs/v2-p3/2026-09-06-observed-001 --replay
```

Replay validates the source/registration identity and records before display.
It is explicitly labelled REPLAY. Space freezes only the view; C resets the
camera. Closing a view does not delete results. Do not use a new output path
to bypass the registered one-run decision.

The affected V2 suite passed 260 tests with one skip before the run. The
same suite passed again after the documentation update (11.05 seconds).
CLI replay was opened and visually verified at no_feedback-primary, t=36.6,
with a REPLAY label, then closed; the completed live view was left open.
The
historical V1 suite was not rerun for this isolated addition. No files were
published, and the unrelated uv.lock change was preserved.
