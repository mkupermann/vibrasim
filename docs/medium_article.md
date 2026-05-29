# I Built a Universe to Break My Own Problem-Solving

I charge $$$ a day to solve problems. Thirty years of software architecture. I'm good at it, and that became the problem — I stopped noticing when I was pattern-matching instead of thinking.

So I picked a topic I know nothing about. Not "a little rusty" nothing. Four disciplines past my training nothing. I decided to build matter from vibrations in a 3D box. No atoms pre-installed, no chemistry, no biology. Just oscillating points with frequencies, and a few local rules about when they stick together.

I wanted to watch what I actually do when the usual playbook is empty. Write it down. See what survives.

What I didn't expect is that the tools I'd build along the way would turn out to be more useful than the simulation itself.

## The Simulation Stalled for Months

Two vibrations bind into an "electron" if their frequencies differ by 8% and they're close enough with opposite polarity. Electrons bind into pairs, pairs into triads, triads into atoms. Same rule each level. Clean, local, no magic.

Except it didn't work past level 2. Electrons formed fine. Pairs, sometimes. Triads, almost never. Atoms, never.

I did what I always do — sweep parameters. Density up, box size down, tolerance wider. Hundreds of runs. The logbook got long. The results didn't change. The 8% frequency window was too narrow for random electrons to hit, and no amount of parameter tuning was going to fix that because the problem wasn't the parameters.

I wasted two months before I understood that.

## The Fix Came From Outside

When I finally stopped tweaking and started reading, I found Kuramoto synchronization — coupled oscillators pulling each other's frequencies toward alignment. Pendulum clocks on the same wall. Fireflies. It's textbook physics, decades old.

I added one rule. Nearby objects drift their frequencies toward each other. Heavier objects resist more.

Atoms. Ten seconds.

Level 5 molecules in minutes. Level 8 chains — five atoms bonded through six hierarchical steps — shortly after. From vibrations. No template. No design.

The two months of parameter sweeps taught me nothing about the simulation. They taught me something about myself: I default to staying inside the system. Adjusting knobs. Running variations. It feels like work. It isn't. The actual work was reading a physics textbook I should have opened on day one.

## The Neural Network Was a Comfortable Detour

Parallel to the substrate work, I built a spiking neural network. Brian2, 10,000 neurons, four cortical layers, STDP plasticity. Fed it English audiobook for hours. No labels, no pre-trained models — that was the rule.

Twenty experiments. Pre-registered bars. Negative controls. Scaling sweeps. Clean methodology. Great infrastructure.

Zero acoustic selectivity. The network learned to distinguish speech from silence. That's it. Every cluster responded to the same thing.

The methodology was real. The rigor was real. The result was real. But I'd spent weeks on it because it felt productive — import a library, configure, measure, report. That workflow is my comfort zone. And it was a detour from the actual question, which was never "can Brian2 learn from audio" but "can structure emerge from my substrate without borrowing anyone else's science."

Brian2 IS someone else's science. Every equation in it encodes decades of neuroscience. Using it was the consulting move: find someone who already solved a piece, borrow their work. Good move at €1,300 a day. Wrong move when the whole point is to not have moves.

## What Actually Came Out of This

I didn't plan for what happened next. The tools I built to manage this mess turned out to be more useful than the simulation.

**Pre-registered experiments.** Every run has acceptance criteria written before the data exists. PASS, FAIL, or NULL — the verdict is mechanical. No post-hoc threshold adjustments. Three NULLs on the same mechanism means stop, not retry. This discipline didn't come from a methodology book. It came from catching myself reinterpreting failed runs as "interesting partial results" at 2am.

**Failure records.** For each module I wrote a document: "Why This Shell Is Too Thin." What was deliberately simplified, what it ignores, when the simplification breaks. These turned out to be more useful than any test suite. When I got stuck, the failure records told me exactly where to look.

**The autopilot.** An autonomous pipeline that pre-registers experiments, runs them, evaluates against bars, logs verdicts, commits to git, and decides what to run next. No human input. It ran twenty experiments over a weekend while I wasn't looking. Most of them failed — that's the point. The autopilot doesn't care about failure. It cares about coverage.

**The process itself.** I learned to tell the difference between productive rigor and comfortable busywork. I learned that tweaking parameters feels like work but isn't, and that reading a textbook I'd been avoiding always was. I also learned — late, and expensively — when to throw away an entire approach because it was a detour dressed up as progress.

I extracted the pipeline into its own repo — [single-mac-autopilot](https://github.com/mkupermann/single-mac-autopilot). It runs on a MacBook. It does pre-registered research autonomously. The simulation is its test bed. But the pipeline travels without the simulation.

## The Chain

The simulation itself produces eight levels of hierarchical structure from raw vibrations:

```
Vibrations → Electrons → Pairs → Triads → Atoms → Molecules → Chains
```

Each level emerged from local rules without top-down design. Each level stalled the project until I imported a mechanism from outside — Kuramoto resonance for frequency synchronization, thermal motion for atom mobility, the recognition that atoms aren't waves and shouldn't be bound by wave rules.

Whether it goes further, I don't know. Membranes. Cells. Synapses made of the substrate's own material instead of imported equations. That's the open question.

## Why This Matters Outside My Hobby Project

Everyone hits deadlocks where the usual moves don't work. A product that won't converge. A team that's stuck. A technical decision where every option has a fatal flaw. The instinct is always the same: stay inside the system, tweak harder, build more infrastructure, borrow someone else's solution.

The moves that actually worked came from outside. Every single time. I'd go read something in a field I hadn't looked at yet, and bring back a principle that reframed the problem. The parameter sweeps never got me there.

That's not a finding about vibration physics. That's a finding about problem-solving. And it took building an entire fake universe to see it clearly, because in my real work, the domain shortcuts are always available, and I always take them.

---

*Everything is open source. The simulation, the experiments, the logbook, the failures, the autopilot. It runs on a laptop in pure Python.*

*Repository: github.com/mkupermann/vibrasim*
