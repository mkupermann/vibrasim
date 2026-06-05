# What We're Building — in plain language

*A guide for anyone, no science background needed.*

---

## The big question

Today's famous AIs (ChatGPT and friends) work by reading almost the entire internet and learning to
**predict the next word**. They're astonishing — but they're essentially gigantic pattern-matchers trained on
borrowed human writing. They don't really "understand" in the way a person does; they're very good at sounding like
they do.

This project asks a different, more old-fashioned question:

> **Can we build genuine understanding from the ground up — the way a child slowly figures out the world — instead
> of copying it wholesale from the internet?**

So we deliberately tied one hand behind our back. **We are not allowed to use any of today's big AI models** (no
ChatGPT, no "language models," no pretrained shortcuts). Everything has to be built from simple, well-understood
pieces that we fully control and can explain. It's harder this way — but if something works, we actually understand
*why*.

---

## What we built

Over time, this turned into **two connected things**.

### 1. A tiny artificial "world" (the substrate)

Imagine a sealed box full of little vibrating specks. They bump into each other, occasionally stick together to form
larger structures, and those structures can fall apart again. We wrote the physics rules and then just... let it run,
to see what would naturally emerge — like watching a terrarium.

The hope was that, with the right rules, useful behaviour (memory, communication, simple "thinking") would arise on
its own from the bottom up, the way life emerged from chemistry. We call this little world the **substrate**.

### 2. An "Understanding Engine" that reads and answers in plain English

Separately, we built a program that can **read simple factual sentences and actually reason about them** — without
any modern AI. You give it a short passage like:

> *"A poodle is a dog. A dog is a mammal. A mammal is an animal. A heart is part of a dog. A dog can bark.
> Smoking causes cancer."*

…and afterwards you can ask it questions in ordinary English, and it answers correctly:

- *"Is a poodle an animal?"* → **"Yes. A poodle is a dog, a dog is a mammal, a mammal is an animal."**
  (It chained three facts together — it wasn't told that directly.)
- *"Does a poodle have a heart?"* → **"Yes"** (it figured out that poodles, being dogs, inherit a dog's parts).
- *"Can a penguin fly?"* (after reading *"A bird can fly. A penguin cannot fly."*) → **"No"** — it correctly lets
  the specific exception override the general rule, just like a person would.
- *"What causes cancer?"*, *"Is an elephant bigger than a cat?"*, *"What happened first?"* — all answered from what
  it read.

It can also **explain its reasoning**, **notice contradictions** in what it was told, and even **learn a brand-new
kind of relationship** from examples it's never seen before. All of this with zero "big AI" — just clear rules we
wrote and can inspect line by line.

---

## What we experimented with, and what we honestly learned

We run this like a science lab, not a product team. Before every experiment we **write down in advance exactly what
would count as success or failure** — so we can't fool ourselves afterwards. A result that says *"nope, that didn't
work"* is just as valuable as a success, and we record it honestly. (We've kept a running scorecard of our own
predictions: we're right about 8 times out of 10, and every miss became a lesson we don't repeat.)

A few honest highlights:

- **The little world hit a wall for long-term memory.** After dozens of careful experiments, we found the substrate
  *cannot* reliably hold a specific memory over time — there's a fundamental trade-off: make it stable enough to
  remember and it freezes; make it lively enough to think and it forgets. That's a genuine finding, not a failure —
  it tells us something real about what these systems can and can't do.
- **…but the same little world turned out to be a surprisingly good "communication line."** The very thing that
  ruined memory (constant resetting) makes it excellent at *passing messages*. We literally sent the words
  *"EQMOD SUBSTRATE SPEAKS"* through it, intact.
- **The substrate can hold the engine's knowledge after all — as memory, not as a calculator.** Recently we showed
  that the engine's facts and its reasoning can run *inside* the little physical world (using a classic, well-known
  memory mechanism). It reliably stores about 20 facts per "module," can be expanded by adding more modules, and even
  reasons in English through it. This finally answers a question we'd been chasing for a long time: *where does the
  hand-built physics actually fit into a thinking machine?*
- **The biggest obstacle to reading real text isn't cleverness — it's the *kind* of writing.** Plain, factual,
  encyclopedia-style sentences ("A dog is a mammal") our engine reads beautifully. But a novel, a poem, or a
  philosophical argument? Those are written to *persuade and evoke*, not to *describe*, and our engine (with no
  modern AI) can't crack them. Knowing exactly where that line is, is itself a useful result.

---

## What we've achieved

- A working **Understanding Engine** that reads everyday factual English across many topics — animals, chemistry,
  geography, biology, history — and answers questions, explains itself, spots contradictions, and learns new patterns
  — **with no modern AI inside it at all.** It handles essentially the full range of common "X is a Y," "X is part of
  Y," "X causes Y," "X is bigger than Y," "X before Y," "how many," "does X have Y," and similar everyday sentences,
  and it's been stress-tested to not break on garbage input.
- A **map** of what a hand-built "physics world" genuinely can and cannot do (it's a great communication channel and
  a decent short-term reasoning store, but not a long-term memory).
- A demonstrated **bridge** between the two: the engine's knowledge and reasoning can live inside that physics world.
- Most importantly: a **disciplined, honest way of working** — predict first, test fairly, never move the goalposts,
  write down every result including the disappointing ones, and never dress up a borrowed idea as a new invention.

We're careful to say what this is **not**: it is **not** human-level understanding, and we did **not** invent new
mathematics. Everything is assembled from established, decades-old building blocks. The real products are *the working
engine*, *a handful of genuine insights*, and *the honest method*.

---

## What we're doing right now, and the goal

**Right now** we're doing three things in parallel:

1. **Toughening up the reading engine** by feeding it fresh passages from new subjects and fixing whatever trips it
   up — one honest, tested fix at a time. It now reads a comprehensive mixed-topic document with essentially perfect
   accuracy.
2. **Deepening the connection to the little physics world**, so that the "understanding" genuinely runs on the
   bottom-up substrate rather than just on ordinary computer code.
3. **Giving it SENSES, and teaching it slowly like a child — with you in the loop.** This is the newest direction.
   We've started letting it *see* and *hear*: it now looks at real photos and recognizes them, and it links a *sound*
   to a *written shape* (it can "hear" the letter A and connect it to the written "A"). Crucially, it learns the way a
   child does — **slowly, and it asks when it isn't sure.** There's now a simple **teaching tool**: it shows you what
   it's looking at, tells you its guess and how confident it is, and when it's *unsure* it asks you — you click
   *Correct* or *Not correct* (and later you'll answer in full sentences). Because it only asks when genuinely
   uncertain, you teach it the whole alphabet with a handful of answers instead of labelling everything. And it has
   started **reading**: it sees a written word, recognizes the letters, puts them together, *and understands the word*
   using what it read — so "seeing the world" and "understanding it" join up. (All of this is still simple, with
   home-made senses and a tiny vocabulary — but the full loop *perceive → learn from you → read → understand* now
   works end to end, with no modern AI.)

4. **Giving it a memory that survives and grows like a brain's.** The newest milestone. Until recently the
   substrate's knowledge lived only in the computer's working memory — close the program and it was gone. Now it
   **saves itself to disk** (a folder you can copy and back up), so it **remembers across sessions** and **keeps
   growing without forgetting** what it already knew. It keeps separate things separate — "German politics" and
   "Hungarian politics" stay distinct even though both are "politics," so learning that one is corrupt doesn't
   smear onto the other (the same trick a brain uses to keep "John's coffee" and "Mary's coffee" apart). And it
   doesn't just *recall* — it **reasons across what it stored**: tell it "a poodle is a dog, a dog is a mammal, a
   mammal is an animal, an animal is an organism," close it, reopen it tomorrow, and it can still work out "yes, a
   poodle is an organism" by chaining those facts together — none of which it was told directly. (We also measured
   the honest limits: each memory "module" holds a few hundred facts before it would blur, so to grow further it
   simply adds more modules — like a brain adding capacity.)

**The goal** — the north star — is to move, step by careful step, toward something with **human-like learning,
understanding, and communication**: a system that learns from what it reads and from experience, *actually*
understands the relationships between things, and can talk with you about them — built the honest, transparent way,
without leaning on today's giant AIs. We don't expect to reach human level; the real aim is to **break new ground on
the process and draw an honest map of what's reachable** under these strict, self-imposed rules. As the project motto
goes: *we don't stop.*

The honest edges of the map — what would need either special data or relaxing our "no big AI" rule — are: reading
genuinely messy real-world writing, *richer* real-world senses (real microphones and cameras rather than our simple
home-made ones), and freely *generating* new ideas rather than answering from what it was told. We know exactly where
those walls are, and why. That clarity is the point — and the new "teach it slowly, with you in the loop" direction is
how we start chipping at the senses wall.

---

*Everything above is recorded in detail, experiment by experiment, in this project's logbook and notes — including
every prediction we got wrong.*
