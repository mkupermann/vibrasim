"""G189 finite-dose local-aging reference; no integrations on import."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime,timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.run_g188_continuous_reference import scipy_license,scipy_sources
PROTOCOL='docs/amendments/g189_local_aging_transfer.md'
ARMS=('paired','late','early','source-only','teacher-only','frozen','sham')
DEADLINE=datetime(2026,9,14,2,39,14,tzinfo=timezone.utc).timestamp()
FIELDS=('y','v','kS','kG','W_source','W_teacher','Q_drag','Q_aging','W_absolute')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path,value):
    temporary=Path(str(path)+'.tmp');temporary.write_text(json.dumps(value,allow_nan=False,indent=2)+'\n');os.replace(temporary,path)


def required_sources():
    return ['tools/__init__.py',PROTOCOL,'docs/amendments/g189_accounting_clarification.md','tools/run_g189_local_aging_transfer.py','tools/run_g188_continuous_reference.py','pyproject.toml','uv.lock']


def verify_seal(path):
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],timeout=15)
    raw=Path(path).read_bytes();seal=json.loads(raw);head=git('rev-parse','HEAD').decode().strip()
    if seal['status']!='approved-local-aging-transfer' or git('show',head+':'+str(Path(path).resolve().relative_to(ROOT)))!=raw:raise ValueError('Uncommitted/unapproved seal')
    p,i=seal['protocol_commit'],seal['implementation_commit']
    if p==i:raise ValueError('Separate protocol/implementation commits required')
    git('merge-base','--is-ancestor',p,i);git('merge-base','--is-ancestor',i,head)
    if set(seal['sources'])!=set(required_sources()):raise ValueError('Incomplete source seal')
    for name,digest in seal['sources'].items():
        if sha(ROOT/name)!=digest or git('show',i+':'+name)!=(ROOT/name).read_bytes():raise ValueError('Source mismatch '+name)
    for protocol in (PROTOCOL,'docs/amendments/g189_accounting_clarification.md'):
        if git('show',p+':'+protocol)!=(ROOT/protocol).read_bytes():raise ValueError('Changed protocol '+protocol)
    if importlib.metadata.version('scipy')!='1.17.1' or seal['scipy_version']!='1.17.1' or seal['scipy_license_sha256']!=sha(scipy_license()) or seal['scipy_sources']!=scipy_sources():raise ValueError('SciPy source/distribution mismatch')
    return dict(head=head,seal=seal,seal_sha256=hashlib.sha256(raw).hexdigest(),python=sys.version,numpy=np.__version__)


def pulse(t):
    if t<0 or t>8:return 0.,0.,0.
    a=np.pi/8
    return .5*np.sin(a*t)**2,.5*a*np.sin(2*a*t),a*a*np.cos(2*a*t)


def segments():
    out=[dict(start=0.,end=8.,phase='teaching',piece=0),dict(start=8.,end=16.,phase='teaching',piece=1),dict(start=16.,end=36.,phase='hold',piece=0)]
    for cycle in range(10):
        base=36+20*cycle
        for piece,(left,right) in enumerate(((0,2),(2,8),(8,10),(10,20))):out.append(dict(start=float(base+left),end=float(base+right),phase='read',piece=piece,cycle=cycle+1))
    return out


def inputs(arm,segment,t):
    if arm not in ARMS:raise ValueError('Unknown arm')
    if segment['phase']=='teaching':
        source_shift=8 if arm=='early' else 0
        teacher_shift=8 if arm=='late' else 0
        u,du,_=pulse(t-source_shift) if arm not in ('teacher-only','sham') and segment['piece']==source_shift//8 else (0.,0.,0.)
        y,v,a=pulse(t-teacher_shift) if arm not in ('source-only','sham') and segment['piece']==teacher_shift//8 else (0.,0.,0.)
        return u,du,y,v,a,True
    if segment['phase']=='hold':return 0.,0.,0.,0.,0.,False
    local=t-(36+20*(segment['cycle']-1));piece=segment['piece']
    if piece==0:
        z=np.clip(local,0,2);u=.01*np.sin(np.pi*z/4)**2;du=.01*np.pi/4*np.sin(np.pi*z/2)
    elif piece==1:u,du=.01,0.
    elif piece==2:
        z=np.clip(local-8,0,2);u=.01*np.cos(np.pi*z/4)**2;du=-.01*np.pi/4*np.sin(np.pi*z/2)
    else:u,du=0.,0.
    return u,du,0.,0.,0.,False


def quantities(arm,segment,t,state):
    z=np.asarray(state)
    if z.shape!=(9,) or not np.isfinite(z).all() or np.any(z[2:4]<=0):raise ValueError('Invalid material state')
    u,du,teacher_y,teacher_v,teacher_a,clamped=inputs(arm,segment,t)
    y,v=(teacher_y,teacher_v) if clamped else (z[0],z[1])
    es,eg=y-u,-y
    if 10+es<=1e-6 or 10+eg<=1e-6:raise ValueError('Node crossing/singular spring')
    ks,kg=z[2:4];gamma=0. if arm=='frozen' else 1.
    force=ks*(u-y)-kg*y;ps=ks*(u-y)*du;pt=(4*teacher_a-force+4*v)*v if clamped else 0.
    drag=4*v*v;aging=.5*gamma*(ks*es**4+kg*eg**4)
    derivative=np.array([teacher_v if clamped else v,teacher_a if clamped else force/4-v,-gamma*ks*es*es,-gamma*kg*eg*eg,ps,pt,drag,aging,abs(ps)+abs(pt)])
    return derivative,dict(u=u,du=du,teacher_y=teacher_y,teacher_v=teacher_v,teacher_acceleration=teacher_a,clamped=clamped,physical_y=y,physical_v=v,force=force,P_source=ps,P_teacher=pt,P_drag=drag,P_aging=aging,E=2*v*v+.5*ks*es*es+.5*kg*eg*eg)


def expected_stiffness():
    return {'paired':[8.,8*np.exp(-.75)],'late':[8*np.exp(-1.5),8*np.exp(-.75)],'early':[8*np.exp(-1.5),8*np.exp(-.75)],'source-only':[8*np.exp(-.75),8.],'teacher-only':[8*np.exp(-.75),8*np.exp(-.75)],'frozen':[8.,8.],'sham':[8.,8.]}


def evaluate_arm(arm,t,z,energy,clamped,teacher_power):
    teaching=int(round(16/.02));hold=int(round(36/.02))
    k_error=float(np.max(np.abs(z[teaching,2:4]-expected_stiffness()[arm])))
    responses=[];blank_limits=[]
    for cycle in range(10):
        start=36+20*cycle
        baseline=(t>=start-2-1e-10)&(t<=start+1e-10)
        read=(t>=start+6-1e-10)&(t<=start+8+1e-10)
        blank=(t>=start+18-1e-10)&(t<=start+20+1e-10)
        responses.append(float((z[read,0].mean()-z[baseline,0].mean())/.01))
        blank_limits.append(dict(y=float(np.max(np.abs(z[blank,0]))),v=float(np.max(np.abs(z[blank,1])))))
    lo,hi=(.64,.72) if arm=='paired' else (.28,.37) if arm in ('late','early','source-only') else (.46,.54)
    response_drift=max(abs(x-responses[0]) for x in responses)
    stiffness_drift=float(np.max(np.abs(z[hold:,2:4]-z[hold,2:4])/z[hold,2:4]))
    residual=energy-energy[0]-z[:,4]-z[:,5]+z[:,6]+z[:,7]
    err=float(np.max(np.abs(residual)));scale=max(1.,float(z[-1,8]))
    if np.any(teacher_power[~clamped]!=0):raise ValueError('Teacher power in free phase')
    return dict(responses=responses,blank_limits=blank_limits,teaching_k=z[teaching,2:4].tolist(),post_hold_k=z[hold,2:4].tolist(),teaching_k_error=k_error,response_drift=response_drift,relative_stiffness_drift=stiffness_drift,min_stiffness=float(z[:,2:4].min()),max_energy_residual=err,energy_scale=scale,predictions=dict(P_K=k_error<=1e-6,P_T=all(lo<=x<=hi for x in responses),P_R=response_drift<=.005 and stiffness_drift<=.01 and all(b['y']<=1e-5 and b['v']<=1e-5 for b in blank_limits),P_S=bool(z[:,2:4].min()>=1.5),P_E=err<=1e-6*scale))


def run(output,seal):
    started=time.monotonic();stop=[False]
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:stop.__setitem__(0,True))
    provenance=verify_seal(seal);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    from scipy.integrate import solve_ivp
    results={};calls=0;last=None;completed=0
    def budget():
        if stop[0] or time.monotonic()-started>=300 or time.time()>=DEADLINE:raise TimeoutError('G189 stop/budget/campaign deadline')
    try:
        for arm in ARMS:
            state=np.array([0.,0.,8.,8.,0.,0.,0.,0.,0.]);all_t=[];all_z=[];records=[]
            for index,segment in enumerate(segments()):
                budget();initial=state.copy();label=f'{arm}-{index:02d}'
                def rhs(t,z):
                    nonlocal calls,last
                    budget();calls+=1;last=dict(arm=arm,index=index,t=float(t),z=z.copy());derivative,_=quantities(arm,segment,t,z)
                    if calls%100==1:atomic(output/'progress.json',dict(experiment='G189',state='active_reference',scope='local-aging reference material integration; no World ticks or cognition',updated_unix=time.time(),runner_pid=os.getpid(),history=arm,sequence=segment['phase'],segment=index,rhs_evaluations=calls,completed_segments=completed,physical_time=float(t),stiffness=z[2:4].tolist()))
                    return derivative
                count=int(round((segment['end']-segment['start'])/.02))+1;grid=np.linspace(segment['start'],segment['end'],count)
                sol=solve_ivp(rhs,(segment['start'],segment['end']),initial,method='DOP853',rtol=1e-9,atol=1e-11,max_step=.05,t_eval=grid)
                # t_eval includes the exact segment endpoint: carry unrounded solver state.
                np.savez_compressed(output/(label+'.npz'),time=sol.t,state=sol.y.T,initial=initial,final=sol.y[:,-1])
                record=dict(segment=segment,success=bool(sol.success),status=sol.status,nfev=sol.nfev,message=sol.message,file=label+'.npz',sha256=sha(output/(label+'.npz')))
                records.append(record);atomic(output/(arm+'-segments.json'),records)
                if not sol.success or len(sol.t)!=count:raise ValueError('Solver failed/incomplete')
                state=sol.y[:,-1].copy();start=0 if index==0 else 1
                all_t.extend(sol.t[start:]);all_z.extend(sol.y.T[start:].copy());completed+=1
                if sum(p.stat().st_size for p in output.iterdir() if p.is_file())>59_000_000:raise ValueError('Evidence size cap')
            t=np.asarray(all_t);z=np.asarray(all_z)
            if t.shape!=(11801,) or not np.allclose(t,np.arange(11801)*.02,rtol=0,atol=1e-10):raise ValueError('Global sample grid mismatch')
            # Unique boundary samples use the new segment (teacher off at t=16).
            q=[]
            for ti,zi in zip(t,z):
                segment=next((s for s in segments() if s['start']<=ti<s['end']),segments()[-1])
                _,values=quantities(arm,segment,float(ti),zi);q.append(values)
            arrays={name:np.asarray([row[name] for row in q]) for name in q[0]}
            tracking=dict(y=float(np.max(np.abs(z[:,0]-arrays['physical_y']))),v=float(np.max(np.abs(z[:,1]-arrays['physical_v']))),tolerance=1e-7)
            if tracking['y']>tracking['tolerance'] or tracking['v']>tracking['tolerance']:raise ValueError('Teaching kinematic bookkeeping mismatch '+repr(tracking))
            np.savez_compressed(output/(arm+'.npz'),time=t,state=z,**arrays)
            results[arm]=evaluate_arm(arm,t,z,arrays['E'],arrays['clamped'],arrays['P_teacher'])
            results[arm]['kinematic_bookkeeping_error']=tracking
            results[arm]['data_sha256']=sha(output/(arm+'.npz'));atomic(output/'partial-results.json',results)
        contrasts={arm:(np.array(results['paired']['responses'])-np.array(results[arm]['responses'])).tolist() for arm in ('early','late')}
        contrast_ok=all(v>=.25 for values in contrasts.values() for v in values)
        atomic(output/'result.json',dict(validity='VALID',verdict='REFERENCE_COMPLETE',results=results,paired_minus_unpaired=contrasts,contrast_prediction=contrast_ok,provenance=provenance,state_fields=FIELDS,rhs_evaluations=calls,completed_segments=completed,wall_seconds=time.monotonic()-started))
        atomic(output/'progress.json',dict(experiment='G189',state='completed_evidence',scope='known local-aging reference; no multimodal learning claim',updated_unix=time.time(),verdict='REFERENCE_COMPLETE',rhs_evaluations=calls,completed_segments=completed))
    except Exception as error:
        if last is not None:np.savez_compressed(output/'failed-last-rhs.npz',time=last['t'],state=last['z'])
        atomic(output/'FAILED.json',dict(validity='INVALID',error=repr(error),results=results,last=None if last is None else {k:v for k,v in last.items() if k!='z'},provenance=provenance,rhs_evaluations=calls,completed_segments=completed))
        atomic(output/'progress.json',dict(experiment='G189',state='failed',updated_unix=time.time(),error=repr(error),rhs_evaluations=calls));raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seal',type=Path,required=True);a=p.parse_args();run(a.output,a.seal)
