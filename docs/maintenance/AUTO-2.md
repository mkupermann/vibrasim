# AUTO-2 — WorldConfig __post_init__ validation

**Status: pre-registered. Not implemented.**
**Frozen: 2026-05-13. Author (pre-registration): Claude (autopilot setup session).**
**Reviewer at return: Michael Kupermann.**

## Why this exists

`WorldConfig` (in `world/config.py`) has ~50 fields covering substrate geometry, vibration dynamics, binding rules, BTSP, plasticity, neuron dynamics, etc. There is currently no `__post_init__` validator: a typo in a TOML config (e.g. `r_1 = 30, r_2 = 10` — swapped), or a copy-paste mishap (`box_size = (-60, 60, 60)`), boots a `World` that runs but produces silently nonsensical physics for an entire session before the experimenter notices.

LOGBOOK Session 1 documents one such confusion ("smaller box (300×300) didn't help — likely because r_1 is now relatively large compared to box…"). That kind of config-drift fingerprint would have been caught instantly by an assertion.

AUTO-2 adds a `__post_init__` that asserts the basic invariants. Pure plumbing. Zero substrate behavior change.

## What is built

A `__post_init__` method on `WorldConfig` in `world/config.py` that raises `ValueError` with a clear message on any of:

1. `dt <= 0` — time-step must be positive.
2. `box_size` is not a 3-tuple of positive floats.
3. `n_initial_vibrations < 0` or `n_initial_vibrations > n_vibrations_max`.
4. `n_vibrations_max <= 0`.
5. `n_nodes_max <= 0`.
6. `r_1 <= 0` or `r_2 <= 0` or `r_1 >= r_2` — binding radii must be ordered.
7. `freq_tolerance <= 0` or `freq_tolerance >= 1.0` — fractional tolerance must be in `(0, 1)`.
8. `freq_ratio <= 0` — binding band centre must be positive.
9. `pair_decay_time <= 0` or `triad_decay_time <= 0` — decay-time-constants must be positive.
10. `lambda_gen < 0` or `lambda_dec < 0` — rates must be non-negative.
11. `rng_seed < 0` — seeds are non-negative integers by convention.

Each `raise ValueError("WorldConfig: <field> = <value>, expected <constraint>")` form. No silent clamping or correction — fail fast.

## Acceptance — pre-registered

Test target: `tests/test_config_validation.py`. The autopilot session implements this file.

All seven test items below must hold for AUTO-2 to be marked **passed**.

1. `tests/test_config_validation.py::test_default_config_validates_clean PASSES` — `WorldConfig()` with no overrides constructs without raising.
2. `tests/test_config_validation.py::test_growth_config_validates_clean PASSES` — the config used in `tests/test_substrate_growth_e2e.py::_growth_config()` validates clean. (Loaded by importing the helper; do not duplicate the config.)
3. `tests/test_config_validation.py::test_post_init_rejects_negative_box_size PASSES` — `WorldConfig(box_size=(-60, 60, 60))` raises `ValueError`.
4. `tests/test_config_validation.py::test_post_init_rejects_zero_dt PASSES` — `WorldConfig(dt=0)` raises `ValueError`.
5. `tests/test_config_validation.py::test_post_init_rejects_r1_geq_r2 PASSES` — `WorldConfig(r_1=20, r_2=10)` raises `ValueError`.
6. `tests/test_config_validation.py::test_post_init_rejects_freq_tolerance_out_of_range PASSES` — both `freq_tolerance=0` and `freq_tolerance=1.5` raise.
7. `tests/test_config_validation.py::test_existing_test_configs_all_validate PASSES` — every `WorldConfig(...)` literal under `tests/` parses-and-constructs without raising. Glob `tests/test_*.py`, import each test module, and for any module that exposes a `_make_world`, `_growth_config`, or `_make_config` helper, call it and confirm no raise.

## Negative control

Conceptually weak for plumbing of this type. The discriminating evidence is acceptance item 3–6: the validator must REJECT specific malformed configs. If it accepts a `WorldConfig(box_size=(-60, 60, 60))`, the validator is a state detector that fires on nothing.

A matched-wallclock no-engram substrate run is not meaningful here — this is dataclass validation, not substrate emergence.

## Risks the autopilot must respect

1. **Do not modify any existing config field defaults.** The validator is additive. If a default value would itself fail the validator (which it should not, by acceptance item 1), the autopilot must change the validator, not the default — but only after writing the issue to LOGBOOK with rationale.

2. **Do not change behavior of any existing test.** Acceptance items 1 and 2 are the canary: the default config and the growth-foundation config must continue to validate clean. If they don't, autopilot has changed semantics, not added validation.

3. **Do not validate things that depend on substrate state.** The validator runs at construction time. No `self.simulate_one_step()` or other side-effecty checks. Pure field-level invariants only.

4. **Numba JIT caching.** If `world/config.py` is touched in a way that changes the dataclass layout, the `.numba_cache/` may need invalidation. The autopilot may delete `.numba_cache/` once at the start of the session if it changes config field order. Otherwise leave it alone.

## What this does NOT claim

- Does not validate semantic correctness of parameter combinations (e.g., "this `freq_tolerance` makes physical sense for this `freq_ratio`"). That is research judgment, not boundary validation.
- Does not validate values loaded from TOML beyond what the dataclass already does — the TOML loader is a separate concern.
- Does not add new fields. Only validates the ones already there.

## Implementation hints (for the autopilot)

- `world/config.py` line 23 has `freq_tolerance: float = 0.005`. The file uses `@dataclass`. `__post_init__` is the canonical extension point.
- For acceptance item 7, use `importlib.util.spec_from_file_location` to load test modules without triggering pytest's collection. Or simpler: `pytest.collect_only`. The autopilot picks whichever is more readable.
- Negative tests (3–6) use `pytest.raises(ValueError, match="<field name>")` — the regex match makes the test specific to which validator fired.

## Out of scope for AUTO-2

- Validating dataclass field types beyond what `@dataclass` already enforces.
- Cross-field semantic checks (e.g., "is this freq_ratio reasonable for this box_size?").
- Refactoring `WorldConfig` itself.

## Budget

- **Realistic**: 1 day (one autopilot tick).
- **Hard ceiling**: 3 attempts × 4h = 12h compute.

## What FAILED looks like

- Validator rejects an existing legitimate config used somewhere in the test suite.
- Validator fails to reject one of the deliberately-bad fixtures in acceptance 3–6.
- Existing tests start failing because the validator changed implicit behavior (e.g., the substrate used to tolerate `lambda_gen = -0.001` because the code took `max(0, lambda_gen)`).

Any of these → `null`. After 3 attempts → `failed`. Postmortem via Opus path.
