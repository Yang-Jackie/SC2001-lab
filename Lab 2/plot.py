"""Summarize measured samples and plot medians with interquartile ranges."""
import csv
from collections import defaultdict
from pathlib import Path
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

def plot():
    groups = defaultdict(list)
    with (HERE / 'results.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            key = (row['experiment'], int(row['V']), int(row['E']), row['algorithm'])
            groups[key].append(float(row['elapsed_ms']))
    summary = []
    for (experiment, n, m, algorithm), values in sorted(groups.items()):
        q1, _, q3 = statistics.quantiles(values, n=4, method='inclusive')
        summary.append(dict(experiment=experiment, V=n, E=m, density=m/(n*(n-1)),
            algorithm=algorithm, samples=len(values), median_ms=statistics.median(values),
            q1_ms=q1, q3_ms=q3, min_ms=min(values), max_ms=max(values)))
    with (HERE / 'summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    titles = {'sparse_v': 'Sparse directed graphs: E = 4V',
              'dense_v': 'Dense directed graphs: density = 50%',
              'density': 'Increasing density: V = 1,500'}
    for experiment, title in titles.items():
        fig, ax = plt.subplots(figsize=(9, 5.4))
        for algorithm, label, color in [('matrix_array', 'Matrix + array', '#b45309'),
                                        ('list_heap', 'Lists + indexed heap', '#0369a1')]:
            rows = [r for r in summary if r['experiment'] == experiment and r['algorithm'] == algorithm]
            x = [100*r['density'] if experiment == 'density' else r['V'] for r in rows]
            ax.plot(x, [r['median_ms'] for r in rows], 'o-', color=color, label=label)
            ax.fill_between(x, [r['q1_ms'] for r in rows], [r['q3_ms'] for r in rows], color=color, alpha=.2)
        ax.set(title=title, xlabel='Directed edge density (%)' if experiment == 'density' else 'Vertices, V',
               ylabel='Algorithm elapsed time (ms)')
        ax.grid(alpha=.25)
        ax.legend()
        fig.text(.5, .015, f'Median of {rows[0]["samples"]} runs across 3 graphs; shading: 25th-75th percentiles', ha='center', fontsize=9)
        fig.tight_layout(rect=(0,.035,1,1))
        fig.savefig(HERE / f'{experiment}.png', dpi=180)
        plt.close(fig)
    print('Saved summary.csv and three charts.')

if __name__ == '__main__':
    plot()
