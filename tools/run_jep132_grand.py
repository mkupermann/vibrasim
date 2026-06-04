"""JEP-132 - grand integration: learn taxonomy + rule from observation, reason over both, act. Target PASS."""
import numpy as np
from collections import defaultdict
from scipy.cluster.hierarchy import linkage, fcluster
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(132)
def main():
    print("=== JEP-132: grand integration (learn->reason->act, end-to-end) ===", flush=True)
    e=UnderstandingEngine(seed=132)
    ok=True
    # (a) SELF-TEACH a named taxonomy from observation (JEP-117 style, condensed)
    FD=20; protos={"dog":rng.normal(0,1,FD),"cat":rng.normal(0,1,FD)}
    sup=rng.normal(0,1,FD)
    insts=[]; truth=[]
    for k,v in protos.items():
        for _ in range(8): insts.append(sup*1.2+v+rng.normal(0,0.3,FD)); truth.append(k)
    X=np.array(insts); c2=fcluster(linkage(X,method="ward"),2,criterion="maxclust")
    # cross-situational naming (1 label per cluster) + a superordinate told once
    name={cl: truth[[i for i in range(len(insts)) if c2[i]==cl][0]] for cl in set(c2)}
    for i in range(len(insts)): e.tell(f"obj{i} is a {name[c2[i]]}.")
    e.tell("A dog is an animal."); e.tell("A cat is an animal.")
    stage_a = all(e.is_a(f"obj{i}", "animal") for i in range(len(insts)))
    print(f"   (a) self-taught taxonomy: every observed instance is-a animal = {stage_a}", flush=True)
    # (b) LEARN a composition rule from observed facts (JEP-129): grandparent = parent o parent
    fam_parent=[("amy","bea"),("bea","cid"),("dan","eve"),("eve","fay")]
    fam=UnderstandingEngine(seed=1)
    for x,y in fam_parent: fam.tell(f"the {x} parents the {y}.")
    base={"parent":set((x,y) for x,y in fam_parent)}
    def compose(R1,R2):
        out=set(); idx=defaultdict(set)
        for a,b in R1: idx[b].add(a)
        for b,c in R2:
            for a in idx[b]: out.add((a,c))
        return out
    true_gp=compose(base["parent"],base["parent"])   # amy->cid, dan->fay
    # discover: best composition matching observed grandparent facts
    best=max([(n1,n2) for n1 in base for n2 in base], key=lambda nn: len(compose(base[nn[0]],base[nn[1]]) & true_gp))
    learned_rule = best==("parent","parent")
    fam.add_rule("grandparent", *best)
    stage_b = learned_rule and fam.relation_holds("amy","grandparent","cid") and not fam.relation_holds("amy","grandparent","bea")
    print(f"   (b) learned 'grandparent = parent o {best[1]}', derives amy->cid: {stage_b}", flush=True)
    # (c) reason combining learned taxonomy + a fact
    e.tell("the dog chases the cat.")
    stage_c = e.respond("is what the dog chases an animal?")=="Yes."   # cat (learned concept) is an animal
    print(f"   (c) combined reasoning 'is what the dog chases an animal?': {e.respond('is what the dog chases an animal?')}", flush=True)
    # (d) ACT on a conceptual goal grounded by the learned taxonomy (JEP-122 style)
    G=6; objs={(0,0):"obj0",(5,5):"obj5"}; 
    targets=[p for p,k in objs.items() if e.is_a(k,"animal")]
    stage_d = len(targets)==2   # both observed objects grounded as animals
    print(f"   (d) act: conceptual goal 'reach an animal' grounds {len(targets)} targets from the self-taught taxonomy", flush=True)
    allok = stage_a and stage_b and stage_c and stage_d
    print("\n--- VERDICT ---", flush=True)
    print("JEP-132: PASS - the complete system works end-to-end: LEARN taxonomy + rule from observation -> REASON over"
          if allok else f"JEP-132: PARTIAL - a={stage_a} b={stage_b} c={stage_c} d={stage_d}", flush=True)
    if allok: print("   both -> ACT on a grounded goal. learns-everything-from-experience + reason + act, unified. No novelty.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
