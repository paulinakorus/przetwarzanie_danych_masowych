from typing import List

from lr import base


class LinearRegressionProcess(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        raise NotImplementedError()
