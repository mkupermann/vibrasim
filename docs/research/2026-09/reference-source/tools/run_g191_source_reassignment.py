"""G191 guided local-aging reference. Import and static helpers do not integrate."""
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
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.run_g188_continuous_reference import scipy_license,scipy_sources
from tools.run_g189_local_aging_transfer import DEADLINE,atomic,sha
PROTOCOLS=('docs/amendments/g191_source_reassignment.md','docs/amendments/g191_forecast_clarification.md')
FIELDS=('y','v','kA','kB','kG','WA','WB','WT','Qdrag','Qaging','Wabs')
BRANCHES=('acquisition','switch','continue','separated','frozen')


def required_sources():
    return list(PROTOCOLS)+['tools/run_g191_source_reassignment.py','tools/run_g189_local_aging_transfer.py','tools/run_g188_continuous_reference.py','tools/__init__.py','pyproject.toml','uv.lock']


def verify_seal(path):
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],timeout=15)
    raw=Path(path).read_bytes();seal=json.loads(raw);head=git('rev-parse','HEAD').decode().strip()
    if seal['status']!='approved-source-reassignment' or git('show',head+':'+str(Path(path).resolve().relative_to(ROOT)))!=raw:raise ValueError('Uncommitted/unapproved seal')
    p,i=seal['protocol_commit'],seal['implementation_commit']
    if p==i:raise ValueError('Separate protocol and implementation required')
    git('merge-base','--is-ancestor',p,i);git('merge-base','--is-ancestor',i,head)
    if set(seal['sources'])!=set(required_sources()):raise ValueError('Source inventory mismatch')
    for name,digest in seal['sources'].items():
        if sha(ROOT/name)!=digest or git('show',i+':'+name)!=(ROOT/name).read_bytes():raise ValueError('Source mismatch '+name)
    for name in PROTOCOLS:
        if git('show',p+':'+name)!=(ROOT/name).read_bytes():raise ValueError('Protocol changed '+name)
    if importlib.metadata.version('scipy')!='1.17.1' or seal['scipy_version']!='1.17.1' or seal['scipy_license_sha256']!=sha(scipy_license()) or seal['scipy_sources']!=scipy_sources():raise ValueError('SciPy mismatch')
    return dict(head=head,seal=seal,seal_sha256=hashlib.sha256(raw).hexdigest(),numpy=np.__version__,python=sys.version)


def pulse(t,dose):
    a=np.pi/8;amplitude=np.sqrt(dose/3)
    return amplitude*np.sin(a*t)**2,amplitude*a*np.sin(2*a*t),2*amplitude*a*a*np.cos(2*a*t)


def teaching(label,kind):
    teacher=(1 if label=='A' else 0) if kind in ('switch','frozen') else 2 if kind=='separated' else (0 if label=='A' else 1)
    return [dict(start=8.*j,end=8.*(j+1),phase='teach',slot=j,teacher=teacher,dose=.2 if kind=='initial' else .4) for j in range(3)]+[dict(start=24.,end=44.,phase='hold')]


def reads():
    return [dict(start=20.*j+l,end=20.*j+r,phase='read',piece=p,cycle=j,source=j%2) for j in range(10) for p,(l,r) in enumerate(((0,2),(2,8),(8,10),(10,20)))]


def inputs(segment,t):
    u=np.zeros(2);du=np.zeros(2);y=v=a=0.;clamped=segment['phase']=='teach'
    if clamped:
        value,velocity,acceleration=pulse(t-segment['start'],segment['dose']);slot=segment['slot']
        if slot<2:u[slot]=value;du[slot]=velocity
        if slot==segment['teacher']:y,v,a=value,velocity,acceleration
    elif segment['phase']=='read':
        local=t-20*segment['cycle'];piece=segment['piece']
        if piece==0:
            z=np.clip(local,0,2);value=.01*np.sin(np.pi*z/4)**2;velocity=.01*np.pi/4*np.sin(np.pi*z/2)
        elif piece==1:value,velocity=.01,0.
        elif piece==2:
            z=np.clip(local-8,0,2);value=.01*np.cos(np.pi*z/4)**2;velocity=-.01*np.pi/4*np.sin(np.pi*z/2)
        else:value,velocity=0.,0.
        u[segment['source']]=value;du[segment['source']]=velocity
    return u,du,y,v,a,clamped


def quantities(segment,t,z,gamma=1.):
    z=np.asarray(z)
    if z.shape!=(11,) or not np.isfinite(z).all() or np.any(z[2:5]<=0):raise ValueError('Invalid state')
    u,du,ty,tv,ta,clamped=inputs(segment,t);y,v=(ty,tv) if clamped else z[:2]
    extension=np.array([y-u[0],u[1]-y,-y]);k=z[2:5]
    if np.min(np.array([10.,10.,20.])+extension)<=1e-6:raise ValueError('Invalid physical length')
    force=k[0]*(u[0]-y)+k[1]*(u[1]-y)-k[2]*y
    powers=k[:2]*(u-y)*du;pt=(4*ta-force+4*v)*v if clamped else 0.
    drag=4*v*v;aging=.5*gamma*np.sum(k*extension**4)
    dz=np.r_[tv if clamped else v,ta if clamped else force/4-v,-gamma*k*extension**2,powers,pt,drag,aging,np.abs(powers).sum()+abs(pt)]
    return dz,dict(uA=u[0],uB=u[1],duA=du[0],duB=du[1],teacher_y=ty,teacher_v=tv,teacher_acceleration=ta,clamped=clamped,physical_y=y,physical_v=v,force=force,PA=powers[0],PB=powers[1],PT=pt,Qdrag_rate=drag,Qaging_rate=aging,E=2*v*v+.5*np.sum(k*extension**2))


def expected_k(label,kind,starting):
    factors=np.ones(3);l=0 if label=='A' else 1;o=1-l
    if kind=='initial':factors[o]=np.exp(-.4);factors[2]=np.exp(-.2)
    elif kind=='switch':factors[l]=np.exp(-.8);factors[2]=np.exp(-.4)
    elif kind=='continue':factors[o]=np.exp(-.8);factors[2]=np.exp(-.4)
    elif kind=='separated':factors[:2]=np.exp(-.8);factors[2]=np.exp(-.4)
    elif kind!='frozen':raise ValueError(kind)
    return np.asarray(starting)*factors


def read_metrics(t,z,baseline):
    gains=[];blanks=[]
    for j in range(10):
        start=20*j
        before=baseline if j==0 else z[(t>=start-2-1e-10)&(t<=start+1e-10),0].mean()
        plateau=(t>=start+6-1e-10)&(t<=start+8+1e-10)
        blank=(t>=start+18-1e-10)&(t<=start+20+1e-10)
        gains.append(float((z[plateau,0].mean()-before)/.01))
        blanks.append(np.max(np.abs(z[blank,:2]),axis=0).tolist())
    return np.array(gains),blanks


def run(output,seal):
    started=time.monotonic();stopped=[False]
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:stopped.__setitem__(0,True))
    provenance=verify_seal(seal);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    from scipy.integrate import solve_ivp
    calls=0;completed=0;last=None;results={};manifest={}
    def budget():
        if stopped[0] or time.monotonic()-started>=300 or time.time()>=DEADLINE:raise TimeoutError('G191 fixed budget/deadline')
    def save(name,**data):
        budget();path=output/(name+'.npz');np.savez_compressed(path,**data)
        with np.load(path,allow_pickle=False) as saved:
            if set(saved.files)!=set(data) or any(saved[key].dtype!=np.asarray(value).dtype or saved[key].shape!=np.asarray(value).shape or saved[key].tobytes()!=np.asarray(value).tobytes() for key,value in data.items()):raise ValueError('Nonexact evidence reload')
        manifest[path.name]=sha(path)
        if sum(p.stat().st_size for p in output.iterdir() if p.is_file())>=99_000_000:raise ValueError('Evidence cap')
        atomic(output/'files.json',manifest)
    def evolve(name,initial,schedule,gamma,forecast=False):
        nonlocal calls,completed,last
        z=initial.copy();ts=[];zs=[];records=[]
        for index,seg in enumerate(schedule):
            start=z.copy()
            def rhs(t,state):
                nonlocal calls,last
                budget();calls+=1;last=dict(name=name,t=float(t),state=state.copy())
                if forecast:
                    u=inputs(seg,t)[0];dy=state[1];dv=(np.dot(initial[2:4],u-state[0])-initial[4]*state[0])/4-state[1]
                    derivative=np.r_[dy,dv,np.zeros(9)]
                    quantities(seg,t,state,0.)  # Same finite/positive-length checks, no material updates.
                else:derivative,_=quantities(seg,t,state,gamma)
                if calls%200==1:atomic(output/'progress.json',dict(experiment='G191',state='active_reference',scope='guided local-aging reassignment; no World ticks or general learning',updated_unix=time.time(),runner_pid=os.getpid(),history=name,phase=seg['phase'],physical_time=float(t),rhs_evaluations=calls,completed_segments=completed,stiffness=state[2:5].tolist()))
                return derivative
            count=round((seg['end']-seg['start'])/.02)+1;grid=np.linspace(seg['start'],seg['end'],count)
            sol=solve_ivp(rhs,(seg['start'],seg['end']),start,method='DOP853',rtol=1e-9,atol=1e-11,max_step=.05,t_eval=grid)
            if sol.y.size==0:raise ValueError('Empty solution')
            save(f'{name}-segment-{index:02d}',time=sol.t,state=sol.y.T,initial=start,final=sol.y[:,-1])
            records.append(dict(segment=seg,success=bool(sol.success),nfev=sol.nfev,message=sol.message));atomic(output/(name+'-segments.json'),records)
            if not sol.success or len(sol.t)!=count:raise ValueError('Incomplete solution')
            z=sol.y[:,-1].copy();skip=0 if index==0 else 1;ts.extend(sol.t[skip:]);zs.extend(sol.y.T[skip:].copy());completed+=1
        t=np.array(ts);states=np.array(zs)
        if not np.allclose(t,np.arange(len(t))*.02+schedule[0]['start'],rtol=0,atol=1e-10):raise ValueError('Grid mismatch')
        metadata=[]
        for ti,zi in zip(t,states):
            seg=next((s for s in schedule if s['start']<=ti<s['end']),schedule[-1])
            _,q=quantities(seg,ti,zi,0. if forecast else gamma);metadata.append(q)
        arrays={key:np.array([q[key] for q in metadata]) for key in metadata[0]}
        tracking=np.max(np.abs(states[:,:2]-np.c_[arrays['physical_y'],arrays['physical_v']]),axis=0)
        if np.any(tracking>1e-7):raise ValueError('Clamp bookkeeping mismatch')
        save(name,time=t,state=states,initial=initial,final=z,**arrays)
        residual=arrays['E']-states[:,5]-states[:,6]-states[:,7]+states[:,8]+states[:,9]
        metrics=dict(accounting_scope='forecast channels copied and not evolved; energy residual is not a conservation test' if forecast else 'physical accounting inherited from initialization',min_k=float(states[:,2:5].min()),max_energy_residual=float(np.max(np.abs(residual))),Wabs_final=float(z[10]),clamp_bookkeeping_error=tracking.tolist(),data_sha256=manifest[name+'.npz'])
        return t,states,metrics
    try:
        for label in ('A','B'):
            initial=np.r_[0.,0.,8.,8.,8.,np.zeros(6)]
            ti,zi,mi=evolve(label+'-initial',initial,teaching(label,'initial'),1.)
            parent=zi[-1].copy();save(label+'-parent',state=parent)
            initial_k_error=float(np.max(np.abs(zi[1200,2:5]-expected_k(label,'initial',initial[2:5]))))
            results[label]={}
            for branch in BRANCHES:
                name=label+'-'+branch;fork=parent.copy()
                if not np.array_equal(fork,parent):raise ValueError('Nonexact fork')
                save(name+'-fork',state=fork,parent_state=parent)
                gamma=0. if branch=='frozen' else 1.
                if branch=='acquisition':hold_t,hold_z,teach_metrics=ti,zi,mi;k_error=initial_k_error
                else:
                    if np.max(np.abs(fork[:2]))>1e-12:raise ValueError('Teaching would reset receiver')
                    hold_t,hold_z,teach_metrics=evolve(name+'-teaching',fork,teaching(label,branch),gamma)
                    k_error=float(np.max(np.abs(hold_z[1200,2:5]-expected_k(label,branch,fork[2:5]))))
                endpoint=hold_z[-1].copy();baseline=float(hold_z[(hold_t>=42-1e-10)&(hold_t<=44+1e-10),0].mean())
                save(name+'-endpoint',state=endpoint,initial_baseline=baseline)
                ft,fz,fm=evolve(name+'-forecast',endpoint,reads(),0.,forecast=True)
                # Persist the entire forecast and derived gains before actual integration.
                predicted,_=read_metrics(ft,fz,baseline)
                atomic(output/(name+'-forecast.json'),dict(gains=predicted.tolist(),data_sha256=fm['data_sha256'],scope='conditioned on measured starting k,y,v; no subsequent observations',created_unix=time.time()))
                at,az,am=evolve(name+'-actual',endpoint,reads(),gamma)
                gains,blanks=read_metrics(at,az,baseline);d=(gains[::2]-gains[1::2])*(1 if label=='A' else -1)
                limit=-.08 if branch=='switch' else .16 if branch=='continue' else .08
                preference=bool(np.all(d<=limit) if branch=='switch' else np.all(d>=limit))
                forecast_error=np.max(np.abs(az[:,:2]-fz[:,:2]),axis=0);gain_error=float(np.max(np.abs(gains-predicted)))
                drift={source:float(np.max(np.abs(gains[j::2]-gains[j]))) for j,source in enumerate(('A','B'))}
                k_drift=float(np.max(np.abs(az[:,2:5]-endpoint[2:5])/endpoint[2:5]))
                # Full-path energy maxima include inherited initial teaching/hold.
                energy_error=max(mi['max_energy_residual'],teach_metrics['max_energy_residual'],am['max_energy_residual'])
                min_k=min(mi['min_k'],teach_metrics['min_k'],am['min_k'])
                predictions=dict(P_L=preference and bool(np.all((gains>=.15)&(gains<=.75))),P_F=bool(np.all(forecast_error<=1e-4) and gain_error<=.01),P_K=initial_k_error<=1e-6 and k_error<=1e-6,P_S=min_k>=1.5,P_E=energy_error<=1e-6*max(1.,am['Wabs_final']),P_M=k_drift<=.01 and all(v<=.005 for v in drift.values()),R=bool(np.max(blanks)<=1e-5))
                results[label][branch]=dict(gains=gains.tolist(),differences=d.tolist(),forecast_gains=predicted.tolist(),forecast_y_v_error=forecast_error.tolist(),forecast_gain_error=gain_error,blank_y_v_max=blanks,source_gain_drift=drift,k_relative_drift=k_drift,initial_k_error=initial_k_error,teaching_k_error=k_error,min_k=min_k,max_energy_residual=energy_error,actual=am,forecast=fm,teaching=teach_metrics,predictions=predictions)
                atomic(output/'partial-results.json',results)
        atomic(output/'result.json',dict(validity='VALID',verdict='REFERENCE_COMPLETE',scope='finite source reassignment in known guided local aging; no general learning',results=results,return_failure_predicted=any(not b['predictions']['R'] for l in results.values() for b in l.values()),provenance=provenance,state_fields=FIELDS,files=manifest,rhs_evaluations=calls,completed_segments=completed,wall_seconds=time.monotonic()-started))
        atomic(output/'progress.json',dict(experiment='G191',state='completed_evidence',updated_unix=time.time(),verdict='REFERENCE_COMPLETE'))
    except Exception as exc:
        if last is not None:np.savez_compressed(output/'failed-last-rhs.npz',time=last['t'],state=last['state'])
        atomic(output/'FAILED.json',dict(validity='INVALID',error=repr(exc),results=results,provenance=provenance,rhs_evaluations=calls,completed_segments=completed))
        atomic(output/'progress.json',dict(experiment='G191',state='failed',updated_unix=time.time(),error=repr(exc)));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--seal',type=Path,required=True);args=parser.parse_args();run(args.output,args.seal)
