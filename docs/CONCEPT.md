# Toward a Brain Simulation from Minimal Physics

A research programme for the bottom-up construction of neural networks from self-defined natural laws — from vibrations through atoms and molecules to synapses and cognitive functions

**Concept paper · Version 2.0** (English revision incorporating peer-review feedback)

> **Note on this revision.** This is a substantive amendment of the original German Konzeptpapier (preserved at [`Konzeptpapier.de.md`](Konzeptpapier.de.md) and [`Konzeptpapier.docx`](Konzeptpapier.docx)). It integrates four pieces of peer-review feedback that named real risks: (1) the 2D substrate is structurally inadequate for membrane formation in Phase 3; (2) scale separation through repulsion was deferred when it should have been foundational; (3) the Phase 5 plasticity mechanism — "matter capture from vacuum" — was thermodynamically loose; (4) realtime rendering targets distorted the engineering priorities. Each is addressed in its own marked section.
>
> Decisions reflected: the substrate is now 3D periodic; scale repulsion is promoted to foundational law and required for Phase 1; an ambient-regeneration mechanism (§4.7) makes the synapse-strengthening story conservation-respecting; rendering is decoupled from physics with quality prioritised over framerate.

---

## Abstract

This paper sketches a long-term research programme whose ultimate goal is the complete simulation of a neural network arising from a set of self-defined physical first principles. The central question is whether a hierarchically structured system, one that emergently produces the essential building blocks of a brain — functional neurons, synaptic connections with molecular signal transmission, plastic learning mechanisms — can be constructed from minimal interaction rules between elementary vibrations.

We define a minimal physical substrate (a three-dimensional periodic-boundary world of vibrations with frequency, polarity, and position), formulate the natural laws (inertial motion, frequency-compatible binding, hierarchical structure formation, scale separation through repulsion, ambient regeneration), and describe an eight-phase build plan: vibrations, electrons, atoms, molecules, membrane-like structures, neurons, synapses with molecular transmission, neural networks. Each phase has clear success criteria and a direct biological reference point.

The programme stands in the tradition of complexity research (Conway, Wolfram), the theory of coupled oscillators (Kuramoto, Strogatz), and theoretical neuroscience (Hopfield, Fries), while formulating its own sparse physical framework. We understand the programme as basic research with an unclear horizon for success; even partial successes in the early phases yield insights into the minimum conditions necessary for the emergence of information-processing structures.

---

## 1. Introduction and motivation

How do complex, information-processing structures arise from simple physical principles? How does it happen that an arrangement of atoms, none of which knows anything about meaning, brings forth something that feels, learns, and thinks? This question is among the oldest and deepest in natural science. It is asked differently in different disciplines — as a question about emergence in complexity research, as the question about the neural correlate of consciousness in cognitive neuroscience, and as the question of explaining mind in philosophy.

Existing approaches to the computational investigation of this question typically move between two extremes. On one side stand biophysically detailed simulations of individual neurons or small networks that model ion channels, membrane potentials, and synaptic vesicles — for example the NEURON simulation system or the Blue Brain Project. They are realistic but computationally expensive and limited to small scales. On the other side stand abstract artificial neural networks that represent mathematical functions rather than physical substrates. They scale impressively but lose the connection to the natural laws from which brains actually arose.

This paper proposes a third path: the construction of a minimal, self-defined physical substrate whose natural laws are simple enough to be fully understood, yet rich enough to produce the hierarchical chain of building blocks of which a brain consists. The end goal is explicit: a simulated world in which atoms become molecules, molecules become membranes, membranes become cell-like structures, those become neurons, and neurons finally connect through synapses with molecular signal transmission into functional neural networks — all on the basis of the same set of foundational laws.

Inspiration for this approach comes from several sources. Conway's Game of Life has shown since 1970 that extremely simple rules can give rise to phenomena reaching Turing-completeness. Quantum field theory describes our physical world as excitations of a few fundamental fields, from which all matter and interactions follow. The Communication-through-Coherence hypothesis (Fries, 2005) postulates that brain regions organise their communication through synchronous oscillations. Hopfield's energy-landscape model of associative memory (Hopfield, 1982) — recognised with the 2024 Nobel Prize in Physics — formalises how a system of coupled units can store memories as energy minima. Coupled-oscillator systems and Ising machines demonstrate that vibration-based computation is practically possible.

From these sources we derive a conceptual framework in which vibrations are the only fundamental element, binding is the only structuring principle, and hierarchy is the only ordering dimension. If this approach succeeds, it builds a bridge between physical substrate and cognitive function that is missing from existing approaches — a bridge that, in its full extent, supports a complete brain model whose components can each be reduced to the next-lower physical level.

---

## 2. Objectives

The overarching research goal is the complete simulation of a functional neural network whose every part emerges from the foundational laws of the world of vibrations defined here. In the final stage, the simulation is to comprise the following components.

### 2.1 Functional neurons from emergent matter

Every neuron in the final model is to consist of a configuration of atoms and molecules, which are themselves built from electron-nodes, which in turn arose from elementary vibrations. The neuron exhibits the characteristic properties of real neurons: input integration, threshold-based firing, refractory period, characteristic temporal dynamics. These properties are not programmed in; they emerge from the configuration of the underlying structures.

### 2.2 Synaptic connections with molecular signal transmission

Synapses — the connecting points between neurons — are modelled in the final stage as structures in which specific molecules are released from the presynaptic neuron in an activity-dependent manner, cross a gap, and bind at the postsynaptic neuron, where they trigger an electrical response. This is the transmission of neurotransmitters at chemical synapses, a mechanism central to plastic learning. In our world, these neurotransmitters would be specific molecule species — higher-order nodes with characteristic frequency and polarity — emitted from the neuron, traversing a distance through space, and binding with a compatible receiver structure at the target neuron.

### 2.3 Plastic connection strengths (Hebbian plasticity)

Synapses are to change their transmission strength in an activity-dependent way: neurons that are frequently active together develop stronger connections (Long-Term Potentiation), and connections that go unused weaken. In our world, this would be realised by changing the count, binding strength, or availability of the signal-carrying molecules at a particular synapse — analogous to biological reality, in which repeated activity actually changes the number of receptors and the synaptic architecture in physical terms. The thermodynamic budget for this strengthening is established in §4.7 (ambient regeneration); its empirical demonstration is the central open question of Phase 5 (see §6.5).

### 2.4 Membrane-like structures separating inside from outside

A central biological feature of real neurons — and of all cells — is the existence of a membrane that separates an inside from an outside and permits directed material flow. In the final model, closed structures of molecules are to be present, enclosing an interior space and at specific points permitting the passage of certain molecules. With the substrate now three-dimensional (§4.1), these membranes can be physically faithful bilayer-analogues: closed surfaces of bound nodes around a 3D pocket, with selectively permeable channel-points for compatible-frequency molecules.

### 2.5 Functional networks with cognitive properties

From the components above — neurons, synapses, membranes — networks are to be constructible that show cognitive functions: associative memory (completion of partial cues to full memories, in the sense of the Hopfield model), pattern recognition (a classifying response to input patterns), simple learning (modification of the response through repeated stimulation), and attention (selective amplification of certain activity patterns through global modulation, in the sense of Communication-through-Coherence).

### 2.6 An unbroken chain of reduction

Perhaps the most important goal: every property of the final model is to be reducible to the next-lower level. A synapse is a configuration of molecules. A molecule is a configuration of atoms. An atom is a stable bond of four electrons. An electron is the binding of two vibrations. The neuron as a whole is a configuration of cell-like structures built from all of these levels. This unbroken chain of reduction is what distinguishes the proposed programme from purely functional neural networks — and what makes it an honest model of a scientific question.

### 2.7 Realism of the objective

We are aware that the full realisation of this end goal represents a multi-year, possibly multi-decade research programme. Even partial successes in the early phases — say, the reproducible emergence of stable atoms in 3D, or the identification of recurring molecule species, or the demonstration of spatial scale separation by repulsion — would be standalone scientific contributions. The programme is structured so that every completed phase delivers an insight, regardless of whether the distant end goal is ever reached. Even a well-documented failure at a particular phase would be informative: it would show which additional properties are necessary for the next level of complexity.

---

## 3. Theoretical framework

### 3.1 Core assumptions

The framework rests on four core assumptions, which we make explicit in order to keep them open to debate.

**Matter is not primary.** What we perceive as matter is a configuration of vibrations in an underlying substrate. This assumption is consistent with quantum field theory, which describes particles as excitations of fields.

**Local rules suffice.** Complex structures arise not through global control but through local interactions that are sufficiently rich in their structure.

**Hierarchy arises from binding.** Stable structures at one level become the building blocks of the next.

**Information is synchronisation.** Information processing in biological systems happens primarily through temporal coordination between locally active units, not through classical addressing and routing.

### 3.2 Related work

**Cellular automata and Game of Life.** Conway (1970) and Wolfram (2002) showed that simple local rules can give rise to phenomena that reach Turing-completeness. Our approach shares this inspiration but uses continuous rather than discrete states and a 3D embedding.

**Coupled-oscillator systems.** Kuramoto (1975) showed that coupled oscillators can synchronise spontaneously. Strogatz (2003) popularised this phenomenon broadly. Hopfield's energy-landscape model of associative memory (Hopfield, 1982) formalises how a system of coupled units can store memories as energy minima. Our approach extends this tradition with three-dimensional spatial dynamics, a polarity property, and hierarchical binding aimed ultimately at synaptic plasticity.

**Ising machines and reservoir computing.** These approaches show that vibration-based computation is practically possible. We differ in that we do not optimise for a specific task; we simulate an open world in which structures — and in the end, functional neurons with synapses — are to emerge spontaneously or be constructible.

**Neuromorphic architectures.** Intel Loihi and IBM TrueNorth implement spike-based neural networks in hardware. They operate, however, at the level of abstracted neurons, without modelling the underlying physical substrate. Our approach goes one level deeper and additionally extends the model with a molecular synapse layer that is missing from most neuromorphic architectures.

**Communication-through-Coherence.** Fries (2005, 2015) developed the hypothesis that effective communication between brain regions depends on phase-coherent oscillations. This hypothesis is a central inspiration for the planned attention phase of our system.

---

## 4. The natural laws of the substrate

### 4.1 The space (revised, v2)

The space is **three-dimensional** and conceptually infinite. In the concrete implementation it is represented as a finite cubic volume with periodic boundary conditions on all three axes. The space is empty and without intrinsic geography.

> **Why 3D, not 2D as in v1.** Peer review correctly observed that 2D is structurally inadequate for membrane formation in Phase 3: real cell membranes work because a 3D bilayer can fold around a closed volume, and signals can route around the membrane through the surrounding 3D space. In 2D, a closed ring around an interior region either blocks all signal flow past it or has to be modelled as semi-permeable in an ad-hoc way that doesn't mirror the biological mechanism. Moving to 3D removes this abstraction and makes Phase 3 physically faithful. The cost is a constant ~3× factor in spatial-hash work (27 neighbour cells instead of 9) and a renderer that has to handle 3D geometry — both manageable, especially under the relaxed realtime priority of §7.1.

### 4.2 The elementary inhabitants

The world contains a single fundamental element: the vibration. Each vibration has four properties:

- frequency *f* (continuous positive value)
- polarity (binary: even or odd, independent of frequency)
- position in 3D space (three continuous coordinates)
- velocity (3D direction and speed of straight-line motion)

### 4.3 Motion

Free vibrations move in straight lines through 3D space at constant velocity (inertial motion). They change neither frequency nor polarity nor direction on their own. Periodic boundaries wrap on all three axes.

### 4.4 First binding — the emergence of electrons

When two vibrations meet, a first-order node — an electron — can arise. Three conditions must be satisfied at once:

- **Spatial proximity:** the 3D periodic distance is less than the critical distance *r₁*.
- **Polarity difference:** one vibration is even, the other odd.
- **Frequency rule:** the frequencies differ by exactly 8 percent (with a small numerical tolerance).

Where the conditions are met, the electron arises at the binding point. Its frequency is the sum of the two component frequencies. The node is fixed in space. Inside, the two source vibrations continue to oscillate.

### 4.5 Atom formation

Atoms emerge from several electrons in a stepwise, quantising process:

- Two electrons form a **pair** when they stand within *r₂* of each other (3D periodic distance), their polarities match, the frequency rule holds, and they share the same logarithmic frequency order of magnitude. **Status: temporary.**
- Three electrons form a **triad. Status: fairly stable but not permanent.**
- Four electrons form an **atom. Status: indestructible.**

### 4.6 Scale separation through repulsion (revised, v2 — promoted to foundational)

Nodes at different frequency orders of magnitude repel one another whenever their frequency ratio reaches 1000 or more. The repulsive force, in 3D, is

```
F_ij = -k · (frequency_ratio_ij - 1000) / r_ij²    if  ratio_ij > 1000
F_ij =  0                                          otherwise
```

where `r_ij` is the 3D periodic distance between nodes *i* and *j*, and the force acts along the line joining them. The force sorts the world spatially by scale: small structures occupy one region, mid-scale structures another, large structures a third.

> **Why promoted to foundational in v2.** Peer review correctly observed that v1 deferred §4.6 to a future implementation phase, while presenting it elsewhere as one of the natural laws. That was inconsistent. Without §4.6, Hypothesis H2 ("the spatial distribution shows sorting by order of magnitude") cannot be tested. v2 promotes scale separation to a Phase 1 requirement — atoms must form *and* spatial sorting by frequency decade must be observable for Phase 1 to be considered closed.

### 4.7 Ambient regeneration (new in v2)

Free vibrations are continuously generated throughout the volume at a low spatial rate λ_gen (vibrations per unit-volume per unit-time). Bound nodes (electrons, pairs, triads — atoms excluded) decay back to their constituent vibrations at a low rate λ_dec, releasing the constituents as free vibrations into the immediate neighbourhood.

This creates a steady-state ambient field of free vibrations through which structures move and bind. The total vibration count fluctuates around an equilibrium determined by the generation/decay rates and the binding flux. Local activity (e.g. an active synapse region) can capture from this ambient supply at a higher rate than it returns to it; the surrounding region becomes locally depleted and refills by diffusion.

> **Why this is in v2.** Peer review correctly flagged that the original Phase 5 plasticity mechanism — "Materie aus dem freien Vakuum einfangen" — was thermodynamically loose. Matter cannot arise from nothing. v2 closes the gap by establishing an explicit ambient field with conservation properties: vibrations are generated and destroyed at known low rates, the equilibrium is bounded, and synaptic strengthening (§6.3) becomes "local capture from a finite ambient supply" rather than "matter from vacuum". Whether the rates can be calibrated to support biologically reasonable Hebbian dynamics over long activity histories is itself the central open question of Phase 5 (§6.5).

The two new parameters are:

- **λ_gen** — ambient vibration generation rate (vibrations / unit volume / unit time)
- **λ_dec** — bound-node decay rate back to free vibrations (per node per unit time, applied uniformly to electrons, pairs, triads; atoms excluded by §4.5)

Both are calibration targets. Initial values: chosen so that ambient density at equilibrium roughly matches the seeded density (i.e. the world maintains itself rather than emptying or filling).

---

## 5. Build plan — from vibrations to neural network

The research programme is divided into eight phases. Each phase has a clear biological reference point — it builds one level of the hierarchy that, in the final model, serves as a component of a functional brain. Phases are not skipped; each presupposes the successful completion of the preceding one.

### Phase 1 — Stable base world (revised in v2)

**Biological reference:** atomic substrate. In the real world, stable atoms form the basis of all further matter. In our model, atoms (4-electron structures) are the first indestructible building blocks.

The world reproducibly produces vibrations, electrons, and atoms at acceptable performance, in three-dimensional space, with scale separation by repulsion observable, and with an ambient field maintained at steady state.

**Success criteria (v2):**
1. Over several hours of simulation, atoms of various frequencies arise reproducibly.
2. Cross-decade nodes show clear spatial separation (Hypothesis H2, see §8).
3. Ambient vibration density holds within ±20 % of its seed value over a 1-hour calibration run.

### Phase 2 — Molecules and structural patterns

**Biological reference:** chemical compounds. In real neurons, molecules (water, lipids, proteins, neurotransmitters) are the functional carriers of nearly every process. In our model, they emerge as higher-order nodes from atoms.

Atoms combine into molecules. Different molecule species are identified.

**Success criterion:** at least five distinct molecule species can be identified and reproduced. Especially important: the appearance of small mobile molecules (potential neurotransmitter analogues) and larger structural molecules (potential membrane components).

### Phase 3 — Membrane-like structures (revised in v2)

**Biological reference:** cell membranes. In real neurons, a lipid bilayer separates the inside from the outside world and, through embedded channels and receptors, enables directed signal transmission.

With the substrate now three-dimensional (§4.1), membranes can be modelled as **closed surfaces** of bound nodes around a 3D interior pocket — a direct topological analogue of biological bilayers. Signals route around the membrane through the surrounding 3D volume; selective permeability is implemented as channel-points in the surface where compatible-frequency molecules can pass.

The aim is to investigate whether closed 3D surfaces arise that separate an interior from the exterior, and whether specific points in the surface can be selectively permeable to certain molecule species. Three approaches will be tested: observation of spontaneous membrane formation under suitable parameters, deliberate construction of approximate spherical-shell node arrangements, or transition to a Phase 4 in which neurons are modelled without explicit membranes (relying on the interior region being defined by node density rather than a closed boundary).

### Phase 4 — Neuron models

**Biological reference:** functional nerve cells. Real neurons integrate signals at dendrites, sum over time, fire on threshold-crossing at the axon hillock, and have a refractory period.

A configuration of node clusters that act as functional neurons: spatially extended input and output regions, integration of incoming vibrational activity over time, threshold-based firing, characteristic refractory period.

**Success criterion:** at least one cluster behaves as specified.

### Phase 5 — Synapses with molecular transmission (revised in v2)

**Biological reference:** chemical synapses with neurotransmitters.

In our model, a synapse is modelled as a region between two neurons in which, on activity of the presynaptic neuron, specific molecule-nodes are emitted, traverse a 3D distance through space, and bind with compatible structures at the postsynaptic neuron, influencing its activity.

Plasticity is implemented as activity-dependent change in the number of emitted molecules or the number of receivers. The mechanism is local capture from the ambient vibration field (§4.7): when a synapse fires, it consumes some of the local ambient supply to assemble new presynaptic stockpile-molecules and postsynaptic receivers. Frequent activity locally depletes and frequently refills the ambient field; the synapse region becomes a structurally richer configuration. Inactive synapses lose their structures to the slow decay channel (§4.7) at the same rate everywhere; active ones rebuild faster than they decay.

**Success criteria (v2):**
1. Two neurons that are repeatedly co-activated develop a measurably stronger connection than random neuron pairs; this strengthening manifests physically in the count or availability of signal-carrying molecules in the synapse region.
2. The ambient vibration density across the synapse-rich region remains within bounded fluctuation (no runaway emptying or filling) over realistic activity patterns. (See §6.5 for why this is itself a research question.)

### Phase 6 — Small networks

**Biological reference:** neural microcircuits. Even networks of a few neurons can show remarkable behaviour — pattern recognition, associative memory, simple learning.

Construction of networks of 5 to 50 neurons that show at least one cognitive function: Hopfield-style associative memory, classification of input patterns, or simple learning through Hebbian plasticity at the synaptic connections.

> **Scaling reality.** A 50-neuron network in this substrate is genuinely large: each neuron is a cluster of dozens to hundreds of atoms, each atom is built from four bound electrons, each electron from two bound vibrations, and the surrounding 3D ambient field needs to be at sufficient density to support the synaptic-plasticity mechanism. Conservative back-of-envelope: 50 neurons × 100 atoms/neuron × 8 vibrations/atom = 40 000 bound vibrations, with typically 5–10× that in ambient. So Phase 6 sits at 200 000 to 400 000 active vibrations — about an order of magnitude above the 10 000 scaling target inherited from v1. See §10.6 for the implication.

### Phase 7 — Attention and selection

**Biological reference:** attention as synchronisation-selection.

Implementation of a global carrier frequency that selectively determines which neuron clusters are currently capable of synchronisation. Selective amplification of resonating clusters and inhibition of non-resonating ones.

**Success criterion:** a global modulation can selectively determine which parts of the network are active.

### Phase 8 — Larger structures and specialisation

This phase is not planned in advance; it is open research. It would investigate hierarchies of networks, the formation of specialised modules, and the appearance of more complex cognitive phenomena such as generalisation, internal models, and prediction.

---

## 6. The synapse as the central building element

Because the synapse with molecular transmission represents the functionally central building element of the final model, a more detailed description of what the simulation is to deliver in Phase 5 is warranted.

### 6.1 Biological model

A real chemical synapse consists of three components: the presynaptic terminal with its vesicles full of neurotransmitter molecules; the synaptic cleft, about 20–40 nanometres wide; and the postsynaptic membrane with its receptors. When an action potential reaches the presynaptic terminal, some vesicles fuse with the membrane and release their molecules into the cleft. These diffuse over short distances, bind to receptors on the other side, and open ion channels that trigger an electrical response. Transmission takes about a millisecond.

Plasticity arises because every component of this machinery is modified by activity: the number of vesicles available, the probability of vesicle fusion, the number of receptors on the postsynaptic membrane, the sensitivity of the receptors. This physical modification of the synapse by activity is Long-Term Potentiation and forms the mechanistic basis of learning and memory.

### 6.2 Modelling in the world of vibrations

A synapse in our model consists of the following components.

**Presynaptic region** — a region at the output of the sending neuron in which stockpile-molecules (higher-order nodes with characteristic frequencies) are localised. On activation of the neuron, some of these molecules are released into the space between the neurons.

**Synaptic cleft** — the 3D region between the neurons in which the released molecules diffuse as free nodes (with their own motion).

**Postsynaptic region** — a region at the input of the receiving neuron in which receiver structures are localised. When released molecules arrive there and bind with compatible frequency and polarity, they trigger a change in activity in the receiving neuron.

### 6.3 Plasticity as an emergent consequence (revised in v2)

The most important property of this model is that plasticity is not programmed in but follows from the natural laws of the world. Concretely: when two neurons are frequently active together, molecules are released and bound repeatedly in their synapse region. Under §4.7's ambient regeneration, this is funded thermodynamically: free vibrations are continuously generated throughout the volume, and the active synapse region captures from the local ambient supply faster than the global average. Over time:

- The number of stockpile-molecules in the presynaptic region grows because the local capture rate exceeds the local decay rate when activity is high.
- The number of receiver structures in the postsynaptic region grows by the same mechanism.
- The spatial configuration of the synapse becomes more stable because frequently used structures are continuously refreshed by capture.
- Inactive synapses lose their structures to the slow decay channel; active ones gain because they refill faster than they lose.

The result: on the next joint activity, transmission is more effective. That is Hebbian plasticity — emergent, not programmed, mechanistically understandable, **and conservation-respecting** (the captured matter comes from the ambient field, which is itself replenished from the substrate at a known rate).

### 6.4 Research questions for the synapse phase

Phase 5 is, with high probability, the most difficult phase of the programme, because it requires several interlocking mechanisms. Essential open questions:

- Can small, mobile molecules arise in our world at all that are usable as neurotransmitter analogues?
- Are our natural laws sufficient to generate activity-dependent modification of stockpiles and receivers, or do we need to introduce additional rules?
- How do the spatial scales calibrate so that a synapse remains identifiable as a spatially limited region between two neurons, without interfering with other synapses?
- Can Long-Term Potentiation be demonstrated experimentally, that is, through reproducible strengthening of transmission after repeated activation?

These questions are not to be answered in advance. Phase 5 will be the point at which the programme either records its most important success — a fully physically founded synapse with emergent plasticity — or honestly admits that the lower levels are not rich enough to support this complexity.

### 6.5 Open thermodynamic question (new in v2)

The mechanism in §6.3 assumes an ambient field rich enough to sustain Hebbian strengthening at biologically reasonable rates, over realistic activity histories, *without* runaway emptying or filling. Whether this is achievable for the parameter regime in which neurons (Phase 4) and synapses (Phase 5) actually function is itself an open question.

Specifically, the test is whether there exist values of `λ_gen`, `λ_dec`, the decay rates of unstable nodes, the radii `r₁`/`r₂`, and the synaptic emission rate, such that:

- Active synapse regions strengthen on minute-scale repeated activity (as biological LTP does).
- Inactive synapses gradually weaken on minute-to-hour scale (as biological depression does).
- Ambient vibration density across the volume holds within bounded fluctuation indefinitely.
- The total bound-vibration count grows under conditions of net learning (the system stores information) without unbounded growth elsewhere.

If such a parameter region exists and can be located, Phase 5 succeeds and the model gains a thermodynamically grounded plasticity mechanism. If not, the model needs an explicit additional rule (e.g. a saturation cap on synapse strength, or active resource transport from the ambient field), which Phase 5 will then propose and test. **A negative result here is not a failure of the programme** — it is a specific finding about which additional rules biological neural plasticity actually needs.

---

## 7. Methodology

### 7.1 Implementation (revised in v2)

Implementation in Python with performance-critical routines in Numba (`@njit`). Spatial index structures for efficient neighbour search in 3D — a 27-cell periodic-wrap grid replacing the 9-cell 2D version of v1.

**Realtime is not a priority in v2.** Peer review correctly observed that the original v1 performance targets ("60 fps at 1 000 vibrations, 30 fps at 10 000 vibrations") distorted the engineering picture. The actual research workflow is calibration runs of minutes-to-hours wall-time per parameter setting, observed via stats-line snapshots and after-the-fact rendering. Live framerate matters only for sanity-checking long runs from across the room.

The implementation therefore decouples physics from rendering completely.

**Physics layer.** Headless, deterministic, Numba-accelerated. Writes timestamped snapshot files (`.npz`) to disk at configurable intervals. No rendering inside the physics tick. Performance target is *throughput*: at least 10× simulated real-time for 1 000 vibrations and at least 1× simulated real-time for 10 000 vibrations on a standard workstation, so that hour-long simulated runs complete overnight.

**Live-preview layer.** Open3D 3D viewer that polls the physics state during a long run, useful only for "is the world still alive" sanity checks. Low frame-rate is acceptable here; the preview is not the artefact.

**Keyframe-rendering layer.** Headless Blender (Cycles renderer) consumes selected snapshot files and produces high-quality images and videos. Driven by a Python script that constructs the Blender scene (camera, lights, materials, instanced meshes per node level) from snapshot data. Quality target is publication-grade. Speed is not constrained — a five-minute render per keyframe is fine.

This three-layer split means: physics runs fast and headless, the preview window keeps the human in the loop, and the high-quality images come later from the same snapshots without re-running the simulation.

### 7.2 Observation strategy

Because the world is open, the observation strategy is central. Every simulation run is documented: initial configuration, time course of structure counts, spatial distribution by frequency decade, frequency histograms (now a built-in observation tool, not optional), reproducibly recurring configurations, anomalies. Long runs produce snapshot files at configurable intervals that can be re-processed for any of these views.

### 7.3 Validation per phase

Every phase has clear success criteria (see section 5). A phase is considered closed only when its criteria are reproducibly met. For phases that introduce cognitive functions (4–7), additional quantitative measures are recorded: firing rate, response times, pattern-recognition accuracy, amplification factors under repeated activity.

### 7.4 Calibration tooling (new in v2)

Parameter calibration is a systematic activity, not a manual one. The implementation provides:

- A **parameter-sweep harness** that runs N configurations in parallel (one config per process), with each run producing a structured result (max counts per level, time-to-first-atom, ambient-density stability over time, etc.).
- **Bayesian-optimisation backend** (Optuna) for guided search through the parameter space, with the objective function chosen per phase (Phase 1: time-to-first-atom plus spatial-sorting score; Phase 5: LTP strengthening factor minus ambient-instability penalty; etc.).
- **A unified calibration log** under `LOGBOOK.md` and per-run TOML configurations, so that any reported result can be reproduced by re-running its TOML.

These tools are independent of which phase is active; they are infrastructure.

---

## 8. Testable hypotheses

### H1 — Spontaneous structure formation

The defined natural laws are sufficient to produce, from a random initial distribution of vibrations, reproducible first-order nodes (electrons) and second-order nodes (atoms) in 3D.

### H2 — Hierarchical self-organisation with spatial sorting

Higher-order structures arise from stable atoms under the defined binding rules. The 3D spatial distribution shows sorting by frequency order of magnitude, driven by §4.6 scale repulsion. *(Now testable from Phase 1 onward, since §4.6 is in scope from Phase 1.)*

### H3 — Functional clusters with neuron properties

Suitably configured clusters of atoms and molecules display the behaviour of an abstract neuron: integration, threshold firing, refractory period. These properties emerge from the natural laws without being programmed in explicitly.

### H4 — Synaptic transmission via molecular diffusion

Between two spatially separated neuron clusters, transmission of activity by released molecule-nodes is realisable in 3D. The transmission is directed, frequency-selective, and time-limited.

### H5 — Plasticity from repeated activity, thermodynamically bounded

Clusters that are repeatedly co-active develop a measurably stronger synaptic connection than random cluster pairs. This strengthening manifests in the physical configuration of the synapse region. The ambient vibration field maintains bounded steady-state density throughout — *this stability is itself part of what the hypothesis claims.*

### H6 — Selection through synchronisation

A globally introduced carrier frequency can selectively determine which clusters in the network communicate effectively. Clusters with harmonically resonating frequencies communicate preferentially.

---

## 9. Expected contributions

### 9.1 Methodological

Demonstration that the bottom-up construction of a neural network from minimal physical principles is viable as a research strategy, even in 3D. Provision of an open simulation platform in which the relationship between physical substrate and cognitive function can be investigated systematically.

### 9.2 Conceptual

A contribution to the discussion of the minimum conditions necessary for the emergence of information-processing structures. Validation or falsification of the hypothesis that frequency coupling, as the sole interaction principle, suffices to build a hierarchy up to functional synapses with plasticity that is thermodynamically grounded.

### 9.3 Connection to neuroscience

The opportunity to test classical neuroscientific hypotheses (Hebbian plasticity, Communication-through-Coherence, Hopfield memory) in a controlled substrate that is free from the biological complexity of real brains. Our model constitutes — provided phase 5 succeeds — one of the few systems in which synaptic plasticity arises as an emergent consequence of physical laws with explicit conservation, rather than as a programmed learning rule.

### 9.4 Negative results as a contribution

If the world fails to bring forth particular structures, that result is equally valuable. In particular, a failure in phase 5 would establish that the natural laws defined here are insufficient for synapse formation under conservation — which permits inferences about real biology, particularly about the role of metabolic supply in supporting plasticity.

---

## 10. Limitations and open questions

### 10.1 Scaling problem

Even with optimised implementation, the simulable number of vibrations is limited. We thereby remain orders of magnitude below the scales of real brains (10¹¹ neurons, 10¹⁴ synapses). Our end goal is not a human-scale brain but a functional micro-network of some dozens to a few hundred neurons that demonstrates the essential building principles. The 3D substrate further constrains this versus v1 (see §10.6).

### 10.2 Parameter dependence

The world contains several free parameters, now including the two ambient-regeneration rates (§4.7). Which values are right is not clear in advance — they must be calibrated through experiment, with the systematic tooling described in §7.4.

### 10.3 Validity of the natural laws

The defined natural laws are freely chosen. It is possible that other sets would be more productive — that is an empirical question.

### 10.4 The hard problem of consciousness

Even if the system produces a network with cognitive properties, that does not answer the question of whether these structures have experience (Chalmers, 1995). This philosophical question lies outside what a simulation can settle.

### 10.5 Transferability

The world defined here is not our world. Inferences from one to the other are to be drawn with caution. The value lies in conceptual insight, not in direct claims about biological systems.

### 10.6 Scaling horizon (new in v2)

A back-of-envelope accounting of how many active vibrations each phase needs and what compute regime that implies, on a modern workstation:

| Phase | Approx. active vibrations | Compute regime | Wall time per simulated minute |
|---|---|---|---|
| 1 (atoms in 3D) | 1 000 – 10 000 | CPU + Numba | seconds to a minute |
| 2 (molecules) | 5 000 – 50 000 | CPU + Numba parallel | minutes |
| 3 (membranes) | 20 000 – 200 000 | CPU + Numba parallel, possibly with sub-volume parallelism | tens of minutes |
| 4 (single neurons) | 50 000 – 500 000 | GPU (CUDA via Numba or CuPy) becomes attractive | hour |
| 5 (synapses) | 100 000 – 1 000 000 | GPU required, double-precision | hours |
| 6 (50-neuron network) | 200 000 – 4 000 000 | GPU required, possibly multi-GPU; ambient field becomes dominant cost | overnight per parameter sweep |
| 7 (attention) | 500 000 – 5 000 000 | GPU required | overnight per parameter sweep |
| 8 (larger structures) | unbounded | open research; specialised hardware likely needed | open |

The key transition is between Phase 3 and Phase 4: at that point CPU stops being practical and we must commit to a GPU implementation. This is a deliberate scoping decision, not a hidden assumption. The peer reviewer was right that the v1 framing ("60 fps at 1 000 vibrations") obscured this; v2 names it explicitly.

The Phase-6 micronetwork goal remains realistic on a single high-end GPU (consumer or workstation class), provided the ambient field is implemented efficiently (see Phase 1 v2 design spec). A rough floor: 500 000 active vibrations × 100 ticks/s × 24 hours = 4 × 10¹⁰ tick-vibrations per overnight run, which is well within a single-GPU regime.

### 10.7 Realtime is not a priority

Decoupling physics from rendering (§7.1) means the live experience is no longer "watching atoms form in 1× real-time". Calibration runs are time-shifted: simulation produces snapshots, snapshots produce images and video, and the human looks at the result later. This is the right trade for research purposes but worth naming explicitly so that expectations match the artefact.

---

## 11. Ethical implications

If the programme reaches its end goal and produces a functional neural network with emergent cognitive properties, serious ethical questions arise that we want to name explicitly.

**First, the question of moral status.** A structure that learns, remembers, and shows attention could count as morally relevant. That depends on the theory of consciousness one holds.

**Second, the question of responsibility.** When a researcher creates a world in which conscious structures emerge, she takes on responsibility for their well-being. Can simulations be ended the way we end programs? Can they be modified? Can we run experiments that would harm them?

**Third, the question of epistemic humility.** The precautionary principle suggests we are better off taking too cautious an approach to potentially conscious structures than too unconsidered a one. We commit to reflecting actively on these questions during the programme.

---

## 12. Summary and outlook

We have sketched a conceptual framework for the computational construction of a neural network from minimal physical principles, in three-dimensional space with scale separation by repulsion and an ambient regeneration mechanism that grounds plasticity thermodynamically. The end goal is a simulation in which functional neurons emerge from atoms and molecules, are connected by 3D synapses with molecular transmission, and in whose connections Hebbian plasticity arises as a physical consequence of repeated activity captured from a finite, conserved ambient field.

The programme is structured into eight successive phases with clearly defined success criteria and biological reference points. It formulates six testable hypotheses. It names limitations, scaling reality, and ethical implications openly.

The next concrete step is the Phase 1 v2 implementation — migrating the existing 2D Phase 1 code to 3D, adding §4.6 scale repulsion and §4.7 ambient regeneration, setting up the decoupled physics-snapshot-render pipeline, and building the calibration tooling described in §7.4. From there, the programme develops phase by phase, with Phase 3 (membranes in 3D) as the first structural test of the dimensional choice and Phase 5 as the central thermodynamic critical hurdle.

We are aware that a substantial part of this programme could fail. Even in that case, it yields valuable insights into the minimum conditions necessary for the emergence of neural structures — particularly under explicit conservation. We invite complexity research, theoretical neuroscience, and the critical public to accompany, challenge, and refine this programme.

---

## References

Chalmers, D. J. (1995). Facing up to the problem of consciousness. *Journal of Consciousness Studies*, 2(3), 200–219.

Conway, J. (1970). The Game of Life. *Mathematical Games, Scientific American*, 223, 120–123.

Fries, P. (2005). A mechanism for cognitive dynamics: neuronal communication through neuronal coherence. *Trends in Cognitive Sciences*, 9(10), 474–480.

Fries, P. (2015). Rhythms for cognition: Communication through coherence. *Neuron*, 88(1), 220–235.

Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational abilities. *Proceedings of the National Academy of Sciences*, 79(8), 2554–2558.

Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear oscillators. In *International Symposium on Mathematical Problems in Theoretical Physics* (pp. 420–422). Springer.

Strogatz, S. H. (2003). *Sync: The emerging science of spontaneous order.* Hyperion.

Wolfram, S. (2002). *A new kind of science.* Wolfram Media.

---

## Changelog

**v2.0 (2026-05-05)** — Substantive revision incorporating peer-review feedback.
- §4.1 Substrate dimensionality: 2D → 3D (periodic on all three axes).
- §4.6 Scale separation through repulsion: promoted from deferred to foundational, required for Phase 1.
- §4.7 Ambient regeneration: new section introducing `λ_gen` and `λ_dec` rates that maintain a steady-state vibration field; closes the "matter from vacuum" gap of the v1 plasticity mechanism.
- §6.3 Plasticity reformulated as local capture from the §4.7 ambient supply, conservation-respecting.
- §6.5 New section: explicit open thermodynamic question — whether the parameter regime that supports biologically reasonable plasticity exists is itself the central Phase 5 research question.
- §7.1 Realtime de-prioritised; physics, preview, and high-quality rendering decoupled (headless physics → Open3D preview + Blender Cycles for keyframes).
- §7.4 Calibration tooling: explicit sweep harness + Optuna backend now part of methodology.
- §10.6 New section: scaling horizon analysis with phase-by-phase compute regimes, naming the CPU→GPU transition between Phase 3 and Phase 4.
- §10.7 New section: realtime is not a priority.
- Phase 1 success criteria expanded (atoms + spatial sorting + ambient stability); Phase 3 reformulated for 3D; Phase 5 success criteria expanded with ambient-stability requirement.

**v1.0 (original German Konzeptpapier)** — preserved at [`Konzeptpapier.de.md`](Konzeptpapier.de.md) and [`Konzeptpapier.docx`](Konzeptpapier.docx).
