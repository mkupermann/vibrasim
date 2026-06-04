"""GEO-96 — grounded generation with conflicting context."""
import sys, os, warnings
warnings.filterwarnings("ignore")
from transformers import AutoModelForCausalLM, AutoTokenizer

CASES=[("Alice","team",["Analytics","Platform"]),("Bob","city",["Boston","Denver"]),
       ("Carol","role",["designer","engineer"]),("David","project",["Falcon","Orion"]),
       ("Eve","team",["Design","Product"]),("Frank","city",["Austin","Seattle"])]


def main():
    print("=== GEO-96: conflicting context ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=30):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip().lower()
    picks=0; flags=0
    for name,attr,vals in CASES:
        ctx=f"{name}'s {attr} is {vals[0]}. {name}'s {attr} is {vals[1]}."
        q=f"What is {name}'s {attr}?"
        a=gen(f"Context: {ctx}\nUsing ONLY the context, answer: {q}")
        picks+= int(vals[0].lower() in a or vals[1].lower() in a)   # picked a stored value (not a 3rd)
        ca=gen(f"Context: {ctx}\nUsing ONLY the context. If the context gives conflicting answers, say 'conflicting'. {q}")
        flags+= int("conflict" in ca or ("and" in ca and vals[0].lower() in ca and vals[1].lower() in ca))
    n=len(CASES)
    print(f"  plain: picked a STORED value (no hallucinated 3rd) = {picks/n:.2f}", flush=True)
    print(f"  conflict-aware: FLAGGED the inconsistency          = {flags/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if picks/n>=0.8 and flags/n>=0.5:
        print(f"GEO-96: PASS - under CONFLICTING context the generator picks a stored value (no hallucinated third, {picks/n:.2f}) and a conflict-aware prompt flags the inconsistency ({flags/n:.2f}). Grounding contains the damage even with inconsistent retrieval; a conflict-aware prompt surfaces it. Robust-ish to imperfect retrieval at generation time.", flush=True)
    else:
        print(f"GEO-96: PARTIAL - picks-stored {picks/n:.2f}, flags {flags/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
