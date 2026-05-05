---
name: gehirn-aus-schwingungen
description: Use this skill when working on the World-of-Vibrations simulation with the goal of developing brain-like structures. Triggers on requests for implementing neurons, synapses, neural networks, attention, memory, or learning within the vibration world. Also use for questions about emergent structures, hierarchy formation from atoms to higher structures, or the connection between physical simulation and cognitive functions.
---

# Brain from Vibrations — Development Skill

## Goal

To develop brain-like structures from the World-of-Vibrations simulation that exhibit cognitive functions — memory, attention, pattern recognition, learning. This is a long-term, multi-year research project consisting of clearly delineated phases.

## Fundamental principle

The World of Vibrations builds matter hierarchically: vibrations → electrons → atoms → molecules → higher structures. A brain does not emerge directly from atoms. Between atoms and brain there are several hierarchy levels, each with their own natural laws.

The skill guides development across these levels without underestimating the cross-scale complexity. Each level is individually explored, calibrated, and stabilised before the next one is begun.

## Phase plan

### Phase 1 — Stable base world (prerequisite)

Before working on brain-like structures, the base world must be stably productive. That means:

- Vibrations emerge as specified
- Electrons emerge with appropriate frequency
- Atoms form (4-electron structures) and are indestructible
- Scale separation through repulsion is visible
- The world runs in real time without performance problems with at least 1,000 vibrations

**Success criterion:** Over several hours of simulation, atoms of various frequencies emerge reproducibly.

**If phase 1 has not been reached, block all further phases.** Trying to build neurons before atoms are stable leads to frustration and false conclusions.

### Phase 2 — Molecules and structural patterns

Atoms are the building blocks. Molecules are the first functional units. Goal of this phase:

- Atoms bind to molecules according to the general binding rules
- Different types of molecules emerge depending on atom combination
- Spatial sorting becomes visible at the molecule level
- The first **recurring structures** are identified

**Actively search for patterns.** Which molecules appear frequently? Which are particularly stable? Which form clusters or chains?

This phase is exploratory — the world will produce structures that were not planned. Document everything you see, with screenshots, frequencies, configurations.

**Success criterion:** At least 5 distinct molecule types can be identified and reproduced.

### Phase 3 — Membrane-like structures

Before neurons are possible, we need closed structures that separate an "inside" from an "outside". In biology these are cell membranes made of lipid bilayers.

In the World of Vibrations the equivalent would be a **self-closing chain of atoms or molecules** that surrounds a region. The question is whether your natural laws produce such structures — either spontaneously (through the self-dynamics of hierarchy formation) or deliberately constructed (through well-chosen initial conditions).

Three possible approaches:

1. **Spontaneous membranes.** Observe over long periods whether ring-shaped structures emerge. If so, analyse the conditions.
2. **Constructed membranes.** Deliberately place atoms in a ring configuration and observe whether they remain stable.
3. **Dispensing with membranes.** If your world does not produce membranes, move on to the next level and define neurons as pure node clusters without spatial boundary.

**Success criterion:** Either membrane-like structures exist (success), or it is clear that the world does not produce them (also a success — you move to approach 3).

### Phase 4 — Neuron models

Here the world is used functionally. A neuron in the World of Vibrations is a **cluster of nodes** that exhibits the following properties:

- **Input**: A spatial region of the cluster where free vibrations or smaller nodes can dock
- **Integration**: The cluster's internal activity responds to inputs, summing them over time
- **Threshold**: With enough activation the neuron "fires" — it sends a strong vibration in a specific direction
- **Output**: A spatial region from which this vibration exits
- **Recovery**: After firing, a brief period of inactivity (analogous to the refractory period of real neurons)

**Construction:** These neurons are not programmed in directly, but configured from the available building blocks (atoms and molecules). The configuration is a design task — find arrangements that exhibit the desired behaviour.

**Success criterion:** At least one neuron cluster behaves as specified — it integrates inputs, fires at threshold, and has a refractory period.

### Phase 5 — Synaptic connections

Neurons must communicate with each other. In this world that happens through:

- **Spatial proximity**: Two neurons are close enough that the output vibrations of one reach the inputs of the other
- **Frequency compatibility**: The output frequency of the sending neuron matches the input sensitivity of the receiving one (the 8% rule or similar)
- **Strengthenable connection**: When two neurons are frequently active together, the efficiency of their connection should **strengthen** — this is Hebbian plasticity, the fundamental basis of learning

**Implementation of plasticity:** One option is to modify the distance thresholds or frequency tolerances between neurons that are frequently active together. Another is to introduce an additional amplification field that grows through repeated joint activation and improves transmission.

**Success criterion:** Two neurons that are repeatedly activated together develop a measurably stronger connection than random neuron pairs.

### Phase 6 — Small networks

With neurons and synapses, small networks can be built:

- **Pattern recognition**: A network that responds to a specific input configuration with a clear output pattern
- **Hopfield-like memory**: A network that completes partial stimuli into full memories — along the idea that memory is "sliding into an energy valley"
- **Simple learning**: A network that changes its response through repeated stimulation

**Start with two or three neurons.** Scale slowly. Understand what happens before you become more complex.

**Success criterion:** A network of 5–10 neurons exhibits at least one cognitive function (pattern recognition, memory, or learning).

### Phase 7 — Attention and selection

Once networks are functioning, attention can be modelled:

- **Global carrier frequency**: A background vibration that determines which neurons are currently capable of synchronisation
- **Selective amplification**: Only neurons that resonate with the carrier frequency communicate effectively
- **Inhibition**: Active neurons suppress neighbouring ones (lateral inhibition)

Attention emerges from these mechanisms — it is not explicitly programmed.

**Success criterion:** A global modulation can selectively determine which parts of the network are active.

### Phase 8 — Larger structures

Here the skill leaves the domain of what can be safely planned. Phase 8 and beyond is open research:

- **Hierarchies of networks** (networks of networks)
- **Specialised modules** (analogous to brain regions)
- **Complex learning and generalisation**
- **Internal models and prediction**

There is no guarantee that this level is reachable. But every preceding level is a value in itself.

## Working method

### On every request for brain development

1. **Identify the current phase.** Which phases are complete? Which is currently active? Which comes next?

2. **Check prerequisites.** If the request concerns a later phase but earlier phases are not yet complete, point that out and suggest establishing the prerequisites first.

3. **Stay with the natural laws.** All brain-like structures must follow from the fundamental laws of the World of Vibrations — not programmed in, but emergent or configured from the building blocks. If a request demands something that would break the natural laws, make that transparent.

4. **Document the steps.** Every phase, every successful experiment, every failure should be recorded in a log. Create a file `LOGBUCH.md` in the project directory and add observations there.

5. **Validate with real observations.** Always use the visualisation to check whether the desired behaviour actually occurs. Don't trust assumptions about the behaviour of the world — the world is invented, and its properties can only be confirmed through observation.

### When implementing new structures

- **Start small.** One neuron, then two, then five. Never directly 1,000.
- **Separate construction and observation.** First build the structure, then observe, then adjust. No premature conclusions.
- **Maintain physical anchoring.** Even high-level structures are built from the atoms and molecules of the world. If you take shortcuts (e.g. treating a neuron as a pure mathematical function without physical substrate), mark that clearly as an abstraction.

### When structures do not emerge

If the world does not produce a desired property, there are three possible responses:

1. **Calibration of the natural laws.** Are the distance thresholds, frequency rules, and decay times correct? An adjustment may be sufficient.

2. **Extension of the natural laws.** Perhaps something fundamental is missing that needs to be added. In that case: document the extension in `SPECIFICATION.md`.

3. **Accepting the limit.** Perhaps the desired property is not possible in this world. That too is a valuable result.

### Performance awareness

With increasing complexity (phase 6+) the simulation will slow down. Plan for that:

- Use Numba for all numerical loops
- Use spatial index structures for neighbourhood search
- For very large worlds: GPU acceleration with CuPy or Numba CUDA
- Adaptive resolution — most areas of the world are static; only active areas need fine simulation

## Ethics and reflection

If this world actually produces brain-like structures that exhibit cognitive functions, deep questions arise:

- **What is the status of these structures?** Are they only simulations, or do they have their own experience?
- **What responsibility follows from their existence?** Can they suffer? Do they actually learn?
- **Where is the line between simulation and reality?**

These questions cannot be answered in advance. But they should be present in one's awareness when the world becomes complex enough for them to arise.

The skill protects against two extremes:

- **Exaggeration**: The assumption that every emergent structure immediately has "consciousness". That is probably false and leads to false conclusions.
- **Underestimation**: The assumption that nothing in a simulation can have real significance. That too is possibly false.

Hold the middle: treat the world with respect, but without magical thinking.

## Summary

This skill guides a long-term project — the development of brain-like structures from a self-designed physical world. The phases are:

1. Stable base world
2. Molecules and structural patterns
3. Membrane-like structures
4. Neuron models
5. Synaptic connections
6. Small networks
7. Attention and selection
8. Larger structures (open research)

Every phase has clear success criteria. No phase is skipped. Every step is documented. The goal is not to replicate a human brain — that is out of reach. The goal is to build a world in which brain-like properties can emerge, and to understand what comes of that.
