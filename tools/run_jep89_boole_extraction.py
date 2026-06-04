"""JEP-89 - relation extraction on the REAL Boole text: how much usable structure does classic extraction yield?"""
import re
from collections import Counter
STOP=set("the a an of to in on and or is are was were be been being that which this these those it its his her "
         "we our us i you he she they them their as at by for with from into upon than then so such no not but "
         "if when where what who whom whose will shall may might can could would should must have has had do does "
         "did one two any all some each every other another more most less least very also thus hence therefore "
         "given let us above below here there now also same".split())
DEFVERBS=r"(?:is|are)\s+called|denotes?|represents?|signif(?:y|ies)|express(?:es)?|stands?\s+for|(?:is|are)\s+(?:a|an|the)"
def clean(w): return re.sub(r"[^a-z]","",w.lower())
def good(w): return w and w not in STOP and len(w)>=3
def main():
    print("=== JEP-89: relation extraction from REAL Boole prose (the parse gate) ===",flush=True)
    sents=open("data/sources/boole_clean.txt",encoding="utf-8").read().split("\n")
    triples=[]
    pats=[
        re.compile(r"\b(?:the\s+)?(\w+)\s+(?:is|are)\s+(?:a|an)\s+(\w+)",re.I),
        re.compile(r"\b(\w+)\s+(?:denotes?|represents?|signif(?:y|ies)|stands?\s+for)\s+(?:a|an|the\s+)?(\w+)",re.I),
        re.compile(r"\blet\s+(\w+)\s+(?:denote|represent|stand for)\s+(?:a|an|the\s+)?(\w+)",re.I),
        re.compile(r"\b(\w+)\s+(?:is|are)\s+called\s+(?:a|an|the\s+)?(\w+)",re.I),
    ]
    for s in sents:
        for p in pats:
            for m in p.finditer(s):
                a,b=clean(m.group(1)),clean(m.group(2))
                if good(a) and good(b) and a!=b: triples.append((a,b))
    cnt=Counter(triples)
    uniq=list(cnt.keys())
    print(f"   sentences scanned: {len(sents)}; raw triples: {len(triples)}; unique: {len(uniq)}",flush=True)
    # chains: a->b and b->c
    parents={}
    for a,b in uniq: parents.setdefault(a,set()).add(b)
    chains=[]
    for a in parents:
        for b in parents[a]:
            if b in parents:
                for c in parents[b]:
                    if c!=a: chains.append((a,b,c))
    print(f"   2-hop chains (a->b->c): {len(chains)}",flush=True)
    print("   most frequent extracted triples:",flush=True)
    for (a,b),n in cnt.most_common(15):
        print(f"      {a} -> {b}   (x{n})",flush=True)
    if chains:
        print("   sample chains:",flush=True)
        for ch in chains[:8]: print(f"      {ch[0]} -> {ch[1]} -> {ch[2]}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    plausible=len(uniq)
    if plausible>=50 and len(chains)>=5:
        print(f"JEP-89: PASS - {plausible} unique triples and {len(chains)} 2-hop chains from real Boole prose - enough",flush=True)
        print(f"structure to support inference on real content. (Inspect for precision.)",flush=True)
    else:
        print(f"JEP-89: NULL/PARTIAL - {plausible} unique triples, {len(chains)} chains. Boole's argumentative/",flush=True)
        print(f"mathematical prose yields SPARSE definitional structure - the parse gate is real on dense text. Honest",flush=True)
        print(f"measure of distance to real-text understanding: the mechanisms (JEP-88) work, but feeding them from",flush=True)
        print(f"this prose with classic extraction does not. Robust extraction / learned structure is the open frontier.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
