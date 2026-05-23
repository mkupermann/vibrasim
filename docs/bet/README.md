# Bet pipeline — operator manual

The bet pipeline is the runtime that turns the 2026-05-22 programme-level bet pre-registration (LOGBOOK 2026-05-22 entry "Programme-level bet pre-registered") into actual ≤1h hypothesis-falsification iterations. It runs in parallel to the existing autopilot G-amendment cap and the long-run training queue. It does **not** modify either; the bet queue and dispatcher are independent state.

## What the bet pipeline is for

A separate queue of ≤1h hypothesis iterations. Each iteration tests whether a candidate substrate architecture can pass any of the bet's five pre-registered tests (T1-T5; see LOGBOOK 2026-05-22 entry). The expected mode is NULL: >95 % of iterations are expected to falsify their own hypothesis, and that is exactly what the pipeline is designed to produce at scale.

The win condition is binary: all five tests pass simultaneously on a single substrate instance, on a single training run, within 12 months of the start date (deadline 2027-05-22). The disallowed-technology constraint (LLM / transformer / pretrained embedding / BPE tokenizer) is enforced at the hypothesis-catalogue review layer; the dispatcher does not police it.

The bet pipeline is **not** for retuning the bet's T1-T5 thresholds, extending the deadline, or treating partial passes as success. Those are protocol violations per the pre-registration.

## What the bet pipeline is NOT for

- It does not run autopilot G-amendment items (those go through `.eqmod/autopilot/QUEUE.yaml`).
- It does not run 24h+ substrate training (those go through `~/.eqmod/long-run/queue.yaml`).
- It does not consume the iteration cap for G24-G26 (that cap is exhausted at 3 slots independently of any bet activity).

## Files at a glance

| Path | Role |
|---|---|
| `tools/bet_dispatcher.py` | Polling daemon. Owns one in-flight iteration at a time. |
| `tools/validate_bet_queue.py` | Pre-commit / smoke validator. Uses shared DEPENDENCY_RE. |
| `tests/test_bet_dispatcher.py` | Unit + smoke tests; runs under `pytest -m "not slow"`. |
| `~/.eqmod/bet/queue.yaml` | The bet queue (operator-editable). |
| `~/.eqmod/bet/hypothesis_catalogue.md` | Pre-vetted candidate hypotheses. |
| `~/.eqmod/bet/LOGBOOK.md` | Append-only per-iteration log. |
| `~/.eqmod/bet/current.pid` | PID + ctime of running pytest. |
| `~/.eqmod/bet/current_item.txt` | ID of running item. |
| `~/.eqmod/bet/STOP` | Pause marker. Touch to halt, remove to resume. |
| `~/.eqmod/bet/<ID>/result.json` | Per-iteration result, verdict, log tail. |
| `~/.eqmod/bet/<ID>.log` | Raw pytest stdout/stderr from the iteration. |
| `~/.eqmod/bet/dispatcher.log` | Tick-level dispatcher log. |

## How to add a hypothesis

A hypothesis goes through three places before the dispatcher will pick it up:

1. **Brainstorm and vet** the hypothesis in the catalogue at `~/.eqmod/bet/hypothesis_catalogue.md`. Each entry is one paragraph stating the proposed substrate primitive(s), the existing research it synthesises, and the references being verknüpft. Do not add a hypothesis that depends on a disallowed technology (LLM / transformer / pretrained embedding / BPE tokenizer).
2. **Implement the pytest target.** A bet iteration is concretely a single pytest invocation that exercises the substrate, runs T1-T5 against the result, and writes `result.json` to `$EQMOD_BET_OUT_DIR` (the dispatcher sets this env variable to `~/.eqmod/bet/<ID>/`). The pytest target lives under `tests/bet/` by convention; the path goes into the queue item's `pytest_target` field.
3. **Append an item to** `~/.eqmod/bet/queue.yaml`. Required fields:

```yaml
- id: BET-042                              # short id, monotonic
  hypothesis: |                            # one paragraph free text
    Persistent homology of the flux graph's
    1-skeleton produces a topological invariant
    that distinguishes English from white noise
    (T1 KL > 0.1) within 10k ticks.
  references:                              # papers / textbook chapters being verknüpft
    - "Carlsson, Topology and Data, Bull. AMS 2009, §4"
    - "Edelsbrunner & Harer, Computational Topology, ch. 7"
  pytest_target: tests/bet/test_bet_042_persistent_homology.py
  status: queued
  attempts: 0
  max_runtime_seconds: 3600                # 1h hard cap; ≤ 3600 only
  created_at: "2026-05-22T22:00:00"
  finished_at: null
```

Run the validator before committing:

```sh
.venv/bin/python tools/validate_bet_queue.py
```

The validator refuses queue files whose `pytest_target` does not exist, whose `max_runtime_seconds` exceeds the 1h cap, or whose blocker text declares an explicit dependency on an item that has already terminated non-passed (`R-X must reach status...` shape; uses the same `queue_semantics.DEPENDENCY_RE` regex as the autopilot pipeline).

## Iteration cadence

The dispatcher polls every 60 s by default (`--interval` overrides). One iteration runs at a time. The hard cap is 1h per iteration; iterations exceeding their `max_runtime_seconds` are SIGTERMed and then SIGKILLed (process-group kill so any pytest-spawned children die too). A killed iteration's status becomes `failed` and the kill reason is appended to that item's `blockers` list. This mirrors the R-LR-3 incident pattern from 2026-05-20 (long-run dispatcher silent-overrun bug) — the bet dispatcher enforces the cap at code level, not at "comment in queue.yaml" level.

Expected throughput: ~24 iterations per day if every iteration runs the full hour (worst case), ~144-200 iterations per day if iterations average 5-10 min (likely most NULL iterations). Over 12 months that is ~9k-72k iterations, comfortably above the 3000-5000 estimate in the bet pre-registration.

## Where per-iteration LOGBOOK entries live

The autopilot uses `LOGBOOK.md` at the repo root. The bet pipeline keeps its own at `~/.eqmod/bet/LOGBOOK.md` so the high-volume iteration entries do not drown the lower-volume amendment record. Each iteration appends one entry of the form:

```markdown
## 2026-05-23T12:34:56 — bet BET-042 → NULL

```
=== result.json (...) ===
{ "verdict": "null", ... }
=== pytest tail ===
[short pytest output, last 1500 chars]
```
```

The detailed result.json sits next to the LOGBOOK entry (one per item, overwritten each attempt). The raw pytest stdout/stderr from that iteration is `~/.eqmod/bet/<ID>.log`.

## How to read `/results` in Telegram for bet items

Telegram exposes a `/bet` command (added to `tools/notify_telegram_receiver.py`). Output shape:

```
Bet queue: X queued / Y running / Z passed / N null / M failed

Last 3 completed iterations:
- BET-042 NULL 2026-05-23T12:34
- BET-041 NULL 2026-05-23T11:18
- BET-040 NULL 2026-05-23T10:02

Win-condition progress (T1-T5 passes in a single iteration):
- 0 / 5 tests have ever been passed in a single iteration
- Best iteration so far: BET-038 (3/5 — T1, T2, T4)
```

The win-condition section is the only one that matters strategically. It tracks how close any single iteration has come to a simultaneous 5/5 pass. NULL iterations do not move the win condition (a partial 4/5 still records as NULL because the bet is binary, but the "best iteration so far" line surfaces it). The `/results` autopilot command keeps reporting the short and long-run queues; `/bet` is the bet-specific readout.

## What PASS / NULL / FAILED mean for a 1h iteration vs a 4h amendment item

The verdict vocabulary is shared with the autopilot pipeline but the semantics differ:

| Verdict | Autopilot G-amendment item (4h) | Bet iteration (1h) |
|---|---|---|
| **PASS** | Pre-registered acceptance met after one attempt. | All five T1-T5 tests passed in this single iteration. **This is the win condition.** Counts toward the 12-month bet. |
| **NULL** | Acceptance not met after 3 attempts. Verdict is a finding. | The expected mode (>95 % of iterations). A single hypothesis failed to pass 5/5. Constrains the design space; counts as a research finding but not as a win. |
| **FAILED** | Operator-administrative closure or implementation crash. | Hard-cap kill (process exceeded `max_runtime_seconds`), pytest non-zero exit, or operator-administrative closure via `/fail`. **Not** a content-level "did not pass" — that is NULL. |

A 4h amendment item is allowed three attempts before NULL. A bet iteration is **single-attempt**: NULL after one run, no retry within the bet pipeline. Re-trying a hypothesis means appending a fresh `BET-N+1` entry with a refined pytest target. This is intentional — the bet's discipline is "many shots, log every one, move on fast."

A bet iteration that PASSes is the bet's win condition. Per the pre-registration, a PASS must include passing negative controls (matched-noise input and matched-wallclock no-training, both failing the same T1-T5 battery on the same substrate code) for the result to be defensible. The dispatcher does not enforce this — the pytest target for a bet item must include the negative controls in its own test code. Items without negative controls in the pytest body are protocol-violating and will be rejected during win-condition verification.

## Pause / resume

```sh
touch ~/.eqmod/bet/STOP                    # pauses at next 60s tick
rm    ~/.eqmod/bet/STOP                    # resumes
```

Pause does **not** kill the in-flight iteration; the dispatcher checks STOP before launching the next one. To stop the running iteration immediately, kill the process group (`os.killpg(os.getpgid(<pid>), SIGTERM)`), then touch STOP.

## Telegram commands relevant to the bet pipeline

- `/bet` — bet queue counter, last 3 iterations, T1-T5 progress.
- `/results` — natural-language summary across short and long-run queues (does not include bet — by design, since bet entries are too high-volume).
- `/stop` / `/resume` — apply to the short autopilot only; the bet STOP marker is `~/.eqmod/bet/STOP` (currently no Telegram command for it — operate via filesystem).

## See also

- `LOGBOOK.md` 2026-05-22 entry "Programme-level bet pre-registered" — the pre-registration that this pipeline serves.
- `LOGBOOK.md` 2026-05-22 entry "Bet pre-data constraint correction" — the allowed-technology widening from "literature-novel substrate" to "verknüpfung of existing research".
- `tools/long_run_dispatcher.py` — the sibling pipeline for ≥4h substrate training items.
- `tools/queue_semantics.py` — shared dependency regex used by all three validators.
