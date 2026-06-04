"""GEO-15 — relational geometry at the SENTENCE level (toward text understanding). MiniLM, CPU."""
import numpy as np
from sentence_transformers import SentenceTransformer

PAIRS = [("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),
         ("Japan","Tokyo"),("China","Beijing"),("Egypt","Cairo"),("Canada","Ottawa"),
         ("Russia","Moscow"),("Greece","Athens"),("Poland","Warsaw"),("Norway","Oslo")]


def main():
    print("=== GEO-15: sentence-level relational geometry ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    facts = [f"The capital of {c} is {city}." for c,city in PAIRS]
    ques  = [f"What is the capital of {c}?" for c,_ in PAIRS]
    F = np.array(m.encode(facts, normalize_embeddings=True))
    Q = np.array(m.encode(ques,  normalize_embeddings=True))
    n = len(PAIRS)
    # (a) retrieval: question -> nearest fact
    S = Q @ F.T
    retr = np.mean([int(np.argmax(S[i])==i) for i in range(n)])
    # control: shuffled
    perm = np.array([ (i+5)%n for i in range(n)])
    ctrl = np.mean([int(np.argmax(S[i])==perm[i]) for i in range(n)])
    # (b) sentence analogy via relation offset (leave-one-out)
    hits=0
    for i in range(n):
        tr=[j for j in range(n) if j!=i]
        off=np.mean([F[j]-Q[j] for j in tr],0)
        pred=Q[i]+off
        d=np.linalg.norm(F-pred,axis=1)
        hits+=int(np.argmin(d)==i)
    ana=hits/n
    print(f"  (a) retrieval question->fact   hits@1 = {retr:.2f}  (chance {1/n:.2f})", flush=True)
    print(f"      shuffled control                  = {ctrl:.2f}", flush=True)
    print(f"  (b) sentence analogy via offset hits@1 = {ana:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if retr>=0.75 and ana>=0.6:
        print("GEO-15: PASS - relational geometry LIFTS to the sentence level (retrieval + analogy both work on full LLM sentence embeddings).", flush=True)
    elif retr>=0.75:
        print(f"GEO-15: PARTIAL - retrieval works ({retr:.2f}) but sentence analogy weak ({ana:.2f}); sentence offsets less linear than word offsets.", flush=True)
    else:
        print(f"GEO-15: NULL - retrieval {retr:.2f}, analogy {ana:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
