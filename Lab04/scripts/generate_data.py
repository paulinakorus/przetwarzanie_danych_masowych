"""Script for generation of artificial datasets."""
import argparse
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
    pass


def main() -> None:
    """Runs script."""
    pass


if __name__ == "__main__":
    main()
