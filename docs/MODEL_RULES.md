# Model Rules — Canonical Description

One document. All rules. No code, no TOML, no amendments to chase.
Last updated: 2026-05-28.

---

## What the model IS

A 3D periodic-boundary simulation where discrete oscillating objects
("vibrations") bind into hierarchical structures through frequency-
matching and spatial proximity. Structures that form can further bind,
creating a hierarchy: vibrations → electrons → pairs → triads →
atoms → molecules → (open-ended).

## What the model CLAIMS

That hierarchical structure can emerge from simple local rules without
global coordination, pre-designed templates, or external labeling.
Specifically: frequency synchronization (Kuramoto resonance) between
nearby objects drives them into binding windows, enabling cascade
formation that does not occur without resonance.

## What the model does NOT claim

- These "electrons" and "atoms" are NOT physical electrons and atoms.
  The names are analogies for hierarchical levels, not physics claims.
- The 8% frequency rule is NOT derived from quantum mechanics. It is
  an engineered binding criterion.
- The model does NOT claim to explain consciousness, life, or any
  specific biological phenomenon. It explores whether hierarchical
  emergence is possible from oscillatory primitives.

---

## Objects

### Vibrations (Level 0)
- State: position (3D), velocity (3D), frequency (scalar Hz),
  polarity (boolean), alive (boolean)
- Motion: constant velocity, periodic wrap on all axes
- Created: at initialization + ambient regeneration (lambda_gen)
- Destroyed: when bound into an electron

### Nodes (Level 1-32)
- State: position (3D), frequency (scalar Hz), polarity (boolean),
  level (integer), alive (boolean), composition (CSR array of
  constituent indices)
- Motion: none (stationary at binding midpoint) unless repulsion
  or node-move is enabled
- Created: when two compatible objects bind
- Destroyed: by decay (pairs/triads) or when bound into higher level

---

## Binding Rules

### Vibration → Electron (Level 0 → 1)
Two vibrations bind if ALL of:
1. Distance < r_1 (default 5.0)
2. Opposite polarity
3. Frequency ratio (f_max - f_min) / min(f_max, f_min) is in
   [freq_ratio - freq_tolerance, freq_ratio + freq_tolerance]
   (default: [0.075, 0.085] = 8% ± 0.5%)

Product: electron at midpoint, freq = f1 + f2, random polarity.
Both vibrations are consumed.

### Node → Higher Node (Level 1+ → Level+1)
Two nodes bind if ALL of:
1. Distance < r_2 (default 10.0)
2. Opposite polarity
3. Same frequency ratio rule as above
4. Same frequency decade: floor(log10(f1)) == floor(log10(f2))
5. Upgrade table permits the level combination (see below)

Product: new node at midpoint, freq = f1 + f2, random polarity.
Both constituent nodes are consumed.

### Upgrade Table
  (1,1) → 2  (electron + electron → pair)
  (1,2) → 3  (electron + pair → triad)
  (1,3) → 4  (electron + triad → atom)
  (4,4) → 5  (atom + atom → di-atomic molecule)
  (4,N) → N+1 for N in 5..31  (atom + molecule → bigger molecule)

When mol_fusion_enabled=True, additionally:
  (A,B) → max(A,B)+1 for any A,B both >= 4 (capped at 32)

### Lock Rule
Each node can participate in at most one binding per tick
(k_locked_this_tick flag).

---

## Decay Rules

### Unstable Nodes
- Pairs (level 2): exponential decay, mean lifetime = pair_decay_time
  (default 5.0s). On decay, constituent electrons are revived.
- Triads (level 3): exponential decay, mean lifetime = triad_decay_time
  (default 30.0s). Constituents revived.
- Atoms (level 4+): permanent by default. No decay unless
  lambda_dec_mol > 0 (strength-modulated decay for molecules).

---

## Resonance (Kuramoto Synchronization)

Enabled when resonance_coupling > 0. Applied every 10 ticks.

For each pair of alive nodes (i, j) within distance r_2:

  delta_freq_i += (coupling / level_i) * (freq_j - freq_i) / max(freq_i, freq_j) * dt

Level scaling: higher-level nodes have more inertia (drift slower).
Electrons (level 1) synchronize fastest; atoms (level 4) drift 4x
slower.

This is the mechanism that enables the binding cascade: nodes whose
frequencies initially differ by >8% slowly synchronize until they
enter the binding window.

---

## Ambient Regeneration

New vibrations are injected volumetrically at rate lambda_gen per
unit volume per second. This provides fresh material for the binding
cascade when initial vibrations are consumed.

---

## Parameters (defaults)

| Parameter | Default | Meaning |
|-----------|---------|---------|
| n_initial_vibrations | 1000 | starting count |
| box_size | (60,60,60) | 3D periodic box |
| r_1 | 5.0 | vibration binding radius |
| r_2 | 10.0 | node binding radius |
| freq_ratio | 0.08 | 8% binding rule |
| freq_tolerance | 0.005 | ±0.5% on 8% rule |
| pair_decay_time | 5.0 | pair mean lifetime (s) |
| triad_decay_time | 30.0 | triad mean lifetime (s) |
| resonance_coupling | 0.0 | Kuramoto coupling (0=off) |
| mol_fusion_enabled | False | molecule+molecule binding |
| lambda_gen | 0.0001 | vibration regeneration rate |
| dt | 1/60 | timestep (s) |

---

## Verified Findings (with pre-registered bars)

| Finding | BET | Verdict |
|---------|-----|---------|
| Resonance enables cascade to atoms | 084 | PASS |
| Without resonance, cascade stalls at pairs | 084 | PASS (negative control) |
| Atoms are permanent (no decay) | design | by construction |
| Level-scaled inertia: atoms drift 4x slower | 084 | verified |

---

## Open Questions

1. Does the cascade reach molecules (level 5+) given enough time/density?
2. Can closed molecular chains form membranes?
3. What is the minimum density for sustained cascade?
4. Is coupling=10.0 in a physically meaningful regime?
