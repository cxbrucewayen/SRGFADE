"""Fixed-seed regression checks against the frozen authoritative source."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
from pathlib import Path
import sys
import types

import numpy as np
import pytest

from srgfade import SRGFADE as PublicSRGFADE


ABS_TOL = 1e-12
REL_TOL = 0.0
AUTHORITATIVE_HASHES = {
    "base.py": "b2e26bae86f45790c635b82853cb23d2b3467fbe04a21a08f47d96401265a965",
    "srgfade.py": "e710aa20da1be9688f62c61a6b854cb2f8f7c2708f651bcbf3981e111cef04a2",
}


def _authoritative_directory() -> Path:
    workspace_root = Path(__file__).resolve().parents[2]
    directory = (
        workspace_root
        / "1SPADE"
        / "pyswarm-experiment"
        / "src"
        / "algorithms"
    )
    if not directory.is_dir():
        pytest.skip("authoritative workspace source is not available")
    return directory


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_authoritative_class():
    directory = _authoritative_directory()
    for filename, expected_hash in AUTHORITATIVE_HASHES.items():
        assert _sha256(directory / filename) == expected_hash

    package_name = "_srgfade_authoritative"
    package = types.ModuleType(package_name)
    package.__path__ = [str(directory)]
    sys.modules[package_name] = package

    for module_name, filename in (("base", "base.py"), ("core", "srgfade.py")):
        qualified_name = f"{package_name}.{module_name}"
        spec = importlib.util.spec_from_file_location(
            qualified_name,
            directory / filename,
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified_name] = module
        spec.loader.exec_module(module)

    return sys.modules[f"{package_name}.core"].SRGFADE


def _weighted_shifted_sphere(x: np.ndarray) -> float:
    weights = np.arange(1, x.size + 1, dtype=float)
    target = np.linspace(-0.25, 0.25, x.size)
    return float(np.sum(weights * (x - target) ** 2))


def _authoritative_perturbation_argument(
    authoritative_class,
    value: float,
) -> dict[str, float]:
    """Map the public perturbation coefficient to the frozen signature."""
    authoritative_parameters = set(
        inspect.signature(authoritative_class).parameters
    )
    public_parameters = set(inspect.signature(PublicSRGFADE).parameters)
    release_only_parameters = {"perturbation_scale"}
    source_only_parameters = (
        authoritative_parameters
        - public_parameters
        - release_only_parameters
    )
    assert len(source_only_parameters) == 1
    return {source_only_parameters.pop(): value}


@pytest.mark.parametrize(
    ("seed", "dimension", "population", "budget"),
    [
        (0, 2, 8, 37),
        (42, 5, 12, 113),
        (2026, 8, 16, 257),
        (7, 3, 6, 6),
    ],
)
def test_public_result_matches_authoritative_result(
    seed: int,
    dimension: int,
    population: int,
    budget: int,
) -> None:
    authoritative_class = _load_authoritative_class()
    common = {
        "dim": dimension,
        "lb": np.full(dimension, -3.0),
        "ub": np.full(dimension, 4.0),
        "pop_size": population,
        "max_fes": budget,
        "seed": seed,
        "svd_var_threshold": 0.8,
        "alpha_g": 0.3,
        "sa_accept_scale": 0.3,
    }

    authoritative_result = authoritative_class(
        **common,
        **_authoritative_perturbation_argument(
            authoritative_class,
            1.0,
        ),
    ).optimize(_weighted_shifted_sphere)
    public_result = PublicSRGFADE(
        **common,
        perturbation_scale=1.0,
    ).optimize(_weighted_shifted_sphere)

    assert public_result.total_fes == authoritative_result.total_fes
    assert public_result.total_fes == budget
    np.testing.assert_allclose(
        public_result.best_fitness,
        authoritative_result.best_fitness,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )
    np.testing.assert_allclose(
        public_result.best_position,
        authoritative_result.best_position,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )


def test_public_perturbation_name_preserves_nondefault_behavior() -> None:
    authoritative_class = _load_authoritative_class()
    common = {
        "dim": 4,
        "lb": np.full(4, -2.0),
        "ub": np.full(4, 2.0),
        "pop_size": 10,
        "max_fes": 97,
        "seed": 11,
    }

    authoritative_result = authoritative_class(
        **common,
        **_authoritative_perturbation_argument(
            authoritative_class,
            0.35,
        ),
    ).optimize(_weighted_shifted_sphere)
    public_result = PublicSRGFADE(
        **common,
        perturbation_scale=0.35,
    ).optimize(_weighted_shifted_sphere)

    assert public_result.total_fes == authoritative_result.total_fes
    np.testing.assert_allclose(
        public_result.best_fitness,
        authoritative_result.best_fitness,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )
    np.testing.assert_allclose(
        public_result.best_position,
        authoritative_result.best_position,
        rtol=REL_TOL,
        atol=ABS_TOL,
    )
