import numpy as np
import time

def insertion_sort(arr: list, l, r) -> int:
    comparisons = 0
    for i in range(l+1, r):
        j = i
        while j > l:
            comparisons += 1
            if arr[j] < arr[j - 1]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
            else:
                break
            j -= 1
    return comparisons

def _merge(arr: list, l: int, mid: int, r: int) -> int:
    left = arr[l:mid]
    right = arr[mid:r]
    i = 0
    j = 0

    comparisons = 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] < right[j]:
            arr[l+i+j] = left[i]
            i += 1
        else:
            arr[l+i+j] = right[j]
            j += 1

    if i < len(left): arr[l+i+j : r] = left[i:]
    if j < len(right): arr[l+i+j : r] = right[j:]

    return comparisons

def _hybrid_sort(arr: list, l: int, r: int, s: int) -> int:
    if r-l <= s:
        return insertion_sort(arr, l, r)

    mid = (r+l) // 2
    left_comparisons = _hybrid_sort(arr, l, mid, s)
    right_comparisons = _hybrid_sort(arr, mid, r, s)

    merge_comparisons = _merge(arr, l, mid, r)
    return left_comparisons + right_comparisons + merge_comparisons

def hybrid_sort(arr: list | np.ndarray, s: int) -> tuple[list, int, float]:
    if isinstance(arr, np.ndarray):
        arr = arr.tolist()

    copied_arr = arr.copy()
    time_start = time.perf_counter()
    comparisons = _hybrid_sort(copied_arr, 0, len(arr), s)
    duration = time.perf_counter() - time_start
    return copied_arr, comparisons, duration

def merge_sort(arr: list | np.ndarray) -> tuple[list, int, float]:
    if isinstance(arr, np.ndarray):
        arr = arr.tolist()
    copied_arr = arr.copy()
    time_start = time.perf_counter()
    comparisons = _hybrid_sort(copied_arr, 0, len(arr), 1)
    duration = time.perf_counter() - time_start
    return copied_arr, comparisons, duration
