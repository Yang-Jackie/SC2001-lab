# Project 2: Dijkstra's Algorithm

The C++17 program implements both required algorithms itself; Python generates graphs, runs experiments and plots results. No shortest-path or heap library is used. All commands below start at the repository root in PowerShell.

## Build and correctness tests

A C++17 compiler and Python 3.10+ are required. Matplotlib is needed only for plotting and is already in the shared environment. A fresh environment can install it with `python -m pip install matplotlib`.

```powershell
# Compiler on this machine (or substitute g++ from your PATH):
& 'C:/Program Files/CodeBlocks/MinGW/bin/g++.exe' -O2 -std=c++17 -Wall -Wextra -static 'Lab 2/dijkstra.cpp' -o 'Lab 2/dijkstra.exe'
& './Lab 2/dijkstra.exe' test
& './Lab 2/dijkstra.exe' demo
& './.venv/Scripts/python.exe' 'Lab 2/benchmark.py' --check
```

On Linux/macOS, use `g++ -O2 -std=c++17 -Wall -Wextra 'Lab 2/dijkstra.cpp' -o 'Lab 2/dijkstra'` and run `'./Lab 2/dijkstra' test` or `demo`. The benchmark automatically selects the platform filename. Static linking on Windows avoids missing MinGW runtime DLLs.

`test` checks the known demo, empty/disconnected and singleton graphs, zero weights, invalid sources/endpoints/weights, duplicate arcs, self-loops, maximum supported finite distance, and overflow. It compares both implementations against independent Bellman-Ford on 300 deterministic random graphs (1-18 vertices), from every source. Every reachable reconstructed path is checked for correct endpoints, existing edges and total weight. Unreachable paths must be empty. Tests throw on failure even with compiler optimizations enabled.

`benchmark.py --check` also verifies generated edge counts (including exactly the cycle and a complete graph), unique arcs, endpoint/weight ranges, seed reproducibility and C++ file/timer integration. It does not overwrite the saved experiment results.

## Demonstration and custom graphs

```powershell
& './Lab 2/dijkstra.exe' demo
& './Lab 2/dijkstra.exe' run 'Lab 2/demo_graph.txt' 9 'Lab 2/demo_timings.csv'
```

The second command optionally times a file; it creates a new CSV. Format: first line `V E source`, then exactly E lines `u v weight`. Vertices are numbered 0 through V-1. Directed simple graphs are used: one ordered pair (u,v) counts as one edge; no self-loops or duplicate arcs. To represent an undirected edge, supply both arcs; each counts toward E. Density is E/[V(V-1)]. Graphs need not be connected. Missing matrix entries use -1, so zero-weight edges remain distinct.

Weights and finite distances use signed 64-bit integers; supported range is 0 to INT64_MAX-1. INT64_MAX means infinity. Negative weights and the reserved infinity value are rejected. Before an explored relaxation to an unsettled vertex adds a weight, it checks for overflow and throws if the candidate is outside the supported range. This is deliberately conservative: even if another route would be finite, an overflowing explored candidate rejects the run. It never silently wraps or treats overflow as unreachable. Invalid inputs cause a diagnostic and nonzero exit. Allocation failures are also reported. Use the public validated algorithm entry points; the `_core` functions assume a constructed Graph and a validated source.

Both algorithms return distance and predecessor arrays. `path(result, source, target)` reconstructs the path, returns an empty vector for unreachable vertices and checks for predecessor cycles. Strict improvement updates avoid cycles on zero-weight ties; different equally short paths may be valid.

## Reproduce experiments and plots

```powershell
& './.venv/Scripts/python.exe' 'Lab 2/benchmark.py'
& './.venv/Scripts/python.exe' 'Lab 2/plot.py'
```

Alternatively use `python 'Lab 2/benchmark.py'` and `python 'Lab 2/plot.py'` with an environment containing Matplotlib. Generation/timing orchestration uses only Python's standard library. `--trials 9` is the default; `--exe 'Lab 2/dijkstra.exe'` can select another compiled binary. Running the benchmark replaces results.csv and machine.json; plotting replaces summary.csv and the three PNGs. Each graph is regenerated from seeds 2001, 2002, 2003. Graph files are temporary; the demo is retained.

Experiments: sparse E=4V at V=250,500,1000,2000,4000; 50%-dense at V=250,500,1000,1500,2000; fixed V=1500 at densities 0.2%,1%,5%,20%,50%,90%. A directed cycle guarantees every vertex is reachable. Remaining edges are sampled without replacement, with integer weights uniformly 0..100. Each graph/source is shared by both algorithms; two warm-up pairs precede nine measured pairs, alternating which algorithm runs first. See SLIDES_HANDOFF.md for the full methodology and limitations.

Timing uses C++ steady_clock elapsed milliseconds. Only each algorithm core call is timed, including distance/predecessor/settled/heap allocation and initialization. Input parsing, graph generation, constructing both representations, source/input validation, correctness checks, path reconstruction, result destruction, CSV output, Python/subprocess startup and plotting are excluded. Checked addition is an essential part of the algorithm and remains timed.

## Files to use

- `dijkstra.cpp`: both implementations, indexed binary heap, reconstruction, reference, tests and C++ timer.
- `benchmark.py`, `plot.py`: reproducible experiment and chart commands.
- `demo_graph.txt`: demonstration input.
- `results.csv`: all individual measured samples (864 rows for the default experiment).
- `summary.csv`: median, quartiles, minimum and maximum (32 rows).
- `sparse_v.png`, `dense_v.png`, `density.png`: medians with interquartile shading.
- `machine.json`: recorded runtime/compiler/machine details.
- `SLIDES_HANDOFF.md`: complete slide content and TA questions; no slides were created.

The comparison driver holds both representations and an edge list simultaneously, so its total storage is O(V^2+E). This is distinct from the representation-specific space analysis. The largest matrix uses 128,000,000 bytes of weight payload (V=4000); dense cases stop at V=2000 to limit adjacency-list and edge-list memory. No peak-memory measurement is claimed.
