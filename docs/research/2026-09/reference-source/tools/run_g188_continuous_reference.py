"""G188 explicit continuous reference using SciPy DOP853; never World.tick."""
from pathlib import Path
import argparse
import dataclasses
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
PROTOCOL='docs/amendments/g188_continuous_reference.md'
STAGES=('acquisition','reversal')
FREE=np.array([1,4,7,10,12])


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path,data):
    tmp=Path(str(path)+'.tmp');tmp.write_text(json.dumps(data,allow_nan=False,indent=2)+'\n');os.replace(tmp,path)


def required_sources():
    return sorted({str(p.relative_to(ROOT)) for p in (ROOT/'world').rglob('*.py')}|{PROTOCOL,'tools/run_g188_continuous_reference.py','pyproject.toml','uv.lock'})


def required_data():return ['result.json']+[f'{s}-frozen-zero-start.npz' for s in STAGES]


def scipy_license():
    dist=importlib.metadata.distribution('scipy')
    candidates=[dist.locate_file(f) for f in dist.files if str(f).endswith('.dist-info/licenses/LICENSE.txt') or str(f).endswith('.dist-info/LICENSE.txt')]
    if len(candidates)!=1:raise ValueError('Cannot identify installed SciPy license')
    return Path(candidates[0])


def scipy_sources():
    import scipy
    base=Path(scipy.__file__).parent
    return {name:sha(base/name) for name in ('integrate/_ivp/rk.py','integrate/_ivp/ivp.py','integrate/_ivp/common.py','integrate/_ivp/base.py','integrate/_ivp/dop853_coefficients.py')}


def verify_seal(path,root):
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],timeout=15)
    raw=Path(path).read_bytes();seal=json.loads(raw);head=git('rev-parse','HEAD').decode().strip()
    if seal['status']!='approved-continuous-reference' or git('show',head+':'+str(Path(path).resolve().relative_to(ROOT)))!=raw:raise ValueError('Uncommitted/unapproved seal')
    p,i=seal['protocol_commit'],seal['implementation_commit']
    if p==i:raise ValueError('Separate protocol/implementation commits required')
    git('merge-base','--is-ancestor',p,i);git('merge-base','--is-ancestor',i,head)
    if set(seal['sources'])!=set(required_sources()) or set(seal['data'])!=set(required_data()):raise ValueError('Incomplete seal')
    for name,h in seal['sources'].items():
        if sha(ROOT/name)!=h or git('show',i+':'+name)!=(ROOT/name).read_bytes():raise ValueError('Source mismatch '+name)
    if git('show',p+':'+PROTOCOL)!=(ROOT/PROTOCOL).read_bytes():raise ValueError('Changed protocol')
    for name,h in seal['data'].items():
        if sha(root/name)!=h:raise ValueError('Data mismatch '+name)
    if importlib.metadata.version('scipy')!=seal['scipy_version'] or seal['scipy_version']!='1.17.1' or sha(scipy_license())!=seal['scipy_license_sha256']:raise ValueError('SciPy distribution mismatch')
    if seal['scipy_sources']!=scipy_sources():raise ValueError('SciPy solver source mismatch')
    return dict(head=head,seal=seal,seal_sha256=hashlib.sha256(raw).hexdigest(),python=sys.version,numpy=np.__version__)


@dataclasses.dataclass
class Model:
    positions:np.ndarray
    velocities:np.ndarray
    edges:np.ndarray
    rests:np.ndarray
    stiffness:np.ndarray
    mass:np.ndarray
    damping:np.ndarray
    free:np.ndarray
    box:np.ndarray

    def __post_init__(self):
        self.branch=np.round((self.positions[self.edges[:,1]]-self.positions[self.edges[:,0]])/self.box)
        self.fixed=np.setdiff1d(np.arange(len(self.positions)),self.free)
        self.size=3*len(self.free)

    def initial(self):return np.r_[self.positions[self.free].ravel(),self.velocities[self.free].ravel(),0.]

    def unpack(self,y):
        y=np.asarray(y)
        if y.shape!=(2*self.size+1,) or not np.isfinite(y).all():raise ValueError('Invalid ODE state')
        x=self.positions.copy();v=np.zeros_like(x);x[self.free]=y[:self.size].reshape(-1,3);v[self.free]=y[self.size:2*self.size].reshape(-1,3)
        return x,v

    def force_energy(self,x):
        if x.shape!=self.positions.shape or not np.isfinite(x).all() or not np.array_equal(x[self.fixed],self.positions[self.fixed]):raise ValueError('Nonfinite/fixed mapping failure')
        raw=x[self.edges[:,1]]-x[self.edges[:,0]]
        if not np.array_equal(np.round(raw/self.box),self.branch):raise ValueError('Minimum-image branch crossing')
        d=raw-self.box*self.branch;length=np.linalg.norm(d,axis=1)
        if np.any(length<=1e-6):raise ValueError('Singular bond')
        extension=length-self.rests;pair=self.stiffness[:,None]*extension[:,None]*d/length[:,None];force=np.zeros_like(x)
        # Preserve supplied traversal, do not sort the experimental intervention.
        for (i,j),f in zip(self.edges,pair):force[i]+=f;force[j]-=f
        return force,float(np.sum(.5*self.stiffness*extension**2))

    def rhs(self,t,y):
        x,v=self.unpack(y);f,_=self.force_energy(x)
        acc=f[self.free]/self.mass[self.free,None]-self.damping[self.free,None]*v[self.free]
        diss=float(np.sum(self.mass[self.free]*self.damping[self.free]*np.sum(v[self.free]**2,axis=1)))
        return np.r_[v[self.free].ravel(),acc.ravel(),diss]

    def energy(self,y):
        x,v=self.unpack(y);_,potential=self.force_energy(x)
        return potential+float(.5*np.sum(self.mass*np.sum(v*v,axis=1)))


def analytic_model(x0):
    return Model(np.array([[-2.,0,0],[x0,0,0],[2.,0,0]]),np.zeros((3,3)),np.array([[0,1],[1,2]]),np.ones(2),np.ones(2),np.ones(3),np.ones(3),np.array([1]),np.ones(3)*1e6)


def analytic_solution(t):
    omega=np.sqrt(7)/2;decay=np.exp(-t/2)
    x=.1*decay*(np.cos(omega*t)+np.sin(omega*t)/np.sqrt(7))
    v=-.4/np.sqrt(7)*decay*np.sin(omega*t)
    return x,v


def fixture(world,reverse=False):
    cfg=world.config
    if (world.k_count!=17 or world.b_count!=16 or np.count_nonzero(world.k_alive)!=17 or np.count_nonzero(world.b_alive)!=16 or not world.k_alive[:17].all() or not world.b_alive[:16].all() or not np.all(world.k_level[:17]==4) or cfg.material_memory_rate!=0 or cfg.material_memory_mode!='rest_shift' or cfg.material_memory_rest_shift!=1 or cfg.bridge_tension_k!=8 or cfg.bridge_tension_damping!=.95 or cfg.dt!=1/60 or not cfg.per_bond_rest_enabled or not cfg.material_memory_enabled or np.any(world.k_vel[:17]!=0)):raise ValueError('Inherited fixture/config mismatch')
    edges=np.column_stack((world.b_atom_i[:16],world.b_atom_j[:16])).copy();q=world.b_material_state[:16].copy();rests=world.b_rest_len[:16].copy()
    if not np.isfinite(q).all() or np.any(q<0) or np.any(q>1) or not np.all(world.b_strength[:16]==1) or np.any(rests<=0):raise ValueError('Invalid inherited bonds')
    if np.any(edges<0) or np.any(edges>=17) or len({tuple(sorted(e)) for e in edges})!=16:raise ValueError('Invalid edge mapping')
    degree=np.bincount(edges.ravel(),minlength=17);order=np.arange(15,-1,-1) if reverse else np.arange(16)
    return Model(world.k_pos[:17].copy(),world.k_vel[:17].copy(),edges[order],(rests+q)[order],np.full(16,8.),np.full(17,4.),-degree*np.log(.95)/(1/60),FREE.copy(),np.asarray(cfg.box_size,float)),dict(original_rests=rests[order].tolist(),material_states=q[order].tolist(),order=order.tolist(),degree=degree.tolist())


def run(root,output,seal):
    started=time.monotonic();stopped=[False]
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:stopped.__setitem__(0,True))
    root=Path(root);output=Path(output);provenance=verify_seal(seal,root);output.mkdir(parents=True,exist_ok=False)
    from scipy.integrate import solve_ivp
    from world.snapshot import load_snapshot
    calls=0;integrations=0;results={};last=None
    def budget():
        if stopped[0] or time.monotonic()-started>=300:raise TimeoutError('G188 stopped or300 second cap')
    def integrate(model,label,end,samples,rtol=1e-8,atol=1e-10):
        nonlocal calls,integrations,last
        budget();integrations+=1
        atomic(output/(label+'-mapping.json'),dict(positions=model.positions.tolist(),velocities=model.velocities.tolist(),edges=model.edges.tolist(),effective_rests=model.rests.tolist(),stiffness=model.stiffness.tolist(),mass=model.mass.tolist(),damping=model.damping.tolist(),free=model.free.tolist(),box=model.box.tolist(),branch=model.branch.tolist()))
        def rhs(t,y):
            nonlocal calls,last
            budget();calls+=1;last=dict(label=label,t=float(t),y=y.copy());value=model.rhs(t,y)
            if calls%100==1:atomic(output/'progress.json',dict(experiment='G188',state='active_reference',scope='continuous-reference evaluation; no World ticks or learning',updated_unix=time.time(),runner_pid=os.getpid(),integrations_started=integrations,rhs_evaluations=calls,sequence=label,physical_time=float(t)))
            return value
        sol=solve_ivp(rhs,(0,end),model.initial(),method='DOP853',t_eval=np.linspace(0,end,samples),rtol=rtol,atol=atol,max_step=.1)
        x=[];v=[];energy=[]
        for row in sol.y.T:
            a,b=model.unpack(row);x.append(a);v.append(b);energy.append(model.energy(row))
        data=dict(time=sol.t,positions=np.asarray(x),velocities=np.asarray(v),Q=sol.y[-1],E=np.asarray(energy))
        np.savez_compressed(output/(label+'.npz'),**data)
        record=dict(success=bool(sol.success),status=sol.status,nfev=sol.nfev,message=sol.message,rtol=rtol,atol=atol,samples=len(sol.t),data_sha256=sha(output/(label+'.npz')))
        atomic(output/(label+'-solver.json'),record)
        if not sol.success or len(sol.t)!=samples or any(not np.isfinite(a).all() for a in data.values()):raise ValueError('Solver failed/incomplete/nonfinite')
        if sum(p.stat().st_size for p in output.iterdir() if p.is_file())>59_000_000:raise ValueError('Evidence size cap')
        return data,record
    try:
        m=analytic_model(.1);force,_=m.force_energy(m.positions);h=1e-5;plus=m.positions.copy();minus=plus.copy();plus[1,0]+=h;minus[1,0]-=h
        gradient=(m.force_energy(plus)[1]-m.force_energy(minus)[1])/(2*h)
        fd=abs(force[1,0]+gradient);balance=float(np.max(np.abs(force.sum(0))))
        moving,meta=integrate(m,'control-oscillator',10,601);xx,vv=analytic_solution(moving['time'])
        error=max(float(np.max(np.abs(moving['positions'][:,1,0]-xx))),float(np.max(np.abs(moving['velocities'][:,1,0]-vv))))
        zero,zero_meta=integrate(analytic_model(0.),'control-balanced',10,601)
        zero_error=max(float(np.max(np.abs(zero['positions'][:,1]))),float(np.max(np.abs(zero['velocities'][:,1]))))
        controls=dict(force_gradient_error=fd,force_balance_error=balance,analytic_error=error,balanced_error=zero_error)
        atomic(output/'controls.json',controls)
        if fd>1e-8 or balance>1e-12 or error>1e-7 or zero_error>1e-12:raise ValueError('Analytic control failure; fixture integrations forbidden')
        old=json.loads((root/'result.json').read_text())
        if old['validity']!='VALID':raise ValueError('Invalid predecessor')
        for stage in STAGES:
            path=root/f'{stage}-frozen-zero-start.npz'
            if sha(path)!=old['results'][stage]['frozen-zero']['start_sha256']:raise ValueError('Original snapshot provenance mismatch')
            world=load_snapshot(path);results[stage]={};solutions={}
            for name,reverse,rtol,atol in (('original',False,1e-8,1e-10),('reverse',True,1e-8,1e-10),('refined',False,1e-10,1e-12)):
                model,mapping=fixture(world,reverse);label=stage+'-'+name;data,record=integrate(model,label,100,6001,rtol,atol);solutions[name]=data
                E0=model.energy(model.initial());scale=max(1.,E0);balance_error=float(np.max(np.abs(data['E']+data['Q']-E0)));increase=max(0.,float(np.max(np.diff(data['E']))))
                results[stage][name]=dict(solver=record,mapping=mapping,E0=E0,energy_balance_error=balance_error,max_energy_increase=increase,P_E=balance_error<=1e-6*scale and increase<=1e-8*scale,D=float(data['positions'][-1,12,0]-world.k_pos[12,0]))
                atomic(output/'partial-results.json',results)
            discrepancies={}
            for name in ('reverse','refined'):
                discrepancies[name]={field:float(np.max(np.abs(solutions['original'][field][:,FREE]-solutions[name][field][:,FREE]))) for field in ('positions','velocities')}
            results[stage]['comparison']=dict(discrepancies=discrepancies,P_C=max(discrepancies['refined'].values())<=1e-5,P_O=max(discrepancies['reverse'].values())<=1e-7,legacy_D=old['results'][stage]['frozen-zero']['D'])
            if sha(path)!=provenance['seal']['data'][path.name]:raise ValueError('Source snapshot changed')
        atomic(output/'result.json',dict(validity='VALID',verdict='REFERENCE_COMPLETE',controls=controls,results=results,integrations=integrations,rhs_evaluations=calls,provenance=provenance,wall_seconds=time.monotonic()-started))
        atomic(output/'progress.json',dict(experiment='G188',state='completed_evidence',scope='continuous-reference diagnostic; no learning',updated_unix=time.time(),verdict='REFERENCE_COMPLETE',integrations=integrations,rhs_evaluations=calls))
    except Exception as error:
        if last is not None:np.savez_compressed(output/'failed-last-rhs.npz',time=last['t'],state=last['y'])
        atomic(output/'FAILED.json',dict(validity='INVALID',error=repr(error),results=results,last_label=None if last is None else last['label'],integrations=integrations,rhs_evaluations=calls,provenance=provenance))
        atomic(output/'progress.json',dict(experiment='G188',state='failed',scope='continuous-reference diagnostic; no World ticks or learning',updated_unix=time.time(),error=repr(error),integrations=integrations,rhs_evaluations=calls));raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seal',type=Path,required=True);a=p.parse_args();run(a.input,a.output,a.seal)
