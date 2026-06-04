"""GEO-79 — does grounding improve a 0.5B LLM on general-knowledge questions?"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))
from transformers import AutoModelForCausalLM, AutoTokenizer

# less-common real facts (capitals of smaller/less-famous countries) where a 0.5B model may err
QA=[("Kazakhstan","Astana"),("Myanmar","Naypyidaw"),("Nigeria","Abuja"),("Bolivia","Sucre"),
    ("Tanzania","Dodoma"),("Sri Lanka","Sri Jayawardenepura Kotte"),("Ivory Coast","Yamoussoukro"),
    ("Bhutan","Thimphu"),("Palau","Ngerulmud"),("Kiribati","Tarawa"),("Brunei","Bandar Seri Begawan"),
    ("Eswatini","Mbabane")]


def main():
    print("=== GEO-79: grounding on general knowledge ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=16):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    bare=0; grnd=0
    for country,cap in QA:
        b=gen(f"What is the capital of {country}? Answer with just the city name.")
        bare+= int(cap.split()[0].lower() in b.lower())
        g=gen(f"Context: The capital of {country} is {cap}.\nUsing ONLY the context, what is the capital of {country}?")
        grnd+= int(cap.split()[0].lower() in g.lower())
    n=len(QA)
    print(f"  BARE 0.5B (parametric)  = {bare/n:.2f}", flush=True)
    print(f"  GROUNDED (retrieved fact) = {grnd/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if grnd/n>=0.8 and grnd/n-bare/n>=0.2:
        print(f"GEO-79: PASS - grounding reduces small-LLM errors on GENERAL knowledge ({bare/n:.2f}->{grnd/n:.2f}): the 0.5B model is unreliable on less-common facts from memory, but grounding it with the retrieved correct fact fixes it. The standard RAG value holds — grounding helps even when the model 'should' know.", flush=True)
    else:
        print(f"GEO-79: bare {bare/n:.2f}, grounded {grnd/n:.2f} - grounding {'helps' if grnd/n>bare/n else 'does not help'}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
