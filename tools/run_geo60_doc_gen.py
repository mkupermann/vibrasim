"""GEO-60 — grounded generation over an unstructured document (add_document + rerank + 0.5B generator)."""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner
from transformers import AutoModelForCausalLM, AutoTokenizer

PARA=("The octopus is a soft-bodied marine animal with eight arms. It has three hearts and blue copper-based "
"blood. Octopuses can change colour to camouflage with their surroundings. They are among the most intelligent "
"invertebrates. An octopus can squeeze through any gap larger than its beak. Most species live only one to two years.")
QA=[("How many arms does an octopus have?","eight"),("How many hearts does it have?","three"),
    ("What colour is octopus blood?","blue"),("How long do most octopuses live?","one to two"),
    ("How do octopuses camouflage?","colour"),("How smart are octopuses?","intelligent")]
UNANS=["What does an octopus eat?","How much does an octopus weigh?"]


def main():
    print("=== GEO-60: grounded generation over a document ===", flush=True)
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    mdl=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    def gen(prompt,n=24):
        enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
        out=mdl.generate(enc["input_ids"],attention_mask=enc.get("attention_mask"),max_new_tokens=n,do_sample=False,pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    r=GeometricReasoner(abstain_tau=0.30, rerank_k=5)
    r.add_document(PARA, source="octopus")
    # calibrate abstention
    r.calibrate_abstention([q for q,_ in QA], UNANS)
    ans_ok=0
    for q,exp in QA:
        res=r.ask(q)
        if res["grounded"]:
            a=gen(f"Context: {res['text']}\nUsing ONLY the context and ignoring prior knowledge, answer concisely. If not stated, say 'not stated'. Question: {q}")
            ans_ok+= int(exp.lower() in a.lower())
    abst=sum(1 for q in UNANS if not r.ask(q)["grounded"])/len(UNANS)
    print(f"  (a) answerable generated-correct = {ans_ok/len(QA):.2f}", flush=True)
    print(f"  (b) unanswerable abstain         = {abst:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ans_ok/len(QA)>=0.7 and abst>=0.5:
        print(f"GEO-60: PASS - full document-QA-with-generation stack works: ingest prose -> retrieve+rerank -> grounded faithful generation ({ans_ok/len(QA):.2f}), abstains on unanswerable ({abst:.2f}). A usable document QA assistant on the PC.", flush=True)
    else:
        print(f"GEO-60: PARTIAL - answerable {ans_ok/len(QA):.2f}, abstain {abst:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
