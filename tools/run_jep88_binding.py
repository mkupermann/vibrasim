"""JEP-88 - does VSA role-binding distinguish same-bag true/false claims that bag-of-words tied (JEP-87)?"""
import numpy as np
rng=np.random.default_rng(88)
DIM=2048
def rv():
    v=rng.normal(0,1/np.sqrt(DIM),DIM); return v
_voc={}
def vec(w):
    if w not in _voc: _voc[w]=rv()
    return _voc[w]
SUBJ,REL,OBJ=rv(),rv(),rv()
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def fact(s,r,o): return cconv(SUBJ,vec(s))+cconv(REL,vec(r))+cconv(OBJ,vec(o))
def bow(facts):  # bag-of-words: just sum all word vectors, no binding
    acc=np.zeros(DIM)
    for s,r,o in facts: acc=acc+vec(s)+vec(r)+vec(o)
    return acc
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
# (true_facts, false_facts) — false = subject/object swapped (same word multiset)
PAIRS=[
 ([("one","rep","universe"),("zero","rep","nothing")],[("zero","rep","universe"),("one","rep","nothing")]),
 ([("product","denotes","commonclass")],[("commonclass","denotes","product")]),
 ([("x","denotes","class")],[("class","denotes","x")]),
 ([("proposition","maybe","true")],[("true","maybe","proposition")]),
 ([("probability","between","zeroone")],[("zeroone","between","probability")]),
]
def main():
    print("=== JEP-88: VSA role-binding vs bag-of-words on same-bag true/false (the JEP-87 ceiling) ===",flush=True)
    # true-fact memory = all true facts
    mem=[fact(*f) for T,_ in PAIRS for f in T]
    def score_bind(facts): return float(np.mean([max(cos(fact(*f),m) for m in mem) for f in facts]))
    mem_bow=[bow([f]) for T,_ in PAIRS for f in T]
    def score_bow(facts): return float(np.mean([max(cos(bow([f]),m) for m in mem_bow) for f in facts]))
    bind_win=bow_win=bow_tie=0
    print("   pair   bind(true) bind(false)   bow(true) bow(false)",flush=True)
    for i,(T,F) in enumerate(PAIRS):
        bt,bf=score_bind(T),score_bind(F); wt,wf=score_bow(T),score_bow(F)
        bind_win+=int(bt>bf+1e-6); bow_win+=int(wt>wf+1e-6); bow_tie+=int(abs(wt-wf)<1e-6)
        print(f"   {i+1}      {bt:.3f}     {bf:.3f}        {wt:.3f}    {wf:.3f}",flush=True)
    bind_acc=bind_win/len(PAIRS); 
    print(f"\n   BINDING true>false: {bind_win}/{len(PAIRS)} ({bind_acc:.2f}); BAG-OF-WORDS true>false: {bow_win}/{len(PAIRS)} (ties: {bow_tie})",flush=True)
    print("--- VERDICT ---",flush=True)
    if bind_acc>=0.90 and bow_win<=len(PAIRS)//2:
        print(f"JEP-88: PASS - VSA role-binding SEPARATES the same-bag true/false pairs ({bind_acc:.2f}) that",flush=True)
        print(f"bag-of-words TIES ({bow_tie}/{len(PAIRS)} exact ties). STRUCTURE - a substrate primitive (HRR/VSA,",flush=True)
        print(f"JEP-66) - is the mechanism that breaks the comprehension ceiling: who-plays-which-role is encoded, so",flush=True)
        print(f"swapping subject/object changes the representation. Established (HRR, Plate 1995), named; no novelty.",flush=True)
    else:
        print(f"JEP-88: NULL/PARTIAL - binding {bind_acc:.2f}, bow wins {bow_win}. Recorded honestly.",flush=True)
    print("HONEST BOUND: assumes a PARSE into (s,r,o) roles (JEP-85 bottleneck) and a CURATED true-fact memory -",flush=True)
    print("structured verification of KNOWN facts, NOT understanding of novel prose. The mechanism, not the system.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
