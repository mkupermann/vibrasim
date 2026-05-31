# EQMOD Experiment Harness — Tutorial

How to run pre-registered substrate experiments ("BETs"), single or as parallel
sweeps, and watch results live. This is the tooling that produced the
BET-089→109 chain. Companion skills: `bet-experiment`, `watch-results`.

## 0. Mental model

One **BET** = one pre-registered experiment with a defensible verdict
(PASS / NULL / FAIL). The discipline (bars before the run, negative controls, no
post-hoc tuning, NULL is valid) is what makes the verdict mean something. See
`CLAUDE.md` and `docs/marker_protocol.md`.

```
pre-register bars  →  implement (gated off)  →  smoke  →  run  →  record  →  commit
        |                                                    |
   docs/amendments/bet_<NNN>_<name>.md              LOGBOOK.md + result.json
```

## 1. Anatomy of a runner

Every `tools/run_bet<NNN>.py` follows the same shape (copy the nearest one):

```python
from world.config import WorldConfig
from world.state import World
from world.physics import tick

def make_cfg(): ...                      # all params; new knobs default OFF
def run_arm(name, uniform, wall_budget): # treatment + control arms
    cfg = make_cfg(); world = World(cfg)
    for step in range(40000):
        # phase logic: WARMUP -> (starve/cull/blank) -> STIM -> clear -> POST
        tick(world, cfg.dt)
        if step % 1000 == 999:  # checkpoint readout
            ...
        if time.time()-t0 > wall_budget: break
    return {...}
# evaluate pre-registered bars in code; print "--- VERDICT ---", bars,
# "BET-<NNN>: PASS|NULL/FAIL", "DONE"; write ~/.eqmod/bet/BET-<NNN>/result.json
```

Conventions the watcher and discipline rely on:
- Print a header line `=== BET-<NNN>: ... ===`, a `--- VERDICT ---` block, the
  bar lines (`T<NNN>x ... : True/False`), the final `BET-<NNN>: <verdict>`, and
  `DONE`. Use `flush=True`.
- Write stdout DIRECTLY to `bet<NNN>_out.txt` (not through `tail`/`grep`).

## 2. Run one experiment

```bash
# smoke first (cheap error catch)
.venv/Scripts/python.exe -c "import tools.run_bet<NNN> as r; ..."   # ~15s budget
# full run, background, streamed to the watcher
.venv/Scripts/python.exe tools/run_bet<NNN>.py > bet<NNN>_out.txt 2> bet<NNN>_err.txt &
```

Then record the verdict in the amendment doc + `LOGBOOK.md`, and commit:
`bet: BET-<NNN> <VERDICT> — <finding>` (+ Co-Authored-By trailer).

## 3. Parallel sweep (the fast way to answer "which value works")

Make the runner parameterized — `run_bet<NNN>.py <label> <param...> [budget]` —
then launch 3–5 variants as separate background processes in one go:

```bash
for v in "a 4 15" "b 6 15" "c 8 15" "d 6 0" "e 4 99"; do
  set -- $v
  .venv/Scripts/python.exe tools/run_bet<NNN>.py $1 $2 $3 800 \
    > bet<NNN>$1_out.txt 2> bet<NNN>$1_err.txt &
done
```

Each writes `bet<NNN><label>_out.txt` + its own `result.json`. Wait for ALL to
finish, then consolidate per-variant verdicts + the **pattern** (often monotonic)
into the amendment RESULT. Always include a matched **control** variant that must
fail. ~5 parallel is fine on 8 cores (slower per-arm under contention → bump
`budget`). If a variant logs `wall budget hit` before POST, re-run it with more
budget rather than recording a truncated NULL.

## 4. Watch results live

In a separate terminal:
```bash
python tools/watch_results.py          # live: board on startup, then streams new verdicts
python tools/watch_results.py --once   # one-shot board of all current results
```
Only verdict/bar lines show; the per-checkpoint spam is filtered. See the
`watch-results` skill.

## 5. Hard-won gotchas (read before you debug a NULL)

- **`WorldConfig` is frozen** → `object.__setattr__(cfg, 'k', v)` to mutate at runtime.
- **Blank slate fully** at warmup→stim: reset bridge strength, `k_charge`,
  refractory, AND any lock/consolidate set — leftover warmup state fakes results.
- **`vel=0` exactly** for confined stimuli; any velocity homogenizes the field
  ballistically in a small periodic box.
- **Molecules vs persistence**: built-in STDP/G6 act on level-5+ molecules;
  `fusion_bond_block` forbids molecules. Use atom-bridge mechanisms if you need both.
- **Noisy small-n readout** → use fraction-of-checkpoints-selective, not any-single.
- **Commit promptly** — the running `autopilot.py` otherwise sweeps uncommitted
  files into an "idle" commit. (Consider pausing autopilot during manual runs.)

## 6. Pattern 01 triage for any NULL

Before believing a NULL, check three things (`docs/patterns/01-...`):
1. Did the mechanism **fire** at all? (counter)
2. Did it have its **local effect**? (probe the quantity it directly acts on)
3. If it fired and worked but the outcome didn't move — a **different constraint
   binds**. Find it; don't tune this knob.

See also Pattern 02 (`docs/patterns/02-...`): if two fixes trade the same knob in
opposite directions and neither passes, the coupling is over-loaded — reshape its
locality/selectivity, don't scale its gain.
