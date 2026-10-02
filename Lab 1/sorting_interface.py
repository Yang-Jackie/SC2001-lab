import time
import numpy as np
import algorithms as algorithms_python


_backend = algorithms_python
_using_cpp = False

def select_backend(use_cpp: bool):
    global _backend, _using_cpp
    if use_cpp:
        try:
            import cppimport
            import cppimport.import_hook
            algorithms_cpp = cppimport.imp("algorithms_cpp")
        except Exception as error:
            _backend = algorithms_python
            _using_cpp = False
            print(f"C++ backend failed; backend is using Python: {error}")
        else:
            _backend = algorithms_cpp
            _using_cpp = True
            print("Backend is using C++")
    else:
        _backend = algorithms_python
        _using_cpp = False
        print("Backend is using Python")

def hybrid_sort(arr: list | np.ndarray, s) -> tuple[list, int, float]:
    return _backend.hybrid_sort(arr, s)

def merge_sort(arr: list | np.ndarray) -> tuple[list, int, float]:
    return _backend.merge_sort(arr)
