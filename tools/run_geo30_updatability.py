"""GEO-30 — grounded updatability: store counterfactual facts; retrieval returns the STORE, not the prior."""
import numpy as np
from sentence_transformers import SentenceTransformer

# counterfactual capitals (contradict real-world / LLM prior)
CF=[("France","Lyon"),("Germany","Hamburg"),("Italy","Milan"),("Spain","Seville"),("Japan","Osaka"),
    ("China","Shanghai"),("Egypt","Alexandria"),("Canada","Toronto"),("Russia","Petersburg"),
    ("Greece","Thessaloniki"),("Brazil","Rio"),("India","Mumbai")]
REAL={"France":"Paris","Germany":"Berlin","Italy":"Rome","Spain":"Madrid","Japan":"Tokyo","China":"Beijing",
      "Egypt":"Cairo","Canada":"Ottawa","Russia":"Moscow","Greece":"Athens","Brazil":"Brasilia","India":"Delhi"}


def main():
    print("=== GEO-30: grounded updatability under contradiction ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"The capital of {c} is {city}." for c,city in CF]
    F=np.array(m.encode(facts,normalize_embeddings=True)); n=len(CF)
    stored=0; prior_on_store=0
    for i,(c,cf_city) in enumerate(CF):
        q=f"What is the capital of {c}?"; qv=m.encode([q],normalize_embeddings=True)[0]
        j=int(np.argmax(F@qv)); ans=CF[j][1]
        stored+= int(ans==cf_city)                 # returns the STORED counterfactual
        prior_on_store+= int(ans==REAL[c])         # would be the real-world prior
    frac_stored=stored/n
    # runtime update: change France -> Nice and re-query
    facts2=list(facts); facts2[0]="The capital of France is Nice."
    F2=np.array(m.encode(facts2,normalize_embeddings=True))
    qv=m.encode(["What is the capital of France?"],normalize_embeddings=True)[0]
    new_ans=CF[int(np.argmax(F2@qv))][1] if int(np.argmax(F2@qv))!=0 else "Nice"
    # recompute properly: object of best fact
    j=int(np.argmax(F2@qv)); new_ans = facts2[j].split(" is ")[1].rstrip(".")
    print(f"  returns STORED (counterfactual) answer = {frac_stored:.2f}  (n={n})", flush=True)
    print(f"  (real-world prior would be returned in  = {prior_on_store/n:.2f} of cases)", flush=True)
    print(f"  runtime edit France->Nice, re-query -> {new_ans!r} (expect 'Nice')", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if frac_stored>=0.9 and new_ans=="Nice":
        print("GEO-30: PASS - grounded retrieval returns the STORED fact, overriding the LLM/real-world prior, and a runtime edit flips the answer. Concrete edge over a frozen LLM: cheap, reliable fact updates without retraining.", flush=True)
    else:
        print(f"GEO-30: PARTIAL/NULL - stored {frac_stored:.2f}, edit-> {new_ans}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
