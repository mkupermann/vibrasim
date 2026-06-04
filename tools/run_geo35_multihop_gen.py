"""GEO-35 — multi-hop grounded generation: geometric chain (P->team->city) feeds the LLM generator."""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner
from transformers import AutoModelForCausalLM, AutoTokenizer

EMP=[("Alice","Analytics","Zogby"),("Bob","Platform","Quenville"),("Carol","Design","Marnos"),
     ("David","Analytics","Zogby"),("Eve","Platform","Quenville"),("Frank","Product","Tarsin"),
     ("Grace","Design","Marnos"),("Heidi","Product","Tarsin")]  # invented cities the LLM cannot know


def main():
    print("=== GEO-35: multi-hop grounded generation ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=20):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    r=GeometricReasoner(abstain_tau=0.35)
    for p,team,city in EMP:
        r.add_fact(f"{p} is on the {team} team.", subject=p, object=team)
        r.add_fact(f"The {team} team is based in {city}.", subject=team, object=city)
    bare=0; grnd=0; examples=[]
    for i,(p,team,city) in enumerate(EMP):
        q=f"Which city does {p} work in?"
        b=gen(f"{q} Answer with just the city name.")
        bare+= int(city.lower() in b.lower())
        # geometric chain P->team->city
        hits=r.chain([f"What team is {p} on?","Where is the {bridge} team based?"])
        facts=""
        if hits:
            # reconstruct the two supporting fact texts
            tq=r.retrieve(f"What team is {p} on?")[0]; 
            facts=f"{r.fact_texts[tq]} " if tq is not None else ""
            cq=r.retrieve(f"Where is the {hits[0].get('object')} team based?")[0]
            facts+= r.fact_texts[cq] if cq is not None else ""
        g=gen(f"Context: {facts}\nUsing ONLY the context and IGNORING prior knowledge, answer concisely: {q}")
        grnd+= int(city.lower() in g.lower())
        if i<2: examples.append((p,city,b,g))
    n=len(EMP)
    for p,city,b,g in examples:
        print(f"  [{p}->{city}] bare={b!r}  grounded={g!r}", flush=True)
    print(f"  bare-LLM city accuracy    = {bare/n:.2f}", flush=True)
    print(f"  grounded multi-hop accuracy = {grnd/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if grnd/n>=0.8 and bare/n<=0.2:
        print("GEO-35: PASS - multi-hop grounded generation: the geometric layer chains private facts and the generator answers correctly, where the bare LLM (lacking the private knowledge) cannot. Full reasoning+generation stack works on the PC.", flush=True)
    else:
        print(f"GEO-35: PARTIAL/NULL - grounded {grnd/n:.2f}, bare {bare/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
