"""Script for generation of artificial datasets."""
import argparse
import os
import pickle
import random
from typing import List
from typing import Tuple


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-samples",
        required=True,
        help="Number of samples to generate",
        type=int,
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Name of directory to save generated data",
        type=str,
    )

    return parser.parse_args()


def generate_data(num_samples: int) -> Tuple[List[float], List[float]]:
    """Generated X, y with given number of data samples."""
    X = [random.uniform(-100.0, 100.0) for _ in range(num_samples)]
    y = [2.0 * x + 5.0 for x in X]
    return X, y


def main() -> None:
    """Runs script."""
    args = get_args()

    X, y = generate_data(args.num_samples)

    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, f"{args.num_samples}.pkl")
    with open(path, "wb") as f:
        pickle.dump((X, y), f)


if __name__ == "__main__":
    main()