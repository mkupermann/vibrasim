"""JEP-116 - cross-situational word grounding: align words to perceptual clusters by co-occurrence. Target >=0.8."""
import numpy as np
from collections import defaultdict
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(116)
def main():
    print("=== JEP-116: cross-situational word grounding (meaning without clean labels) ===", flush=True)
    FD=24
    concepts=["dog","cat","bird","fish","tree"]
    proto={c:rng.normal(0,1,FD) for c in concepts}
    distractors=["blicket","dax","wug","fep","gorp","toma","zav"]
    def perceive(feat): return min(concepts, key=lambda c: np.linalg.norm(feat-proto[c]))
    cooc=defaultdict(lambda: defaultdict(int)); word_count=defaultdict(int); clus_count=defaultdict(int)
    N=600
    for _ in range(N):
        present=list(rng.choice(concepts, size=int(rng.integers(1,3)), replace=False))
        # words heard: each present object's NAME + 1-2 distractors (referential ambiguity)
        words=[c for c in present]+list(rng.choice(distractors, size=int(rng.integers(1,3)), replace=False))
        rng.shuffle(words)
        feats={c: proto[c]+rng.normal(0,0.5,FD) for c in present}
        clusters=set(perceive(feats[c]) for c in present)
        for w in set(words):
            word_count[w]+=1
            for cl in clusters: cooc[w][cl]+=1
        for cl in clusters: clus_count[cl]+=1
    # PMI-align each cluster to its best word
    total=N
    def pmi(w,cl):
        pwc=cooc[w][cl]/total; pw=word_count[w]/total; pc=clus_count[cl]/total
        return np.log((pwc+1e-9)/(pw*pc+1e-9))
    cluster_name={cl: max(word_count, key=lambda w: pmi(w,cl)) for cl in concepts}
    correct=sum(int(cluster_name[c]==c) for c in concepts)
    acc=correct/len(concepts)
    print(f"   {N} ambiguous scenes; learned cluster->word names:", flush=True)
    for c in concepts: print(f"      cluster {c!r:7} -> '{cluster_name[c]}' {'(correct)' if cluster_name[c]==c else '(WRONG)'}", flush=True)
    print(f"   naming accuracy (no clean labels): {acc:.2f}", flush=True)
    # feed into engine: name a perceived instance, reason
    e=UnderstandingEngine(seed=116)
    e.tell("A dog is an animal."); e.tell("A bird is an animal.")
    newdog=proto["dog"]+rng.normal(0,0.5,FD)
    learned=cluster_name[perceive(newdog)]
    grounded_ok = (learned=="dog") and e.is_a(learned,"animal")
    print(f"   perceive a new instance -> grounded word '{learned}' -> is it an animal? {e.is_a(learned,'animal')}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.8 and grounded_ok:
        print(f"JEP-116: PASS - cross-situational learning grounds words to clusters WITHOUT clean labels ({acc:.2f});",flush=True)
        print(f"a perceived instance is named and reasoned about. The symbol-grounding bridge via co-occurrence",flush=True)
        print(f"statistics (Yu-Smith 2007), no explicit teaching. Established, named; no novelty.",flush=True)
    else:
        print(f"JEP-116: PARTIAL/NULL - naming {acc:.2f}, grounded_ok={grounded_ok}. Recorded honestly.",flush=True)
    print("HONEST: needs many scenes + consistent name-referent co-occurrence above the ambiguity; very high",flush=True)
    print("ambiguity or synonymy/polysemy would degrade it. The word forms are still arbitrary tokens, not semantics.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
