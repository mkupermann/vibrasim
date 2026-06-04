"""GEO-80 — does grounding propagate WRONG retrieved facts? (honest downside of RAG)."""
import sys, os, warnings
warnings.filterwarnings("ignore")
from transformers import AutoModelForCausalLM, AutoTokenizer

QA=[("France","Paris","Lyon"),("Japan","Tokyo","Osaka"),("Italy","Rome","Milan"),("Spain","Madrid","Seville"),
    ("Germany","Berlin","Hamburg"),("Egypt","Cairo","Alexandria"),("Greece","Athens","Sparta"),
    ("Russia","Moscow","Petersburg"),("China","Beijing","Shanghai"),("Canada","Ottawa","Toronto")]


def main():
    print("=== GEO-80: does grounding propagate WRONG facts? ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=12):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    bare=0; gc=0; gw=0; gw_wrong=0
    for c,true,wrong in QA:
        b=gen(f"What is the capital of {c}? One word."); bare+= int(true.lower() in b.lower())
        g=gen(f"Context: The capital of {c} is {true}.\nUsing ONLY the context, what is the capital of {c}? One word."); gc+= int(true.lower() in g.lower())
        w=gen(f"Context: The capital of {c} is {wrong}.\nUsing ONLY the context, what is the capital of {c}? One word.")
        gw+= int(true.lower() in w.lower())            # still correct despite wrong context
        gw_wrong+= int(wrong.lower() in w.lower())     # followed the WRONG context
    n=len(QA)
    print(f"  (a) BARE (memory)        true-acc = {bare/n:.2f}", flush=True)
    print(f"  (b) GROUNDED-CORRECT     true-acc = {gc/n:.2f}", flush=True)
    print(f"  (c) GROUNDED-WRONG       true-acc = {gw/n:.2f}  (followed wrong fact: {gw_wrong/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if gw/n <= bare/n - 0.3:
        print(f"GEO-80: CONFIRMED (honest GIGO) - grounding PROPAGATES retrieval errors: with a WRONG retrieved fact the model's true-accuracy collapses to {gw/n:.2f} (vs bare {bare/n:.2f}), following the wrong context {gw_wrong/n:.2f} of the time. Grounding is only as good as retrieval — a wrong retrieval yields a CONFIDENT wrong answer. Critical deployment caveat: invest in retrieval quality; abstention (GEO-23) limits but does not eliminate this.", flush=True)
    else:
        print(f"GEO-80: bare {bare/n:.2f}, grounded-correct {gc/n:.2f}, grounded-wrong {gw/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
