# Dual-Path Autopilot

**Dual-hypothesis research automation for vibrasim**

This autopilot system manages two parallel research paths that together address the project's core question: *Can we build non-LLM systems that learn and communicate?*

## Overview

### Path A: Elimination (Not LLM)
**Mandate**: *"Wir forschen solange bis wir was finden was nicht LLM ist"*

Find substrate architectures that are **fundamentally NOT** large-language-model family:
- No attention mechanisms
- No transformer architectures  
- No embeddings
- No BPE tokenization

Pre-LLM era mechanisms only. Pure elimination approach.

**Success**: A substrate that passes T0-T9 + output-side bars AND is provably not statistical pattern matching.

### Path B: Differentiation (LLM Advantage)
**Mandate**: *"Build what LLMs can't do"*

Build systems with capabilities that **LLMs fundamentally cannot match**:
- Continual learning without catastrophic forgetting
- Energy efficiency (100-1000x improvement)
- Distribution shift robustness
- Unsupervised discovery from raw sensory input
- Sensorimotor grounding (embodied agents)

Base mechanism may use pattern matching, but **must add brain-like properties** that LLMs lack.

**Success**: Outperforms LLM baselines on Brain-Advantage benchmarks while maintaining core performance.

---

## Structure

```
autopilot/
├── paths.yaml              # Dual-path configuration (allocations, success criteria)
├── dual_path_dispatcher.py # Main dispatcher managing both paths
├── example_queues/
│   ├── path_a_queue.yaml    # Example items for Path A (Elimination)
│   └── path_b_queue.yaml   # Example items for Path B (Differentiation)
└── README.md               # This file

State directories:
├── ~/.eqmod/autopilot/path_a_elimination/  # Path A state (queue, logs, results)
└── ~/.eqmod/autopilot/path_b_differentiation/  # Path B state
```

---

## Configuration

Edit `paths.yaml` to:

1. **Adjust path allocations** (default: 40% Path A, 60% Path B):
   ```yaml
   autopilot:
     path_allocation:
       path_a_elimination: 40
       path_b_differentiation: 60
   ```

2. **Define Brain-Advantage benchmarks** for Path B:
   ```yaml
   brain_advantage_benchmarks:
     - name: "Continual Learning"
       metric: "Retention Score"
       llm_baseline: "~50%"
       target: ">80%"
   ```

3. **Set stop conditions** for the overall autopilot:
   ```yaml
   stop_conditions:
     - "Path A finds a non-LLM substrate that passes all bars"
     - "Path B achieves >2x LLM baseline on all Brain-Advantage benchmarks"
   ```

---

## Usage

### Run both paths (default)
```bash
python autopilot/dual_path_dispatcher.py
```

### Run single tick
```bash
python autopilot/dual_path_dispatcher.py --once
```

### Run only Path A
```bash
python autopilot/dual_path_dispatcher.py --path path_a_elimination
```

### Run only Path B
```bash
python autopilot/dual_path_dispatcher.py --path path_b_differentiation
```

### Check status
```bash
python autopilot/dual_path_dispatcher.py --status
```

### Stop all paths
```bash
touch ~/.eqmod/autopilot/STOP
```

### Stop a single path
```bash
touch ~/.eqmod/autopilot/path_a_elimination/STOP
touch ~/.eqmod/autopilot/path_b_differentiation/STOP
```

---

## Queue Format

Both paths use the same queue format as the original bet_dispatcher, with an added `path` field:

```yaml
items:
  - id: EA-001  # Path A prefix
    hypothesis: "..."
    pytest_target: tests/bet/test_*.py
    status: queued
    path: path_a_elimination
    max_runtime_seconds: 3600
    
  - id: DB-001  # Path B prefix
    hypothesis: "..."
    pytest_target: tests/bet/test_*.py
    status: queued
    path: path_b_differentiation
    benchmarks: [continual_learning, distribution_shift_robustness]
    max_runtime_seconds: 7200
```

**Naming convention**:
- Path A items: `EA-###` (Elimination Path A)
- Path B items: `DB-###` (Differentiation Path B)

---

## Item Selection Logic

The dispatcher selects the next item using **weighted random selection** based on:

1. **If only one path has queued items** → select from that path
2. **If multiple paths have items** → weighted by `path_allocation` percentages
3. **If a path is STOPped** → skip it
4. **If a path already has a running item** → skip it (one at a time per path)

Example with default 40/60 allocation:
- 40% chance: select from Path A queue
- 60% chance: select from Path B queue

---

## Path-Specific State

Each path maintains its own:
- `queue.yaml` - list of items (queued, running, passed, null, failed)
- `STOP` marker - pause this path only
- `current.pid` - PID of currently running item
- `current_item.txt` - ID of currently running item
- `dispatcher.log` - tick-by-tick log
- `LOGBOOK.md` - per-iteration entries
- `<item_id>/result.json` - per-item results

---

## Brain-Advantage Benchmarks

Path B items can optionally specify which benchmarks they target:

```yaml
benchmarks:
  - continual_learning
  - energy_efficiency
  - distribution_shift_robustness
  - unsupervised_discovery
  - sensorimotor_grounding
```

These are defined in `paths.yaml` and track progress toward the Path B success criteria.

---

## Integration with Existing BET System

The dual-path dispatcher **reuses** the existing `tools/bet_dispatcher.py`:

- Each path has its own `BetDispatcher` instance
- The dual-path dispatcher coordinates between them
- All existing BET tests work unchanged
- New BET tests can specify which path they belong to via ID prefix

---

## Migration from Original System

To migrate existing BET items:

1. **Path A (Elimination)**: Items testing non-LLM substrates
   - Reaction-Diffusion, cog_map β>0, SDM, SOM-saturating, PC, etc.
   - Rename: `BET-###` → `EA-###`
   - Move to: `~/.eqmod/autopilot/path_a_elimination/queue.yaml`

2. **Path B (Differentiation)**: Items testing LLM-advantage capabilities
   - R-STDP, closed-loop, continual learning, energy efficiency
   - Rename: `BET-###` → `DB-###`
   - Move to: `~/.eqmod/autopilot/path_b_differentiation/queue.yaml`

3. **Shared items**: SOM+replay (works for both) can be in both queues with different hypotheses

---

## Design Rationale

### Why Dual Path?

The original mandate (Path A) is philosophically important but has hit limits:
- Most working substrates are statistical pattern matching (LLM-family)
- Pure non-LLM approaches need scale/infrastructure beyond solo research

Path B accepts the reality that pattern matching works, but asks: *What can we add to it?*
- Continual learning via replay
- Energy efficiency via spiking
- Robustness via unsupervised discovery

Together, the paths answer both questions:
1. "Is there a non-LLM path?" (Path A)
2. "Can we build better systems than LLMs?" (Path B)

### Why Weighted Allocation?

- **Path A (40%)**: Continue the elimination mandate, but with reduced focus
- **Path B (60%)**: Prioritize building capabilities that matter

Allocation can be adjusted as findings emerge.

---

## Example Workflow

1. **Start autopilot**:
   ```bash
   python autopilot/dual_path_dispatcher.py &
   ```

2. **Add Path A item** (new substrate to eliminate):
   ```yaml
   # Edit ~/.eqmod/autopilot/path_a_elimination/queue.yaml
   items:
     - id: EA-004
       hypothesis: "Hopfield network with modern retrieval will pass T13"
       pytest_target: tests/bet/test_hopfield_t13.py
       status: queued
   ```

3. **Add Path B item** (new capability):
   ```yaml
   # Edit ~/.eqmod/autopilot/path_b_differentiation/queue.yaml
   items:
     - id: DB-006
       hypothesis: "SOM+replay maintains >80% accuracy across 50 tasks"
       pytest_target: tests/bet/test_continual_50_tasks.py
       benchmarks: [continual_learning]
       status: queued
   ```

4. **Monitor**:
   ```bash
   python autopilot/dual_path_dispatcher.py --status
   tail -f ~/.eqmod/autopilot/logs/dual_path_dispatcher.log
   ```

---

## Success Metrics

### Path A Success
- A substrate passes all bars (T0-T9 + output-side)
- Mechanism is provably not statistical pattern matching
- Reproducible across multiple seeds

### Path B Success  
- >2x LLM baseline on at least 3 Brain-Advantage benchmarks
- Maintains core performance (discrimination, generation)
- Demonstrates at least one LLM-impossible capability

### Overall Success
- Either Path A OR Path B succeeds
- OR: Combined findings constrain the search space sufficiently

---

## Philosophy

This dual-path approach **honors the original mandate** while **accepting practical realities**:

> "Wir forschen solange bis wir was finden was nicht LLM ist **ODER** wir bauen was LLMs nicht können."

(We research until we find what's not LLM **OR** we build what LLMs can't do.)

Both paths are valid. Both paths contribute to the project's goal of understanding learning and communication without relying on the LLM paradigm as the only solution.
