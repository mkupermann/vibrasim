"""JEP-87 - comprehension probe: can the Boole-trained substrate separate TRUE from FALSE claims (same vocab)?"""
import numpy as np
from world.knowledge import KnowledgeBase
PAIRS = [
 ("the symbol x represents a class of things","the symbol x represents a number greater than ten"),
 ("x multiplied by x is equal to x in the symbols of logic","x multiplied by x is equal to zero in the symbols of logic"),
 ("the symbol 1 represents the universe of all things","the symbol 1 represents nothing at all"),
 ("the symbol 0 represents nothing","the symbol 0 represents the universe of all things"),
 ("logic can be expressed by an algebra of symbols","logic cannot be expressed by any algebra of symbols"),
 ("the laws of thought are the foundation of logic","the laws of thought are the foundation of geometry"),
 ("a proposition may be either true or false","a proposition may be either heavy or light"),
 ("the operation of election selects a class of objects","the operation of election selects a colour of light"),
 ("probability is a quantity between zero and one","probability is a quantity between ten and twenty"),
 ("the sign of equality expresses that two classes are the same","the sign of equality expresses that two classes are different"),
]
def main():
    print("=== JEP-87: comprehension probe - TRUE vs FALSE Boole claims (same vocabulary) ===", flush=True)
    sents=open("data/sources/boole_clean.txt",encoding="utf-8").read().split("\n")
    kb=KnowledgeBase(dim=4096, lam_ctx=0.8, lam_ng=0.3); kb.ingest("\n".join(sents))
    def score(stmt):
        s=kb._scores(stmt)
        return float(np.max(s)) if s.size else 0.0
    wins=0; gaps=[]
    for t,f in PAIRS:
        st,sf=score(t),score(f); wins+=int(st>sf); gaps.append(st-sf)
    acc=wins/len(PAIRS)
    print(f"   pairs: {len(PAIRS)}; TRUE scores higher than matched FALSE in {wins}/{len(PAIRS)} ({acc:.2f})", flush=True)
    print(f"   mean(score_true - score_false) = {np.mean(gaps):+.4f}  (near 0 => can't tell truth from vocabulary)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.80:
        print(f"JEP-87: PARTIAL - weak comprehension signal: the Boole geometry separates true from false {acc:.2f} of",flush=True)
        print(f"the time even with matched vocabulary. Worth probing why; still far from understanding.",flush=True)
    else:
        print(f"JEP-87: NULL (expected, honest) - retrieval does NOT equal comprehension. The substrate scores by",flush=True)
        print(f"VOCABULARY overlap, not TRUTH: true vs false matched-vocab claims separate at {acc:.2f} (~chance). It",flush=True)
        print(f"matches words, it does not judge whether a statement about Boole's logic is correct. This is the honest",flush=True)
        print(f"understanding gap on the real text - exactly the line between retrieval and human-level understanding.",flush=True)
    print("HONEST: judging truth needs entailment/contradiction over MEANING (structure + inference), which",flush=True)
    print("bag-of-words retrieval lacks. Bridging it without a transformer is the open frontier. Established, named.",flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
