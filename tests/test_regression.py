"""Self-contained fixed-seed regression checks for the public release."""

from __future__ import annotations

import numpy as np
import pytest

from srgfade import SRGFADE


ABS_TOL = 1e-12
REL_TOL = 0.0


def _weighted_shifted_sphere(x: np.ndarray) -> float:
    weights = np.arange(1, x.size + 1, dtype=float)
    target = np.linspace(-0.25, 0.25, x.size)
    return float(np.sum(weights * (x - target) ** 2))


@pytest.mark.parametrize(
    (
        "seed",
        "dimension",
        "population",
        "budget",
        "coefficient",
        "expected_value",
        "expected_position",
    ),
    [
        (
            0,
            2,
            8,
            37,
            1.0,
            0.16901261352215655,
            [-0.6493320602321959, 0.31908878053948553],
        ),
        (
            42,
            5,
            12,
            113,
            1.0,
            1.8637621632670696,
            [
                0.616380091937393,
                -0.1565487762791935,
                -0.3087613002583187,
                -0.24149231657724135,
                0.010045856489219795,
            ],
        ),
        (
            2026,
            8,
            16,
            257,
            1.0,
            7.117822702598474,
            [
                0.9345396812003771,
                1.0057644788991558,
                0.04489123376333726,
                -0.15728717720942387,
                0.0012623811351622771,
                0.34719485787917526,
                0.6286731258816102,
                -0.10550970172971703,
            ],
        ),
        (
            7,
            3,
            6,
            6,
            1.0,
            17.105992788783663,
            [-2.4658419743823, 2.4594315456808022, 0.06886462008625438],
        ),
        (
            11,
            4,
            10,
            97,
            0.35,
            0.3259188226531642,
            [
                0.1468108479451304,
                -0.2004454303902142,
                0.130105554688134,
                0.0666515851031684,
            ],
        ),
    ],
)
def test_fixed_seed_result_matches_frozen_release_baseline(
    seed: int,
    dimension: int,
    population: int,
    budget: int,
    coefficient: float,
    expected_value: float,
    expected_position: list[float],
) -> None:
    lower = -3.0 if coefficient == 1.0 else -2.0
    upper = 4.0 if coefficient == 1.0 else 2.0
    result = SRGFADE(
        dim=dimension,
        lb=np.full(dimension, lower),
        ub=np.full(dimension, upper),
        pop_size=population,
        max_fes=budget,
        seed=seed,
        svd_var_threshold=0.8,
        alpha_g=0.3,
        perturbation_scale=coefficient,
        sa_accept_scale=0.3,
    ).optimize(_weighted_shifted_sphere)

    assert result.total_fes == budget
    np.testing.assert_allclose(
        result.best_fitness,
        expected_value,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )
    np.testing.assert_allclose(
        result.best_position,
        expected_position,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )
