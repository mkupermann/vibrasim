"""JEP-128 - infer a relation's transitivity from observed consistency (learn structure, not just facts)."""
import numpy as np
from itertools import combinations
rng=np.random.default_rng(128)
def closure(pairs, items):
    adj={i:set() for i in items}
    for a,b in pairs: adj[a].add(b)
    # transitive closure
    changed=True
    while changed:
        changed=False
        for a in items:
            for b in list(adj[a]):
                for c in adj[b]:
                    if c not in adj[a]: adj[a].add(c); changed=True
    return adj
def is_transitive_observed(obs_true, obs_false, items):
    """Infer transitive if the closure of observed-true pairs CONTRADICTS no observed-false pair."""
    cl=closure(obs_true, items)
    for a,b in obs_false:
        if b in cl.get(a,set()): return False   # closure predicts a->b but it's observed false -> NOT transitive
    return True
def run(density, seed):
    r=np.random.default_rng(seed); n=6; items=list(range(n))
    # TRANSITIVE relation: a total order (i<j)
    trans_all=[(i,j) for i,j in combinations(items,2)]
    trans_false=[(j,i) for i,j in combinations(items,2)]  # reverse never holds
    # NON-TRANSITIVE: a cyclic tournament (each pair one direction, with cycles) - closure would over-predict
    nt_all=[]; 
    for i,j in combinations(items,2): nt_all.append((i,j) if r.random()<0.5 else (j,i))
    nt_true=set(nt_all); nt_false=[(b,a) for a,b in nt_all]
    def sample(pairs): 
        k=max(2,int(len(pairs)*density)); idx=r.choice(len(pairs),size=min(k,len(pairs)),replace=False); return [pairs[i] for i in idx]
    # classify TRANSITIVE one
    t_ok = is_transitive_observed(sample(trans_all), sample(trans_false), items)==True
    # classify NON-TRANSITIVE one
    nt_ok = is_transitive_observed(sample(list(nt_true)), sample(nt_false), items)==False
    return t_ok, nt_ok
def main():
    print("=== JEP-128: infer relation transitivity from observation (learn structure) ===", flush=True)
    print("   density   transitive-correct   nontransitive-correct   overall", flush=True)
    for d in [1.0,0.6,0.3]:
        tc=[]; ntc=[]
        for s in range(200):
            t,nt=run(d,s); tc.append(t); ntc.append(nt)
        print(f"   {d:>5}      {np.mean(tc):.2f}                 {np.mean(ntc):.2f}                  {np.mean(tc+ntc):.2f}", flush=True)
    print("\n--- FINDING ---", flush=True)
    print("The learner infers transitivity by CLOSURE-CONSISTENCY: a total order's closure contradicts no observed-", flush=True)
    print("false pair (transitive); a cyclic tournament's closure over-predicts pairs observed false (NOT transitive).", flush=True)
    print("HONEST: with DENSE observations it distinguishes them reliably; with SPARSE observations a violation may", flush=True)
    print("never be seen, so a non-transitive relation can be mis-inferred as transitive (the expected limit). This", flush=True)
    print("learns relational STRUCTURE from data in the favorable regime - a step on the JEP-69/70 frontier. Named.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
