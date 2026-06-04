"""JEP-83 - the substrate LEARNS FROM A SOURCE and communicates (retrieval), on world.knowledge (no transformer)."""
import numpy as np
from world.knowledge import KnowledgeBase, tokenize
CORPUS = """
A cat is a small animal that people keep as a pet. The cat likes to sleep and chase a mouse.
A dog is an animal that people keep as a pet. The dog likes to run and play and bark.
A pet animal lives in the home with people who feed it and care for it.
A car is a vehicle that people drive on the road. The car has wheels and an engine.
A truck is a large vehicle that people drive on the road to carry goods.
A vehicle moves on the road using wheels and an engine and needs fuel to drive.
"""
QA = [
    ("what does the cat like to chase", "mouse"),
    ("what does a dog like to do", "bark"),
    ("what does a car drive on", "road"),
    ("what does a vehicle need to drive", "fuel"),
]
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def main():
    print("=== JEP-83: substrate LEARNS FROM A SOURCE (world.knowledge VSA/HDC, no transformer) ===", flush=True)
    kb=KnowledgeBase(dim=4096)
    kb.ingest(CORPUS)
    print(f"   ingested {len(kb.passages)} passages from the source; vocab df={len(kb.df)} words", flush=True)
    # (a) distributional meaning learned from co-occurrence
    pets=["cat","dog","pet","animal"]; veh=["car","truck","vehicle","road"]
    def rep(w): return kb._rep(w)
    within=[cos(rep(a),rep(b)) for i,a in enumerate(pets) for b in pets[i+1:]]+\
           [cos(rep(a),rep(b)) for i,a in enumerate(veh) for b in veh[i+1:]]
    cross=[cos(rep(a),rep(b)) for a in pets for b in veh]
    wm,cm=float(np.mean(within)),float(np.mean(cross))
    # probe pairs: related vs unrelated ordering
    probes=[("cat","dog","engine"),("car","truck","mouse"),("pet","animal","road"),("vehicle","road","cat")]
    correct=sum(int(cos(rep(a),rep(b))>cos(rep(a),rep(c))) for a,b,c in probes)
    print(f"   (a) distributional: within-topic sim {wm:.3f} vs cross-topic {cm:.3f} (gap {wm-cm:+.3f});"
          f" related>unrelated {correct}/{len(probes)}", flush=True)
    # (b) retrieval QA: does the top passage contain the answer word?
    hit=0
    for q,ans in QA:
        a=kb.answer(q); hit+=int(ans in tokenize(a))
    qa=hit/len(QA)
    print(f"   (b) retrieval QA: top passage contains the answer for {hit}/{len(QA)} questions ({qa:.2f})", flush=True)
    # (c) online local learning from feedback
    hardq="which animal likes to run and play"
    before=[i for i,(idx,_,_) in enumerate(kb.query(hardq,k=len(kb.passages))) if idx==1]
    for _ in range(5): kb.learn(hardq, correct_idx=1, lr=0.5)
    after=[i for i,(idx,_,_) in enumerate(kb.query(hardq,k=len(kb.passages))) if idx==1]
    print(f"   (c) online learning: target passage rank {before[0]} -> {after[0]} after local feedback updates", flush=True)
    print("\n--- VERDICT ---", flush=True)
    a_ok=(wm-cm)>=0.05 and correct>=3; b_ok=qa>=0.75; c_ok=after[0]<=before[0]
    if a_ok and b_ok and c_ok:
        print(f"JEP-83: PASS - the substrate LEARNS FROM A SOURCE with no transformer: distributional co-occurrence", flush=True)
        print(f"gives related words similar vectors (within {wm:.2f} > cross {cm:.2f}); it retrieves answers ({qa:.2f});", flush=True)
        print(f"and it improves from local feedback (rank {before[0]}->{after[0]}). This is step ONE of 'learn from", flush=True)
        print(f"sources and communicate' - established VSA/HDC + Random Indexing (Kanerva/Sahlgren), named; no novelty.", flush=True)
    else:
        print(f"JEP-83: PARTIAL/NULL - a={a_ok}(gap {wm-cm:+.2f},{correct}/4) b={b_ok}({qa:.2f}) c={c_ok}. Recorded honestly.", flush=True)
    print("HONEST CEILING: this RETRIEVES and RE-RANKS passages from the source. It does NOT (yet) GENERATE novel", flush=True)
    print("fluent English, do multi-hop INFERENCE, or demonstrate grounded UNDERSTANDING. That gap - learned,", flush=True)
    print("generative, grounded language without a transformer - is the open multi-year frontier, not today's result.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
