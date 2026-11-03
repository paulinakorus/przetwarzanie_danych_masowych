from typing import List

from lr import base


class LinearRegressionNumpy(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        raise NotImplementedError()
