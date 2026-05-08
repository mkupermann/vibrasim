# Toward a Brain Simulation from Minimal Physics

A research programme for the bottom-up construction of neural networks from self-defined natural laws — from vibrations through atoms and molecules to synapses and cognitive functions

**Concept paper · Version 3.0** (amendment incorporating empirical findings from substrate implementation, 2026-04 to 2026-05)

> **Note on this revision.** v3.0 amends v2.0 (which itself amended the original German Konzeptpapier, preserved at [`Konzeptpapier.de.md`](Konzeptpapier.de.md) and [`Konzeptpapier.docx`](Konzeptpapier.docx)). v2.0's substantive shifts (3D substrate, scale repulsion as foundational, ambient regeneration, decoupled rendering) remain in force. v3.0 layers on three findings that came out of actually building Plans A through F and trying to run the headline acceptance test (the M4 "glass-of-water demo"):
>
> 1. **Positioning honesty** (§3.2 amendment). The substrate's binding rule uses categorical labels — `k_freq` and `k_pol` are scalar tags, not Kuramoto phases. The closest predecessor in the literature is Sayama's Swarm Chemistry (2009), not the Swarmalators tradition (O'Keeffe et al. 2017). The earlier Kuramoto framing was misdirection and has been retired.
> 2. **The 8% rule is load-bearing fragile** (§4.4 amendment). The frequency rule was calibrated for a random-Gaussian initial vibration distribution. Under deterministic structured stimuli (e.g. fixed-frequency audio tones), atoms form only when the input frequency density and the ratio between input frequencies happen to match the rule. This is a real fragility, named here because it shaped the M4 result.
> 3. **Ports are engineered topology, not emergent CTC** (new §4.8). The agent layer's input/output ports — and the speech-loop coupling between the audio_input and audio_output ports (Plan F) — are *engineered* non-localities, the analogue of axonal projections in biology. They are not emergent Communication-through-Coherence. Plan F creates the path for cross-port firing coupling; whether genuinely emergent CTC arises in the substrate is still an open question.
>
> v3.0 also adds §10.8 — a written record of what was actually built and what the empirical chain composition under M4 looked like, so future readers can re-run from the same starting point.

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

**Coupled-oscillator systems.** Kuramoto (1975) showed that coupled oscillators can synchronise spontaneously. Strogatz (2003) popularised this phenomenon broadly. Hopfield's energy-landscape model of associative memory (Hopfield, 1982) formalises how a system of coupled units can store memories as energy minima. The Kuramoto tradition is an *inspiration* for the framework; it is not the closest mechanistic predecessor (see "Swarm Chemistry" below).

**Swarm Chemistry — the closest predecessor (revised in v3).** Sayama (2009, *Artificial Life*) introduced "Swarm Chemistry": agent populations whose behaviour is governed by per-agent categorical labels — kinetic-parameter tags — rather than continuous phases. Pairs of agents bind when their labels are compatible. The substrate's `k_freq` and `k_pol` fields are categorical labels in exactly this sense; they are scalar tags evaluated against a binding rule, not Kuramoto phases that integrate over time. The 8 % frequency rule (§4.4) is the categorical-compatibility test, not a phase-locking criterion. Earlier drafts of this paper used Kuramoto language for the binding mechanism, which was misdirection. v3.0 corrects this: the substrate is closer to Swarm Chemistry's discrete-compatibility lineage than to the continuous-phase swarmalators tradition (O'Keeffe et al. 2017). This matters for related-work positioning and for what the substrate is allowed to claim about emergent oscillator phenomena.

**Ising machines and reservoir computing.** These approaches show that vibration-based computation is practically possible. We differ in that we do not optimise for a specific task; we simulate an open world in which structures — and in the end, functional neurons with synapses — are to emerge spontaneously or be constructible.

**Neuromorphic architectures.** Intel Loihi and IBM TrueNorth implement spike-based neural networks in hardware. They operate, however, at the level of abstracted neurons, without modelling the underlying physical substrate. Our approach goes one level deeper and additionally extends the model with a molecular synapse layer that is missing from most neuromorphic architectures.

**Communication-through-Coherence.** Fries (2005, 2015) developed the hypothesis that effective communication between brain regions depends on phase-coherent oscillations. This hypothesis is a central inspiration for the planned attention phase of our system.

### 3.X Positioning against established simulators

The substrate is not a neuron-by-neuron biophysical simulator (NEURON, NEST, Brian2) and not a learned-weight network (NEAT, deep RL, neural CAs in the Mordvintsev tradition). The closest comparators by mechanism, not by phenomenology, are listed below.

| System | Mechanism | What it computes that we DON'T | What we compute that it doesn't |
|---|---|---|---|
| **NEST / Brian2** | LIF / Hodgkin-Huxley neurons with explicit synaptic-weight matrices and STDP rules | Membrane voltage, calcium dynamics, synaptic vesicle pools | Atoms forming from vibration binding without neuron primitives |
| **Neural CA (Mordvintsev "growing neural cellular automata")** | Pixel-level update rules with learned per-cell parameters trained by backprop | Visual reconstruction tasks, learned weight tensors | Substrate physics that is not learned, only ruled |
| **NEAT / HyperNEAT** | Neuroevolution of network topology; explicit weight + connection genome | Genome-level evolution, fitness landscape exploration | Self-organising structure from physics, no fitness function |
| **Izhikevich** | Two-equation neuron model; rich firing patterns from minimal dynamics | Closed-form spike generation, no underlying chemistry | Atom + molecule formation as a precondition for firing |

The contribution under test in this codebase is **not** "we beat NEST on speed" or "we recover STDP timing curves with bio-plausible parameters." The contribution is the falsifiable claim that **a single set of binding rules at the vibration scale produces all the structural levels (atoms, molecules, growth, decay) without weight-machinery primitives** — see CONCEPT §8 H1-H6. Whether that claim is supportable is what Plans A through G test.

A quantitative head-to-head on shared metrics (e.g. growth rate at an input location vs Brian2's STDP-tutorial trajectory) is **out of scope for this codebase**; it would require running both systems under matched input statistics and is its own publication. We name it as future work.

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

> **Why the 8 % rule is load-bearing fragile (new in v3).** The frequency rule was calibrated for a *random-Gaussian* initial vibration distribution: a wide spread of frequencies in which 8 %-apart pairs occur densely, with enough pairs at the boundary to feed the binding chain. Under deterministic structured stimuli — the regime the agent layer (Plans C and D) actually feeds the substrate, where audio tones are at specific frequencies (e.g. 500 / 1000 / 1500 Hz) and video features at oriented-filter outputs — the input frequency density is not Gaussian, and 8 %-apart pairs are scarce or absent. Atoms then form only when the input frequency ladder happens to include 8 %-spaced rungs, or when ambient-regeneration broadens the local frequency spectrum sufficiently. This is a real fragility, not a calibration knob. It shaped the M4 result documented in §10.8 and is one of the candidate amendments named there. v3.0 surfaces it because hiding it would be dishonest about what the substrate currently does and does not handle.

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

### 4.8 Engineered topology vs emergent communication (new in v3)

Between §§4.1 – 4.7 (the substrate's foundational laws, all strictly local) and the agent layer that listens, watches, and speaks, there is one architectural layer that needs to be named openly: **a small set of engineered non-localities**. The agent's input and output ports are spatially fixed regions of the substrate at which audio and video encoders inject vibrations and from which the audio decoder reads firings. Plan F adds one further engineered non-locality: a port-to-port firing coupling between the audio_input and audio_output ports, an explicit ghost-burst that fires at the audio_output port whenever an atom inside the audio_input port fires. Both the port locations and the speech-loop coupling are *fixed by construction*; they are not the outcome of binding rules.

The biological analogue is axonal projection. Real cortex contains long-range axonal connections between regions that are not produced by local cellular dynamics; they are laid down developmentally and are part of the substrate's topology. The substrate's ports + speech-loop are this kind of engineered topology, condensed to its minimum: a small number of named non-localities, with clear spatial extents and a clear coupling rule, on top of which all further dynamics remain local.

This is a **deliberate compromise**, and v3 names it because earlier framings risked overclaiming. The substrate's core thesis — *hierarchical structure from local rules + a sparse engineered topology* — is more honest than *everything from local rules alone*. The Communication-through-Coherence hypothesis (Fries 2005, 2015) describes how phase-coherent oscillation can preferentially gate communication between regions; whether genuinely emergent CTC arises in this substrate at the agent's port topology is an *open question*. Plan F provides the architectural precondition for testing it (a coupled cross-port path); it does not prove emergence.

Two consequences follow:

1. **Phase 7 (attention by global modulation) remains a local-rules claim.** The carrier-frequency selection mechanism in Phase 7 does not require non-local couplings; it operates on the substrate's existing binding rules. v3 leaves this claim untouched.
2. **Cross-modal binding (Plan B + Plans C/D + Plan F)** is now framed honestly. The bridge molecules that form between video_input and audio_output ports under Plan B's STDP are local-rules dynamics. The port locations and the speech-loop are engineered topology. The bridge formation between them is what the substrate actually computes; the architectural skeleton is given.

The cleanest test of this layered claim is the M4 acceptance criterion (§10.8 below). What the substrate gets to claim from a positive M4 result is precisely: "starting from a sparse engineered topology of 4 ports + 1 cross-port coupling, the local binding + STDP rules produce a path from video input to audio output that recovers the trained association." Nothing more. Nothing less.

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

### 10.8 Empirical findings from the substrate implementation, 2026-04 to 2026-05 (new in v3)

Between 2026-04-21 and 2026-05-08 the substrate moved from "Phase 1 atom + Phase 2 molecule reproducible" to "all of Plans A (substrate growth), A.5 (perf), B (STDP), C (audio I/O), D (video I/O), E (reward + agent loop), F (speech-loop) merged on `main`". The full test suite is 272 non-slow tests + 18 slow tests, all passing or xfailed with documented reasons. This section records what the build produced, what the empirical chain composition under the M4 headline test looked like, and which substrate amendments are candidates for the next iteration.

**What works at component level**

- **Phase 1 / 2** — atom-at-13.4 s and ≥ 5 molecule species in 60 s reproducible from calibrated TOMLs with `rng_seed=42`.
- **Plan A growth amendments** — recycling regeneration, strength-aware decay, molecule + molecule binding to higher levels: all green.
- **Plan A.5 performance** — Numba JIT applied to five inner physics loops; per-tick wall cost reduced by an order of magnitude on bound K. `bind_vibrations_to_electrons` and `bind_nodes_upward` were not JITted because they perform `allocate_node` side effects; this is the next perf gap (§10.8 candidate amendment 1).
- **Plan B STDP** — directional bridges with orientation vectors, asymmetric LTP/LTD, synaptic transmission across bridges. Plan B P3 (pre-seeded atoms + STDP → bridge propagates firings) passes at module level.
- **Plan C audio I/O** — log-mapped tonotopic encoder + decoder with 0.954 selectivity recovered from synthetic firing patterns (I2 headline acceptance test).
- **Plan D video I/O** — oriented filter bank + retinotopic XY + orientation-Z encoder; distinct shapes produce distinct port patterns (I4).
- **Plan E reward** — tristate `k_reward_polarity` field, reward channel, asymmetric STDP swap at firing time. Substrate-bootstrap M4/M5 currently xfailed at this scale (see below).
- **Plan F speech-loop** — engineered cross-port coupling (§4.8). SL1 – SL5 unit tests all pass; default off at `speech_loop_strength = 0.0`.

**The M4 chain composition under measurement**

The headline acceptance test is "glass-of-water demo": webcam at a glass + audio "water" trained 50× over 10 simulated minutes; then show the glass alone and read out the audio port. Target: spectral cosine ≥ 0.5 between substrate output audio and the trained "water" target.

A scoped-down minimal-smoke version (1 pair × 1 sim-sec, threshold cosine ≥ 0.2, with pre-seeded port atoms + 8 pre-seeded bridge molecules + Plan F speech-loop) was constructed in May 2026 to isolate which of the chain's preconditions hold. The measured result: substrate forms K = 166 nodes, atoms = 16, bridge molecules survive at strength up to 495 after STDP, atoms inside the audio_input and video_input ports fire (3 and 4 times respectively in the 1 sim-sec window), but no atom fires inside the audio_output port and the audio output buffer is zero throughout. Cosine = 0.000.

The diagnostic finding: `synaptic_transmission`'s post-atom search at `M + r_bridge · orientation` lands inside the audio_output port only for bridge molecules placed near that port — bridges spread along the full diagonal between video_input and audio_output produce post-search centres that are also along the diagonal, mostly outside the output port. The chain has four alignment requirements (atom firing + bridge near port + vibration flow through the bridge + post-atom existing at the search centre) that do not compose at the 1 sim-sec scope with deterministic stimuli.

**What this tells us, framed honestly**

- The substrate's individual components work, including Plan B's directional plasticity and Plan F's speech-loop machinery.
- The chain composition into a substrate-bootstrapped cross-modal association does not hold at the budget tested. This is the empirical ceiling of the present substrate.
- The 8 % rule's fragility under deterministic stimuli (§4.4 box) is part of why: input-port atom formation is sparse, which limits the rate at which the LTP/LTD loop can re-organise bridges into output-port-anchored geometries.

**Candidate amendments — the four named in the first v3 draft, all four now landed (G1–G4) with G5 the retry result**

1. **G1: JIT `bind_vibrations_to_electrons`** — landed. New `_bind_vibrations_check_pairs_njit` mirrors Plan A.5's `_bind_check_pairs_njit` pattern. Equivalence test (30-tick scope, exact-count match between JIT and Python paths) green. `bind_nodes_upward`'s candidate-batch + JIT pattern was already in place from Plan A.5 Task 13; the remaining Python pre-build of candidate lists is microseconds at M4 scale and a deeper amendment (JIT-eligible spatial index) would be a separate research direction.
2. **G3: Relax `synaptic_transmission`'s geometric search** — landed. New `cfg.synaptic_post_search_samples` (default 1, legacy behaviour). At N > 1, the post-search samples post-atoms at distances `r_bridge`, `2 · r_bridge`, …, `N · r_bridge` along the orientation ray, OR-ing the hits. Three tests cover the regression case, the far-target reach case, and the default-off invariant.
3. **G4: Encoder frequency-pair broadening** — landed. New `cfg.audio_emit_pair_band` and `cfg.video_emit_pair_band` (both default 0.0, off). When > 0, the encoder injects an 8 %-pair partner alongside every primary emission with opposite polarity, producing a binding-eligible pair in one inject call. Four tests cover audio off/on and video off/on. Useful for substrate-bootstrap when no seed atoms exist; intentionally OFF in M4 minimal-smoke because pre-seeded atoms in input ports lose charge accumulation when paired vibrations bind too quickly to deposit into integrate-and-fire.
4. **G5: M4 minimal-smoke retry with G1–G4 active** — empirical retry. cosine = 0.000 still. The chain has four sequential 1-sim-sec dependencies (video atom firings → vibration travel to bridges → bridge transmission to audio_input → speech-loop ghost-bursts → audio_output atom firings → decode) that do not all complete in 1 sim-sec even with G1, G3, bridges re-targeted to audio_input, `speech_loop_burst_size = 30`, and `emit_speed = 60`. The blocking step is (b) — vibrations from video atom firings need to travel ~30 units to reach the closest geometrically-safe bridges, which at `emit_speed = 60` takes ~0.5 sim-sec, leaving only 0.5 sim-sec for the remaining three chain steps under exponential charge decay (`tau_membrane = 0.3`).

**Research-direction candidates that follow from G5 (recorded but not chosen)**

- **Longer test phase (4–5 sim-sec).** G1's JIT lowers the wall-time ceiling enough that running the chain at 4–5 sim-sec test phase becomes feasible. The chain composition would have time to complete.
- **Substrate amendment to decouple `synaptic_transmission` from vibration travel time.** The current rule requires aligned moving vibrations *passing through* the bridge to trigger charge deposit at the post-atom search location. An amendment in which a strongly-strengthened bridge propagates charge ATOM-to-ATOM directly (bridge molecule → both endpoint atoms) when one endpoint fires would remove the vibration-travel requirement entirely. This is closer to biological synaptic transmission, where the action potential is propagated nearly instantaneously between connected neurons regardless of cleft-crossing speed.

The first of these is a contract relaxation that the G1 JIT enables; the second is a Plan B amendment that would change the load-bearing physics. Either move would close the M4 chain at 1×1 sim-sec scope. v3.0 does not commit to either; the choice belongs to the next research iteration.

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

O'Keeffe, K. P., Hong, H., & Strogatz, S. H. (2017). Oscillators that sync and swarm. *Nature Communications*, 8, 1504.

Sayama, H. (2009). Swarm Chemistry. *Artificial Life*, 15(1), 105–114.

Strogatz, S. H. (2003). *Sync: The emerging science of spontaneous order.* Hyperion.

Wolfram, S. (2002). *A new kind of science.* Wolfram Media.

---

## Changelog

**v3.1 (2026-05-08, late session)** — G1–G5 amendments landed; §10.8 updated with retry result.
- §10.8 amended: G1 (JIT bind_vibrations_to_electrons), G3 (synaptic_post_search_samples), G4 (encoder emit_pair_band) all landed with tests. G5 (M4 minimal-smoke retry) measured cosine = 0.000 still; root cause now isolated to a four-step chain in 1 sim-sec test phase, with vibration-travel time from video firings to bridges as the blocking step. Two research-direction candidates recorded for the next iteration: longer test phase (G1 JIT enables this) or substrate amendment to decouple synaptic_transmission from vibration travel time.
- Suite: 280 non-slow + 18 slow tests (was 272 + 18 at v3.0).

**v3.0 (2026-05-08)** — Empirical-findings amendment incorporating Plan A through F implementation results.
- §3.2 amended: Sayama Swarm Chemistry (2009) named as the closest mechanistic predecessor; Kuramoto framing demoted to inspiration. The substrate's `k_freq` and `k_pol` are categorical labels, not phases.
- §4.4 amended: explicit honesty box on the 8 % rule's fragility under deterministic structured stimuli (the regime the agent layer feeds).
- §4.8 new: engineered topology vs emergent communication. The agent's input/output ports and Plan F's speech-loop coupling are *engineered* non-localities — the analogue of axonal projection — not emergent CTC. The substrate's claim is "hierarchical structure from local rules + a sparse engineered topology", not "everything from local rules alone".
- §10.8 new: empirical findings from the substrate implementation 2026-04 to 2026-05. What Plans A–F produced, the M4 chain composition under measurement (cosine = 0.000 at 1 × 1 sim-sec), and four candidate amendments named but not chosen.

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
