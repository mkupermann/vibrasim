"""GEO-57 — long-document QA (~40 sentences) bi-encoder vs re-rank."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

DOC="""
Kyoto served as Japan's capital for over a thousand years before Tokyo. The Gion district is known for its geisha culture. The Kamo River runs through the centre of Kyoto. Kyoto has seventeen UNESCO World Heritage sites.
The octopus has three hearts and blue copper-based blood. Octopuses can change colour to camouflage. An octopus has eight arms and a soft body. Most octopus species live only one to two years.
A solid-state drive stores data on flash memory with no moving parts. SSDs are faster than mechanical hard drives for random access. Wear levelling spreads writes to extend an SSD's lifespan. SSDs consume less power and produce no noise.
Mount Everest is the highest mountain above sea level. It lies on the border between Nepal and Tibet. Climbers face dangerously low oxygen in the death zone above eight thousand metres.
The Amazon is the largest rainforest on Earth. It produces a large share of the world's oxygen. The Amazon river carries more water than any other river.
Photosynthesis converts sunlight into chemical energy in plants. It releases oxygen as a byproduct. Chlorophyll gives plants their green colour and captures light.
Honey bees communicate the location of flowers through a waggle dance. A bee colony has one queen and many workers. Bees pollinate a large fraction of food crops.
The speed of light in a vacuum is about three hundred thousand kilometres per second. Nothing with mass can reach the speed of light. Light from the sun takes about eight minutes to reach Earth.
The Great Wall of China stretches thousands of kilometres. It was built over many centuries to defend against invasions. The wall is not actually visible from space with the naked eye.
"""
QA=[("What was Japan's capital before Tokyo?","Kyoto served"),
    ("What district is known for geisha?","Gion"),
    ("How many hearts does an octopus have?","three hearts"),
    ("How long do octopuses live?","one to two years"),
    ("What do SSDs store data on?","flash memory"),
    ("What extends an SSD's lifespan?","Wear levelling"),
    ("Where is Mount Everest located?","Nepal and Tibet"),
    ("What is the death zone?","death zone"),
    ("What does the Amazon river carry?","more water"),
    ("What does photosynthesis release?","oxygen as a byproduct"),
    ("How do bees communicate flower locations?","waggle dance"),
    ("How fast is light?","three hundred thousand"),
    ("How long does sunlight take to reach Earth?","eight minutes"),
    ("Is the Great Wall visible from space?","not actually visible")]


def main():
    print("=== GEO-57: long-document QA ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2"); ce=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    sents=[s.strip() for s in re.split(r"(?<=[.!?])\s+", DOC.replace("\n"," ")) if s.strip()]
    print(f"  document = {len(sents)} sentences", flush=True)
    S=np.array(m.encode(sents,normalize_embeddings=True))
    base=0; rr=0
    for q,exp in QA:
        qv=m.encode([q],normalize_embeddings=True)[0]; sims=S@qv
        jb=int(np.argmax(sims)); base+= int(exp.lower() in sents[jb].lower())
        topk=np.argsort(-sims)[:5]; sc=ce.predict([(q,sents[t]) for t in topk])
        jr=int(topk[int(np.argmax(sc))]); rr+= int(exp.lower() in sents[jr].lower())
    n=len(QA)
    print(f"  bi-encoder hits@1      = {base/n:.2f}", flush=True)
    print(f"  + cross-encoder rerank = {rr/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if rr/n>=0.8 and rr/n>=base/n:
        print(f"GEO-57: PASS - long-document QA holds at {len(sents)} sentences ({base/n:.2f} bi-encoder, {rr/n:.2f} re-ranked). Document QA scales with re-ranking.", flush=True)
    else:
        print(f"GEO-57: PARTIAL - base {base/n:.2f}, reranked {rr/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
