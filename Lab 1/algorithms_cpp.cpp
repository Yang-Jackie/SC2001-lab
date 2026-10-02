/*
<%
setup_pybind11(cfg)
cfg["compiler_args"] += ["-O2", "-std=c++20"]
%>
*/

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>
#include <utility>
#include <cstdint>

namespace py = pybind11;

using RunResult = std::tuple<std::vector<int>, int, double>;

int _insertion_sort(std::vector<int>& arr, int l, int r) {
    int comparisons = 0;

    for (int i = l+1; i < r; ++i) {
        int j = i;
        while (j > l && arr[j] < arr[j - 1]) {
            std::swap(arr[j], arr[j - 1]);
            --j;
            ++comparisons; // Count the comparison that succeeded
        }
        if (j > l) {
            ++comparisons; // Count the comparison that failed the while condition
        }
    }

    return comparisons;
}
int _merge(std::vector<int>& arr, int l, int mid, int r) {
    std::vector<int> left(arr.begin() + l, arr.begin() + mid);
    std::vector<int> right(arr.begin() + mid, arr.begin() + r);
    std::vector<int>::iterator itr = arr.begin() + l;
    int comparisons = 0;

    size_t i = 0, j = 0;
    while (i < left.size() && j < right.size()) {
        if (left[i] < right[j]) {
            *(itr++) = left[i++];
        } else {
            *(itr++) = right[j++];
        }
        ++comparisons; // Count the comparison made during merging
    }

    // Append remaining elements
    while (i < left.size()) {
        *(itr++) = left[i++];
    }
    while (j < right.size()) {
        *(itr++) = right[j++];
    }

    return comparisons;
}

int _hybrid_sort(std::vector<int>& arr, int l, int r, int s) {
    if (r - l <= s) {
        return _insertion_sort(arr, l, r);
    }

    int mid = (r+l) >> 1;
    int left_comparisons = _hybrid_sort(arr, l, mid, s);
    int right_comparisons = _hybrid_sort(arr, mid, r, s);

    int merged_comparisons = _merge(arr, l, mid, r);

    return left_comparisons + right_comparisons + merged_comparisons;
}


RunResult hybrid_sort(std::vector<int>& arr, int threshold) {
    auto start = std::chrono::steady_clock::now();

    int res = _hybrid_sort(arr, 0, arr.size(), threshold);

    auto end = std::chrono::steady_clock::now();

    double seconds = std::chrono::duration<double>(end - start).count();
    
    return {arr, res, seconds};
}

RunResult merge_sort(std::vector<int>& arr) {
    auto start = std::chrono::steady_clock::now();

    int res = _hybrid_sort(arr, 0, arr.size(), 1);

    auto end = std::chrono::steady_clock::now();

    double seconds = std::chrono::duration<double>(end - start).count();
    
    return {arr, res, seconds};
}

PYBIND11_MODULE(algorithms_cpp, m) {
    m.def("hybrid_sort", &hybrid_sort, py::arg("arr"), py::arg("threshold"));
    m.def("merge_sort", &merge_sort, py::arg("arr"));
}
