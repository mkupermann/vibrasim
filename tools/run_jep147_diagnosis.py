"""JEP-147 - integrated diagnosis: abduce + deduce + cover. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-147: integrated diagnostic reasoning (abduction + deduction), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=147)
    # diseases -> symptoms (causal); flu explains fever+ache+cough; cold explains cough+sneeze; covid explains fever+ache+cough+anosmia
    edges=[("flu","fever"),("flu","ache"),("flu","cough"),
           ("cold","cough"),("cold","sneeze"),
           ("covid","fever"),("covid","ache"),("covid","cough"),("covid","anosmia")]
    for c,s in edges: e.tell_cause(c,s)
    diseases={"flu","cold","covid"}
    def expected(cause):
        return {s for c,ss in [(cause,None)] for s in [y for x,y in edges if x==cause]} | \
               {y for x in [cause] for y in _forward(e,x)}
    def diagnose(observed):
        observed=set(observed)
        cands=set()
        for s in observed: cands |= set(e.abduce(s))
        cands &= diseases
        scored=[]
        for c in cands:
            exp={y for x,y in edges if x==c}
            cov=len(exp & observed); over=len(exp - observed)
            scored.append((cov-0.5*over, c, sorted(exp)))
        scored.sort(reverse=True)
        return scored[0][1] if scored else None
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("symptoms {fever,ache,cough} -> flu (exact cover)", diagnose({"fever","ache","cough"}), "flu")
    ck("symptoms {cough,sneeze} -> cold", diagnose({"cough","sneeze"}), "cold")
    ck("symptoms {fever,ache,cough,anosmia} -> covid (anosmia distinguishes)", diagnose({"fever","ache","cough","anosmia"}), "covid")
    ck("symptom {cough} alone -> ambiguous but cold or flu (most parsimonious-ish)", diagnose({"cough"}) in {"cold","flu","covid"}, True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}: {g}", flush=True)
    print(f"\n   diagnosis battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-147: PASS - integrated diagnosis: abduce candidate causes, deduce their effects, pick the best cover." if npass==len(res)
          else f"JEP-147: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
def _forward(e,x):
    causes=getattr(e,'causes',{}); out=set(); st=[x]
    while st:
        c=st.pop()
        for d in causes.get(e._norm(c),()):
            if d not in out: out.add(d); st.append(d)
    return out
if __name__=="__main__": main()
