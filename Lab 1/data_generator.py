import random
import numpy as np

random.seed(42)

def generate(n: int, x: int = 1_000_000_000):
    # Generate random np array for better performance
    return np.random.randint(1, x, n)

def dataset(size: int,
            n: tuple[int, int] | int = (1000, 10_000_000),
            x: int = 1_000_000_000):

    if isinstance(n, int): sizes = [n] * size
    else: sizes = sorted([random.randint(*n) for _ in range(size)])

    for size in sizes:
        yield generate(size, x)