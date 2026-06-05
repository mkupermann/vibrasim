"""JEP-165 - aggregate read() validation on a realistic connected encyclopedic paragraph (known ground truth)."""
from world.understanding import UnderstandingEngine
# Simple-Wikipedia-register paragraph; includes structures read() CANNOT handle (relative clauses, 'which is',
# embedded) to get an HONEST recall number, not a tuned one.
PARAGRAPH = """
A dog is a mammal. A mammal is a warm-blooded animal. Dogs and wolves are canines.
A poodle, a kind of dog, is intelligent. A heart is part of a dog. The heart pumps blood.
A virus causes an infection. An infection causes a fever. A fever causes tiredness.
A cat is a feline. Felines such as lions and tigers are predators. A predator is an animal.
A salmon, which is a fish, lives in rivers. A fish has gills. A bird has feathers and wings.
Robins and sparrows are birds. A bird is an animal. It can usually fly.
"""
# Ground-truth facts a competent reader SHOULD extract (child, parent / relation):
GOLD_ISA = {("dog","mammal"),("mammal","animal"),("dog","canine"),("wolf","canine"),("poodle","dog"),
            ("cat","feline"),("lion","predator"),("tiger","predator"),("predator","animal"),
            ("salmon","fish"),("robin","bird"),("sparrow","bird"),("bird","animal")}
GOLD_PART = {("heart","dog"),("gill","fish"),("feather","bird"),("wing","bird")}
GOLD_CAUSE = {("virus","infection"),("infection","fever"),("fever","tiredness")}
def main():
    print("=== JEP-165: aggregate read() on connected encyclopedic prose ===", flush=True)
    e=UnderstandingEngine(seed=165)
    e.read(PARAGRAPH)
    # recover extracted is-a/part/causal by querying the gold + checking for spurious via a probe set
    got_isa={(c,p) for (c,p) in GOLD_ISA if e.is_a(c,p)}
    got_part={(c,p) for (c,p) in GOLD_PART if e.part_of(c,p)}
    got_cause={(c,p) for (c,p) in GOLD_CAUSE if e.causes_effect(c,p)}
    # precision probe: count spurious is-a among a set of WRONG pairs that should NOT hold
    NEG=[("dog","fish"),("cat","bird"),("heart","animal"),("blood","dog"),("river","fish"),
         ("salmon","mammal"),("bird","fish"),("predator","plant"),("virus","animal"),("fever","animal")]
    spurious=[(c,p) for (c,p) in NEG if e.is_a(c,p)]
    def line(name,got,gold):
        rec=len(got)/len(gold)
        print(f"   {name:8s} recall {rec:.2f} ({len(got)}/{len(gold)})  missed={sorted(gold-got)}", flush=True)
    line("is-a",got_isa,GOLD_ISA); line("part-of",got_part,GOLD_PART); line("causal",got_cause,GOLD_CAUSE)
    tot_got=len(got_isa)+len(got_part)+len(got_cause); tot_gold=len(GOLD_ISA)+len(GOLD_PART)+len(GOLD_CAUSE)
    print(f"\n   AGGREGATE recall: {tot_got}/{tot_gold} = {tot_got/tot_gold:.2f}", flush=True)
    print(f"   spurious is-a among {len(NEG)} wrong probes: {len(spurious)} {spurious}", flush=True)
    print(f"   (precision proxy: 0 spurious = high precision; conservative guards)", flush=True)
    print("\n--- FINDING (fill from numbers) ---", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
