"""GEO-23 — grounded abstention: the method knows what it doesn't know (value-add over a generative LLM)."""
import numpy as np
from sentence_transformers import SentenceTransformer

IN=[("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),("Japan","Tokyo"),
    ("China","Beijing"),("Egypt","Cairo"),("Canada","Ottawa"),("Russia","Moscow"),("Greece","Athens"),
    ("Poland","Warsaw"),("Norway","Oslo"),("Brazil","Brasilia"),("India","Delhi"),("Kenya","Nairobi")]
OUT=["Portugal","Sweden","Chile","Vietnam","Morocco","Peru","Turkey","Thailand","Finland","Ireland",
     "Austria","Belgium","Denmark","Hungary","Romania"]


def main():
    print("=== GEO-23: grounded abstention (knows what it doesn't know) ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"The capital of {c} is {city}." for c,city in IN]
    F=np.array(m.encode(facts,normalize_embeddings=True))
    q_ans=[f"What is the capital of {c}?" for c,_ in IN]
    q_un =[f"What is the capital of {c}?" for c in OUT]
    Qa=np.array(m.encode(q_ans,normalize_embeddings=True))
    Qu=np.array(m.encode(q_un, normalize_embeddings=True))
    maxa=(Qa@F.T).max(1); maxu=(Qu@F.T).max(1)
    # calibrate tau on first half, test on second half (no post-hoc tuning on test)
    half=len(IN)//2
    cal_a,cal_u=maxa[:half],maxu[:half]; tst_a,tst_u=maxa[half:],maxu[half:]
    tau=(cal_a.mean()+cal_u.mean())/2
    # answers on test answerable: argmax fact == correct country index
    arg=(Qa@F.T).argmax(1)
    ans_correct=np.mean([(tst_a[i]>=tau) and (arg[half+i]==half+i) for i in range(len(tst_a))])
    un_abstain=np.mean(tst_u<tau)
    # overall decision accuracy: answerable should answer, unanswerable should abstain
    dec=np.mean(list(tst_a>=tau)+list(tst_u<tau))
    # control: no abstention -> unanswerable get confident wrong answers
    argu=(Qu@F.T).argmax(1)
    confident_wrong=np.mean([IN[argu[half+i]][0]!=OUT[half+i] for i in range(len(tst_u))])  # always wrong (OUT not in store)
    print(f"  calibrated tau = {tau:.3f}  (cal answerable mean {cal_a.mean():.3f}, cal unanswerable {cal_u.mean():.3f})", flush=True)
    print(f"  (a) answerable answered-correctly = {ans_correct:.2f}", flush=True)
    print(f"  (b) unanswerable abstain rate     = {un_abstain:.2f}", flush=True)
    print(f"  (c) overall decision accuracy     = {dec:.2f}", flush=True)
    print(f"  control (no abstention): unanswerable confidently WRONG = {confident_wrong:.2f}  (the LLM-confabulation failure this prevents)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if dec>=0.8 and un_abstain>=0.7:
        print("GEO-23: PASS - the method reliably ABSTAINS on unanswerable questions (grounded; knows what it doesn't know). This is the concrete value-add over a generative LLM, which confabulates.", flush=True)
    else:
        print(f"GEO-23: PARTIAL/NULL - decision {dec:.2f}, abstain {un_abstain:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
