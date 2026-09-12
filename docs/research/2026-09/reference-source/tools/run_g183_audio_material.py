"""G183 real-audio material habituation. No World is constructed on import."""
from pathlib import Path
import argparse
import copy
import dataclasses
import hashlib
import json
import os
import subprocess
import sys
import time
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
CLASSES = ('church_bells', 'dog', 'rain')
BANDS = np.array([0,62.5,125,250,500,1000,2000,4000,8000])
DT = 1/60
PROTOCOL = 'docs/amendments/g183_real_audio_material_prediction.md'
MANIFEST = 'archive/datasets/esc50-mm6/manifest.json'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, obj):
    tmp = Path(str(path)+'.tmp')
    with tmp.open('w') as f:
        json.dump(obj,f,allow_nan=False); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)


def transduce(audio):
    """Fixed nonoverlapping 100ms mean-removed symmetric-Hann frames, no fitted parameters."""
    audio=np.asarray(audio,dtype=float)
    if audio.shape != (80000,) or not np.isfinite(audio).all(): raise ValueError('Expected five seconds at 16 kHz')
    frames=audio.reshape(50,1600)
    frames=frames-frames.mean(axis=1,keepdims=True)
    window=np.hanning(1600)
    power=np.abs(np.fft.rfft(frames*window,axis=1))**2
    freq=np.fft.rfftfreq(1600,1/16000)
    energy=np.stack([power[:,(freq>=lo)&((freq<hi) if hi<8000 else (freq<=hi))].sum(1) for lo,hi in zip(BANDS[:-1],BANDS[1:])],axis=1)
    total=energy.sum(1)
    proportions=np.divide(energy,total[:,None],out=np.zeros_like(energy),where=total[:,None]>1e-12)
    return proportions, total


def select_rows(rows):
    selected=[r for r in rows if int(r['fold']) in (1,2) and r['category'] in CLASSES]
    for fold in (1,2):
        for category in CLASSES:
            if sum(int(r['fold'])==fold and r['category']==category for r in selected)!=8: raise ValueError('Expected eight clips per split/class')
    for key in ('filename','sha256'):
        if len({r[key] for r in selected})!=48: raise ValueError('Duplicate '+key)
    if {r['src_file'] for r in selected if int(r['fold'])==1}&{r['src_file'] for r in selected if int(r['fold'])==2}: raise ValueError('Source overlap')
    return sorted(selected,key=lambda r:r['filename'])


def required_sources():
    return sorted({str(p.relative_to(ROOT)) for p in (ROOT/'world').rglob('*.py')} | {PROTOCOL,MANIFEST,'tools/run_g183_audio_material.py','tools/run_g176_material_memory.py','tools/__init__.py','pyproject.toml','uv.lock'})


def verify_seal(path):
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],timeout=30)
    raw=Path(path).read_bytes(); seal=json.loads(raw); head=git('rev-parse','HEAD').decode().strip()
    if seal['status']!='approved-audio-material' or git('show',head+':'+str(Path(path).resolve().relative_to(ROOT)))!=raw: raise ValueError('Uncommitted/unapproved seal')
    p,i=seal['protocol_commit'],seal['implementation_commit']
    if p==i:raise ValueError('Separate protocol and implementation commits required')
    git('merge-base','--is-ancestor',p,i);git('merge-base','--is-ancestor',i,head)
    if set(seal['sources'])!=set(required_sources()):raise ValueError('Incomplete seal')
    for name,digest in seal['sources'].items():
        if sha(ROOT/name)!=digest or git('show',i+':'+name)!=(ROOT/name).read_bytes():raise ValueError('Changed source '+name)
    if git('show',p+':'+PROTOCOL)!=(ROOT/PROTOCOL).read_bytes():raise ValueError('Changed protocol')
    return dict(head=head,seal=seal,seal_sha256=hashlib.sha256(raw).hexdigest(),python=sys.version,numpy=np.__version__)


def setup(reverse,frozen):
    from world.state import World
    from world.config import WorldConfig
    cfg=WorldConfig(rng_seed=42,box_size=(160.,160.,160.),repulsion_cell_size=160.,n_initial_vibrations=0,n_vibrations_max=32,n_nodes_max=32,lambda_gen=0.,lambda_dec=0.,repulsion_k=0.,atom_repulsion_k=0.,node_thermal_speed=0.,resonance_coupling=0.,neuron_dynamics_enabled=False,stdp_enabled=False,btsp_enabled=False,anchor_damping=0.,atom_valence=1,r_2=12.,per_bond_rest_enabled=True,bridge_tension_k=8.,bridge_tension_damping=.95,dt=DT,graceful_capacity=True,material_memory_enabled=True,material_memory_mode='softening',material_memory_softening=.75,material_memory_barrier=8.,material_memory_rate=0. if frozen else 1.,bond_turnover_rate=0.,bridge_cooldown=0.)
    w=World(cfg); ids=np.empty((8,2),dtype=int)
    order=list(np.ndindex(8,2))
    for b,j in reversed(order) if reverse else order:
        ids[b,j]=w.allocate_node(np.array([20+8.5*j,20+16*b,30.]),1.,True,4,np.empty(0,dtype=np.int32),0)
    return w,ids


def clamp(w,ids,deltas):
    from world.bridges import material_energy
    work=0.; removed=float(2*np.sum(w.k_vel[ids]**2))
    for b,(left,right) in enumerate(ids):
        if w.b_count:
            edges=np.flatnonzero(w.b_alive[:w.b_count] & (((w.b_atom_i[:w.b_count]==left)&(w.b_atom_j[:w.b_count]==right))|((w.b_atom_i[:w.b_count]==right)&(w.b_atom_j[:w.b_count]==left))))
            if len(edges)==1:
                s=w.b_material_state[edges[0]]; old=np.linalg.norm(w.k_pos[right]-w.k_pos[left])-8.5
                work+=material_energy(deltas[b],s,8,.75,8)-material_energy(old,s,8,.75,8)
        w.k_pos[left]=[20.,20+16*b,30.];w.k_pos[right]=[28.5+deltas[b],20+16*b,30.]
    w.k_vel[ids]=0
    return work,removed


def mapped_states(w,ids):
    out=[]; used=[]
    for left,right in ids:
        edges=np.flatnonzero(w.b_alive[:w.b_count] & (((w.b_atom_i[:w.b_count]==left)&(w.b_atom_j[:w.b_count]==right))|((w.b_atom_i[:w.b_count]==right)&(w.b_atom_j[:w.b_count]==left))))
        if len(edges)!=1:raise ValueError('Original pair topology lost')
        used.append(int(edges[0]));out.append(float(w.b_material_state[edges[0]]))
    if w.b_count!=8 or len(set(used))!=8 or np.count_nonzero(w.b_alive)!=8 or w.k_count!=16 or np.count_nonzero(w.k_alive)!=16 or not np.all(w.b_rest_len[used]==8.5) or not np.all(w.b_strength[used]==1):raise ValueError('Topology integrity')
    s=np.array(out)
    if not np.isfinite(w.k_pos).all() or not np.isfinite(w.k_vel).all() or not np.isfinite(s).all() or np.any(s<0) or np.any(s>1) or w.n_alive!=0:raise ValueError('Numerical integrity')
    expected_y=np.repeat((20+16*np.arange(8))[:,None],2,axis=1)
    if not np.all(w.k_level[ids]==4) or np.max(np.abs(w.k_pos[ids,1]-expected_y))>1e-10 or np.max(np.abs(w.k_pos[ids,2]-30))>1e-10 or np.any(w.s_alive):raise ValueError('Geometry/force channel integrity')
    if w.config.material_memory_rate==0 and np.any(s!=0):raise ValueError('Frozen state changed')
    return s


def force_ratio(forces,deltas):
    den=float(np.sum(8*np.asarray(deltas)**2))
    if den<=0:raise ValueError('Silent query has no defined response')
    return float(np.sum(np.asarray(forces)*deltas)/den)


def aggregate(results):
    """Precommitted gates, each allocation variant must meet all bars."""
    gates={}
    for variant in ('canonical','reversed'):
        arms=results[variant]
        queries=[q for name,a in arms.items() if 'queries' in a for q in a['queries'].values()]
        means={a:{c:float(np.mean([q['ratio'] for q in arms[a]['queries'].values() if q['category']==c])) for c in CLASSES} for a in CLASSES}
        M=all(.25-1e-6<=q['ratio']<=1+1e-6 and abs(q['ratio']-q['predicted'])<=1e-6 for q in queries)
        C=all(abs(q['ratio']-1)<=.001 for a in ('frozen','sham','erased') for q in arms[a]['queries'].values()) and all(q['drift']<=.01 and abs(q['ratio']-q['retained_prediction'])<=.01 for q in queries)
        contrasts={'bell':(means['dog']['church_bells']+means['rain']['church_bells'])/2-means['church_bells']['church_bells'],
                   'dog':means['church_bells']['dog']-means['dog']['dog'],
                   'rain':means['church_bells']['rain']-means['rain']['rain']}
        H=means['church_bells']['church_bells']<=.80 and all(v>=.10 for v in contrasts.values())
        gates[variant]=dict(M=M,C=C,H=H,means=means,contrasts=contrasts)
    gates['all_predictions']=all(gates[v][p] for v in ('canonical','reversed') for p in ('M','C','H'))
    m=all(gates[v]['M'] for v in ('canonical','reversed'))
    c=all(gates[v]['C'] for v in ('canonical','reversed'))
    h=all(gates[v]['H'] for v in ('canonical','reversed'))
    gates['decision']=dict(physical_integrity='VALID',
        assay_validity='VALID' if m and c else 'UNRESOLVED' if not m else 'INVALID',
        measurement_prediction='CONFIRMED' if m else 'REFUTED',
        control_prediction='CONFIRMED' if c else 'REFUTED',
        selectivity_prediction=('CONFIRMED' if h else 'REFUTED') if m and c else 'UNDECIDABLE',
        reason='MEASUREMENT_PREDICTION_FAILED' if not m else 'RETAINED_ASSAY_FAILED' if not c else 'SELECTIVITY_SUPPORTED' if h else 'SELECTIVITY_REFUTED',
        verdict='INCONCLUSIVE' if not (m and c) else 'PASS' if h else 'NULL')
    return gates


def run(data,output,seal):
    provenance=verify_seal(seal)
    import importlib.metadata
    provenance['environment']={name:importlib.metadata.version(name) for name in ('numpy','numba','scipy','soundfile')}
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    from math import gcd
    import soundfile as sf
    from scipy.signal import resample_poly
    from world.physics import tick
    from world.snapshot import save_snapshot,load_snapshot
    from tools.run_g176_material_memory import equal_state
    rows=select_rows(json.loads((ROOT/MANIFEST).read_text())); features={}; totals={}; pcm={}
    started=time.monotonic(); observed=0; active={}; results={}; traces={}
    def step(w,ids,delta,work):
        nonlocal observed
        if time.monotonic()-started>1200:raise TimeoutError('G183 twenty minute hard cap')
        work+=clamp(w,ids,delta); pre=mapped_states(w,ids).copy()
        tick(w,DT);observed+=1
        post=mapped_states(w,ids);force=4*np.abs(w.k_vel[ids[:,0],0])/(DT*.95)
        work+=clamp(w,ids,delta)
        return np.r_[delta,force,pre,post,work],post
    def progress(phase,**extra):
        if time.monotonic()-started>1200:raise TimeoutError('G183 twenty minute hard cap')
        atomic(output/'progress.json',dict(experiment='G183',state='active_physics',phase=phase,updated_unix=time.time(),runner_pid=os.getpid(),observed_ticks=observed,material_states=active,**extra))
    try:
        for row in rows:
            path=Path(data)/row['filename']
            if sha(path)!=row['sha256']:raise ValueError('Audio hash mismatch')
            audio,sr=sf.read(path,dtype='float64')
            if audio.ndim!=1 or len(audio)!=5*sr or not np.isfinite(audio).all():raise ValueError('Audio shape')
            g=gcd(sr,16000);audio=resample_poly(audio,16000//g,sr//g)
            pcm[row['filename']]=hashlib.sha256(audio.tobytes()).hexdigest()
            features[row['filename']],totals[row['filename']]=transduce(audio)
        if len(set(pcm.values()))!=48:raise ValueError('Duplicate decoded audio')
        np.savez_compressed(output/'ports.npz',**{k:v for k,v in features.items()},**{'energy_'+k:v for k,v in totals.items()})
        summaries={name:dict(silent_frames=int(np.sum(total<=1e-12)),strain_squared_dose=(.36*features[name].sum(0)*.1).tolist(),above_threshold_seconds=(np.sum(.6*np.sqrt(features[name])>.3582,axis=0)*.1).tolist()) for name,total in totals.items()}
        atomic(output/'inputs.json',dict(rows=rows,pcm_sha256=pcm,provenance=provenance,port_summaries=summaries))
        for reverse in (False,True):
            variant='reversed' if reverse else 'canonical'; results[variant]={}; retained={}
            for history in (*CLASSES,'frozen','sham'):
                w,ids=setup(reverse,history=='frozen'); trace=[]; work=np.zeros(2)
                traces[variant+'-'+history]=trace
                for _ in range(8):
                    work+=clamp(w,ids,np.zeros(8));tick(w,DT);observed+=1
                mapped_states(w,ids)
                save_snapshot(w,output/(variant+'-'+history+'-before.npz'))
                train=[r for r in rows if int(r['fold'])==1 and r['category']==(history if history in CLASSES else 'church_bells')]
                for row in train:
                    for frame,p in enumerate(features[row['filename']]):
                        delta=np.zeros(8) if history=='sham' else .6*np.sqrt(p)
                        for _ in range(6):
                            record,s=step(w,ids,delta,work);trace.append(record)
                        active={history:s.tolist()};progress('exposure',variant=variant,history=history,clip=row['filename'],frame=frame,physical_time=w.t)
                before=mapped_states(w,ids).copy()
                save_snapshot(w,output/(variant+'-'+history+'-exposed.npz'))
                retention=[];traces[variant+'-'+history+'-retention']=retention
                for n in range(1200):
                    record,s=step(w,ids,np.zeros(8),work);retention.append(record)
                    active={history:s.tolist()}
                    if n%60==0:progress('retention',variant=variant,history=history,physical_time=w.t)
                s=mapped_states(w,ids);retained[history]=(w,ids)
                path=output/(variant+'-'+history+'.npz');save_snapshot(w,path);restored=load_snapshot(path)
                if not equal_state({k:v for k,v in vars(w).items() if k!='rng'},{k:v for k,v in vars(restored).items() if k!='rng'}) or not equal_state(w.rng.bit_generator.state,restored.rng.bit_generator.state):raise ValueError('Snapshot mismatch')
                traces[variant+'-'+history]=np.asarray(trace)
                traces[variant+'-'+history+'-retention']=np.asarray(retention)
                results[variant][history]=dict(retained_s=s.tolist(),pre_retention_s=before.tolist(),work=work.tolist(),config=dataclasses.asdict(w.config),snapshot_sha256=sha(path),before_snapshot_sha256=sha(output/(variant+'-'+history+'-before.npz')),exposed_snapshot_sha256=sha(output/(variant+'-'+history+'-exposed.npz')),uniform_response=1-.75*float(s.mean()),queries={})
            erased_before=sha(output/(variant+'-church_bells.npz'))
            retained['erased']=(copy.deepcopy(retained['church_bells'][0]),retained['church_bells'][1]);retained['erased'][0].b_material_state[:8]=0
            save_snapshot(retained['erased'][0],output/(variant+'-erased.npz'))
            results[variant]['erasure_provenance']=dict(before_sha256=erased_before,after_sha256=sha(output/(variant+'-erased.npz')),intervention='only b_material_state zeroed on copied bell-trained retained World')
            retained['restored']=(load_snapshot(output/(variant+'-church_bells.npz')),retained['church_bells'][1])
            for history,(saved,ids) in retained.items():
                result=results[variant].setdefault(history,dict(retained_s=mapped_states(saved,ids).tolist(),queries={}))
                initial=mapped_states(saved,ids)
                for row in [r for r in rows if int(r['fold'])==2]:
                    w=copy.deepcopy(saved); forces=[];deltas=[];states=[];query_trace=[];query_work=np.zeros(2)
                    traces[variant+'-'+history+'-'+row['filename']]=query_trace
                    for frame,p in enumerate(features[row['filename']]):
                        delta=.02*np.sqrt(p)
                        for _ in range(6):
                            record,post=step(w,ids,delta,query_work);query_trace.append(record)
                            states.append(post);forces.append(record[8:16]);deltas.append(delta.copy())
                    f,d,s=np.asarray(forces),np.asarray(deltas),np.asarray(states)
                    ratio=force_ratio(f,d); predicted=force_ratio(8*(1-.75*s)*d,d); retained_prediction=force_ratio(8*(1-.75*initial)*d,d)
                    result['queries'][row['filename']]=dict(category=row['category'],ratio=ratio,predicted=predicted,retained_prediction=retained_prediction,drift=float(np.max(np.abs(s-initial))),max_force_error=float(np.max(np.abs(f-8*(1-.75*s)*d))))
                    traces[variant+'-'+history+'-'+row['filename']]=np.asarray(query_trace)
                    if not np.array_equal(mapped_states(saved,ids),initial):raise ValueError('Probe contaminated retained source')
                    active={history:s[-1].tolist()};progress('probe',variant=variant,history=history,clip=row['filename'],frame=49,physical_time=w.t)
            if results[variant]['restored']['queries']!=results[variant]['church_bells']['queries']:raise ValueError('Restored query mismatch')
            for row in [r for r in rows if int(r['fold'])==2]:
                if not np.array_equal(traces[variant+'-restored-'+row['filename']],traces[variant+'-church_bells-'+row['filename']]):raise ValueError('Restored trace mismatch')
        np.savez_compressed(output/'traces.npz',**traces)
        gates=aggregate(results)
        atomic(output/'result.json',dict(results=results,gates=gates,provenance=provenance,observed_ticks=observed,wall_seconds=time.monotonic()-started,verdict=gates['decision']['verdict'],validity='VALID',trace_columns='delta8,force8,s_pre8,s_post8,cumulative_boundary_work,cumulative_removed_kinetic'))
        atomic(output/'progress.json',dict(experiment='G183',state='completed_evidence',updated_unix=time.time(),observed_ticks=observed,verdict=gates['decision']['verdict']))
    except Exception as e:
        if 'w' in locals():
            try:save_snapshot(w,output/'failed-world.npz')
            except Exception:pass
        np.savez_compressed(output/'partial-traces.npz',**traces)
        atomic(output/'FAILED.json',dict(error=repr(e),observed_ticks=observed,results=results))
        atomic(output/'progress.json',dict(experiment='G183',state='failed',updated_unix=time.time(),observed_ticks=observed,error=repr(e)));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--seal',type=Path,required=True)
    args=parser.parse_args();run(args.data,args.output,args.seal)
