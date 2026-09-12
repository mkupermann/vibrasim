"""Render saved audiovisual evidence. No training or material integration."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import wave
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from render_research_overview import ROOT, OUT, INK, MUTED, ACCENT, BORDER, verify


def main():
    verify()
    base = ROOT / 'archive/run-logs/mm1/20260912-024636-605403'
    mm1 = json.loads((base / 'result.json').read_text())
    mm2 = json.loads((ROOT / 'archive/run-logs/mm2/20260912-030202-607396/result.json').read_text())
    mm3 = json.loads((ROOT / 'archive/run-logs/mm3/20260912-first/result.json').read_text())
    source = OUT / 'reference-source/vibrasim2/learning.py'
    spec = importlib.util.spec_from_file_location('archived_learning', source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    encoder = module.SensoryPorts(module.LearningConfig(**mm1['config']))
    strength = np.asarray(mm1['arms']['trained']['strength'])
    initial_strength = strength.copy()
    clips = {}
    for split, count in [('train', 18), ('test', 9)]:
        clips[split] = []
        for i in range(count):
            with np.load(base / f'{split}-{i:03d}.npz', allow_pickle=False) as a:
                clips[split].append((a['frames'].copy(), a['audio'].copy()))
    # Labels are used only to verify archived evaluator outputs, never for readout.
    trainmeta = [v for v in mm1['clips'] if v['split']=='train']
    candidates=[]
    for label in mm1['candidates']:
        j=next(i for i,v in enumerate(trainmeta) if v['label']==label)
        candidates.append(encoder.encode(clips['train'][j][0][0],np.zeros(1600))[1][:64])
    discrepancy=0.0
    for j,row in enumerate(v for v in mm1['trials'] if v['arm']=='retained'):
        responses=[]
        for f in range(10):
            x,_=encoder.encode(np.zeros((32,32)),clips['test'][j][1][f*1600:(f+1)*1600])
            responses.append((x@strength/(mm1['config']['leak']+strength.sum(axis=0)))[:64])
        _,scores=module.retrieval_score(np.mean(responses,axis=0),candidates,mm1['candidates'].index(row['expected']))
        discrepancy=max(discrepancy,float(np.max(np.abs(np.asarray(scores)-row['candidate_similarities']))))
    if discrepancy>1e-12: raise ValueError('Reconstructed readout disagrees with saved retained probes.')
    (OUT/'audiovisual-replay-provenance.json').write_text(json.dumps({
        'scope':'Saved synthetic inputs and aggregate history; reconstructed equilibrium response from final state. No learning updates.',
        'source_result':'archive/run-logs/mm1/20260912-024636-605403/result.json',
        'state':'arms/trained is the final post-hold matrix; no additional retention decay applied',
        'compared_retained_trials':9,'maximum_similarity_discrepancy':discrepancy,
        'individual_training_bond_trajectories_available':False,'duration_seconds':32
    },indent=2)+'\n')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.edgecolor': BORDER, 'savefig.facecolor': 'white'})
    fig, axs = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
    names = ['trained', 'retained', 'frozen', 'erased', 'shuffled']
    axs[0].bar(range(5), [mm1['accuracies'][n] for n in names], color=[ACCENT, ACCENT, MUTED, MUTED, MUTED])
    axs[0].set_xticks(range(5), ['Trained', 'Retained', 'Frozen', 'Erased', 'Shuffled'], rotation=35, ha='right')
    axs[0].set_ylim(0, 1.18); axs[0].set_ylabel('Forced-choice credit')
    axs[0].axhline(1/3, ls='--', color=INK, lw=1)
    axs[0].set_title('MM1 · synthetic pairs\nDesigned association works', loc='left')
    vals = [mm2['summary'][n]['cosine_similarities'][0] for n in ['before', 'trained']]
    axs[1].bar(['Before exposure', 'After exposure'], vals, color=[MUTED, ACCENT])
    for j, v in enumerate(vals): axs[1].text(j, v+.02, f'{v:.3f}', ha='center')
    axs[1].set_ylim(0, 1.18); axs[1].set_ylabel('Similarity to previous bell image')
    axs[1].set_title('MM2 · real bell video\nBell already ranked first before', loc='left')
    for name in names:
        axs[2].plot([c['exposure_seconds'] for c in mm3['checkpoints']],
                    [c['arms'][name]['accuracy'] for c in mm3['checkpoints']],
                    marker='o', label=name, color=ACCENT if name=='trained' else MUTED, alpha=.65)
    axs[2].set_ylim(0, 1.18); axs[2].set_xlabel('Total exposure (seconds)')
    axs[2].set_ylabel('Test forced-choice credit')
    axs[2].set_title('MM3 · real-video transfer\nAll five conditions remain at 1/3', loc='left')
    axs[2].text(15, .42, 'All five curves overlap', ha='center', color=MUTED, fontsize=9)
    fig.suptitle('Three audiovisual studies · three different conclusions', fontsize=16, weight='bold')
    fig.savefig(OUT / 'audiovisual-results.png', dpi=170); plt.close(fig)

    fig, axs = plt.subplots(2, 2, figsize=(10, 6), layout='constrained')
    title = fig.suptitle('', fontsize=15, weight='bold')
    image = axs[0,0].imshow(np.zeros((32,32)), vmin=0, vmax=1, cmap='gray')
    response = axs[0,1].imshow(np.zeros((8,8)), vmin=0, vmax=1, cmap='gray')
    for ax in axs[0]: ax.set_xticks([]); ax.set_yticks([])
    axs[0,1].set_title('Visual-port response\nReconstructed frozen equilibrium', fontsize=11)
    wave_line, = axs[1,0].plot(np.arange(1600)/16000, np.zeros(1600), color=ACCENT, lw=.7)
    axs[1,0].set(xlim=(0,.1), ylim=(-1,1), xlabel='Audio frame (seconds)', ylabel='PCM amplitude')
    axs[1,0].set_title('Saved synthetic audio', fontsize=11)
    history = mm1['history']; times = np.array([v['time'] for v in history]); masses=np.array([v['spring_mass'] for v in history])
    trace, = axs[1,1].plot([], [], color=ACCENT, marker='.', ms=4)
    axs[1,1].set(xlim=(0,32), ylim=(0,90), xlabel='Experiment time (seconds)', ylabel='Summed spring strength')
    axs[1,1].set_title('Measured aggregate history\nNo individual bond trajectories recorded', fontsize=11)
    note=axs[0,1].text(.5,.5,'',transform=axs[0,1].transAxes,color='white',ha='center',va='center',fontsize=10)
    audio_parts=[a for _,a in clips['train']]+[np.zeros(5*16000)]+[a for _,a in clips['test']]
    audio=np.concatenate(audio_parts)
    assert len(audio)==32*16000
    def update(frame):
        sec=frame/10; within=frame%10
        if sec<18:
            i=frame//10; frames,sound=clips['train'][i]; phase=f'Paired exposure {i+1}/18'
            axs[0,0].set_title('Saved visual input · supplied during exposure',fontsize=11)
            visual=frames[within]; output=np.zeros((8,8)); note.set_text('Training-time responses\nwere not recorded')
            signal=sound[within*1600:(within+1)*1600]
        elif sec<23:
            phase='Silent hold · 5 seconds';visual=np.zeros((32,32));output=np.zeros((8,8));signal=np.zeros(1600)
            axs[0,0].set_title('No sensory input during hold',fontsize=11);note.set_text('No training-time response\nreconstruction')
        else:
            i=(frame-230)//10;frames,sound=clips['test'][i];phase=f'Audio-only probe {i+1}/9'
            visual=frames[within];signal=sound[within*1600:(within+1)*1600]
            bands,_=encoder.encode(np.zeros((32,32)),signal)
            output=((bands@strength)/(mm1['config']['leak']+strength.sum(axis=0)))[:64].reshape(8,8)
            axs[0,0].set_title('Reference image · NOT supplied during probe',fontsize=11);note.set_text('')
        title.set_text(f'MM1 · synthetic saved-data replay | {phase} | {sec:.1f}s')
        image.set_data(visual);response.set_data(output);wave_line.set_ydata(signal)
        mask=times<=sec+1e-9;trace.set_data(times[mask],masses[mask])
        return image,response,wave_line,trace,title,note
    movie=FuncAnimation(fig,update,frames=320,interval=100,blit=False)
    encoders=subprocess.check_output(['ffmpeg','-hide_banner','-encoders'],stderr=subprocess.DEVNULL,text=True)
    codec='libx264' if 'libx264' in encoders else 'libopenh264'
    if codec not in encoders: raise RuntimeError('An H.264 ffmpeg encoder is required.')
    with tempfile.TemporaryDirectory(prefix='vibrasim-replay-') as tmp:
        silent=Path(tmp)/'silent.mp4';wav=Path(tmp)/'audio.wav'
        movie.save(silent,writer=FFMpegWriter(fps=10,codec=codec,extra_args=['-pix_fmt','yuv420p']),dpi=100)
        with wave.open(str(wav),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000)
            f.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(wav),'-c:v','copy','-c:a','aac','-shortest','-movflags','+faststart',str(OUT/'audiovisual-replay.mp4')],check=True)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-filter_complex','fps=3,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse','-loop','0',str(OUT/'audiovisual-replay.gif')],check=True)
    assert np.array_equal(strength,initial_strength)
    update(235);fig.savefig(OUT/'audiovisual-replay-still.png',dpi=140);plt.close(fig)
    print('Rendered audiovisual figures and 32-second replay. No learning updates executed.')


if __name__=='__main__': main()
