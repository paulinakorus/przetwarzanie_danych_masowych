from typing import List

from lr import base


class LinearRegressionSequential(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        n = len(X)
        sx = 0.0
        sy = 0.0
        sxy = 0.0
        sxx = 0.0
        for xi, yi in zip(X, y):
            sx += xi
            sy += yi
            sxy += xi * yi
            sxx += xi * xi

        b1 = (n * sxy - sx * sy) / (n * sxx - sx ** 2)
        b0 = (sy - b1 * sx) / n
        self._coef = (b0, b1)

        return self