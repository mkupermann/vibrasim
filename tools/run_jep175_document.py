"""JEP-175 - full-DOCUMENT scale: read a multi-paragraph encyclopedic article, reason across topics."""
from world.understanding import UnderstandingEngine
DOCUMENT = """
A dog is a mammal. A mammal is a warm-blooded animal. A dog has a heart and a brain.
The heart pumps blood. Dogs and wolves are canines. A poodle is a kind of dog.
A cat is a feline. Felines such as lions and tigers are predators. A predator is an animal.
A cat has whiskers. A whisker is a sensory organ.

A bird is an animal. A bird has feathers and wings. Birds such as robins and eagles can fly.
An eagle is a bird of prey. A penguin is a bird that cannot fly. A feather is part of a wing.

A virus is a microbe. A virus causes an infection. An infection causes inflammation.
Inflammation causes pain. A bacterium is a microbe. Antibiotics kill bacteria.

A tree is a plant. A plant is a living thing. An oak is a kind of tree.
A tree has roots and leaves. A leaf makes food. Photosynthesis happens in a leaf.
"""
GOLD_ISA = {("dog","mammal"),("mammal","animal"),("poodle","dog"),("dog","canine"),("wolf","canine"),
            ("cat","feline"),("lion","predator"),("tiger","predator"),("predator","animal"),
            ("robin","bird"),("eagle","bird"),("penguin","bird"),("bird","animal"),
            ("virus","microbe"),("bacterium","microbe"),("oak","tree"),("tree","plant"),("plant","living thing"),
            ("whisker","sensory organ")}
GOLD_PART = {("heart","dog"),("brain","dog"),("feather","wing"),("whisker","cat"),
             ("root","tree"),("leaf","tree"),("wing","bird"),("feather","bird")}
GOLD_CAUSE = {("virus","infection"),("infection","inflammation"),("inflammation","pain")}
def main():
    print("=== JEP-175: full-document scale ===", flush=True)
    e=UnderstandingEngine(seed=175)
    learned=e.read(DOCUMENT)
    print(f"read a {DOCUMENT.count('.')}-sentence document -> {learned}", flush=True)
    gi={p for p in GOLD_ISA if e.is_a(*p)}; gp={p for p in GOLD_PART if e.part_of(*p)}; gc={p for p in GOLD_CAUSE if e.causes_effect(*p)}
    tg=len(gi)+len(gp)+len(gc); tt=len(GOLD_ISA)+len(GOLD_PART)+len(GOLD_CAUSE)
    print(f"recall: is-a {len(gi)}/{len(GOLD_ISA)}, part {len(gp)}/{len(GOLD_PART)}, causal {len(gc)}/{len(GOLD_CAUSE)} = {tg}/{tt} ({tg/tt:.2f})", flush=True)
    print(f"missed: {sorted((GOLD_ISA-gi)|(GOLD_PART-gp)|(GOLD_CAUSE-gc))}", flush=True)
    # CROSS-TOPIC reasoning (combining facts from different paragraphs)
    print("\ncross-topic Q&A:", flush=True)
    for q in ["is a poodle an animal?","is a heart part of an animal?","does a virus cause pain?",
              "is an oak a living thing?","is a penguin an animal?","what causes inflammation?"]:
        print(f"  {q:34s} -> {e.respond(q)}", flush=True)
    # precision probe
    NEG=[("dog","bird"),("virus","animal"),("oak","animal"),("cat","dog"),("leaf","animal"),("heart","cat")]
    sp=[p for p in NEG if e.is_a(*p)]
    print(f"\nspurious is-a among {len(NEG)} wrong probes: {len(sp)} {sp}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
