"""Run a fixed-seed SRGFADE example on the sphere objective."""

from __future__ import annotations

import numpy as np

from srgfade import SRGFADE


def sphere(x: np.ndarray) -> float:
    """Return the sum of squared coordinates."""
    return float(np.dot(x, x))


def main() -> None:
    """Minimize the five-dimensional sphere function and print the result."""
    dimension = 5
    optimizer = SRGFADE(
        dim=dimension,
        lb=np.full(dimension, -5.0),
        ub=np.full(dimension, 5.0),
        pop_size=30,
        max_fes=600,
        seed=42,
    )
    result = optimizer.optimize(sphere)

    print(f"best_fitness={result.best_fitness:.12g}")
    print(f"best_position={result.best_position}")
    print(f"total_fes={result.total_fes}")


if __name__ == "__main__":
    main()
