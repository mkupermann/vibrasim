"""Animate archived measurements, never physics; presentation time is arbitrary."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from render_research_overview import ROOT, OUT, INK, MUTED, ACCENT, BORDER, verify


def main():
    verify()
    sources = {'mm3': 'archive/run-logs/mm3/20260912-first/result.json',
               'g191': 'archive/run-logs/g191/first/result.json'}
    data = {k: json.loads((ROOT / v).read_text()) for k, v in sources.items()}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.edgecolor': BORDER})
    encoders = subprocess.check_output(['ffmpeg', '-hide_banner', '-encoders'], text=True, stderr=subprocess.DEVNULL)
    codec = 'libx264' if 'libx264' in encoders else 'libopenh264'
    if codec not in encoders:
        raise RuntimeError('H.264 encoder required')
    manifest = {'scope': 'Silent staged presentations of saved measurements. No simulation, training, interpolation, or new experiment.', 'videos': {}}
    for study, stages in [('mm3', 3), ('g191', 5)]:
        with tempfile.TemporaryDirectory() as tmp:
            for stage in range(stages):
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.subplots_adjust(left=.12, right=.96, bottom=.36, top=.76)
                fig.text(.06, .94, 'SAVED EVIDENCE  /  RESULT WALKTHROUGH', color=MUTED, fontsize=11)
                if study == 'mm3':
                    fig.text(.06, .87, 'Real-video transfer: exposure did not improve retrieval', fontsize=17, weight='bold')
                    names = ['trained', 'retained', 'frozen', 'erased', 'shuffled']
                    cp = data[study]['checkpoints'][stage]
                    vals = [cp['arms'][n]['accuracy'] for n in names]
                    ax.bar(names, vals, color=[ACCENT, ACCENT, MUTED, MUTED, MUTED])
                    ax.axhline(1/3, color=INK, ls='--', label='Chance reference: 1/3')
                    ax.set(ylim=(0, 1), ylabel='Forced-choice credit', title=f"Measured checkpoint: {cp['exposure_seconds']:g} seconds of exposure")
                    for j, v in enumerate(vals): ax.text(j, v+.025, f'{v:.3f}', ha='center')
                    ax.legend(frameon=False, loc='upper right')
                    note = 'Six training recordings; three test recordings. All five conditions score 1/3.\nSmall, confounded sample: this is a negative result on this task, not an impossibility proof.'
                else:
                    fig.text(.06, .87, 'Mechanical preference can reverse; return to rest fails', fontsize=17, weight='bold')
                    branches = ['acquisition', 'switch', 'continue', 'separated', 'frozen']
                    for label, offset, marker, color in [('A', -.08, 'o', ACCENT), ('B', .08, 's', MUTED)]:
                        for j, branch in enumerate(branches[:stage+1]):
                            vals = data[study]['results'][label][branch]['differences']
                            ax.plot(np.full(len(vals), j+offset), vals, marker, color=color,
                                    alpha=.8, label=f'Initially {label}' if j == 0 else None)
                    ax.axhline(0, color=INK, ls='--')
                    ax.set(ylim=(-.21, .46), xlim=(-.5, 4.5), ylabel='Preference: original gain − other gain')
                    ax.set_xticks(range(5), ['Acquired', 'Opposite\nteaching', 'Continued\nteaching', 'Separated', 'Frozen'])
                    ax.legend(frameon=False, loc='upper left')
                    note = 'Guided reference model; dots show saved read probes, not independent repeats.\nBranches are sibling state copies, not a continuous sequence. Return fails at all 10 endpoints.'
                fig.text(.06, .18, note, fontsize=11, linespacing=1.6)
                fig.text(.06, .07, f'{study.upper()} | Silent presentation; reveal timing is arbitrary, not simulation time.\nNo new run. Methods and original measurements are linked in the README.', fontsize=10, color=MUTED)
                fig.savefig(Path(tmp)/f'frame-{stage:02d}.png', dpi=100)
                if stage == stages-1: fig.savefig(OUT/f'{study}-results-still.png', dpi=100)
                plt.close(fig)
            dest = OUT/f'{study}-results.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-framerate','1/4','-i',str(Path(tmp)/'frame-%02d.png'),'-c:v',codec,'-r','10','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)], check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-filter_complex','fps=1,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse','-loop','0',str(OUT/f'{study}-results.gif')], check=True)
            manifest['videos'][study] = {'source': sources[study], 'source_sha256': hashlib.sha256((ROOT/sources[study]).read_bytes()).hexdigest(), 'stages': stages, 'seconds_per_stage': 4,
                                        'output_sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}
    (OUT/'result-videos-provenance.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
