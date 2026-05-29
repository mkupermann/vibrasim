# What Happens When You Pick a Problem You Can't Solve

*A software architect with 30 years of experience walks into a field where none of his moves work. On purpose.*

---

I have been solving problems professionally for three decades. I am good at it. That's exactly the problem.

When you have thirty years of pattern-matching in a domain, every new challenge triggers a shortcut. You've seen something like it before. You reach for the move that worked last time. It usually works again. And slowly, without noticing, you stop actually thinking. You start performing expertise instead.

I wanted to know what I do when none of my moves work. Not what I think I'd do — what I actually do, observed in real time, written down as it happens. So I picked the most far-fetched problem I could imagine and walked straight into it.

## The Setup

I built a 3D box of vibrations. Points oscillating at different frequencies, bouncing around, carrying polarities. No atoms, no molecules, no cells, no neurons — just shakes in a box. A few local rules: things that match in frequency and proximity stick together. Things that stick together can stick to other things. That's it.

The topic sits four disciplines past anything I have training in. I am not a physicist. Not a chemist. Not a neuroscientist. Not a consciousness researcher. Every layer of this project lives in a field where my professional instincts give me nothing. That's not a limitation. It's the experimental design.

The question was never "can I simulate physics?" The question was: **what happens to my problem-solving process when the usual playbook is empty?**

## The First Deadlock: Nothing Grows

For months, the cascade stalled. Vibrations formed electrons (level 1). Electrons occasionally formed pairs (level 2). But higher structures — triads, atoms — never appeared. The binding rule required an 8% frequency match, and random electrons almost never hit that window.

I tried the obvious moves. Increase density. Widen the box. Run longer. Sweep parameters. This is what I'd do in consulting: if the system isn't producing the desired output, vary the inputs systematically until it does.

It didn't work. Hundreds of parameter combinations. All the same result: pairs, but nothing higher. My logbook records the failures with the same discipline I'd use for a client deliverable — because the discipline is what I came to observe.

This was the first clean deadlock. No domain shortcut available. No "in my experience, this usually means X." I was stuck the way you're stuck when you genuinely don't know something, not the way you're stuck when you're pretending not to know because the answer is uncomfortable.

## What I Did When Stuck

I read physics. Not because I needed to become a physicist, but because I needed a mechanism I couldn't invent from software intuition alone.

The answer was Kuramoto synchronization: nearby oscillators pull each other's frequencies toward alignment. It's one of the most studied phenomena in nonlinear dynamics. Pendulum clocks on the same wall. Fireflies. Cardiac cells. The mechanism exists everywhere in nature.

I added it. One rule: nearby objects pull each other's frequencies slightly toward each other. Heavier objects resist more.

The cascade unlocked immediately. Electrons that had been frequency-incompatible for months of simulation time began drifting into the binding window. Pairs formed. Triads followed. Atoms appeared. Then molecules. Then chains of molecules — structures at level 8, containing five atoms, assembled through six hierarchical binding events from raw vibrations.

**Without the mechanism:** max level 2 after 30 seconds. With it: level 4 in 10 seconds, level 8 in minutes.

The deadlock didn't break because I found the right parameters. It broke because I went outside the system's existing rules and imported a physical principle from a field I'd never studied.

That's the move I wanted to observe: **when do I stop tweaking and start learning?** The answer, uncomfortably, is "much later than I should."

## The Second Deadlock: The Shortcut That Wasn't

In parallel, I built a spiking neural network using Brian2 — a proper neuroscience simulation framework. 10,000 neurons, four cortical layers, spike-timing-dependent plasticity. I fed it raw English audiobook and asked: can it learn acoustic categories without labels?

This was a shortcut, and I knew it was a shortcut. Brian2 is someone else's abstraction of how neurons work. Using it meant borrowing thirty years of computational neuroscience instead of building from first principles. But it was fast, it was rigorous, and I told myself the results would "inform" the substrate work.

Twenty experiments later: silhouette score 0.90, zero distinct acoustic clusters. The network formed sharp internal structure but couldn't distinguish "the" from "and" — everything was either "speech" or "silence." The feedback loop collapsed. The weight analysis showed exactly why. Three separate architectural fixes all produced the same result.

The finding was clean and quantitative. But the real lesson wasn't about STDP. It was about me. I had spent weeks on the Brian2 work because it felt like progress. Import a library. Configure parameters. Run experiments. Get numbers. Write them up. The whole workflow felt productive. The infrastructure was polished. The pre-registration was meticulous.

And none of it addressed the actual project, which is: **can structure emerge from vibrations without borrowing from existing knowledge?** Brian2 is existing knowledge. Every neuron equation in it encodes decades of experimental neuroscience. Using it was the exact move my thirty years of consulting taught me: when you're stuck, find someone who already solved a piece of it and borrow their work.

That's a good move in consulting. It's a terrible move when the entire point is to observe yourself not having good moves.

## What the Deadlocks Taught Me

**I reach for infrastructure before understanding.** My first response to being stuck is always to build more tooling. A dashboard. A test suite. An autopilot. A pre-registration framework. All of these are useful. None of them solve the problem. They defer it in a way that feels productive.

**I substitute rigor for insight.** Pre-registered acceptance bars, negative controls, systematic parameter sweeps — these are the mechanics of science, and they're important. But I noticed myself using them as a substitute for the uncomfortable part: sitting with "I don't know" long enough to actually think.

**The useful move is always outside the system.** Parameter tweaks stay inside the rules. Kuramoto resonance came from outside. The decision to make atoms mobile came from outside. The realization that frequency matching is a wave phenomenon, not an atom phenomenon, came from reading chemistry instead of tuning binding radii. Every breakthrough was an import from a field I hadn't looked at yet.

**Failure records matter more than success records.** For each module in the project, I wrote a document titled "Why This Shell Is Too Thin" — what it deliberately ignores and when the simplification breaks. These turned out to be the most useful documents in the entire repository. Not the test results. Not the logbook. The failure records, because they told me where to look when I got stuck again.

## The Chain

As of today, the simulation produces hierarchical structure from vibrations through eight levels:

```
Vibrations → Electrons → Pairs → Triads → Atoms → Molecules → Chains
```

Each level emerged from local rules. No template, no blueprint, no top-down design. Each level stalled the project until a new mechanism — imported from physics I hadn't read yet — unlocked it.

Whether it goes further — whether chains can close into membranes, whether membranes can grow and divide, whether something like a neuron can emerge from the substrate's own material — I don't know. I'll find out the same way I found out everything so far: by getting stuck, staying stuck longer than is comfortable, and eventually reading something I should have read months earlier.

## Why I'm Writing This

The simulation is open source. The code runs on a laptop. But the simulation isn't the point.

The point is: I have thirty years of evidence that I'm good at solving problems in my domain. I have exactly zero evidence that my problem-solving process works outside that domain. EQMOD is the test case. Every deadlock I hit here is a clean deadlock — no shortcuts available, no domain intuition to fall back on. The moves I make under those conditions are the ones that actually generalize.

A process for breaking deadlocks that has only been tested on problems you can already solve is not a process. It's a story you tell yourself about being good at hard things.

I'd rather know what actually works.

---

*Repository: github.com/mkupermann/vibrasim — every experiment, every failure, every pre-registered acceptance bar, every logbook entry.*
