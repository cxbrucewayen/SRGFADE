"""Smoke tests for the public SRGFADE minimization interface."""

from __future__ import annotations

from pathlib import Path
import runpy

import numpy as np
import pytest

import srgfade
from srgfade import BaseAlgorithm, OptimizationResult, SRGFADE


def _sphere(x: np.ndarray) -> float:
    return float(np.dot(x, x))


def _optimizer(**overrides) -> SRGFADE:
    parameters = {
        "dim": 4,
        "lb": np.full(4, -2.0),
        "ub": np.full(4, 3.0),
        "pop_size": 10,
        "max_fes": 83,
        "seed": 19,
    }
    parameters.update(overrides)
    return SRGFADE(**parameters)


def test_public_import_surface() -> None:
    assert srgfade.SRGFADE is SRGFADE
    assert issubclass(SRGFADE, BaseAlgorithm)
    assert srgfade.__version__ == "1.0.0"


def test_fixed_seed_is_repeatable_on_reused_instance() -> None:
    optimizer = _optimizer()

    first = optimizer.optimize(_sphere)
    second = optimizer.optimize(_sphere)

    assert first.total_fes == second.total_fes
    assert first.best_fitness == second.best_fitness
    np.testing.assert_array_equal(first.best_position, second.best_position)
    np.testing.assert_array_equal(
        first.convergence_curve,
        second.convergence_curve,
    )
    assert first.convergence_fes == second.convergence_fes


@pytest.mark.parametrize("budget", [1, 10, 37, 83])
def test_budget_is_not_exceeded_and_matches_objective_calls(budget: int) -> None:
    calls = 0

    def counted_sphere(x: np.ndarray) -> float:
        nonlocal calls
        calls += 1
        return _sphere(x)

    result = _optimizer(max_fes=budget).optimize(counted_sphere)

    assert result.total_fes == calls
    assert result.total_fes == budget
    assert result.total_fes <= budget


def test_all_evaluated_points_and_returned_solution_respect_bounds() -> None:
    lower = np.array([-4.0, -1.0, 2.0, -0.5])
    upper = np.array([-1.0, 3.0, 5.0, 0.5])
    evaluated: list[np.ndarray] = []

    def bounded_objective(x: np.ndarray) -> float:
        evaluated.append(x.copy())
        return float(np.sum((x - lower) ** 2))

    result = _optimizer(lb=lower, ub=upper).optimize(bounded_objective)

    points = np.asarray(evaluated)
    assert np.all(points >= lower)
    assert np.all(points <= upper)
    assert np.all(result.best_position >= lower)
    assert np.all(result.best_position <= upper)


def test_result_reports_the_smallest_observed_objective_value() -> None:
    observations: list[tuple[float, np.ndarray]] = []
    target = np.array([0.75, -0.25, 1.25, -1.5])

    def shifted_objective(x: np.ndarray) -> float:
        value = float(np.sum((x - target) ** 2) + 7.0)
        observations.append((value, x.copy()))
        return value

    result = _optimizer().optimize(shifted_objective)
    observed_value, observed_position = min(observations, key=lambda item: item[0])

    assert isinstance(result, OptimizationResult)
    assert result.best_fitness == observed_value
    np.testing.assert_array_equal(result.best_position, observed_position)


@pytest.mark.parametrize(
    "overrides",
    [
        {"dim": 0, "lb": np.array([]), "ub": np.array([])},
        {"pop_size": 0},
        {"pop_size": 1},
        {"pop_size": 2},
        {"pop_size": 3},
        {"max_fes": 0},
        {"lb": np.full(3, -1.0)},
        {"ub": np.full(3, 1.0)},
        {"lb": np.array([-2.0, -2.0, np.nan, -2.0])},
        {"ub": np.array([3.0, 3.0, np.inf, 3.0])},
        {"lb": np.array([-2.0, -2.0, 3.0, -2.0])},
    ],
)
def test_invalid_constructor_inputs_raise_value_error(overrides) -> None:
    with pytest.raises(ValueError):
        _optimizer(**overrides)


@pytest.mark.parametrize(
    "invalid_value",
    [np.nan, np.inf, np.array([1.0])],
)
def test_invalid_objective_values_raise_value_error(invalid_value) -> None:
    def invalid_objective(_x: np.ndarray):
        return invalid_value

    with pytest.raises(ValueError):
        _optimizer().optimize(invalid_objective)


def test_quick_start_runs_and_prints_minimal_result(capsys) -> None:
    example = Path(__file__).resolve().parents[1] / "examples" / "quick_start.py"

    runpy.run_path(str(example), run_name="__main__")
    output_lines = capsys.readouterr().out.strip().splitlines()

    assert len(output_lines) == 3
    assert output_lines[0].startswith("best_fitness=")
    assert output_lines[1].startswith("best_position=")
    assert output_lines[2] == "total_fes=600"
