"""Subspace Rotation Gradient Field Adaptive Differential Evolution.

The optimizer combines four paper-aligned mechanisms: subspace rotation
crossover, gradient-field-guided mutation, annealed Gaussian perturbation,
and restricted simulated-annealing acceptance. The mechanisms operate on an
adaptive current-to-pbest/1 differential evolution backbone with an external
archive and midpoint boundary reflection.
"""

from __future__ import annotations

import time
from typing import Callable

import numpy as np

from .base import BaseAlgorithm, OptimizationResult


class SRGFADE(BaseAlgorithm):
    """Minimize a continuous, box-constrained objective with SRGFADE.

    Parameters
    ----------
    dim
        Search-space dimension.
    lb
        Lower bounds, convertible to a floating-point vector of length
        ``dim``.
    ub
        Upper bounds, convertible to a floating-point vector of length
        ``dim``.
    pop_size
        Population size. ``None`` resolves to ``max(4, 10 * dim)``.
    max_fes
        Maximum number of objective-function evaluations.
    seed
        Seed for the NumPy ``RandomState`` stream.
    svd_var_threshold
        Cumulative directional-energy threshold used to choose the rotation
        subspace dimension. The default is ``0.8``.
    alpha_g
        Learning rate of the gradient-field memory. The default is ``0.3``.
    perturbation_scale
        Amplitude coefficient of the annealed Gaussian perturbation. The
        default is ``1.0``.
    sa_accept_scale
        Multiplier applied to the restricted simulated-annealing acceptance
        probability. The default is ``0.3``.

    Notes
    -----
    The objective must accept one one-dimensional NumPy array and return one
    scalar value. The optimizer performs minimization. Each call to
    :meth:`optimize` restores the constructor seed before population
    initialization.
    """

    def __init__(
        self,
        dim: int,
        lb,
        ub,
        pop_size: int | None = None,
        max_fes: int = 10_000,
        seed: int = 42,
        svd_var_threshold: float = 0.8,
        alpha_g: float = 0.3,
        perturbation_scale: float = 1.0,
        sa_accept_scale: float = 0.3,
    ) -> None:
        if pop_size is None:
            pop_size = max(4, 10 * dim)
        super().__init__(
            dim=dim,
            lb=lb,
            ub=ub,
            pop_size=pop_size,
            max_fes=max_fes,
            seed=seed,
        )
        self.svd_var_threshold = svd_var_threshold
        self.alpha_g = alpha_g
        self.perturbation_scale = perturbation_scale
        self.sa_accept_scale = sa_accept_scale

    def optimize(
        self,
        func: Callable[[np.ndarray], float],
    ) -> OptimizationResult:
        """Run SRGFADE on ``func`` until the evaluation budget is spent."""
        self._reset_state()
        start_time = time.perf_counter()

        pop_size = self.pop_size
        dimension = self.dim

        population = self._init_population()
        costs = np.empty(pop_size, dtype=float)
        for index in range(pop_size):
            if self._fes >= self.max_fes:
                break
            costs[index] = self._evaluate(func, population[index])

        mean_scale = 0.5
        mean_crossover = 0.5
        gradient_rate = self.alpha_g
        gradient_field = np.zeros(dimension, dtype=float)

        history_capacity = min(dimension, pop_size)
        difference_history = np.zeros(
            (history_capacity, dimension),
            dtype=float,
        )
        history_pointer = 0
        history_count = 0

        archive: list[np.ndarray] = []

        self._record_convergence()

        while self._fes < self.max_fes:
            temperature = (1.0 - self._fes / self.max_fes) ** 2

            successful_scales: list[float] = []
            successful_crossovers: list[float] = []
            successful_improvements: list[float] = []

            ranking = np.argsort(costs)
            elite_rate = max(
                2.0 / pop_size,
                0.2 * (1.0 - self._fes / self.max_fes) + 0.05,
            )
            elite_count = max(2, int(np.ceil(pop_size * elite_rate)))
            elite_indices = ranking[:elite_count]

            coordinate_spread = np.std(population, axis=0) + 1e-30

            use_subspace = False
            basis: np.ndarray | None = None
            if history_count >= 2:
                valid_rows = min(history_count, history_capacity)
                history_matrix = difference_history[:valid_rows]
                try:
                    _, singular_values, right_vectors = np.linalg.svd(
                        history_matrix,
                        full_matrices=False,
                    )
                    cumulative_energy = np.cumsum(singular_values ** 2) / (
                        np.sum(singular_values ** 2) + 1e-30
                    )
                    threshold_index = np.searchsorted(
                        cumulative_energy,
                        self.svd_var_threshold,
                    )
                    basis_count = int(threshold_index) + 1
                    basis_count = max(
                        2,
                        min(
                            basis_count,
                            min(valid_rows, (dimension + 1) // 2),
                        ),
                    )
                    basis_count = min(basis_count, right_vectors.shape[0])
                    basis = right_vectors[:basis_count].T
                    use_subspace = True
                except np.linalg.LinAlgError:
                    use_subspace = False

            for index in range(pop_size):
                if self._fes >= self.max_fes:
                    break

                parent = population[index].copy()

                scale = mean_scale + 0.1 * np.tan(
                    np.pi * (self.rng.random() - 0.5)
                )
                scale = float(np.clip(scale, 0.1, 1.0))
                crossover_rate = float(
                    np.clip(
                        mean_crossover + 0.1 * self.rng.randn(),
                        0.0,
                        1.0,
                    )
                )

                elite_index = int(
                    elite_indices[self.rng.randint(0, elite_count)]
                )

                population_candidates = np.delete(
                    np.arange(pop_size),
                    index,
                )
                first_donor = int(
                    population_candidates[
                        self.rng.randint(0, len(population_candidates))
                    ]
                )

                archive_size = len(archive)
                union_size = pop_size + archive_size
                union_candidates = np.setdiff1d(
                    np.arange(union_size),
                    [index, first_donor],
                )
                if len(union_candidates) == 0:
                    union_candidates = np.delete(
                        np.arange(pop_size),
                        index,
                    )
                second_donor = int(
                    union_candidates[
                        self.rng.randint(0, len(union_candidates))
                    ]
                )
                if second_donor < pop_size:
                    second_donor_position = population[second_donor]
                else:
                    second_donor_position = archive[second_donor - pop_size]

                mutant = (
                    parent
                    + scale * (population[elite_index] - parent)
                    + scale
                    * (
                        population[first_donor]
                        - second_donor_position
                    )
                )

                gradient_strength = (
                    temperature
                    * np.linalg.norm(coordinate_spread)
                    / (np.sqrt(dimension) + 1e-30)
                )
                mutant = mutant + (
                    gradient_strength
                    * gradient_field
                    * (
                        coordinate_spread
                        / (np.max(coordinate_spread) + 1e-30)
                    )
                )

                if temperature > 0.1:
                    perturbation = (
                        self.perturbation_scale
                        * temperature ** 2
                        * coordinate_spread
                        * self.rng.randn(dimension)
                    )
                    mutant = mutant + perturbation

                lower_mask = mutant < self.lb
                upper_mask = mutant > self.ub
                mutant[lower_mask] = (
                    self.lb[lower_mask] + parent[lower_mask]
                ) / 2.0
                mutant[upper_mask] = (
                    self.ub[upper_mask] + parent[upper_mask]
                ) / 2.0

                displacement = mutant - parent
                use_current_subspace = (
                    use_subspace
                    and basis is not None
                    and self.rng.random()
                    < 0.5 + 0.3 * (1.0 - temperature)
                )

                if use_current_subspace:
                    projection_coefficients = basis.T @ displacement
                    subspace_component = basis @ projection_coefficients
                    complement_component = (
                        displacement - subspace_component
                    )

                    trial = parent + subspace_component
                    crossover_mask = (
                        self.rng.random(dimension) < crossover_rate
                    )
                    forced_coordinate = self.rng.randint(0, dimension)
                    crossover_mask[forced_coordinate] = True
                    trial = trial + crossover_mask * complement_component
                else:
                    trial = parent.copy()
                    forced_coordinate = self.rng.randint(0, dimension)
                    crossover_mask = (
                        self.rng.random(dimension) < crossover_rate
                    )
                    crossover_mask[forced_coordinate] = True
                    trial = np.where(crossover_mask, mutant, parent)

                lower_trial_mask = trial < self.lb
                upper_trial_mask = trial > self.ub
                trial[lower_trial_mask] = (
                    self.lb[lower_trial_mask] + parent[lower_trial_mask]
                ) / 2.0
                trial[upper_trial_mask] = (
                    self.ub[upper_trial_mask] + parent[upper_trial_mask]
                ) / 2.0

                trial_cost = self._evaluate(func, trial)
                cost_change = trial_cost - costs[index]

                if cost_change < 0:
                    successful_scales.append(scale)
                    successful_crossovers.append(crossover_rate)
                    successful_improvements.append(abs(cost_change))

                    accepted_displacement = trial - parent
                    displacement_norm = (
                        np.linalg.norm(accepted_displacement) + 1e-30
                    )
                    gradient_field = (
                        (1 - gradient_rate) * gradient_field
                        + gradient_rate
                        * (abs(cost_change) / displacement_norm)
                        * (accepted_displacement / displacement_norm)
                    )
                    gradient_norm = np.linalg.norm(gradient_field)
                    if gradient_norm > 1.0:
                        gradient_field /= gradient_norm

                    history_pointer = (
                        history_pointer % history_capacity
                    )
                    difference_history[history_pointer] = (
                        accepted_displacement / displacement_norm
                    )
                    history_pointer = (
                        history_pointer + 1
                    ) % history_capacity
                    history_count += 1

                    if len(archive) < pop_size:
                        archive.append(parent.copy())
                    else:
                        archive[self.rng.randint(0, pop_size)] = (
                            parent.copy()
                        )

                    population[index] = trial
                    costs[index] = trial_cost
                elif temperature > 0.1:
                    fitness_scale = max(
                        abs(self._best_fitness),
                        1e-10,
                    )
                    acceptance_probability = np.exp(
                        -cost_change
                        / (
                            temperature * fitness_scale
                            + 1e-30
                        )
                    )
                    if (
                        self.rng.random()
                        < acceptance_probability * self.sa_accept_scale
                    ):
                        if len(archive) < pop_size:
                            archive.append(parent.copy())
                        else:
                            archive[
                                self.rng.randint(0, pop_size)
                            ] = parent.copy()
                        population[index] = trial
                        costs[index] = trial_cost

            if successful_scales:
                weights = np.array(
                    successful_improvements,
                    dtype=float,
                )
                weights = weights / (weights.sum() + 1e-30)
                scale_array = np.array(successful_scales, dtype=float)
                crossover_array = np.array(
                    successful_crossovers,
                    dtype=float,
                )
                mean_scale = float(
                    np.clip(
                        0.9 * mean_scale
                        + 0.1
                        * np.sum(weights * scale_array ** 2)
                        / (
                            np.sum(weights * scale_array)
                            + 1e-30
                        ),
                        0.1,
                        0.9,
                    )
                )
                mean_crossover = float(
                    np.clip(
                        0.9 * mean_crossover
                        + 0.1
                        * np.sum(weights * crossover_array),
                        0.05,
                        0.95,
                    )
                )

            self._record_convergence()

        return OptimizationResult(
            best_fitness=self._best_fitness,
            best_position=(
                self._best_position.copy()
                if self._best_position is not None
                else np.zeros(dimension)
            ),
            convergence_curve=self._convergence,
            convergence_fes=self._convergence_fes,
            total_fes=self._fes,
            wall_time=time.perf_counter() - start_time,
        )

    def get_params(self) -> dict:
        """Return the common and SRGFADE-specific parameters."""
        params = super().get_params()
        params.update(
            svd_var_threshold=self.svd_var_threshold,
            alpha_g=self.alpha_g,
            perturbation_scale=self.perturbation_scale,
            sa_accept_scale=self.sa_accept_scale,
        )
        return params
