"""Verify saved research evidence and render figures; never run a simulation."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/research/2026-09'
# Editorial palette: neutral text, indigo emphasis, explicit dashed thresholds.
INK, MUTED, ACCENT, SECONDARY = '#111827', '#6B7280', '#6366F1', '#8B5CF6'
BORDER, SURFACE = '#E5E7EB', '#F9FAFB'


def verify():
    files = json.loads((OUT / 'evidence-manifest.json').read_text())['files']
    for name, expected in files.items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Evidence checksum mismatch: {name}')
    print(f'Verified {len(files)} saved evidence files. No experiment executed.')


def render():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED,
                         'axes.edgecolor': BORDER, 'axes.spines.top': False,
                         'axes.spines.right': False, 'savefig.facecolor': 'white'})
    audio = json.loads((ROOT / 'archive/run-logs/g183/first/result.json').read_text())
    reassignment = json.loads((ROOT / 'archive/run-logs/g191/first/result.json').read_text())
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), layout='constrained')
    fig.suptitle('Evidence snapshot · September 2026', fontsize=18, weight='bold')
    ax = axs[0]
    vals = list(audio['gates']['canonical']['contrasts'].values())
    ax.bar(['Bell', 'Dog', 'Rain'], vals, color=[ACCENT, MUTED, MUTED], width=.5)
    ax.axhline(.1, color=INK, ls='--', lw=1.2, label='Required for every contrast: 0.100')
    ax.axhline(0, color=BORDER, lw=1)
    for i, val in enumerate(vals):
        ax.text(i, val + .006, f'{val:.3f}', ha='center', va='bottom', weight='bold')
    ax.set_ylim(-.035, .18)
    ax.set_ylabel('Reciprocal selectivity contrast')
    ax.set_title('G183 · real audio\nSelectivity criterion not met', loc='left', pad=15)
    ax.legend(frameon=False, fontsize=9, loc='upper right')
    ax = axs[1]
    for label, marker, offset in [('A', 'o', -.08), ('B', 's', .08)]:
        for j, branch in enumerate(['acquisition', 'switch', 'continue', 'separated', 'frozen']):
            vals = np.array(reassignment['results'][label][branch]['differences'])
            ax.plot(np.full(len(vals), j+offset), vals, marker, color=ACCENT if label=='A' else MUTED,
                    ms=5, alpha=.8, label=f'Initially {label}' if j==0 else None)
    ax.axhline(0, color=INK, ls='--', lw=1)
    ax.set_xticks(range(5), ['Acquired', 'Opposite\nteaching', 'Continue', 'Separated', 'Frozen'])
    ax.set_ylim(-.21, .46)
    ax.set_ylabel('Preference D: original-source gain − other gain')
    ax.set_title('G191 · guided reference\nPreference reverses; return fails 10/10', loc='left', pad=15)
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    fig.savefig(OUT / 'evidence.png', dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(12, 3.1), layout='constrained')
    ax.set(xlim=(0, 12), ylim=(0, 3.1)); ax.axis('off')
    ax.text(.1, 2.82, 'A testable path from exposure to evidence', size=17, weight='bold')
    panels = [(.15, '01  INPUT', 'Measured sensory signals', 'Fixed transduction;\nno category-derived target'),
              (4.15, '02  MATERIAL', 'Local changes in bonds', 'Record state, dynamics\nand mechanical work'),
              (8.15, '03  READOUT', 'Physical response to a cue', 'Compare frozen, shuffled\nand retained-state controls')]
    for x, label, title, body in panels:
        ax.add_patch(FancyBboxPatch((x,.45),3.55,1.95,boxstyle='round,pad=.12',facecolor=SURFACE,edgecolor=BORDER))
        ax.text(x+.15,2.08,label,color=ACCENT,size=10,weight='bold')
        ax.text(x+.15,1.69,title,size=12,weight='bold')
        ax.text(x+.15,1.12,body,size=11,color=MUTED,linespacing=1.6)
    for x in [3.83,7.83]:
        ax.annotate('',xy=(x+.22,1.42),xytext=(x-.1,1.42),arrowprops={'arrowstyle':'->','color':MUTED})
    ax.text(.15,.05,'Experimental design, not a claim that the full sensory-learning path has been demonstrated.',size=10,color=MUTED)
    fig.savefig(OUT / 'method.png', dpi=180)
    plt.close(fig)
    print('Rendered evidence.png and method.png from saved measurements and declared scope.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Verify evidence only; do not render.')
    args = parser.parse_args()
    verify()
    if not args.verify:
        render()
