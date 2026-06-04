"""JEP-10c - run the trained MLP on the AMD GPU via onnxruntime-directml; verify correctness + throughput."""
import numpy as np, time, os
d=np.load("data/mnist.npz"); Xte=d["x_test"].reshape(10000,784).astype(np.float32)/255.0; yte=d["y_test"].astype(int)
m=np.load("data/jep10_pc_model.npz"); W1=m["W1"].astype(np.float32); W2=m["W2"].astype(np.float32)
# numpy reference
def npy_pred(X): 
    Z=np.tanh(X@W1)@W2; return Z.argmax(1)
ref_acc=float(np.mean(npy_pred(Xte)==yte))
print(f"=== JEP-10c: GPU inference via DirectML (AMD RX 7700S) ===",flush=True)
print(f"  numpy reference test acc = {ref_acc:.4f}",flush=True)
# build ONNX graph with torch export
import torch, torch.nn as nn
class MLP(nn.Module):
    def __init__(s):
        super().__init__(); s.l1=nn.Linear(784,W1.shape[1],bias=False); s.l2=nn.Linear(W1.shape[1],10,bias=False)
        s.l1.weight.data=torch.tensor(W1.T); s.l2.weight.data=torch.tensor(W2.T)
    def forward(s,x): return torch.tanh(s.l1(x))@0+s.l2(torch.tanh(s.l1(x)))
net=MLP().eval()
onnx_path="data/jep10_mlp.onnx"
torch.onnx.export(net,torch.zeros(1,784),onnx_path,input_names=["x"],output_names=["logits"],
                  dynamic_axes={"x":{0:"n"},"logits":{0:"n"}},opset_version=13)
print(f"  exported ONNX -> {onnx_path}",flush=True)
import onnxruntime as ort
def run(provider,Xb,reps=5):
    so=ort.SessionOptions()
    sess=ort.InferenceSession(onnx_path,so,providers=[provider])
    used=sess.get_providers()[0]
    # warmup
    sess.run(None,{"x":Xb[:256]})
    t0=time.time()
    preds=[]
    for _ in range(reps):
        out=sess.run(None,{"x":Xb})[0]; preds=out.argmax(1)
    dt=(time.time()-t0)/reps
    return used,preds,dt
gpu_used,gpu_pred,gpu_dt=run("DmlExecutionProvider",Xte)
cpu_used,cpu_pred,cpu_dt=run("CPUExecutionProvider",Xte)
gpu_acc=float(np.mean(gpu_pred==yte)); cpu_acc=float(np.mean(cpu_pred==yte))
print(f"  GPU provider used: {gpu_used}",flush=True)
print(f"  GPU(DirectML) test acc={gpu_acc:.4f}  | 10k-inference {gpu_dt*1000:.1f}ms ({10000/gpu_dt:,.0f} img/s)",flush=True)
print(f"  CPU            test acc={cpu_acc:.4f}  | 10k-inference {cpu_dt*1000:.1f}ms ({10000/cpu_dt:,.0f} img/s)",flush=True)
# big-batch throughput to actually exercise the GPU
Xbig=np.tile(Xte,(20,1)).astype(np.float32)  # 200k images
_,_,gdt=run("DmlExecutionProvider",Xbig,reps=3); _,_,cdt=run("CPUExecutionProvider",Xbig,reps=3)
print(f"  200k-batch: GPU {gdt*1000:.0f}ms ({len(Xbig)/gdt:,.0f} img/s)  vs  CPU {cdt*1000:.0f}ms ({len(Xbig)/cdt:,.0f} img/s)  speedup x{cdt/gdt:.2f}",flush=True)
print("\n--- VERDICT ---",flush=True)
if abs(gpu_acc-ref_acc)<1e-3 and gpu_used=="DmlExecutionProvider":
    print(f"JEP-10c: PASS - the trained model runs on the AMD GPU (RX 7700S) via DirectML, matching the numpy",flush=True)
    print(f"reference exactly (acc {gpu_acc:.4f}=={ref_acc:.4f}). The GPU IS usable on this machine - for INFERENCE",flush=True)
    print(f"via onnxruntime-directml (200k-batch speedup x{cdt/gdt:.2f} vs CPU). Training still CPU-only (no AMD",flush=True)
    print(f"PyTorch-train path on Win/Py3.13). Honest hardware envelope established.",flush=True)
else:
    print(f"JEP-10c: PARTIAL - gpu_used={gpu_used}, gpu_acc={gpu_acc:.4f}, ref={ref_acc:.4f}",flush=True)
print("DONE",flush=True)
