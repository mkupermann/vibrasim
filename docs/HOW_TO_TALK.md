# How to talk to the substrate — a practical guide

Everything below runs on the substrate's own machinery — **no ChatGPT, no transformer, no pretrained model.** The
brain saves to a folder and keeps everything across days.

## 1. Have a conversation (it learns as you talk)

```
.venv\Scripts\python.exe tools\talk.py
```

Type statements to teach it, and questions to ask it. It learns from every statement (the memory grows), answers
your questions, and remembers across sessions. Example:

```
you> A poodle is a dog.        it> Got it — I learned 1 new fact (I now know 1 facts).
you> A dog is a mammal.        it> Got it — ... And that connects: nothing yet.
you> A dog can bark.           it> Got it — ... And that connects: a dog is an animal.
you> A poodle is a dog.        it> ... And that connects: a poodle is a mammal; an animal; can bark.
you> Smoking causes cancer.    it> ... Why do you think smoking causes cancer?      ← it asks YOU back
you> Is a poodle an animal?    it> Yes.
you> How many legs does a dog have?   it> 4      (after you tell it "A dog has four legs.")
you> Tell me about a poodle    it> A poodle is a dog; it can bark; it has 4 legs.
you> What is not clear to you?  it> A few things aren't clear to me yet — what is a bird?; what is a heart?
you> Draw what you know        it> Here's a picture of what I know — saved to ...png
```

It understands messy phrasing too: "isn't a poodle a dog?", "do poodles bark?", "so, is a poodle an animal?",
"what about a cat?", and multi-sentence turns ("A beagle is a dog. Is it a mammal?").

## 2. Read a whole text / book into it (over days)

Put the text in a `.txt` file, then:

```
.venv\Scripts\python.exe tools\read_to_brain.py mybook.txt
.venv\Scripts\python.exe tools\read_to_brain.py --dir mybrain anotherchapter.txt   # next day, same brain
```

It reads every clear factual sentence, learns it, and the memory **accumulates** across days. Then discuss it with
`talk.py --dir mybrain`. Honest reach today: it reads clear, factual, encyclopedia-style prose well (~93% of such
sentences); it cannot crack novels, opinion, or nuanced argument — that's the documented wall.

## 3. Ask it from the command line (one-off)

```
.venv\Scripts\python.exe tools\ask_brain.py --dir mybrain "is a poodle an animal?"
```

## How the teaching works (your three rules, built in)
- **Make connections** — when you teach it something, it relates it to what it already knows.
- **Open-ended questions** — once it has enough connected knowledge, it asks you "why?" / "what is X?" to make you
  think (it poses the question; it does not invent the answer — that's the honest limit).
- **Visual aids** — "draw what you know" renders the taxonomy it has learned.

## What "remembering" means
The brain is a folder of files (default `~/.eqmod/brain/talk`). Copy it to back up; point `--dir` at it to continue.
Corrections you make ("a whale is not a fish") are applied and kept. It grows without forgetting.
