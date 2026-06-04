"""JEP-64 - does grounded concept formation COMPOSE or only CATEGORIZE? (compositional generalization test)"""
import numpy as np
rng=np.random.default_rng(64)
K=5; AD=24
proto=rng.normal(0,1,(K,AD))  # primitive affordance prototypes
def outcome(subset, sigma=0.3): return sum(proto[k] for k in subset)+rng.normal(0,sigma,AD)
def main():
    print("=== JEP-64: does concept formation COMPOSE or only CATEGORIZE? ===", flush=True)
    # train items: SINGLE primitives (the agent sees each affordance alone)
    singles=[(k,) for k in range(K)]
    train_obs={k: np.mean([outcome((k,)) for _ in range(30)],0) for k in range(K)}  # learned prototype per primitive
    # TEST: novel TWO-primitive combinations (never observed together)
    import itertools
    combos=list(itertools.combinations(range(K),2))
    # (a) CATEGORIZE: nearest single-primitive prototype -> predicts ONE primitive (can it get BOTH? no)
    cat_recall=[]
    # (b) COMPOSE: additive decomposition - solve which primitives sum to the outcome (greedy/threshold on projections)
    comp_recall=[]
    P=np.array([train_obs[k] for k in range(K)])  # K x AD learned prototypes
    for combo in combos:
        for _ in range(20):
            o=outcome(combo)
            # categorize: nearest prototype (single best) -> 1 primitive predicted
            near=int(np.argmin(np.linalg.norm(P-o,axis=1)))
            cat_pred={near}
            cat_recall.append(len(cat_pred & set(combo))/len(combo))
            # compose: least-squares which primitives are present (binary via threshold on nonneg coefs)
            coef,_,_,_=np.linalg.lstsq(P.T,o,rcond=None)  # o ~= sum coef_k * P_k
            comp_pred=set(np.argsort(coef)[-2:])  # top-2 coefficients (we know 2 primitives; honest: uses |combo|)
            comp_recall.append(len(comp_pred & set(combo))/len(combo))
    cr=np.mean(cat_recall); co=np.mean(comp_recall)
    print(f"  CATEGORIZE (nearest-prototype) recall on novel 2-combos = {cr:.3f}", flush=True)
    print(f"  COMPOSE (additive decomposition) recall on novel 2-combos = {co:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if cr<0.6 and co>=0.9:
        print(f"JEP-64: characterization confirmed - the grounded approach CATEGORIZES, it does NOT COMPOSE on its", flush=True)
        print(f"own. Nearest-prototype concept formation gets only {cr:.2f} of a novel combination's affordances (it", flush=True)
        print(f"assigns to ONE category). An EXPLICITLY COMPOSITIONAL model (additive decomposition) recovers {co:.2f}.", flush=True)
        print(f"So composition is NOT emergent from clustering - it must be BUILT IN. This BOUNDS the approach: it", flush=True)
        print(f"does categorization, not compositional understanding - consistent with 'synthesis, not innovation'.", flush=True)
        print(f"Established (clustering, linear decomposition), named as such.", flush=True)
    else:
        print(f"JEP-64: PARTIAL/unexpected - categorize {cr:.2f}, compose {co:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
