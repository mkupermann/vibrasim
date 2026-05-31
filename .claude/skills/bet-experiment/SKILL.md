---
name: bet-experiment
description: Run a pre-registered EQMOD substrate experiment (a "BET") end to end — write acceptance bars BEFORE the run, implement within substrate primitives, run (single or 5-way parallel sweep), record PASS/NULL/FAIL honestly, and commit. Triggers on requests to test a substrate hypothesis, add a BET/amendment, run a parameter sweep, or investigate memory/plasticity/firing in world/. Enforces the pre-registration discipline (no post-hoc tuning; NULL is a valid finding; negative controls must fail).
---

# BET Experiment — Pre-registered Substrate Research

A **BET** is one pre-registered experiment on the EQMOD substrate. The point is
not to "succeed" but to produce a *defensible* verdict — PASS, NULL, or FAIL —
that survives scrutiny. This skill encodes the discipline that produced the
BET-089→109 chain.

## The non-negotiable rules (from CLAUDE.md)

1. **Pre-register before you run.** Write acceptance bars in
   `docs/amendments/bet_<NNN>_<name>.md` BEFORE executing anything. The git diff
   on that file is the proof the bars predate the data.
2. **Stay within substrate primitives.** STDP, BTSP, dream consolidation,
   k_pattern_id segregation, SubstrateLibrary, engineered port topology. No LLM,
   no transformer, no pretrained embedding, no BPE. New capability = an
   amendment that reuses these, never a bolted-on neural layer.
3. **No post-hoc tuning.** Never edit a bar to match a result. To retry, open a
   NEW amendment number (never edit a FAILED/NULL bar).
4. **NULL is a valid verdict.** A clean NULL that names the next mechanism is a
   finding, not a failure. Report ALL outcomes honestly.
5. **Negative controls must FAIL.** A matched control (no-engram, uniform
   stimulus, wall-off, …) must NOT pass, or the positive result is not
   defensible.
6. **Time budget = realistic estimate + hard 2× ceiling.** Overrun → written
   FAILED post-mortem in `LOGBOOK.md`, no quiet extension.
7. **Surface reusable mechanisms** as `docs/patterns/<NN>-<slug>.md`.

## Workflow (single experiment)

1. **Pre-register** `docs/amendments/bet_<NNN>_<name>.md`:
   - Hypothesis; mechanism (which primitive, what changes); acceptance bars in a
     table (id, criterion, threshold); the negative control that must fail; time
     budget; what is NOT claimed.
2. **Implement** the mechanism in `world/` gated OFF by default (a new
   `cfg.*` knob defaulting to 0/False), so the substrate's behaviour is
   unchanged unless the experiment turns it on.
3. **Write a runner** `tools/run_bet<NNN>.py` that builds the config, runs the
   arms (treatment + control), evaluates the pre-registered bars in code, prints
   a `--- VERDICT ---` block ending in `BET-<NNN>: PASS|NULL/FAIL` and `DONE`,
   and writes `~/.eqmod/bet/BET-<NNN>/result.json`.
4. **Smoke first.** Run a ~15 s wall-budget smoke to catch import/runtime errors
   cheaply before the full run.
5. **Run** in the background, redirecting stdout to `bet<NNN>_out.txt` (NOT via
   `tail`/`grep` — those buffer; write the file directly so the watcher streams
   it). Use `run_in_background: true`.
6. **Record** the verdict in the amendment doc's RESULT section and append a
   dated entry to `LOGBOOK.md`. Apply Pattern 01 triage to any NULL (did the
   mechanism fire? did it have a local effect? which constraint actually binds?).
7. **Commit** explicitly and promptly (the running `autopilot.py` will otherwise
   sweep uncommitted files into an "idle" commit). Message style:
   `bet: BET-<NNN> <VERDICT> — <one-line finding>` ending with the
   `Co-Authored-By:` trailer from CLAUDE.md.

## Workflow (5-way parallel sweep)

When a question is "which value/variant works", sweep instead of guessing:

1. Pre-register the variants in a table (label, params, role) with **shared**
   bars and a **falsifiable prediction**, plus at least one matched **control**
   variant expected to fail.
2. Write a **parameterized** runner `tools/run_bet<NNN>.py` taking
   `<label> <param...> [budget]`, writing `bet<NNN><label>_out.txt` +
   `result.json` per variant.
3. Launch all variants as **separate background processes** in one message
   (e.g. `a b c d e`). They stream to the watcher and notify on completion.
4. **Wait for ALL** to finish, then consolidate per-variant PASS/NULL/FAIL + the
   **pattern** (often monotonic) into the amendment RESULT, and commit.
5. Note any variant that hit `wall budget hit` before reaching POST — re-run it
   with more budget rather than recording a truncated NULL.

Concurrency cap ~ cores−2; 5 is fine on an 8-core box but each runs slower under
contention — give heavier sweeps a larger per-arm `budget`.

## Substrate gotchas learned the hard way

- **Frozen config.** `WorldConfig` is a frozen dataclass — mutate at runtime via
  `object.__setattr__(cfg, 'k', v)`.
- **Blank slate.** At a warmup→stim transition, reset EVERYTHING you depend on:
  bridge strength, atom charge (`k_charge`), refractory, and any lock/consolidate
  set. Leftover state from warmup re-ignites or pre-latches and looks like a
  result. (Multiple BET NULLs were this bug.)
- **Vibrations delocalize.** Free vibrations move ballistically with no
  collisions; in a small periodic box any non-zero injection velocity homogenizes
  the field. Use `vel=0` exactly for confined stimuli.
- **Molecules vs persistence.** Built-in STDP / G6 propagation act on level-5+
  *molecules*; `fusion_bond_block` (persistence) forbids molecules. They are
  mutually exclusive — write atom-bridge mechanisms instead if you need both.
- **Readout noise.** Tiny region cores (n≈1–20 bridges) give noisy means — prefer
  a fraction-of-checkpoints-selective metric over any-single-checkpoint.

## Verdict semantics

- **PASS** — all bars met AND the negative control failed as required.
- **NULL** — a bar unmet, but the mechanism/regime is informative; name the next
  mechanism. Valid and common.
- **FAIL** — crash, budget overrun, or a control that should have failed passed
  (result not defensible). Write the post-mortem.

Always end an experiment by committing and, if a reusable principle emerged,
adding a `docs/patterns/` entry.
