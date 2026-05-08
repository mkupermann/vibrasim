# Sub-project F — Speech-loop amendment (port-to-port firing coupling)

**Date:** 2026-05-08
**Status:** draft (awaiting user approval)
**Parent design doc:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md`
**Prerequisite:** Plans A, A.5, B, C, D, E merged. Plan F is the next sub-project the foundation needs to make M4 work as originally claimed.

---

## 1. Why this amendment exists

Five iterations of the autonomous-prototype-build loop on M4 (2026-05-08, log at `/tmp/agent_autonomous.md`) demonstrated empirically that **the substrate as designed has no physics path for atoms to form in the audio output port from input-only stimuli**. The chain that M4 implicitly requires:

```
audio at input port → input atoms fire → ??? → output atoms fire → decode produces water-correlated audio
```

…is broken at the `???` step. STDP forms bridges only between *firing* atoms. Output-port atoms never fire because no stimulus drives them and ambient regeneration does not reliably populate them at densities sustainable in M4's compute budget.

This is the same gap biology has solved with **auditory feedback loops**. A vocalising animal hears its own utterances. Auditory neurons that fire under a sound also activate motor neurons that produce that sound — partly through engineered structure (axons connecting auditory cortex to motor cortex), partly through associative learning (Hebbian co-firing reinforced by the loop itself).

Plan F adds the substrate's analogue: a **port-to-port firing coupling** that, when an atom in the audio input port fires, deposits a small burst of vibrations at the audio output port at the same frequency. This is the new physics that makes M4 achievable AND keeps the substrate's claim ("hierarchical structure forms from local rules") intact, because the rule is local — it's a property of port boundaries, not of individual atoms.

## 2. The rule, formally

A new substrate stage `apply_speech_loop(world, dt)` runs inside `tick()` AFTER `neuron_dynamics` (which logs new firings to `world.firing_events`). The stage reads the firings produced *this tick* and, for each firing whose atom is inside the audio input port, optionally injects a "ghost burst" at the audio output port.

```python
def apply_speech_loop(world, dt: float) -> int:
    """Plan F speech-loop coupling: when an atom in the audio input port
    fires, deposit a small burst of vibrations at the audio output port
    at the same frequency. Models biological auditory feedback.

    Returns the count of ghost-burst events triggered this tick.
    """
    cfg = world.config
    if cfg.speech_loop_strength <= 0.0:
        return 0
    n_events = 0
    n_burst = cfg.speech_loop_burst_size
    for t_fire, atom_idx in world.firing_events:
        # Only events from this tick (since they were just appended).
        if t_fire < world.t - dt:
            continue
        if atom_idx >= world.k_count:
            continue
        pos = world.k_pos[atom_idx]
        # Inside audio input port?
        if not _in_audio_input_port(cfg, pos):
            continue
        f_atom = float(world.k_freq[atom_idx])
        # Allocate n_burst vibrations at random positions inside audio output port.
        free_idx = np.where(~world.s_alive)[0][:n_burst]
        if len(free_idx) == 0:
            continue
        # ... deposit at output port ...
        n_events += 1
    return n_events
```

### 2.1 Configuration parameters

```python
# Plan F — speech-loop port-to-port coupling
speech_loop_strength: float = 0.0    # master gate: 0.0 = off (default)
speech_loop_burst_size: int = 6      # vibrations injected per ghost burst
speech_loop_jitter_hz: float = 50.0  # frequency jitter to widen receptive field
```

**Default off**: existing tests behave identically. Plan F is purely additive.

### 2.2 Energy / conservation argument

§4.7 of CONCEPT.md frames ambient regeneration as a thermodynamic open system: vibrations come from a notional "ambient field" at calibrated rate. Plan F's ghost bursts are **drawn from the same field**. The total vibration injection rate becomes:

```
total_inject_rate = lambda_gen * box_volume + speech_loop_strength * input_firing_rate
```

The two terms have the same physical interpretation: ambient field interactions producing vibrations. The speech-loop adds a SECOND interaction channel (input-port-firing-correlated) on top of the existing uncorrelated channel. Both deplete the same notional ambient energy.

For M4's intended use, `speech_loop_strength` is calibrated such that the speech-loop's peak rate is at most 1× the ambient-regen rate — no thermodynamic novelty.

### 2.3 What's local vs non-local

The rule is locally specified at port boundaries: "if firing occurs inside region X, inject at region Y." This is non-local in 3D space (X and Y are at opposite corners of the box), but it's local in the substrate's TOPOLOGY — the port-to-port coupling is a fixed graph edge defined at world construction.

Biological analogue: the auditory-to-motor pathway is non-local in physical space (different brain regions) but local in connectivity (a defined axonal projection). Plan F's port-to-port coupling models the same "engineered connectivity" property.

This is a **principled, named, explicit** non-locality. Not a magic number; a structural feature.

## 3. Acceptance tests

### 3.1 Necessary (unit)

| ID | Test | Pass criterion |
|---|---|---|
| SL1 | `apply_speech_loop` is no-op when `speech_loop_strength=0` | World state unchanged after call |
| SL2 | Firing of an audio_input atom triggers ghost burst | Atom fires → next tick's `s_alive` count increases by `speech_loop_burst_size` at audio output port positions, with frequencies near firing atom's frequency ± `speech_loop_jitter_hz` |
| SL3 | Firing of a non-input-port atom is ignored | Same setup with atom in arbitrary box position → no ghost burst |
| SL4 | Multiple firings produce multiple bursts | 3 simultaneous input-port firings → 3× burst_size new vibrations at output port |
| SL5 | Bursts respect vibration buffer cap | When `s_alive` is at `n_vibrations_max`, ghost bursts gracefully no-op (not crash) |

### 3.2 Headline integration (slow)

| ID | Test | Pass criterion |
|---|---|---|
| **SL6** | M4 with speech-loop on | M4's existing test passes (cosine ≥ 0.5) when `speech_loop_strength=0.5` is added to its WorldConfig |

SL6 supersedes M4's xfail status — the test moves from xfail (without speech loop) to xpass (with speech loop).

## 4. CONCEPT.md amendment text

Append to §4 (substrate physics) as a new sub-section:

```markdown
### §4.X Speech-loop coupling (Plan F amendment)

**Motivation.** The substrate's claim — *hierarchical structure from local rules* —
holds for *connectivity-defined* locality, not necessarily for *spatial* locality.
Biological brains have engineered axonal projections between distant regions
(auditory cortex to motor cortex, for example) that are local in the topology
of the connectome, even when the regions are physically distant. The
substrate inherits the same property via *port-to-port coupling*.

**Rule.** Each named port (audio_input, audio_output, video_input, ...) may
declare a coupling to another named port via configuration. When an atom
inside source port S fires, a small burst of vibrations is deposited
inside target port T at the firing atom's frequency. The number of
vibrations per burst (`speech_loop_burst_size`) and the rate at which
this happens (`speech_loop_strength`) are configuration parameters with
defaults that disable the coupling.

**Default-off.** Without explicit port coupling, the substrate behaves
exactly as previously specified. The amendment is purely additive.

**Empirical motivation.** The M4 demo (glass-of-water; foundation spec §6)
requires atoms in the audio output port that fire when paired stimuli
arrive at the audio input port and video input port. Without auditory
feedback, output-port atoms have no source: random ambient regeneration
populates them too sparsely, and direct stimulus at the output port
contradicts the demo's "perception-only" framing. The speech-loop
amendment names the missing physics: vocalising animals hear their own
utterances, which closes the auditory-motor loop and lets associative
learning bind input perceptions to output productions.

**Energy conservation.** Speech-loop bursts draw from the same ambient
field as `ambient_regen` (§4.7). The combined rate is bounded by the
field's notional energy budget; no new conservation law is needed.

**Falsifiability.** With `speech_loop_strength=0`, the substrate cannot
demonstrate M4's claim. With `speech_loop_strength=0.5` and matching
training, M4 either passes (cosine ≥ 0.5 on held-out seeds) or it doesn't.
The amendment is testable in either direction.
```

## 5. Module / test layout

```
world/config.py                              # +3 fields
world/physics.py                             # +apply_speech_loop, wired into tick()
tests/test_amendment_speech_loop.py          # SL1-SL5 (fast)
tests/test_agent_m4_glass_of_water.py        # update config, remove xfail (SL6)
db/migrations/0010_planF_speech_loop.sql     # SPEECH-LOOP-R1 amendment
docs/CONCEPT.md                              # add §4.X subsection
```

## 6. Decision log

- **Why a new physics rule and not "make M4 simpler"** — A "simpler M4" (pre-seeded atoms, symmetric drive) reframes the substrate's claim. Plan F preserves the original claim by adding the missing physics. The amendment is biologically motivated, named, default-off, and testable.
- **Why port-to-port coupling, not vibration teleportation per emission** — Atom emissions go in random directions in 3D space. Hijacking the per-emission stream would mix the substrate's spatial physics with port topology. Cleaner: make the coupling a separate stage that runs after `neuron_dynamics` and reads firings, not emissions.
- **Why frequency-preserving** — The output should encode the same content as the input (you-hear-what-you-say). Adding randomization at the output frequency would amount to "echo with noise injection," which is a different (less interesting) physics.
- **Why default off** — Plans A through E plus 267 prior tests all pass without it. Plan F should be additive; existing tests must stay green when `speech_loop_strength=0`.

## 7. Risks

- **Cascading firing**: speech-loop bursts arrive at audio output port, bind into atoms there, those atoms fire, and if they're ALSO inside another coupled port (none in v1), recurse. **Mitigation**: v1 has only one coupling (audio_input → audio_output, one-way). No mutual coupling. Cycles cannot form.
- **Energy budget**: peak speech-loop injection rate must be bounded. **Mitigation**: cap implicit in `s_alive` buffer (when full, bursts no-op). Calibrate `speech_loop_strength` so peak rate ≤ ambient regen rate.
- **STDP cascades**: with output port atoms firing in response to input firings, STDP between input and output fires aggressively. Bridges form fast — possibly too fast (over-fitting on first paired exposure). **Mitigation**: existing `tau_LTP`, `delta_LTP` tuning applies; the speech-loop just gives STDP a path to operate on.
- **Conceptual scope creep**: this is a substantive paper amendment, not just a code change. The CONCEPT.md text needs to be coherent with the rest of §4. **Mitigation**: §4.X stays narrow — port-to-port coupling, named, default-off, biologically motivated. Doesn't change the substrate's other claims.

## 8. Approval gate

Before this becomes a writing-plans plan, the user should confirm:

1. **The amendment is biologically motivated and acceptable as a substrate physics extension.** Y/N — the alternative (Option A from the autonomous-loop escalation) reframes M4's claim but doesn't add physics. This option preserves the claim.

2. **Default off, opt-in via `speech_loop_strength` config field.** Y/N — Plans A through E remain identical for callers who don't enable it.

3. **CONCEPT.md gets a new §4.X subsection.** Y/N — the paper's claim shifts from "hierarchical structure from purely local rules" to "...from local rules + port-to-port coupling for engineered cross-region connectivity." This is a substantive but honest extension.

4. **Test SL6 supersedes M4's xfail.** Y/N — when SL6 passes, M4's xfail decorator is removed and M4 becomes load-bearing again.

5. **Plan F migration in dashboard DB** — Y/N — same pattern as A/B/C/D/E.

If approved, this becomes `docs/superpowers/plans/2026-05-08-plan-F-speech-loop.md` and the autonomous loop resumes with iter7 = implement SL1-SL2 unit tests.
