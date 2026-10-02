# NTU SC2001 Projects

This repository contains two algorithm design and analysis projects:

- **Lab 1/**: hybrid merge sort, implemented in Python and C++.
- **Lab 2/**: Dijkstra's algorithm using an adjacency matrix with an array priority queue, and adjacency lists with an indexed binary min-heap.

Python handles data generation, benchmarking and plotting. Lab 1 supports a Python backend and an optional C++ backend; Lab 2 implements both algorithms in C++.

## Setup

Clone the repository, then open a terminal in the cloned repository's root folder. Python 3.10 or newer is required. Lab 2 also requires a C++17-capable compiler. Lab 1's Python backend does not require a compiler.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the Python dependencies for both labs:

```bash
python -m pip install -r "Lab 1/requirements.txt"
```

The virtual environment is local to your machine and is not included in the repository. If your system names Python `python3`, use `python3` to create the environment.

## Running Lab 1

From the repository root, enter the lab folder and run the Python implementation:

```bash
cd "Lab 1"
python main.py
```

The program runs sanity examples and benchmarks hybrid merge sort over different input sizes. It displays the resulting plot and saves it in `Lab 1/outputs/`.

Choose which experiment to run by editing the function calls at the bottom of `main.py`:

- `plot_over_input_size(...)`: performance against input size.
- `plot_over_s(...)`: performance against insertion-sort threshold S.
- `compare_hybrid_merge(...)`: hybrid sort versus standard merge sort.

The default experiment uses 100 potentially large arrays. Reduce the dataset sizes in `main.py` for a shorter run.

### Optional C++ backend

While in the `Lab 1` folder, run:

```bash
python main.py -cpp
```

The `cppimport` package compiles and loads the C++ implementation. A compatible compiler must be installed; on Windows, this typically requires Microsoft Visual C++ Build Tools. If compilation or loading fails, the program reports the error and falls back to Python.

Return to the repository root before following the Lab 2 commands:

```bash
cd ..
```

## Running Lab 2

All commands in this section start in the repository root. Install a C++17-capable compiler and ensure `g++` is available in your terminal. On Windows, a MinGW-w64 toolchain provides `g++`; on macOS or Linux, use your system's C++ toolchain.

### Build

On Windows:

```bash
g++ -O2 -std=c++17 -Wall -Wextra -static "Lab 2/dijkstra.cpp" -o "Lab 2/dijkstra.exe"
```

On macOS or Linux:

```bash
g++ -O2 -std=c++17 -Wall -Wextra "Lab 2/dijkstra.cpp" -o "Lab 2/dijkstra"
```

The executable is built locally and is not included in the repository.

### Demonstration and tests

On Windows PowerShell:

```powershell
& "./Lab 2/dijkstra.exe" demo
& "./Lab 2/dijkstra.exe" test
```

On macOS or Linux:

```bash
"./Lab 2/dijkstra" demo
"./Lab 2/dijkstra" test
```

The demonstration prints distances and reconstructed paths for both implementations. The tests check known examples, invalid inputs, disconnected graphs, zero-weight edges, overflow and agreement with Bellman-Ford on small random graphs.

To also check graph generation and benchmark integration on either platform:

```bash
python "Lab 2/benchmark.py" --check
```

### Benchmarks and plots

With the virtual environment activated, run:

```bash
python "Lab 2/benchmark.py"
python "Lab 2/plot.py"
```

Both implementations use the same generated graphs and source vertices. The benchmark compares increasing vertex counts on sparse and dense graphs, and increasing density at a fixed vertex count.

Results are saved directly in `Lab 2/`:

- `results.csv`: raw elapsed-time measurements.
- `summary.csv`: medians, quartiles and minimum/maximum timings.
- `sparse_v.png`, `dense_v.png`, `density.png`: comparison charts.
- `machine.json`: environment details for the benchmark run.

Rerunning these commands replaces the saved results and charts with measurements from your machine.

## Further details

- [Lab 1 README](Lab%201/README.md): sorting implementation and experiments.
- [Lab 2 README](Lab%202/README.md): custom graph input, timing boundaries and algorithm conventions.
- [Slide handoff](Lab%202/SLIDES_HANDOFF.md): pseudocode, complexity analysis, measured findings and TA questions for slide creation.
