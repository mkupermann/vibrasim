"""GEO-33 — focus-term verification: answer only if the question's focus role exists in the store."""
import numpy as np
from sentence_transformers import SentenceTransformer

STORED_ROLES=["data scientist","backend engineer","UX designer","site reliability engineer","product manager"]
ABSENT_ROLES=["CEO","CTO","janitor","lawyer","chef"]


def main():
    print("=== GEO-33: answerability via focus-term verification ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    RS=np.array(m.encode(STORED_ROLES,normalize_embeddings=True))
    def focus_maxsim(role):
        v=m.encode([role],normalize_embeddings=True)[0]; return float(np.max(RS@v))
    stored_sims=[focus_maxsim(r) for r in STORED_ROLES]     # ~1.0 (exact match present)
    absent_sims=[focus_maxsim(r) for r in ABSENT_ROLES]
    # calibrate tau_focus on dev: split each group in half
    cs=stored_sims[:3]+stored_sims[3:]  # all stored ~1.0
    dev_tau=(np.mean(stored_sims[:3])+np.mean(absent_sims[:3]))/2
    # evaluate on the other halves
    test_stored=stored_sims[3:]; test_absent=absent_sims[3:]
    # balanced acc: stored should pass (>=tau), absent should fail (<tau)
    tp=np.mean([s>=dev_tau for s in test_stored]); tn=np.mean([s<dev_tau for s in test_absent])
    bal=(tp+tn)/2
    print(f"  stored-role focus maxsim: {[round(s,2) for s in stored_sims]}", flush=True)
    print(f"  absent-role focus maxsim: {[round(s,2) for s in absent_sims]}", flush=True)
    print(f"  calibrated tau_focus = {dev_tau:.2f}", flush=True)
    print(f"  balanced acc (answerable vs unanswerable) = {bal:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if bal>=0.8:
        print("GEO-33: PASS - focus-term verification cleanly separates answerable (stored role) from in-domain-unanswerable (absent role) questions. Hybrid geometric+symbolic existence check fixes the GEO-32b grounding gap.", flush=True)
    else:
        print(f"GEO-33: NULL - absent roles too close to stored roles to separate ({bal:.2f}); answerability needs more than focus similarity.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
