# SRGFADE implementation baseline

This record freezes the source snapshot from which the release implementation is derived. The source files remain read-only during release preparation.

## Authoritative files

| Role | Workspace-relative source | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| Optimizer | `1SPADE/pyswarm-experiment/src/algorithms/srgfade.py` | `e710aa20da1be9688f62c61a6b854cb2f8f7c2708f651bcbf3981e111cef04a2` | 13072 |
| Shared base | `1SPADE/pyswarm-experiment/src/algorithms/base.py` | `b2e26bae86f45790c635b82853cb23d2b3467fbe04a21a08f47d96401265a965` | 9247 |

The optimizer implements Subspace Rotation Gradient Field Adaptive Differential Evolution (SRGFADE). Its four paper-aligned mechanisms are subspace rotation crossover, gradient-field-guided mutation, annealed Gaussian perturbation, and restricted simulated-annealing acceptance.

## Public interface

The authoritative optimizer exposes the class `SRGFADE` with the following constructor:

```python
SRGFADE(
    dim,
    lb,
    ub,
    pop_size=None,
    max_fes=10_000,
    seed=42,
    svd_var_threshold=0.8,
    alpha_g=0.3,
    perturbation_scale=1.0,
    sa_accept_scale=0.3,
)
```

`pop_size=None` resolves to `max(4, 10 * dim)`. The `optimize(func)` method minimizes a callable of the form `func(x) -> float` and returns an `OptimizationResult`. The result contains `best_fitness`, `best_position`, `convergence_curve`, `convergence_fes`, `total_fes`, `wall_time`, `diversity_curve`, and `diversity_fes`. The optimizer also exposes `get_params()` and the inherited `name` property.

The release interface names the perturbation amplitude argument `perturbation_scale`. Its default and numeric use must remain identical to the frozen source value of `1.0`; fixed-seed regression tests must verify the name mapping before publication.

## Dependencies and runtime assumptions

- Python 3.10 or later, required by the source syntax.
- NumPy, the only runtime package imported outside the Python standard library.
- A scalar minimization objective accepting a one-dimensional NumPy array.
- Lower and upper bounds convertible to floating-point NumPy arrays of length `dim`.

## Random-number sequence

The implementation uses `numpy.random.RandomState(seed)`, which provides an MT19937 stream. Every `optimize` call resets the stream to the constructor seed. The observable sequence is determined by the following order:

1. Uniform population initialization draws an array of shape `(pop_size, dim)`.
2. Each processed individual draws the scale factor, crossover rate, elite index, population donor index, union donor index, optional perturbation vector, subspace-use decision, crossover mask, forced-coordinate index, and, when applicable, acceptance and archive-replacement variates in source order.
3. No additional random draw may be introduced by the release-only parameter rename or module reorganization.

An annealed Gaussian perturbation draw occurs only while the shared temperature exceeds `0.1`. A restricted simulated-annealing acceptance draw occurs only for a non-improving trial under the same temperature gate. Archive replacement draws occur only when the archive is full and a replacement is required.

## Boundary handling

The optimizer applies midpoint reflection twice. After mutation, each component below the lower bound is replaced by the midpoint of that bound and the parent component; each component above the upper bound is treated analogously. The same rule is applied to the trial vector after crossover. The rule uses the current parent, not clipping to the nearest bound.

## Evaluation budget and convergence records

- `_evaluate` is the only objective-call site. It increments the function-evaluation counter once and updates the global best.
- Population initialization evaluates candidates in index order and stops if the budget is exhausted.
- The main loop checks the remaining budget before each trial evaluation, so `total_fes` does not exceed `max_fes`.
- Convergence is recorded after initialization and once after each generation, including a partially processed final generation.
- The return structure reports the global best tracked by `_evaluate`, not only the final population minimum.

## Derivation invariants

Release preparation may change module organization, documentation, and the public name of the perturbation scale. It must preserve default parameters, NumPy operations, random draws and their order, midpoint reflection, archive behavior, evaluation counting, convergence checkpoints, and the result fields. Numeric equivalence is established by fixed-seed regression tests, not by values copied from paper tables.
