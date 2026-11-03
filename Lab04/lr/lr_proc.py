from concurrent.futures import ProcessPoolExecutor
from typing import List
from typing import Tuple

from lr import base


def _partial_sums(batch: Tuple[List[float], List[float]]):
    """MAP: sums for a single batch (top-level function, so it can be pickled)."""
    xs, ys = batch
    sx = 0.0
    sy = 0.0
    sxy = 0.0
    sxx = 0.0
    for xi, yi in zip(xs, ys):
        sx += xi
        sy += yi
        sxy += xi * yi
        sxx += xi * xi
    return len(xs), sx, sy, sxy, sxx


def _split(X: List[float], y: List[float], n_batches: int):
    size = -(-len(X) // n_batches)  # ceil division
    return [
        (X[i:i + size], y[i:i + size])
        for i in range(0, len(X), size)
    ]


class LinearRegressionProcess(base.LinearRegression):
    def __init__(self, n_workers: int = 4):
        super().__init__()
        self.n_workers = n_workers

    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        batches = _split(X, y, self.n_workers)

        with ProcessPoolExecutor(max_workers=self.n_workers) as ex:
            parts = list(ex.map(_partial_sums, batches))

        # REDUCE: add up sums from all batches
        n = sum(p[0] for p in parts)
        sx = sum(p[1] for p in parts)
        sy = sum(p[2] for p in parts)
        sxy = sum(p[3] for p in parts)
        sxx = sum(p[4] for p in parts)

        b1 = (n * sxy - sx * sy) / (n * sxx - sx ** 2)
        b0 = (sy - b1 * sx) / n
        self._coef = (b0, b1)

        return self