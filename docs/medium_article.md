# When Waves Become Atoms: Building Hierarchical Matter from First Principles

*How frequency synchronization drives spontaneous structure formation in a simulated universe*

---

I've been building a simulation where everything starts as vibrations. No atoms, no molecules, no cells — just oscillating points in a 3D box with frequencies, velocities, and polarities. The question: can hierarchical structure emerge from local rules alone, without any top-down design?

After months of work, the answer is yes. But the path there revealed something unexpected about what makes emergence possible.

## The Rules

The simulation has remarkably few rules:

1. **Vibrations move** through a periodic 3D box at constant velocity.
2. **Two vibrations bind** into an "electron" if they're close enough, have opposite polarity, and their frequencies differ by exactly 8% (plus or minus 0.5%).
3. **Electrons bind into pairs**, pairs into triads, triads into atoms — same rules each time.
4. **Atoms bind by proximity and polarity alone** — no frequency matching required at this level.
5. **Higher structures are permanent.** Pairs and triads can decay; atoms cannot.

That's it. No forces, no fields, no Schrodinger equation. The names "electron" and "atom" are analogies for hierarchical levels, not physics claims. The question is purely about emergence: do these rules produce interesting structure?

## The Problem

For months, they didn't.

Vibrations formed electrons readily. Electrons occasionally formed pairs. But the cascade stalled there. Triads were rare. Atoms were essentially impossible. The reason: the 8% frequency rule. Two electrons had to differ by *exactly* 7.5-8.5% in frequency to bind. In a random population, that's a narrow window. Most electrons just sat there, close in space but incompatible in frequency, forever.

Increasing density helped marginally. Widening the frequency tolerance felt like cheating — relaxing the rule until it stopped being a rule. I tried dozens of parameter combinations. The logbook records the failures systematically.

## The Breakthrough: Kuramoto Resonance

The fix wasn't a parameter tweak. It was a new mechanism: **frequency synchronization**.

Nearby objects pull each other's frequencies toward alignment, proportional to their difference. This is the Kuramoto model — a well-studied phenomenon in physics where coupled oscillators spontaneously synchronize. I added one line to the frequency update:

```
df/dt = (coupling / level) * (f_neighbor - f_self) / max(f_self, f_neighbor)
```

The `/level` term is important: heavier structures synchronize slower. Electrons (level 1) drift quickly. Atoms (level 4) are four times more sluggish — they maintain their identity while still being influenced by neighbors.

The result was immediate. Within 10 seconds of simulation time, electrons that had been frequency-incompatible for the entire prior run began drifting into the 8% binding window. Pairs formed. Triads followed. Atoms appeared at 20 seconds.

**Without resonance:** max level 2 (pairs) after 30 seconds. 75 electrons, 5 pairs.
**With resonance:** max level 4 (atoms) after 30 seconds. 23 electrons, 14 pairs, 11 triads, 2 atoms.

Same initial conditions. Same seed. Same rules. The only difference: nearby objects influence each other's frequencies.

## From Atoms to Chains

Atoms presented a new problem. They formed, but they were stationary — stuck at the position where their constituent triad and electron had merged. Two atoms across the box couldn't interact.

The fix was physical: **thermal motion**. Atoms get a random velocity inversely proportional to the square root of their level (heavier = slower, per thermal equipartition). Sub-atomic structures stay stationary — they need stillness for frequency synchronization.

This separation was critical. Mobile electrons would drift apart before resonance could bring them into binding range. Stationary electrons + resonance = binding. Mobile atoms + proximity rule = fusion.

With mobile atoms, the cascade continued:

```
500s:  Level 8  {electrons: 4, pairs: 4, triads: 4, L6: 2, L7: 1, L8: 1}
```

Level 8: a structure containing 5 atoms, formed spontaneously from vibrations through six hierarchical levels. No template, no guidance, no pre-designed architecture.

## What Didn't Work: The Neural Network Detour

In parallel, I spent weeks building a spiking neural network (Brian2, 10,000 neurons, 4 cortical layers) to see if STDP could learn acoustic categories from raw audio. No labels, no pre-trained models — just spike-timing-dependent plasticity on a continuous English audiobook stream.

The result was instructive:

- **Silhouette score 0.90** — the network formed sharp internal clusters
- **0 distinct acoustic clusters** — all clusters responded to the same thing (speech vs. silence)
- **Weight analysis:** feedforward pathways differentiated (Gini 0.51), but the feedback loop collapsed entirely (Gini 0.999 = all weights near zero)

Twenty experiments, four feedback-fix variants, a scaling sweep from 2K to 20K neurons. All produced the same result: STDP creates assemblies but not multi-class selectivity. This is a known limitation of pair-based STDP, but seeing it empirically — with pre-registered acceptance bars, negative controls, and systematic parameter variation — was valuable.

The deeper lesson: I was using Brian2 as a shortcut. The real project isn't about bolting neural dynamics onto a substrate. It's about building the substrate itself, layer by layer, and letting neural-like behavior emerge from the physics.

## What I Learned About Methodology

**Pre-registration works, even for one person.** Every experiment had acceptance criteria written before the run. When results came back, the verdict was mechanical: PASS, FAIL, or NULL. No post-hoc threshold tuning, no "well, if we adjust the criterion slightly..." Three sequential NULLs on the same mechanism (credit assignment via R-STDP) were treated as a finding, not a failure to retry.

**Failure records matter more than success records.** For each module in the project, I wrote a document titled "Why This Shell Is Too Thin" — describing what the module deliberately ignores and when the simplification would break. These turned out to be the most useful documents in the repository, because they told me where to look when things stopped working.

**Negative results are findings.** The STDP work produced no acoustic categorization after 50+ hours of GPU time. That's not a waste — it's a quantitative answer: pair-based STDP with 10K neurons and 17 minutes of audio exposure does not produce multi-class selectivity. The inter-cluster cosine of 0.999 means all clusters hear the same thing. That's publishable data, not an embarrassment.

## The Chain So Far

```
Vibrations  ->  Electrons  ->  Pairs  ->  Triads  ->  Atoms  ->  Molecules  ->  Chains
(Level 0)      (Level 1)     (Level 2)   (Level 3)   (Level 4)   (Level 5)    (Level 6-8)
   |              |             |            |           |            |            |
 8% rule      8% rule       8% rule      8% rule    proximity    proximity    proximity
 + polarity   + polarity    + polarity   + polarity  + polarity   + polarity   + polarity
 + proximity  + resonance   + resonance  + resonance + mobility   + mobility   + mobility
```

Each level uses the same binding physics, but with different dominant mechanisms:

- **Levels 0-3:** Frequency matching drives binding. Resonance is the enabler — without it, the cascade stalls at level 2.
- **Levels 4+:** Proximity drives binding. Frequency matching is irrelevant (atoms are not oscillators in the same sense). Thermal mobility is the enabler — without it, atoms never meet.

## What's Next

The chain reaches level 8. The next step is **closed structures** — chains that loop back on themselves, forming a boundary between inside and outside. In biology, that's a membrane. In the simulation, it would be the first structure with a distinct interior.

Whether the current rules can produce closure is an open question. It might require a new mechanism (directional binding, surface tension analogue) or it might emerge from the existing proximity rule at sufficient density. I don't know yet. That's the point.

## The Code

Everything is open source: the simulation, the experiments, the logbook, the failure records. Every finding has a pre-registered acceptance bar and a git commit with the exact code that produced it.

The project isn't trying to model real physics. It's asking a simpler question: **what's the minimum set of local rules that produces hierarchical structure from nothing?** The current answer: oscillation, frequency matching, spatial proximity, polarity, resonance, and thermal motion. Six mechanisms. Eight levels of hierarchy. Zero top-down design.

---

*The simulation runs at 2,200 ticks per second on a laptop using pure numpy — no GPU, no Numba, no CUDA. The entire codebase is Python.*

*Repository: github.com/mkupermann/vibrasim*
