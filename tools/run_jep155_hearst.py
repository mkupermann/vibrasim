"""JEP-155 - Hearst-pattern hypernym extraction on Boole; locate the real-prose gate (extractor vs genre)."""
import re
from world.understanding import UnderstandingEngine
HEARST = [
    (r"\b([a-z][a-z\- ]{1,40}?)\s+is\s+a\s+kind\s+of\s+([a-z][a-z\- ]{1,40})", "is-a-kind-of"),
    (r"\b([a-z][a-z\- ]{1,40}?)\s+is\s+an?\s+([a-z][a-z\- ]{1,40})", "is-a"),
    (r"\b([a-z][a-z\- ]{1,40}?)\s+are\s+([a-z][a-z\- ]{1,40})", "are"),
    (r"\b([a-z][a-z\- ]{1,40}?)\s+such\s+as\s+([a-z][a-z\- ]{1,40})", "such-as(rev)"),
    (r"\b([a-z][a-z\- ]{1,40}?)\s+and\s+other\s+([a-z][a-z\- ]{1,40})", "and-other"),
    (r"\b([a-z][a-z\- ]{1,40}?),?\s+including\s+([a-z][a-z\- ]{1,40})", "including(rev)"),
    (r"\b([a-z][a-z\- ]{1,40}?),?\s+especially\s+([a-z][a-z\- ]{1,40})", "especially(rev)"),
]
def main():
    print("=== JEP-155: Hearst-pattern hypernym extraction on Boole ===", flush=True)
    text=open("data/sources/boole_clean.txt",encoding="utf-8").read().lower()
    sents=re.split(r"[.;:]\s+", text)
    e=UnderstandingEngine(seed=155)
    raw=0; valid=[]
    for s in sents:
        for pat,name in HEARST:
            for m in re.finditer(pat, s):
                raw+=1
                a,b=m.group(1).strip(), m.group(2).strip()
                # normalize + guard with the engine's own concept validity
                try:
                    na, nb = e._norm_phrase(a), e._norm_phrase(b)
                except Exception:
                    continue
                if e._valid_concept(na) and e._valid_concept(nb) and na!=nb and len(na)>1 and len(nb)>1:
                    valid.append((na, nb, name))
    print(f"   raw pattern matches: {raw}", flush=True)
    print(f"   pass _valid_concept guard: {len(valid)}", flush=True)
    # dedup
    uniq=sorted(set((a,b) for a,b,_ in valid))
    print(f"   unique candidate is-a pairs: {len(uniq)}", flush=True)
    print("   --- sample of up to 40 candidate pairs (manual genre check) ---", flush=True)
    for a,b in uniq[:40]:
        print(f"      {a:28s} IS-A  {b}", flush=True)
    # heuristic: how many look like LOGIC/VARIABLE artifacts vs natural kinds
    logic_words={"symbol","term","proposition","equation","expression","quantity","function","class","x","y","z",
                 "value","sign","factor","product","sum","number","letter","case","law","theorem","premiss","conclusion",
                 "proposition","subject","predicate","member","element","part","whole","thing","one","same","other"}
    art=sum(1 for a,b in uniq if any(w in a.split() or w in b.split() for w in logic_words))
    print(f"\n   of {len(uniq)} unique pairs, {art} contain a logic/meta term (likely artifacts), "
          f"{len(uniq)-art} look like content nouns", flush=True)
    print("\n--- FINDING (to be filled from the numbers above) ---", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
