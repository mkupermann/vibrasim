"""Render the completed fixed L0 result; no training or parameter selection."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
result = json.loads((ROOT / 'archive/run-logs/l0/2026-09-16-observed-001/result.json').read_text())
fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.5), sharey=True)
fig.patch.set_facecolor('#fafafa')
panels = [
    ('Phase A: Vergleich der fünf Varianten',
     ['K1', 'Speicher\ngesperrt', 'Feedback\nvertauscht', 'Zufall', 'Einfache\nErfahrung'],
     [result['descriptive'][arm]['a'] for arm in ('full', 'frozen', 'shuffled', 'uniform', 'nearest')]),
    ('K1: Verhalten vor und nach dem Aufgabenwechsel',
     ['A vor\nTraining', 'A nach\nPhase A', 'B vor\nPhase B', 'B nach\nPhase B', 'A nach\nPhase B'],
     [result['descriptive']['full'][stage] for stage in ('initial_a', 'a', 'b_before', 'b', 'a_after_b')])]
for ax, (title, labels, stages) in zip(axes, panels):
    ax.set_title(title, fontsize=11, loc='left', pad=14)
    for index, stage in enumerate(stages):
        ax.scatter(index + np.linspace(-.14, .14, 30), stage['values'], s=15,
                   color='#59758c', alpha=.5, edgecolors='none', label='Einzelne Seeds' if index == 0 else None)
        ax.errorbar(index, stage['mean'], yerr=2.045229642*stage['sd']/np.sqrt(30),
                    fmt='D', color='#17365d', capsize=5, markersize=6,
                    label='Mittelwert mit 95%-t-Intervall' if index == 0 else None)
    ax.axhline(.5, color='#a54353', linestyle='--', linewidth=1.3, label='Absolute Lern-/Umlernschwelle 0,50')
    ax.axhline(0, color='#cccccc', linewidth=.6)
    ax.set_xticks(range(5), labels, fontsize=9)
    ax.set_ylim(-1.03, 1.03)
    ax.set_xlim(-.5, 4.5)
    ax.grid(axis='y', alpha=.18)
    ax.spines[['top', 'right']].set_visible(False)
axes[0].set_ylabel('Mittlerer Prüfreward J pro Seed (−1 bis +1)')
fig.suptitle('L0 · 30 Seeds · Urteil NULL: absolute Mindestleistung verfehlt', x=.07,
             ha='left', fontsize=14, fontweight='bold')
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .075), ncol=3, frameon=False, fontsize=9)
fig.text(.07, .035, 'Quelle: eingefrorener Lauf 2026-09-16-observed-001 · G176/G177 · 200 Prüfkontexte je Seed und Aufgabe', fontsize=8, color='#555555')
fig.subplots_adjust(top=.82, bottom=.25, left=.07, right=.98, wspace=.12)
for extension in ('png', 'svg'):
    fig.savefig(ROOT / f'docs/validation/l0-20260916-results.{extension}', dpi=160, facecolor=fig.get_facecolor())
