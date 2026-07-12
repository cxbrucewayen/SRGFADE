"""Shared runtime types and evaluation accounting for SRGFADE."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


@dataclass
class OptimizationResult:
    """Result returned by one optimization run.

    Parameters
    ----------
    best_fitness
        Smallest objective value observed during the run.
    best_position
        Position at which ``best_fitness`` was observed.
    convergence_curve
        Best-so-far values at the recorded evaluation checkpoints.
    convergence_fes
        Function-evaluation counts associated with the convergence curve.
    total_fes
        Number of objective-function calls made by the optimizer.
    wall_time
        Elapsed optimization time in seconds.
    diversity_curve
        Optional population-diversity values. SRGFADE leaves this empty.
    diversity_fes
        Evaluation checkpoints associated with ``diversity_curve``.
    """

    best_fitness: float
    best_position: np.ndarray
    convergence_curve: list[float]
    convergence_fes: list[int]
    total_fes: int
    wall_time: float = 0.0
    diversity_curve: list[float] = field(default_factory=list)
    diversity_fes: list[int] = field(default_factory=list)


class BaseAlgorithm(ABC):
    """Base class providing deterministic state and budget accounting.

    Subclasses evaluate objective functions through :meth:`_evaluate`. This
    keeps function-evaluation counting and global-best tracking at one call
    site. The legacy ``RandomState`` generator is retained because the
    optimizer depends on its deterministic MT19937 sequence.
    """

    def __init__(
        self,
        dim: int,
        lb: np.ndarray | list[float],
        ub: np.ndarray | list[float],
        pop_size: int,
        max_fes: int,
        seed: int,
    ) -> None:
        """Initialize the shared optimizer parameters and runtime state."""
        if dim <= 0:
            raise ValueError(f"dim must be positive, got {dim}")
        if pop_size < 4:
            raise ValueError(f"pop_size must be at least 4, got {pop_size}")
        if max_fes <= 0:
            raise ValueError(f"max_fes must be positive, got {max_fes}")

        self.dim = dim
        self.lb = np.asarray(lb, dtype=float)
        self.ub = np.asarray(ub, dtype=float)
        expected_shape = (dim,)
        if self.lb.shape != expected_shape:
            raise ValueError(
                f"lb must have shape {expected_shape}, got {self.lb.shape}"
            )
        if self.ub.shape != expected_shape:
            raise ValueError(
                f"ub must have shape {expected_shape}, got {self.ub.shape}"
            )
        if not np.all(np.isfinite(self.lb)):
            raise ValueError("lb must contain only finite values")
        if not np.all(np.isfinite(self.ub)):
            raise ValueError("ub must contain only finite values")
        if np.any(self.lb >= self.ub):
            raise ValueError("each lower bound must be less than its upper bound")
        self.pop_size = pop_size
        self.max_fes = max_fes
        self.seed = seed

        self._diversity: list[float] = []
        self._diversity_fes_list: list[int] = []
        self.rng = np.random.RandomState(seed)

        self._fes: int = 0
        self._convergence: list[float] = []
        self._convergence_fes: list[int] = []
        self._best_fitness: float = np.inf
        self._best_position: np.ndarray | None = None

    @abstractmethod
    def optimize(
        self,
        func: Callable[[np.ndarray], float],
    ) -> OptimizationResult:
        """Minimize ``func`` and return an :class:`OptimizationResult`."""
        ...

    def _evaluate(
        self,
        func: Callable[[np.ndarray], float],
        x: np.ndarray,
    ) -> float:
        """Evaluate one candidate and update the count and global best."""
        objective_value = np.asarray(func(x))
        if objective_value.ndim != 0:
            raise ValueError("the objective must return one scalar value")
        fitness = float(objective_value)
        if not np.isfinite(fitness):
            raise ValueError("the objective must return a finite value")
        self._fes += 1
        if fitness < self._best_fitness:
            self._best_fitness = fitness
            self._best_position = x.copy()
        return fitness

    def _record_convergence(self) -> None:
        """Record the global best at the current evaluation count."""
        self._convergence.append(self._best_fitness)
        self._convergence_fes.append(self._fes)

    def _record_diversity(self, population: np.ndarray) -> None:
        """Record mean normalized coordinate-wise population dispersion."""
        ranges = self.ub - self.lb
        safe_ranges = np.where(ranges > 0, ranges, 1.0)
        normalized = (population - self.lb) / safe_ranges
        diversity = float(np.mean(np.std(normalized, axis=0)))
        self._diversity.append(diversity)
        self._diversity_fes_list.append(self._fes)

    def _init_population(self) -> np.ndarray:
        """Draw the initial population uniformly within the box bounds."""
        return self.rng.uniform(
            self.lb,
            self.ub,
            size=(self.pop_size, self.dim),
        )

    def _reset_state(self) -> None:
        """Reset runtime state and restore the constructor seed."""
        self._fes = 0
        self._convergence = []
        self._convergence_fes = []
        self._best_fitness = np.inf
        self._best_position = None
        self._diversity = []
        self._diversity_fes_list = []
        self.rng = np.random.RandomState(self.seed)

    @property
    def name(self) -> str:
        """Return the optimizer class name."""
        return self.__class__.__name__

    def get_params(self) -> dict:
        """Return the common constructor parameters for result logging."""
        return {
            "name": self.name,
            "dim": self.dim,
            "pop_size": self.pop_size,
            "max_fes": self.max_fes,
            "seed": self.seed,
        }

    def __repr__(self) -> str:
        """Return a concise constructor-style representation."""
        return (
            f"{self.name}(dim={self.dim}, pop_size={self.pop_size}, "
            f"max_fes={self.max_fes}, seed={self.seed})"
        )
