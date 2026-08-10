# Pattern: Flux pattern tagging + energy-conserving generative allocation

**Source:** G15F engineering (2026-08-10), done-criteria in
`tests/flux/test_g15f_engineering.py`. Reusable regardless of G15F-1's NULL-T verdict.

## Tagging (engineered training signal)

`Nodes.active_pattern_id` is a mutable container attribute set ONLY by a training
harness; `Nodes.add()` stamps it into `pattern_id[slot]` unless the caller passes an
explicit pid (explicit 0 included). `remove()` clears the tag before slot recycling.
This is an engineered write (DISCIPLINE_SHARP D5) — mirror of Legacy
`World.active_pattern_id` (world/state.py:95–105, :262) reduced to its core: no bridge
commit, no eligibility gating, no pid routing.

Use when a flux experiment needs labeled structures without porting the full G10
segregation stack.

## Conserving generative allocation (the blend rule)

Any mechanism that CREATES a structure from existing ones must drain its energy from
the sources in the same step (pro-rata; apply drains only after slot allocation
succeeds), and any mechanism that INJECTS energy must report it for the caller to book
(`out["energy_injected"]` → `EnergyAuditor.record_injection`). The F0 ledger
(audit.py) then stays a hard 1e-9 gate even with generative dynamics on.

Anti-pattern (the bug this replaces): allocating a derived node with a fraction of the
sources' summed energy while leaving the sources untouched — silent energy creation
that the auditor only catches if it is actually wired into the run.

## Measurement lesson (from the NULL-T)

Before gating an experiment on a population size (G-T-style trainability gates),
measure the PERSISTENCE of that population in the target regime — a large node count
in a driven steady state is formation-minus-decay flux, not a durable engram store.
