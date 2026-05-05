# World of Vibrations — Specification

This file describes a simulated world whose only fundamental substance is vibrations. From these vibrations, hierarchically structured entities emerge through clear natural laws — electrons, atoms, molecules, and higher levels. The long-term goal is to build brain-like structures on this foundation.

The specification is intended as a handover document for an implementation. It is complete and actionable.

---

## Part 1 — The Constitution of the World

### The Space

The space is two-dimensional and conceptually infinite. In the implementation it is represented as a finite area (e.g. 1000 × 1000 units), but with periodic boundary conditions — vibrations that leave one edge re-enter from the opposite edge. This makes the finite space locally behave like an infinite one.

The space is empty and without intrinsic geography. It is stage, not content.

### The Vibrations

The elementary inhabitants of the world are vibrations. Each vibration has the following properties:

- **Frequency** (continuous, any positive value possible)
- **Polarity** (binary: even or odd — independent of frequency)
- **Position** in 2D space (continuous coordinates)
- **Velocity** (direction and speed of linear motion)

Polarity is a property of its own, not derived from frequency. A vibration at 600 Hz can be either even or odd, depending on its assigned polarity.

### Motion

Free vibrations travel through space in a straight line at constant speed. They change neither frequency, nor polarity, nor direction on their own. Motion is their natural state.

### First binding — formation of electrons

When two vibrations meet, an electron can form. Three conditions must be fulfilled simultaneously:

1. **Spatial proximity**: The distance between the two vibrations is smaller than the critical distance `r_1`.
2. **Polarity difference**: One vibration is even, the other odd.
3. **8% frequency rule**: The frequencies differ by exactly 8% (with a small tolerance of about ±0.5% to account for numerical noise).

When the conditions are met, an **electron** forms at the binding site:

- The frequencies of the two components add up. The electron's frequency is `f1 + f2`.
- The electron is stationary. It stays at the position where the binding occurred.
- Inside, the two original vibrations continue to oscillate — the node is quiet on the outside, alive on the inside.
- Polarity: Since the electron consists of 2 components, its polarity is **even** (variant 3 — parity by size).

### Atom formation — stepwise stabilisation

Atoms form from multiple electrons. The process is stepwise:

**Stage 1 — Electron pair (2 electrons):**
- Two electrons bind when they are spatially within `r_2` of each other, their polarities match (even meets odd), the 8% frequency rule is fulfilled, and they lie within the same frequency order of magnitude.
- Polarity of the pair: odd (3 component elements in total, since the pair contains two electrons each with 2 vibrations — see note below on parity counting).
- **Status: temporary.** If nothing further happens, the pair can decay back into two electrons after a characteristic decay time.

**Stage 2 — Triad (3 electrons):**
- A third electron joins when the conditions are met.
- **Status: fairly stable**, but not permanent. The decay time is considerably longer than for pairs.

**Stage 3 — Atom (4 electrons):**
- At the fourth electron, the atom locks in.
- **Status: indestructible.** The atom can no longer decay into individual electrons.
- From this moment it is a permanent part of the world.

### Note on parity counting

With variant 3 (parity by size), the number of bound vibrations is counted, not bound electrons. Since each electron contains 2 vibrations:

- Electron = 2 vibrations → even polarity
- Electron pair = 4 vibrations → even polarity
- Triad = 6 vibrations → even polarity
- Atom = 8 vibrations → even polarity

Since with this counting all bound structures consist of even numbers, there is a problem with the binding rule "even meets odd".

**Solution:** Polarity is counted at the level of electrons, not vibrations.
- Electron = 1 component element → odd
- Pair = 2 electrons → even
- Triad = 3 electrons → odd
- Atom = 4 electrons → even

With this counting, structures can bind alternately, and the world remains productive.

### Higher hierarchies — molecules and above

Atoms bind to molecules according to analogous rules. In general, the binding between nodes requires:

1. **Spatial proximity**: The distance is smaller than the distance threshold applicable to the hierarchy level.
2. **Polarity difference**: Even meets odd (counted at node level).
3. **8% frequency rule**: The frequencies differ by exactly 8%.
4. **Same frequency order of magnitude**: Both nodes lie within the same logarithmic frequency range (e.g. 1,000–9,999 Hz or 10,000–99,999 Hz).

The frequency order of magnitude is defined as follows:
- Order of magnitude n = floor(log10(frequency))
- Nodes of order of magnitude n bind only to other nodes of order of magnitude n.

### Scale separation through repulsion

Nodes of different orders of magnitude do not do nothing — they repel each other as soon as their frequency ratio is 1000 or more.

The repulsion force is modelled as:

```
F = -k * (frequency_ratio - 1000) / distance²    when ratio > 1000
F = 0                                              otherwise
```

This repulsion spatially sorts the world: small structures live in one region, medium ones in another, large ones in a third.

---

## Part 2 — Implementation Architecture

### Data structures

```python
class Schwingung:
    position: tuple[float, float]
    geschwindigkeit: tuple[float, float]
    frequenz: float
    polaritaet: bool  # True = even, False = odd
    
class Knoten:
    position: tuple[float, float]
    frequenz: float
    polaritaet: bool  # determined by number of components
    bestandteile: list  # list of contained vibrations or nodes
    hierarchie_ebene: int  # 1=electron, 2=pair, 3=triad, 4=atom, ...
    stabilitaet: float  # 0..1, for atoms 1.0 (indestructible)
    erzeugungs_zeit: float
    
class Welt:
    schwingungen: list[Schwingung]
    knoten: list[Knoten]
    raum_groesse: tuple[float, float]
    parameter: WeltParameter
```

### Main loop

```python
def schritt(welt, dt):
    # 1. Movement of free vibrations
    bewege_schwingungen(welt, dt)
    
    # 2. Application of scale repulsion to all nodes
    wende_abstossung_an(welt, dt)
    
    # 3. Search for binding partners (vibration-vibration → electron)
    finde_neue_elektronen(welt)
    
    # 4. Search for binding partners at higher levels
    finde_hoehere_bindungen(welt)
    
    # 5. Check decay of unstable structures
    pruefe_zerfall(welt, dt)
    
    # 6. Update internal dynamics of all nodes
    aktualisiere_innere_dynamik(welt, dt)
```

### Performance

For real-time capability:

- **Numba** (`@njit`) for the hot loops — motion update, distance calculation, binding search.
- **Spatial index structure** (spatial hashing or K-D tree) for efficient neighbourhood search. Naive O(n²) comparisons become too slow with more than 1,000 vibrations.
- **NumPy arrays** for positions, velocities, frequencies — not Python lists.

Target performance: 60 frames/second with 1,000 vibrations, 30 frames/second with 10,000.

---

## Part 3 — Visualisation

### Library

**Pygame** as first choice. Pure Python, simple setup, sufficient for the scales we're targeting.

If needed later: switch to **Pyglet/Arcade** (OpenGL-based, scales better) or **Pygame with GPU acceleration via moderngl**.

### Representation

**Free vibrations** as small dots (radius 2–3 pixels):
- Even polarity: Blue (`#4A90E2`)
- Odd polarity: Red (`#E74C3C`)
- Size slightly varying with frequency (logarithmically scaled)

**Electrons** as stationary dots with a soft glow:
- Colour: Yellow-orange (`#F39C12`)
- Size approximately 5 pixels with soft glow
- Pulses slightly (inner activity visualised)

**Electron pairs** as two connected electrons with a thin line:
- Line colour: Light grey, transparent (`#CCCCCC` with alpha=0.5)
- Visualises the unstable connection

**Triads** as three connected electrons:
- Lines denser, less transparent
- Suggestion of a triangle

**Atoms** as unmistakeable structures:
- Four electrons with thick, solid connecting lines
- Bright aura/glow around the whole structure
- Colour: White (`#FFFFFF`) with warm glow
- Are the "stars" of the world

**Higher-order bindings** (molecules and above):
- Connections become visually more prominent with increasing hierarchy level
- Distinct colours for different orders of magnitude

### Statistics

An info bar at the top of the screen shows:
- Number of free vibrations
- Number of electrons
- Number of pairs / triads / atoms
- Number of molecules (if present)
- Current simulation time
- Current FPS

Optional: a small frequency histogram in the corner.

### Controls

| Key / Action | Function |
|---|---|
| Spacebar | Pause / Resume |
| Arrow up / down | Increase / decrease speed |
| Mouse wheel | Zoom |
| Mouse drag | Pan |
| Left click | Insert new vibration at mouse position |
| R | Reset |
| S | Save (state to disk) |
| L | Load |
| Esc | Quit |

---

## Part 4 — Initial Configuration

Recommended values for the first start. These will be calibrated after the first observations.

```python
ANFANGS_KONFIGURATION = {
    'anzahl_schwingungen': 1000,
    'frequenz_min': 100.0,           # Hz
    'frequenz_max': 10000.0,         # Hz
    'frequenz_verteilung': 'log',    # logarithmically distributed
    'raum_groesse': (1000.0, 1000.0),
    'geschwindigkeit_min': 10.0,     # units/second
    'geschwindigkeit_max': 50.0,
    'r_1': 5.0,                      # distance for vibration-vibration binding
    'r_2': 10.0,                     # distance for electron-electron binding
    'frequenz_toleranz': 0.005,      # 0.5% tolerance for 8% rule
    'paar_zerfallszeit': 5.0,        # seconds
    'triade_zerfallszeit': 30.0,     # seconds
    'abstossung_konstante': 100.0,   # k in the repulsion formula
    'polaritaet_verteilung': 0.5,    # 50% even, 50% odd
}
```

---

## Part 5 — First Expectations and Calibration

On the first start you will probably see problems:

- **If no electrons form**: r_1 is too small or the 8% rule is too strict. Increase r_1 or the frequency tolerance.
- **If too many electrons form**: Reduce r_1.
- **If atoms never form**: The lifetime of pairs/triads is too short, or the density of electrons is too low. Extend the decay times or increase the initial vibration count.
- **If everything fuses into large clumps**: The repulsion is too weak. Increase the repulsion constant.

Budget two to three hours of calibration before the world becomes productive.

---

## Part 6 — Later Extensions

This specification covers only the lower levels of the world. Later extensions will include:

- **Molecules** (multiple atoms connected)
- **Membranes and cell-like structures**
- **Neuron clusters** (functional units built from atoms and molecules)
- **Synaptic connections** (Hebbian plasticity)
- **Activity patterns and synchronisation**
- **Attention mechanisms**
- **Learning and memory structures**

The long-term goal is to develop brain-like structures from within this world. See the accompanying skill `gehirn-aus-schwingungen`.

---

## Appendix — Implementation Checklist

Order of implementation:

1. **Scaffolding** — classes, data structures, empty world with visualisation window
2. **Vibrations** — free motion, visualisation of dots
3. **First binding** — electrons form from vibrations
4. **Pairs and triads** — pre-atom structures with decay
5. **Atoms** — indestructible 4-unit structures
6. **Scale repulsion** — make spatial sorting visible
7. **Statistics and controls** — info bar, pause, reset, save
8. **Performance optimisation** — Numba, spatial index structure

Each step should be fully working before the next one is begun.
