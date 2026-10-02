# Hybrid Merge Sort Benchmark

This project implements and benchmarks a hybrid merge sort algorithm. It uses
merge sort for large subarrays and switches to insertion sort when the subarray
size is at or below a chosen threshold, `S`.

The project is built around Python, which handles data generation,
benchmarking, plotting, and backend selection. The core sorting algorithm is
implemented in both Python and C++ (for faster experiments on large
datasets).

The program measures:

- Number of key comparisons
- Sorting duration
- Performance across different input sizes and threshold values
- Hybrid sort performance against standard merge sort

## Setup

Python 3.10 or newer is required.

```bash
# From the repository root
python -m venv .venv
```

Activate the virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r "Lab 1/requirements.txt"
```

## Running

Run the project using the Python implementation:

```bash
cd "Lab 1"
python main.py
```

Choose which experiment to run by using the function calls at the bottom
of `main.py`:

- `plot_over_input_size(...)` plots performance against input size.
- `plot_over_s(...)` plots performance against threshold `S`.
- `compare_hybrid_merge(...)` compares hybrid sort with merge sort.

Generated plots are saved in the `outputs` directory. If you encounter errors
when enabling C++, refer to the next section.

## C++ Implementation (Optional)

Python alone is enough to run the entire project. It does not require a C++
compiler, although large experiments will run more slowly.

To use the faster C++ sorting implementation, add the `-cpp` flag:

```bash
cd "Lab 1"
python main.py -cpp
```

The project loads and compiles the C++ implementation using the Python package
`cppimport`. If C++ compilation or loading fails, the program automatically
falls back to the Python implementation.

Using the C++ implementation requires a C++ compiler. On Windows, you may be
prompted to install Microsoft Visual C++ (MSVC) if the necessary build tools
are missing. Go ahead with the MSVC installation to use C++ for this project.

## Files

- `main.py` contains the benchmarking and plotting code.
- `algorithms.py` contains the Python sorting implementation.
- `algorithms_cpp.cpp` contains the C++ sorting implementation.
- `sorting_interface.py` selects the Python or C++ backend.
- `data_generator.py` generates random datasets.

Plots always go to Lab 1/outputs/, regardless of the current working directory.
The existing charts at the lab folder root are preserved historical results.

