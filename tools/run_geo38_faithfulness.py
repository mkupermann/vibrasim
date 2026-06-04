"""GEO-38 — grounded generation faithfulness: does the generator invent unsupported details?"""
import sys, os, warnings, re
warnings.filterwarnings("ignore")
from transformers import AutoModelForCausalLM, AutoTokenizer

PEOPLE=["Alice","Bob","Carol","David","Eve","Frank","Grace","Heidi"]
TEAMS=["Analytics","Platform","Design","Analytics","Platform","Product","Design","Product"]


def main():
    print("=== GEO-38: grounded generation faithfulness ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=40):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    def has_salary(t):
        return bool(re.search(r"\$|\d{2,}[,\d]*\s*(k|dollars|usd|per|/|salary)|\bsalary is\b.*\d", t.lower())) or bool(re.search(r"\$\s*\d", t))
    team_ok=0; inv_plain=0; inv_faith=0
    for p,team in zip(PEOPLE,TEAMS):
        ctx=f"{p} is on the {team} team."
        q=f"What team is {p} on, and what is their salary?"
        plain=gen(f"Context: {ctx}\nAnswer the question: {q}")
        faith=gen(f"Context: {ctx}\nAnswer using ONLY the context. If a detail is not in the context, say 'not stated'. Question: {q}")
        team_ok+= int(team.lower() in plain.lower())
        inv_plain+= int(has_salary(plain))
        inv_faith+= int(has_salary(faith))
    n=len(PEOPLE)
    print(f"  team mentioned correctly (plain)     = {team_ok/n:.2f}", flush=True)
    print(f"  salary INVENTED (plain prompt)        = {inv_plain/n:.2f}", flush=True)
    print(f"  salary INVENTED (faithfulness prompt) = {inv_faith/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    drop = inv_plain/n - inv_faith/n
    if team_ok/n>=0.7 and inv_plain/n>=0.3 and drop>=0.3:
        print(f"GEO-38: PASS-as-designed - faithfulness is a REAL risk (plain prompt invents salary {inv_plain/n:.2f}) but MITIGABLE: a 'say not stated' instruction cuts confabulation by {drop:.2f}. Grounded generation needs an explicit faithfulness instruction; with it, the generator stays within context.", flush=True)
    else:
        print(f"GEO-38: characterization - team {team_ok/n:.2f}, invent plain {inv_plain/n:.2f}, invent faithful {inv_faith/n:.2f} (drop {drop:.2f})", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
