"""Script for time measurement experiments on linear regression models."""
import os

# BLAS threads must be set before numpy is imported.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import glob
import json
import pickle
import platform
import statistics
import time
from typing import Callable
from typing import List
from typing import Tuple
from typing import Type

import numpy as np

import lr

WORKERS = [1, 2, 4, 8]


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets-dir",
        required=True,
        help="Name of directory with generated datasets",
        type=str,
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="Directory for results (JSON and plots)",
        type=str,
    )
    parser.add_argument(
        "--repeats",
        default=5,
        help="Number of measured repetitions",
        type=int,
    )

    return parser.parse_args()


def read_datasets(datasets_dir: str) -> List[Tuple[List[float], List[float]]]:
    """Reads all <num-samples>.pkl files, sorted by size."""
    paths = glob.glob(os.path.join(datasets_dir, "*.pkl"))
    paths.sort(key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    datasets = []
    for path in paths:
        with open(path, "rb") as f:
            datasets.append(pickle.load(f))
    return datasets


def measure(
    factory: Callable[[], lr.base.LinearRegression],
    X: List[float],
    y: List[float],
    repeats: int,
) -> dict:
    """Measures fit() time only; the first run is a warm-up and is dropped."""
    factory().fit(X, y)  # warm-up

    times = []
    for _ in range(repeats):
        model = factory()
        t0 = time.perf_counter()
        model.fit(X, y)
        times.append(time.perf_counter() - t0)

    return {
        "mean": statistics.mean(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
        "times": times,
    }


def run_experiments(
    models: List[Type[lr.base.LinearRegression]],
    datasets: List[Tuple[List[float], List[float]]],
    repeats: int = 5,
) -> dict:
    """Runs every model on every dataset. Result: {model: {num_samples: stats}}."""
    results = {}
    for model_cls in models:
        results[model_cls.__name__] = {}
        for X, y in datasets:
            stats = measure(model_cls, X, y, repeats)
            results[model_cls.__name__][str(len(X))] = stats
            print(
                f"{model_cls.__name__:28s} n={len(X):>9d} "
                f"{stats['mean']:.4f} +- {stats['std']:.4f} s"
            )
    return results


def run_scaling(
    datasets: List[Tuple[List[float], List[float]]], repeats: int
) -> dict:
    """Time vs number of threads / processes on the largest dataset."""
    X, y = datasets[-1]
    results = {"num_samples": len(X), "workers": WORKERS}
    for model_cls in (lr.LinearRegressionThreads, lr.LinearRegressionProcess):
        results[model_cls.__name__] = {}
        for w in WORKERS:
            stats = measure(lambda: model_cls(n_workers=w), X, y, repeats)
            results[model_cls.__name__][str(w)] = stats
            print(
                f"{model_cls.__name__:28s} workers={w:<2d} "
                f"{stats['mean']:.4f} +- {stats['std']:.4f} s"
            )
    return results


def get_environment() -> dict:
    env = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "cpu_count": os.cpu_count(),
        "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
        "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
        "blas_threads": None,
    }
    try:
        from threadpoolctl import threadpool_info

        env["blas_threads"] = [
            {"api": i["internal_api"], "num_threads": i["num_threads"]}
            for i in threadpool_info()
        ]
    except ImportError:
        pass
    return env


def plot_comparison(results: dict, path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    for model_name, by_size in results.items():
        sizes = sorted(int(s) for s in by_size)
        means = [by_size[str(s)]["mean"] for s in sizes]
        stds = [by_size[str(s)]["std"] for s in sizes]
        ax.errorbar(sizes, means, yerr=stds, marker="o", capsize=3,
                    label=model_name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Liczba próbek")
    ax.set_ylabel("Czas fit() [s]")
    ax.set_title("Porównanie czasu działania metod")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_scaling(scaling: dict, path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    workers = scaling["workers"]
    for name in ("LinearRegressionThreads", "LinearRegressionProcess"):
        means = [scaling[name][str(w)]["mean"] for w in workers]
        stds = [scaling[name][str(w)]["std"] for w in workers]
        ax.errorbar(workers, means, yerr=stds, marker="o", capsize=3,
                    label=name)
    ax.set_xticks(workers)
    ax.set_xlabel("Liczba wątków / procesów")
    ax.set_ylabel("Czas fit() [s]")
    ax.set_title(f"Skalowanie (n = {scaling['num_samples']})")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    """Runs script."""
    args = get_args()

    models = [
        lr.LinearRegressionNumpy,
        lr.LinearRegressionProcess,
        lr.LinearRegressionSequential,
        lr.LinearRegressionThreads,
    ]

    datasets = read_datasets(args.datasets_dir)

    results = run_experiments(models, datasets, args.repeats)
    scaling = run_scaling(datasets, args.repeats)

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "time_measurements.json"), "w") as f:
        json.dump(
            {
                "environment": get_environment(),
                "repeats": args.repeats,
                "results": results,
                "scaling": scaling,
            },
            f,
            indent=2,
        )

    plot_comparison(results, os.path.join(args.out_dir, "comparison.png"))
    plot_scaling(scaling, os.path.join(args.out_dir, "scaling.png"))


if __name__ == "__main__":
    main()