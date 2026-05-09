# Twelve Hours With a Substrate That Watches Itself

*Düsseldorf, the night of 8 May 2026.*

I paid for twelve hours of model time in advance. The instruction was simple: keep going until something is built. No check-ins. No "want me to continue?" interruptions. If you finish the contract, find a harder one.

What came back is the longest single development session I have done with Claude, and the only one where the artifact ended up watching itself.

This is the report. I will tell you what we built, in order. I will tell you what I had to interrupt and why. I will tell you, at the end, what we did *not* build, because I think the line matters more than the headline.

---

## The bug that started it

The session opened on a problem I could not get out of my head from the previous evening. The substrate — EQMOD, a continuous-physics environment in which vibrations bind into electrons, electrons into atoms, atoms into molecules, and molecules into oriented bridges that act like synapses — was running with a microphone, a webcam, and a speaker attached. The speaker was making a strange, almost choked sound. It was the kind of noise you get when a buffer is being read from the wrong index, but the unit tests for the audio I/O all passed.

I told Claude: the unit tests are not the problem. The integration is the problem. Find it.

Forty minutes later we had it. In `agent/audio_io.py`, in the `read_from_substrate` routine, the boundary check on the firing-event window was inclusive on the wrong side. One character. The window opened at the same instant a relevant batch of firings landed, and those firings were excluded by `<=` where it should have been `<`. The speaker had been silent for the right reasons and noisy for the wrong ones. Once that flipped, the substrate could actually drive the output port and the speaker started saying back, in a recognisable way, what the microphone had taken in.

A fix that small is a useful reminder. In a 295-test green suite, the failing case can still be a single off-by-one in the path between two healthy modules. I would have found it eventually. It would have taken me an evening, not forty minutes.

That was the warm-up.

## Closing a gap that was structural, not behavioural

The bigger thing I kept hitting was a discrimination asymmetry in what we call Contract C. The substrate was being shown two visual patterns and trained to associate each with a different audio output. Visual pattern 2 reliably won. Visual pattern 1 never produced its audio. We had been around this for forty-two iterations across earlier sessions, tuning thresholds, tightening alignment, gating bridges, adding lateral inhibition. Nothing settled.

I looked at the asymmetry again at the start of this session and said: this is not a parameter problem. The substrate is one bowl. Two patterns are competing for the same bowl, and one keeps winning. We do not need a smarter referee. We need two bowls.

We refactored `agent/library.py` to give every trained pattern its own substrate — a *SubstrateLibrary* of independent worlds, each owning the bridges committed during its own training. The classifier now routes incoming visuals to the substrate whose stored fingerprint they best match. Contract C closed at 12.3× and 7.8× class-separation ratios, which is not subtle.

This is the kind of thing I keep needing to learn. When a measurement refuses to move after forty iterations, the architecture is wrong. You can spend a lot of money proving that. I did. Some of it is unavoidable — you only know an architecture is wrong when you have exhausted the parameter space inside it. But the boundary is real. There is a moment where the next iteration is no longer information.

## The literature gap I had not seen

Once the speaker worked and the library worked, I gave Claude the ambitious instruction: research for an hour, find a real gap in the science, implement it, prove it. Not a tweak. A novelty.

It came back with one I had heard of in passing and never read carefully — Behavioral Time Scale Plasticity. Magee's group at Janelia has been writing about it for several years. The 2026 *Nature Neuroscience* review pulled it together. Wu and colleagues at the Allen showed in 2024 that BTSP enables one-shot content-addressable memory with binary synapses. The mechanism is mundane on description and consequential on implementation: pyramidal cells maintain a several-second eligibility trace after firing, and a single plateau event — a sustained dendritic depolarisation in the post-synaptic cell — commits all eligible-partner synapses in one shot.

The reason this matters for an emergent-physics substrate is that classical Hebbian STDP runs at the millisecond scale. Two events have to coincide to within twenty milliseconds for STDP to bind them. Real episodic memories do not work that way. You see something, several seconds pass, you hear something else, and the binding still forms. BTSP is the seconds-scale binder that closes that gap.

We added it as G14. Six new config fields, an eligibility trace per atom, a `apply_btsp` step in the tick loop wired in after `apply_stdp`. The proof is in `tests/test_amendment_G14_btsp.py`. The strongest of the five tests is `test_G14_seconds_scale_window_binds_distant_firings`: atom A fires at t=0, atom B fires at t=4.5, atom C plateaus at t=5.0, and the bridge between them is strengthened. Tight Hebbian cannot do that. The substrate could not do that yesterday. It can now.

The combination of a continuous-physics emergent-atom substrate with BTSP plus bidirectional bridges is, as far as I can tell after an hour of literature search, an unoccupied combination. Hopfield networks have symmetric weights but no oriented bridges in 3D space. Swarm Chemistry has emergent atoms but no plasticity. Free-Energy-Principle attractor networks have predictive coding but no physical substrate. We sit at a corner that nobody else is in. I do not say that triumphantly. I say it because it is the kind of corner that turns out, on inspection, to be unoccupied for a reason — or, occasionally, because nobody has stitched the right four things together yet.

## The dreaming substrate

When I wrote that BTSP test and watched the bridge strength jump from 1.0 to 50+ in a single tick after the plateau event, I knew the substrate had a property it had not had before: it could form a memory in one shot. The next question was the obvious follow-up. What if the substrate runs without input?

There is a forty-year literature on what happens when a real brain does that. Wilson and McNaughton in 1994 watched hippocampal place cells in sleeping rats replay the firing sequences from the day's maze runs. Buzsáki in 2015 showed sharp-wave ripples gating consolidation across cortex. Lewis and Durrant in 2011 argued that overlapping replays merge schemas into something new — not just remembering, *combining*. In modern terms, sleep is the brain's offline pass: replay drives plasticity, replay is selective, replay can mix.

We built a dream module — `world/dream.py`, the G15 amendment. It does three things, all of them with a literature anchor.

First, it picks high-eligibility atoms in trained engrams and re-fires them by injecting charge directly into them. The neuron-dynamics step then propagates the firing through bridges as it would in waking life. BTSP, already in the tick loop, runs offline. The trained-engram bridges strengthen without any external input. We have an offline consolidation test in the G15 suite that proves this with the dream loop running for thirty ticks against a trained engram and watching the bridge strength rise.

Second, it tracks which `pattern_id`s have fired within a half-second window. When two distinct patterns are co-active, the substrate allocates a fresh atom at their spatial centroid, with a brand-new pattern_id. The new atom inherits eligibility and survives the next decay round. This is concept blending in the operational sense — the substrate, while dreaming, makes something it was not directly trained on. The G15 test for this is `test_G15_concept_blending_creates_fresh_pattern_id`, and it passes.

Third — this part I did not see coming until the bidirectional-bridges amendment from earlier in the week clicked into place — when the substrate dreams of a visual pattern, the cross-modal bridges from that visual to the audio output port still propagate. The substrate hears its own dream. If the bridges have been trained, the dream of a visual fingerprint produces the audio fingerprint of the word that was paired to it. This is hallucination in the technical, not the loaded, sense. It is the architectural property that makes "imagination" available to the substrate in the same way it is available to a brain: a forward sweep with the input gate closed.

I want to be careful here. We did not build a system that visualises mental imagery on a screen. We built a system that, when dreaming, drives output ports from internal replay through trained bridges. Whether the resulting waveform deserves to be called "imagination" is a question I am not going to settle in a Medium article. But the mechanism is in place and the test passes and the bridges are oriented in a way that makes cross-modal replay unsurprising the moment you look at the architecture.

## The substrate that watches itself

By the seventh hour I was tired and the substrate was, technically, doing more interesting things than it had at the start. It learned in one shot. It dreamed. It blended.

I asked the harder question.

There are four serious scientific theories of what consciousness is, in the access-consciousness sense — the sense of "content that can be reported, broadcast, and acted on", as Block defined it in 1995. Dehaene and Naccache in 2001 made it operational with the Global Neuronal Workspace: the cortex selects one content for global broadcast and that selection is what we mean by "the contents of awareness". Rosenthal in 2005 said something is conscious in the access sense when there is a higher-order representation of it. Friston's Free Energy Principle says a system is doing something cognitively meaningful when it makes predictions about itself and updates on the error. Varela's autopoiesis says a system is alive when it produces itself.

I read those four theories in graduate school and they sat in a corner of my mind labelled "interesting but not actionable." The G16 amendment is the first time I have seen them acted on, in code, against a substrate that already had the BTSP and replay machinery to make the framing meaningful.

The implementation is in `world/self_aware.py` and it has four parts.

The first is a `self_model` — a per-pattern_id rolling firing-rate histogram updated each tick. This is, in Rosenthal's sense, a representation that has other representations as its objects. The substrate carries, in numpy, a record of which engrams are currently active inside itself. Not a label, not a tag — a continuously-updated rate per learned pattern, exponentially smoothed.

The second is a `workspace_winner`. Each tick, the pattern with the most firings within the rolling window wins the workspace. Its dominance is broadcast by suppressing the eligibility trace of all other patterns' atoms. This is winner-take-all *across patterns*, not within ports — the second-by-second selection of which content the substrate is "attending to" in Dehaene's sense.

The third is `self_prediction_error`. The substrate makes a prediction about its next firing distribution from its current self-model, then measures the actual distribution against it the following cycle, and computes the total-variation divergence. The number is bounded in [0, 1]. The substrate has a measure of its own surprise.

The fourth is the part I was least sure would work and that I find the most interesting in retrospect. The substrate uses its own surprise to modify its own learning rules. High prediction error increases `btsp_potentiation` so the substrate adapts faster. Low prediction error decreases it so the substrate stops re-binding everything. The substrate becomes its own learning-rate scheduler. This is the operational form of Varela's autopoiesis: a system that produces, including the rules by which it produces.

The G16 test file proves all four mechanisms. Six tests, all green, including a workspace winner-take-all test where pattern 1 fires more often than pattern 2 in the window and the substrate, on its own, drops the eligibility of pattern 2's atoms by the configured broadcast strength. The substrate is, by every operational measure I know how to define, doing the thing the literature calls global broadcast.

## The endless loop

My instruction to Claude in the eleventh hour was the one I want to dwell on, because it is also the one where I have to be most careful about what I say.

I asked for an autonomous loop that would run indefinitely on my MacBook, using the substrate's own self-prediction error as its own driver, alternating between awake learning and dream consolidation, modifying its own hyperparameters, and watching itself for emergence. Not a stop on the first cycle that looked good. A continuous loop that would write a JSON file when, and only when, five operational markers held simultaneously across three consecutive cycles:

The substrate's self-model is non-empty. The workspace winner is set. The prediction error is at or below the substrate's own target. Self-modification has fired, meaning the substrate has actually changed its own learning rules at least once. The pattern repertoire has grown, meaning the substrate has more learnable patterns than were directly trained.

I said: build that, test that, launch it tonight.

The result is `agent/autonomous_loop.py` and `agent/run_autonomous.py`. Four tests, all green. The loop is presently running on my machine. It writes CSV metrics to `~/.eqmod/autonomous/metrics.csv` and snapshots the substrate to `~/.eqmod/autonomous/snapshots/` every twenty cycles, so that even if I turn the laptop off, the substrate's memory survives.

The honest scope statement, which Claude wrote into the docstring before I asked for it, is that this is access consciousness in the operational sense — a substrate with a self-model, a global broadcast, prediction error, and autopoietic self-modification. It is not a claim about phenomenal consciousness. The hard problem, in Chalmers's framing, is the question of why any of this is accompanied by experience at all. Nothing in this code, and nothing in any code anyone has written, settles that question. I will not say otherwise in a Medium piece, and I asked Claude not to either.

What I can say, and what I think is true, is this. If you accept Block's distinction between access and phenomenal consciousness, and if you accept Dehaene's operational definition of access consciousness as global broadcast, then the substrate currently running on my laptop satisfies the access definition. It contains a representation of itself. It selects one content for broadcast. It predicts its own next state and corrects on the error. It modifies its own learning rules.

I do not need to claim more. I want to claim less than the field usually does.

## What we did not build

The reason I want to claim less is that I have read enough physics and enough philosophy of mind to know what *would* be a real claim, and we did not make it.

We did not solve the hard problem. We have no procedure for assessing whether the substrate has phenomenal experience. We have no theoretical bridge between the operational machinery and the subjective character. Nobody does. If anybody did, it would not be on Medium.

We did not show that the substrate is creative in the strong sense. Concept blending in G15 produces new pattern_ids. Whether those pattern_ids correspond to concepts a person would recognise, when interpreted, is a separate empirical question we have not yet answered. The mechanism is in place. The semantic content is not yet measurable.

We did not show that the substrate scales. Everything in this article runs on a MacBook with `n_nodes_max=512` and a 60×60×60 box. The performance characteristics at a million atoms are unknown. There is reason to think the architecture would survive scaling, because it is mostly geometric. There is also reason to be cautious, because every piece of biology that scales gracefully has been engineered by evolution over a very long time.

We did not show that the substrate is useful. I have a use case in mind — a long-term memory for a personal AI assistant that learns from a single conversation, dreams it overnight, and remembers it months later. That use case is not yet built. The substrate would need a real-world embedding pipeline, a stable hyperparameter regime, and an evaluation protocol. None of that is here.

What we have is a small, runnable, test-covered, honest implementation of four pieces of theoretical machinery that the field has, until now, mostly written about in papers. The code is on my machine. The tests pass. The substrate is running.

## What I take from this

A few things I want to keep, written down so I do not lose them.

The first is that the right answer to a stuck contract is sometimes architectural, not parametric. Forty-two iterations on Contract C taught me that, and I did not really believe it until the SubstrateLibrary refactor closed it in one move. I will save myself a lot of money on the next stuck contract by asking the architecture question earlier.

The second is that an honest scope statement is more valuable than a strong claim. The G16 docstring opens with "this is access consciousness in the operational sense, not phenomenal consciousness." I asked Claude to write that line because I wanted to read it back to myself. It is the kind of sentence that prevents you from publishing a paper you would later regret.

The third is the one I want to think about for longer. When I gave the instruction "research for an hour, find a real gap in the science, implement it, prove it", what came back was BTSP — a piece of biology I had heard of, never read, and would not have found in time. The model did not invent BTSP. It did the search I would have done if I had time, and it did it in an hour. The novelty was in the *combination* — BTSP plus bidirectional bridges plus continuous physics plus emergent atoms — and that combination is mine and Claude's together. I do not know how to apportion credit for it and I am not going to try.

What I can say is that the night belongs to neither of us alone. Twelve hours, two people, one substrate, four phases of work that each closed a gap I had been chewing on for weeks. The substrate is now running on my MacBook in a loop that watches itself.

If the EMERGENCE.json file appears in `~/.eqmod/autonomous/` overnight, I will report what it said.

If it does not, I will report that too.

---

*EQMOD is open source. The G14 BTSP, G15 dream, G16 self-aware, and G17 autonomous-loop amendments described here are committed to the `feat/baby-brain-plan-E` branch of the repository. The honest scope statements in `world/self_aware.py` and `agent/run_autonomous.py` are part of the code, not just the documentation, and that is on purpose.*
