"""Generate paired directed graphs, call the C++ timer, and record raw results.
All generation, file I/O and representation construction are outside the timer.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SEEDS = (2001, 2002, 2003)


def generate(n, m, seed, destination):
    if n < 2 or not n <= m <= n * (n - 1):
        raise ValueError('Require V <= E <= V(V-1)')
    rng = random.Random(seed)
    # A directed Hamiltonian cycle makes every source reach all vertices.
    ring = {u * (n - 1) + ((u + 1) % n if (u + 1) % n < u else (u + 1) % n - 1)
            for u in range(n)}
    chosen = list(ring)
    for edge_id in rng.sample(range(n * (n - 1)), m):
        if len(chosen) == m:
            break
        if edge_id not in ring:
            chosen.append(edge_id)
            if len(chosen) == m:
                break
    source = rng.randrange(n)
    with open(destination, 'w', encoding='ascii') as f:
        f.write(f'{n} {m} {source}\n')
        for edge_id in sorted(chosen):
            u, offset = divmod(edge_id, n - 1)
            v = offset if offset < u else offset + 1
            f.write(f'{u} {v} {rng.randrange(101)}\n')
    return source


def benchmark(executable, trials):
    cases = [('sparse_v', n, 4 * n) for n in (250, 500, 1000, 2000, 4000)]
    cases += [('dense_v', n, round(.5 * n * (n - 1))) for n in (250, 500, 1000, 1500, 2000)]
    cases += [('density', 1500, round(d * 1500 * 1499)) for d in (.002, .01, .05, .2, .5, .9)]
    fields = ['experiment', 'V', 'E', 'density', 'seed', 'source', 'algorithm', 'trial', 'order', 'elapsed_ms']
    with tempfile.TemporaryDirectory() as temp, (HERE / 'results.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for experiment, n, m in cases:
            for seed in SEEDS:
                graph, times = Path(temp) / 'graph.txt', Path(temp) / 'times.csv'
                source = generate(n, m, seed, graph)
                subprocess.run([str(executable), 'run', str(graph), str(trials), str(times)], check=True)
                with times.open(newline='') as f:
                    for row in csv.DictReader(f):
                        writer.writerow(dict(experiment=experiment, V=n, E=m,
                            density=m/(n*(n-1)), seed=seed, source=source, **row))
                out.flush()
            print(f'{experiment}: V={n}, E={m}', flush=True)
    metadata = dict(platform=platform.platform(), python=platform.python_version(),
        processor=platform.processor(), logical_processors=os.cpu_count(),
        compiler='GCC 14.2.0 MinGW-W64 x86_64-ucrt-posix-seh',
        flags='-O2 -std=c++17 -Wall -Wextra -static', seeds=SEEDS,
        trials_per_graph=trials, warmup_pairs=2,
        timing='std::chrono::steady_clock elapsed milliseconds; algorithm call only, including working-vector/heap allocation and initialization, excluding result destruction',
        graphs='directed simple graphs, no loops, mandatory directed cycle, remaining arcs sampled uniformly without replacement, weights uniformly 0..100')
    (HERE / 'machine.json').write_text(json.dumps(metadata, indent=2)+'\n')


def check(executable):
    subprocess.run([str(executable), 'test'], check=True)
    with tempfile.TemporaryDirectory() as temp:
        a, b, times = [Path(temp) / name for name in ('a.txt', 'b.txt', 'times.csv')]
        for m in (4, 6, 12):
            generate(4, m, 2001, a)
            generate(4, m, 2001, b)
            assert a.read_bytes() == b.read_bytes(), 'Seed reproducibility'
            lines = a.read_text().splitlines()
            edges = [tuple(map(int, line.split())) for line in lines[1:]]
            assert len(edges) == m and len({(u, v) for u, v, w in edges}) == m
            assert all(0 <= u < 4 and 0 <= v < 4 and u != v and 0 <= w <= 100 for u, v, w in edges)
            subprocess.run([str(executable), 'run', str(a), '2', str(times)], check=True)
            assert len(list(csv.DictReader(times.open()))) == 4
    print('PASS: graph counts, endpoints, unique arcs, weights, reproducibility and timer integration')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=HERE / ('dijkstra.exe' if os.name == 'nt' else 'dijkstra'))
    parser.add_argument('--trials', type=int, default=9)
    parser.add_argument('--check', action='store_true', help='Run correctness and generator integration checks without full experiments')
    args = parser.parse_args()
    if args.trials < 1:
        parser.error('trials must be positive')
    if args.check:
        check(args.exe.resolve())
    else:
        benchmark(args.exe.resolve(), args.trials)
