"""GEO-48 — query intent routing: classify the needed operation from the query embedding."""
import numpy as np
from sentence_transformers import SentenceTransformer

CLASSES={
"FACTOID":["Which team is Alice on?","What city does Bob work in?","Where is the Design team based?",
           "What company does Carol work at?","Who does David report to?","What role does Eve have?",
           "Which department is Frank in?","What project is Grace on?","Where does Heidi live?","What team is Ivan on?"],
"COUNT":["How many people work in Boston?","How many are on the Platform team?","Count the employees in Austin.",
         "How many engineers are there?","What is the number of people in Design?","How many work remotely?",
         "How many people report to Frank?","Count the managers.","How many are based in Denver?","What's the headcount in Product?"],
"TEMPORAL":["Which team was Alice on in 2023?","What was Bob's role in 2020?","Where did Carol work in 2019?",
            "What team did David join in 2021?","Who led Platform in 2022?","What was the headcount in 2020?",
            "Which city was Eve in during 2021?","What project ran in 2018?","Who was hired in 2024?","What changed in 2023?"],
"COMPARE":["Who is more senior, Alice or Bob?","Which team is bigger, Design or Platform?","Is Carol older than David?",
           "Who earns more, Eve or Frank?","Which city is larger, Boston or Denver?","Is Grace taller than Heidi?",
           "Who joined first, Ivan or Judy?","Which is faster, A or B?","Who has more experience, X or Y?","Is Mike senior to Nina?"],
"JOIN":["Who is on the same team as Alice?","Which people share Bob's city?","Who works with Carol?",
        "Find everyone in David's department.","Who else is on Platform?","Which colleagues share Eve's role?",
        "Who lives in the same city as Frank?","List people on Grace's team.","Who shares Heidi's manager?","Find Ivan's teammates."],
"EXISTS":["Is there anyone in Miami?","Does anybody work on Platform?","Are there any managers in Austin?",
          "Is there a data scientist on the team?","Does anyone report to Frank?","Are there employees in Denver?",
          "Is there anyone older than 50?","Does any team work remotely?","Are there people who joined in 2024?","Is anyone on two teams?"]}


def main():
    print("=== GEO-48: query intent routing ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    rng=np.random.default_rng(0)
    Xtr=[];ytr=[];Xte=[];yte=[]
    for cls,qs in CLASSES.items():
        emb=np.array(m.encode(qs,normalize_embeddings=True))
        idx=rng.permutation(len(qs)); ntr=int(len(qs)*0.7)
        for k,i in enumerate(idx):
            (Xtr if k<ntr else Xte).append(emb[i]); (ytr if k<ntr else yte).append(cls)
    Xtr=np.array(Xtr);Xte=np.array(Xte)
    classes=list(CLASSES.keys())
    cent={c:Xtr[[i for i,y in enumerate(ytr) if y==c]].mean(0) for c in classes}
    C=np.array([cent[c] for c in classes])
    pred=[classes[int(np.argmax(C@x))] for x in Xte]
    acc=np.mean([p==t for p,t in zip(pred,yte)])
    # confusion of misses
    miss=[(t,p) for t,p in zip(yte,pred) if t!=p]
    print(f"  held-out intent accuracy = {acc:.2f}  (chance {1/len(classes):.2f}, n={len(yte)})", flush=True)
    if miss: print(f"  misclassified: {miss}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.75:
        print(f"GEO-48: PASS - query embeddings reveal the needed OPERATION ({acc:.2f}); a few-shot centroid classifier auto-routes queries to the right operator (factoid/count/temporal/compare/join/exists). The system can self-dispatch.", flush=True)
    else:
        print(f"GEO-48: PARTIAL/NULL - intent routing {acc:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
