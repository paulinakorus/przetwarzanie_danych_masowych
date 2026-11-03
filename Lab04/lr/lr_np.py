from typing import List

import numpy as np

from lr import base


class LinearRegressionNumpy(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        x = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n = x.size

        sx = x.sum()
        sy = y.sum()
        sxy = np.dot(x, y)
        sxx = np.dot(x, x)

        b1 = (n * sxy - sx * sy) / (n * sxx - sx ** 2)
        b0 = (sy - b1 * sx) / n
        self._coef = (b0, b1)

        return self