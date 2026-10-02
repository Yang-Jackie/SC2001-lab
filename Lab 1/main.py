from pathlib import Path
import argparse
import math
import time
import data_generator
import sorting_interface
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).resolve().parent / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)
from matplotlib.ticker import StrMethodFormatter

def plot_comparisons_and_durations(
    x_values,
    comparisons,
    durations,
    *,
    axes=None,
    title=None,
    x_label="Input size",
    comparison_label="Comparisons",
    duration_label="Duration",
    comparison_style=None,
    duration_style=None,
):
    x_values = list(x_values)
    comparisons = list(comparisons)
    durations = list(durations)

    if not (
        len(x_values)
        == len(comparisons)
        == len(durations)
    ):
        raise ValueError(
            "x_values, comparisons, and durations "
            "must have equal lengths"
        )

    if axes is None:
        fig, ax_comparisons = plt.subplots(figsize=(10, 6))
        ax_duration = ax_comparisons.twinx()
    else:
        ax_comparisons, ax_duration = axes
        fig = ax_comparisons.figure

    comp_style = {
        "color": "tab:blue",
        "marker": "o",
    }
    time_style = {
        "color": "tab:red",
        "marker": "x",
    }

    if comparison_style:
        comp_style.update(comparison_style)

    if duration_style:
        time_style.update(duration_style)

    comparison_line, = ax_comparisons.plot(
        x_values,
        comparisons,
        label=comparison_label,
        **comp_style,
    )

    duration_line, = ax_duration.plot(
        x_values,
        durations,
        label=duration_label,
        **time_style,
    )

    ax_comparisons.set_xlabel(x_label)
    ax_comparisons.set_ylabel("Number of comparisons")
    ax_duration.set_ylabel("Duration (seconds)")
    ax_comparisons.grid(alpha=0.3)

    if title:
        ax_comparisons.set_title(title)

    return (
        fig,
        (ax_comparisons, ax_duration),
        (comparison_line, duration_line),
    )

def merge_theoretical_comparisons(n):
    # Upper bound for merge sort: log2(n) levels, at most n comparisons each.
    return n * math.log2(n) if n > 1 else 0

def hybrid_theoretical_comparisons(n, S):
    # Worst case: insertion sort on n/S subarrays of size <= S costs at most
    # n(S-1)/2, plus log2(n/S) merge levels of at most n comparisons each.
    if n <= S:
        return n * (n - 1) / 2
    return n * math.log2(n / S) + n * S

HYBRID_THEORETICAL_LABEL = r"$n\log_2(n/S) + nS$"
MERGE_THEORETICAL_LABEL = r"$n\log_2 n$"

def sanity_check():
    arr = [5, 2, 9, 1, 5, 6]
    print(f"Original array: {arr}")
    sorted_arr, comparisons, _ = sorting_interface.hybrid_sort(arr, 3)
    print(f"Original array after sorting: {arr}")
    print(f"Sorted array: {sorted_arr}\nComparisons made: {comparisons}")

    arr = data_generator.generate(20, 100)
    print(f"Original array: {arr}")
    sorted_arr, comparisons, _ = sorting_interface.hybrid_sort(arr, 3)
    print(f"Original array after sorting: {arr}")
    print(f"Sorted array: {sorted_arr}\nComparisons made: {comparisons}")

def benchmark(dataset, S, log_progress: bool = False):
    input_sizes = []
    comparisons = []
    durations = []

    start = time.perf_counter()

    for i, arr in enumerate(dataset):
        input_sizes.append(len(arr))

        if (i + 1) % 10 == 0:
            print(f"Processing the {i+1}-th array")

        _, comp, duration = sorting_interface.hybrid_sort(arr, S)
        comparisons.append(comp)
        durations.append(duration)

    end = time.perf_counter()
    print(f"Time taken to process {len(input_sizes)} arrays: {end - start:.2f} seconds")

    return input_sizes, comparisons, durations

def plot_over_input_size(dataset, S, show_plot: bool = False):
    input_sizes, comparisons, durations = benchmark(dataset, S, log_progress = True)

    fig, (ax_comparisons, ax_duration), lines = plot_comparisons_and_durations(
        input_sizes,
        comparisons,
        durations,
        title=f"Hybrid Merge Sort vs Input Size (S={S}) on {len(input_sizes)} sample",
        x_label="Input size",
        duration_style={
            "marker": None
        },
    )

    theoretical_line, = ax_comparisons.plot(
        input_sizes,
        [merge_theoretical_comparisons(n) for n in input_sizes],
        color="black",
        linestyle="--",
        label=f"Merge sort theoretical: {MERGE_THEORETICAL_LABEL}",
    )

    hybrid_theoretical_line, = ax_comparisons.plot(
        input_sizes,
        [hybrid_theoretical_comparisons(n, S) for n in input_sizes],
        color="tab:blue",
        linestyle=":",
        label=f"Hybrid theoretical: {HYBRID_THEORETICAL_LABEL}",
    )

    ax_comparisons.xaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )
    ax_comparisons.yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    legend_lines = [*lines, theoretical_line, hybrid_theoretical_line]

    ax_comparisons.legend(
        legend_lines,
        [line.get_label() for line in legend_lines],
    )

    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "plot_over_n.png", dpi=300)
    if show_plot: plt.show()

def plot_over_s(n_samples: int, sizes: list, thresholds: list, show_plot: bool = False):
    n_cols = 2
    n_rows = math.ceil(len(sizes) / n_cols)

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(12, 5 * n_rows)
    )

    axes = axes.flatten()

    time_start = time.perf_counter()

    for ax, size in zip(axes, sizes):
        dataset = list(data_generator.dataset(n_samples, size))

        average_comparisons = []
        average_durations = []
        sample_durations = [[] for _ in range(n_samples)]

        for s in thresholds:
            print(f"Processing size={size}, threshold={s}...")
            _, comparisons, durations = benchmark(dataset, s)

            average_comparisons.append(
                sum(comparisons) / len(comparisons)
            )
            average_durations.append(
                sum(durations) / len(durations)
            )

            for sample_index, duration in enumerate(durations):
                sample_durations[sample_index].append(duration)

        ax_duration = ax.twinx()
        sample_line = None

        for sample_index, durations in enumerate(sample_durations):
            line, = ax_duration.plot(
                thresholds,
                durations,
                color='tab:orange',
                alpha=0.2,
                linewidth=0.8,
                label='Sample durations' if sample_index == 0 else None
            )
            if sample_index == 0:
                sample_line = line

        _, _, average_lines = plot_comparisons_and_durations(
            thresholds,
            average_comparisons,
            average_durations,
            axes=(ax, ax_duration),
            title=f"n = {size:,}",
            x_label="Threshold S",
        )

        legend_lines = [
            average_lines[0],
            sample_line,
            average_lines[1],
        ]

        ax.legend(
            legend_lines,
            [line.get_label() for line in legend_lines],
        )

    print(
        f"Time taken: "
        f"{time.perf_counter() - time_start:.2f} seconds"
    )

    for ax in axes[len(sizes):]:
        ax.remove()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plot_over_s.png", dpi=300)
    if show_plot: plt.show()

def compare_hybrid_merge(dataset, S, show_plot: bool = False):

    input_sizes, hybrid_comparisons, hybrid_durations = benchmark(dataset, S)
    _, merge_comparisons, merge_durations = benchmark(dataset, 1)

    fig, (ax_comparisons, ax_duration) = plt.subplots(
        1,
        2,
        figsize=(14, 6),
    )

    ax_comparisons.plot(
        input_sizes,
        hybrid_comparisons,
        color="tab:blue",
        marker="o",
        label=f"Hybrid sort (S={S})",
    )
    ax_comparisons.plot(
        input_sizes,
        merge_comparisons,
        color="tab:orange",
        marker="s",
        label="Merge sort",
    )
    ax_comparisons.plot(
        input_sizes,
        [hybrid_theoretical_comparisons(n, S) for n in input_sizes],
        color="tab:blue",
        linestyle="--",
        label=f"Hybrid theoretical: {HYBRID_THEORETICAL_LABEL}",
    )
    ax_comparisons.plot(
        input_sizes,
        [merge_theoretical_comparisons(n) for n in input_sizes],
        color="black",
        linestyle="--",
        label=f"Merge sort theoretical: {MERGE_THEORETICAL_LABEL}",
    )

    ax_duration.plot(
        input_sizes,
        hybrid_durations,
        color="tab:blue",
        marker="o",
        label=f"Hybrid sort (S={S})",
    )
    ax_duration.plot(
        input_sizes,
        merge_durations,
        color="tab:orange",
        marker="s",
        label="Merge sort",
    )

    ax_comparisons.set_title("Number of comparisons")
    ax_comparisons.set_xlabel("Input size, n")
    ax_comparisons.set_ylabel("Number of key comparisons")

    ax_duration.set_title("Duration")
    ax_duration.set_xlabel("Input size, n")
    ax_duration.set_ylabel("Runtime (seconds)")

    for ax in (ax_comparisons, ax_duration):
        ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.grid(alpha=0.3)
        ax.legend()

    ax_comparisons.yaxis.set_major_formatter(
        StrMethodFormatter("{x:,.0f}")
    )

    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "plot_hybrid_vs_merge.png", dpi=300)
    if show_plot: plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-cpp",
        "--cpp",
        action="store_true",
        help="Use the C++ sorting implementation",
    )
    args = parser.parse_args()

    sorting_interface.select_backend(use_cpp=args.cpp)

    sanity_check()

    dataset = list(data_generator.dataset(100))

    # plot_over_input_size(dataset, S=32, show_plot=True)

    # plot_over_s(30, [1000, 100_000, 10_000_000], [4, 8, 16, 32, 64, 128, 256])

    S = 64
    compare_hybrid_merge(dataset, S)
