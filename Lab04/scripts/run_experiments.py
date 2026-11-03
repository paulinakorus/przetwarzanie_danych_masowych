"""Script for time measurement experiments on linear regression models."""
import argparse
from typing import List
from typing import Tuple
from typing import Type

import lr


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets-dir",
        required=True,
        help="Name of directory with generated datasets",
        type=str,
    )

    return parser.parse_args()


def run_experiments(
    models: List[Type[lr.base.LinearRegression]],
    datasets: List[Tuple[List[float], List[float]]],
):
    pass



def main() -> None:
    """Runs script."""
    args = get_args()

    models = [
        lr.LinearRegressionNumpy,
        lr.LinearRegressionProcess,
        lr.LinearRegressionSequential,
        lr.LinearRegressionThreads,
    ]

    datasets = []  # TODO: read datasets

    run_experiments(models, datasets)


if __name__ == "__main__":
    main()
