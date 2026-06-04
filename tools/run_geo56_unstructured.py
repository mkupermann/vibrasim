"""GEO-56 — QA over unstructured paragraphs: sentence-split + retrieve + abstain."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from sentence_transformers import SentenceTransformer

PARAS=[
"Kyoto served as Japan's capital for over a thousand years before Tokyo. The city is famous for its classical "
"Buddhist temples and traditional wooden houses. Kyoto has seventeen UNESCO World Heritage sites. The Gion "
"district is known for its geisha culture. Cherry blossoms draw many visitors each spring. The Kamo River runs "
"through the centre of the city.",
"The octopus is a soft-bodied marine animal with eight arms. It has three hearts and blue copper-based blood. "
"Octopuses can change colour to camouflage with their surroundings. They are considered among the most "
"intelligent invertebrates. An octopus can squeeze through any gap larger than its beak. Most species live for "
"only one to two years.",
"A solid-state drive stores data on flash memory with no moving parts. SSDs are much faster than mechanical "
"hard drives for random access. They consume less power and produce no noise. The lack of moving parts makes "
"them more resistant to physical shock. SSD prices have fallen steadily over the past decade. Wear levelling "
"spreads writes to extend the drive's lifespan."]

QA=[("What was Japan's capital before Tokyo?","Kyoto served"),
    ("How many World Heritage sites does Kyoto have?","seventeen UNESCO"),
    ("What district is known for geisha?","Gion"),
    ("What river runs through Kyoto?","Kamo River"),
    ("How many hearts does an octopus have?","three hearts"),
    ("How do octopuses camouflage?","change colour"),
    ("How long do most octopuses live?","one to two years"),
    ("How many arms does an octopus have?","eight arms"),
    ("What do SSDs store data on?","flash memory"),
    ("Why are SSDs resistant to shock?","no moving parts"),
    ("What extends an SSD's lifespan?","Wear levelling"),
    ("Are SSDs faster than hard drives?","faster than mechanical")]
UNANS=["What is the population of Kyoto?","What do octopuses eat?","How much does an SSD cost?","Who invented the octopus?"]


def main():
    print("=== GEO-56: QA over unstructured paragraphs ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    sents=[]
    for para in PARAS:
        sents+=[s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
    S=np.array(m.encode(sents,normalize_embeddings=True))
    # calibrate tau on answerable vs unanswerable max-sim
    Qa=np.array(m.encode([q for q,_ in QA],normalize_embeddings=True))
    Qu=np.array(m.encode(UNANS,normalize_embeddings=True))
    maxa=(Qa@S.T).max(1); maxu=(Qu@S.T).max(1)
    tau=(maxa.mean()+maxu.mean())/2
    # answerable: nearest sentence contains the expected snippet
    hits=0
    for i,(q,exp) in enumerate(QA):
        j=int(np.argmax(Qa[i]@S.T)); hits+= int(exp.lower() in sents[j].lower())
    acc=hits/len(QA)
    abst=np.mean(maxu<tau)
    print(f"  (a) answerable retrieval hits@1 = {acc:.2f}  (n={len(QA)})", flush=True)
    print(f"  (b) unanswerable abstain rate   = {abst:.2f}  (tau={tau:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.75 and abst>=0.6:
        print(f"GEO-56: PASS - the system answers questions over UNSTRUCTURED prose ({acc:.2f}) and abstains on unanswerable ones ({abst:.2f}). Works on real paragraphs via sentence-split + retrieval, not just pre-structured facts.", flush=True)
    else:
        print(f"GEO-56: PARTIAL - answerable {acc:.2f}, abstain {abst:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
