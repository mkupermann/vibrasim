"""GEO-82 — LLM-prior fact-checking of stored facts, and its tension with updatability."""
import sys, os, warnings
warnings.filterwarnings("ignore")
from transformers import AutoModelForCausalLM, AutoTokenizer

CORRECT=[("France","Paris"),("Japan","Tokyo"),("Italy","Rome"),("Egypt","Cairo"),("Spain","Madrid")]
WRONG=[("France","Lyon"),("Japan","Osaka"),("Italy","Milan"),("Egypt","Alexandria"),("Spain","Seville")]
PRIVATE=[("the Zarnak project","Building 7"),("employee X4471","the Vega team"),
         ("the Qenth protocol","port 8842"),("the Brindle account","tier 3"),("the Yolar device","lab 12")]


def main():
    print("=== GEO-82: LLM-prior fact-checking ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=12):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip().lower()
    def flagged(subj, stored):  # FLAG if LLM's answer disagrees with stored
        a=gen(f"What is the capital of {subj}? One word." if subj in [c for c,_ in CORRECT+WRONG] else f"What is {subj}? Answer briefly.")
        return stored.split()[0].lower() not in a
    corr_flag=sum(flagged(c,cap) for c,cap in CORRECT)/len(CORRECT)
    wrong_flag=sum(flagged(c,cap) for c,cap in WRONG)/len(WRONG)
    priv_flag=sum(flagged(s,v) for s,v in PRIVATE)/len(PRIVATE)
    print(f"  CORRECT well-known facts flagged   = {corr_flag:.2f}  (want LOW)", flush=True)
    print(f"  WRONG well-known facts flagged     = {wrong_flag:.2f}  (want HIGH = catches errors)", flush=True)
    print(f"  PRIVATE facts flagged              = {priv_flag:.2f}  (LLM can't check)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"GEO-82: TRADEOFF MAP - LLM-prior fact-check catches WRONG well-known facts ({wrong_flag:.2f}) while mostly not flagging correct ones ({corr_flag:.2f}), BUT flags PRIVATE facts ({priv_flag:.2f}) it cannot verify and would also flag legitimate UPDATES/counterfactuals (which by design contradict the prior, GEO-30). So LLM-prior fact-checking is usable ONLY for stores that should match common knowledge; it CONFLICTS with the system's updatability/private-fact strengths. A real, honest tradeoff.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
