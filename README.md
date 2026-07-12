# SRGFADE

Subspace Rotation Gradient Field Adaptive Differential Evolution (SRGFADE)
is a population-based minimizer for continuous, box-constrained objective
functions. This package contains the Python optimizer, its shared result and
budget support, and a fixed-seed minimal example.

## Function

SRGFADE places four mechanisms on an adaptive current-to-pbest/1 differential
evolution backbone:

- subspace rotation crossover
- gradient-field-guided mutation
- annealed Gaussian perturbation
- restricted simulated-annealing acceptance

The subspace rotation crossover estimates a low-rank basis from recent
successful displacement directions. It retains the projected component of a
mutant and applies binomial crossover to the complementary component. The
directional-energy threshold is controlled by `svd_var_threshold`.

The gradient-field-guided mutation maintains an exponentially weighted field
of improving directions. The field is added to the current-to-pbest/1 mutant
and scaled by temperature and coordinate-wise population spread. The memory
rate is controlled by `alpha_g`.

The annealed Gaussian perturbation adds a spread-scaled random vector while
the shared temperature exceeds `0.1`. Its amplitude decreases with the square
of the temperature. The coefficient is exposed as `perturbation_scale`.

The restricted simulated-annealing acceptance permits a non-improving trial
at high temperature according to a scaled Metropolis probability. The rule
is restricted by the temperature gate and `sa_accept_scale`. Selection
becomes greedy after the temperature gate closes.

The optimizer uses midpoint boundary reflection for the mutant and the trial
vector. It counts one function evaluation at the single objective-call site
and stops when `max_fes` is reached. Each call to `optimize` restores the
constructor seed and therefore restarts the NumPy `RandomState` stream.

## Installation

The package requires Python 3.10 or newer and NumPy. From the repository root,
create an isolated environment and install the package:

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe examples\quick_start.py
```

POSIX shell:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python examples/quick_start.py
```

For an editable installation with the optional test dependency, use:

```bash
python -m pip install -e ".[test]"
```

## Input

Create `SRGFADE` with the following arguments:

- `dim` is the positive search-space dimension.
- `lb` is the lower-bound vector. It must be convertible to a floating-point
  NumPy array whose coordinate semantics match `dim`.
- `ub` is the corresponding upper-bound vector.
- `pop_size` is the population size and must be at least 4. The default is
  `max(4, 10 * dim)`.
- `max_fes` is the positive objective-evaluation budget. The default is
  `10_000`.
- `seed` initializes the deterministic NumPy random stream. The default is
  `42`.
- `svd_var_threshold` is the cumulative directional-energy threshold for the
  rotation subspace. The default is `0.8`.
- `alpha_g` is the gradient-field memory rate. The default is `0.3`.
- `perturbation_scale` is the scalar amplitude coefficient of the annealed
  Gaussian perturbation. The default is `1.0`.
- `sa_accept_scale` is the scalar multiplier for simulated-annealing
  acceptance. The default is `0.3`.

Pass the objective to `optimize(func)`. The objective must accept one
one-dimensional NumPy vector and return one finite scalar value to minimize.
For example, a sphere objective is:

```python
def sphere(x: np.ndarray) -> float:
    return float(np.dot(x, x))
```

The objective is called once for every counted function evaluation. Any
problem-specific constraints or penalties must be represented by the supplied
objective, while `lb` and `ub` define the coordinate-wise box.

## Output

`optimize` returns an `OptimizationResult` with these fields:

- `best_fitness` is the smallest objective value observed.
- `best_position` is the NumPy vector associated with `best_fitness`.
- `convergence_curve` stores the best-so-far value after initialization and
  after each generation.
- `convergence_fes` stores the evaluation count for each convergence value.
- `total_fes` is the number of objective calls made by the optimizer.
- `wall_time` is the measured runtime in seconds.
- `diversity_curve` is present for result-structure compatibility and is empty
  for this optimizer.
- `diversity_fes` is the corresponding empty checkpoint list.

The optimizer also provides `get_params()`, which returns the common runtime
parameters and the four public mechanism coefficients, and the `name`
property, which returns `SRGFADE`.

## Example

The included example minimizes the five-dimensional sphere function with a
fixed seed:

```bash
python examples/quick_start.py
```

The same call can be written directly:

```python
import numpy as np

from srgfade import SRGFADE


def sphere(x: np.ndarray) -> float:
    return float(np.dot(x, x))


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
```

The example is a software-level use of the minimization interface. Users can
replace `sphere` and the bounds with another continuous, box-constrained
objective without changing the optimizer API.

## Citation

Citation metadata for the software and the accompanying manuscript are stored
in `CITATION.cff`. Citation managers that support the Citation File Format can
read that file directly.

The accompanying manuscript is titled *Subspace Rotation Gradient Field
Adaptive Differential Evolution for Constrained Three-Dimensional UAV Path
Planning*. The software metadata identify version `1.0.0` and the manuscript
authors.

## License

The source is available for inspection, evaluation, and execution under the
terms in `LICENSE`.
