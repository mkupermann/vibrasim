"""GEO-9 — boundary map: which RELATION TYPES does the few-shot geometric (offset) method learn? Span easy
linear (capital, plural, past) to harder (comparative, antonym, hypernym/is-a, gender). Few-shot offset,
held-out, ranked among the union vocabulary + distractors. Honest scope map of the geometric+LLM method."""
import numpy as np
from sentence_transformers import SentenceTransformer

REL = {
 "capital": [("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),("Japan","Tokyo"),("China","Beijing"),("Egypt","Cairo"),("Russia","Moscow"),("Greece","Athens"),("Poland","Warsaw")],
 "plural":  [("cat","cats"),("dog","dogs"),("house","houses"),("car","cars"),("tree","trees"),("book","books"),("bird","birds"),("flower","flowers"),("river","rivers"),("star","stars")],
 "past":    [("walk","walked"),("play","played"),("jump","jumped"),("call","called"),("open","opened"),("close","closed"),("paint","painted"),("cook","cooked"),("clean","cleaned"),("learn","learned")],
 "comparative":[("big","bigger"),("small","smaller"),("fast","faster"),("slow","slower"),("strong","stronger"),("weak","weaker"),("tall","taller"),("short","shorter"),("warm","warmer"),("cold","colder")],
 "antonym": [("hot","cold"),("up","down"),("good","bad"),("happy","sad"),("light","dark"),("big","small"),("fast","slow"),("rich","poor"),("open","closed"),("high","low")],
 "is_a":    [("dog","animal"),("rose","flower"),("oak","tree"),("salmon","fish"),("sparrow","bird"),("apple","fruit"),("hammer","tool"),("car","vehicle"),("shirt","clothing"),("violin","instrument")],
 "gender":  [("king","queen"),("man","woman"),("boy","girl"),("father","mother"),("uncle","aunt"),("son","daughter"),("brother","sister"),("husband","wife"),("prince","princess"),("actor","actress")],
}


def main():
    print("=== GEO-9: relation-type boundary map (few-shot offset, held-out) ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    allw = sorted(set(w for pairs in REL.values() for p in pairs for w in p))
    E = np.array(m.encode(allw, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(allw)}
    rng = np.random.default_rng(0)
    for name, pairs in REL.items():
        accs = []
        for trial in range(10):
            idx = rng.permutation(len(pairs)); k = 5
            tr = [pairs[i] for i in idx[:k]]; te = [pairs[i] for i in idx[k:]]
            rv = np.mean([E[vi[b]] - E[vi[a]] for a, b in tr], 0)
            ok = 0
            for a, b in te:
                q = E[vi[a]] + rv; q /= np.linalg.norm(q) + 1e-9
                s = E @ q; s[vi[a]] = -1e9
                if allw[int(np.argmax(s))] == b: ok += 1
            accs.append(ok / len(te))
        print(f"  {name:12s} 5-shot hits@1 = {np.mean(accs):.2f}", flush=True)
    print("\n  (ranked among the full union vocabulary; maps which relation types are geometrically learnable)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
