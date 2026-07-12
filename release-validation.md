# SRGFADE release validation

This report records software-release validation for the public SRGFADE
implementation. The checks below are not additional manuscript experiments,
and no expected result was copied from a manuscript table.

## 1. Setting

The primary release check used Windows 10, Python 3.11.5, NumPy 2.3.2,
pytest 7.4.4, and the package metadata in `pyproject.toml`. A supplementary
workspace check used Python 3.8.15, NumPy 1.24.4, and pytest 8.3.5. The latter
check exercises the source tree but is outside the declared Python 3.10 or
newer installation range.

The following commands were run from the release root:

```text
python -m pytest
py -3.11 -m pytest
```

A newly created temporary Python 3.11 environment was also used for a
non-editable package installation, an import-and-minimize smoke call, and:

```text
python examples/quick_start.py
```

The temporary environment and generated build and test caches were removed
after validation.

The fixed regression tolerances were set before the recorded comparisons:

- best objective value: relative tolerance `0.0`, absolute tolerance `1e-12`
- best position: relative tolerance `0.0`, absolute tolerance `1e-12`
- objective evaluations: exact integer equality

The comparison objective was a deterministic weighted shifted sphere. It was
selected as a small, continuous, box-constrained minimization objective that
does not depend on manuscript results.

## 2. Observation

### 2.1 Frozen source

The two authoritative SHA-256 values matched `BASELINE.md`:

| Component | Observed SHA-256 | Match |
| --- | --- | --- |
| Optimizer | `e710aa20da1be9688f62c61a6b854cb2f8f7c2708f651bcbf3981e111cef04a2` | yes |
| Shared base | `b2e26bae86f45790c635b82853cb23d2b3467fbe04a21a08f47d96401265a965` | yes |

### 2.2 Fixed-seed numeric regression

The public parameter name for the annealed Gaussian perturbation was mapped
to the corresponding authoritative argument. The default and one nondefault
coefficient were checked.

| Seed | Dimension | Population | Budget | Coefficient | Public best value | Maximum position difference | Evaluations |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 8 | 37 | 1.00 | `0.16901261352215655` | `0.0` | 37 |
| 42 | 5 | 12 | 113 | 1.00 | `1.8637621632670696` | `0.0` | 113 |
| 2026 | 8 | 16 | 257 | 1.00 | `7.1178227025984739` | `0.0` | 257 |
| 7 | 3 | 6 | 6 | 1.00 | `17.105992788783663` | `0.0` | 6 |
| 11 | 4 | 10 | 97 | 0.35 | `0.32591882265316419` | `0.0` | 97 |

For every case, the authoritative and public best values were equal at the
recorded precision, the best positions were element-wise equal, and both
implementations used the stated budget exactly.

### 2.3 Public-interface smoke checks

| Check | Observed result |
| --- | --- |
| Import surface | `SRGFADE`, `BaseAlgorithm`, and `OptimizationResult` imported successfully |
| Fixed-seed repeatability | A reused optimizer returned equal best values, positions, convergence values, and checkpoints |
| Budget accounting | Budgets 1, 10, 37, and 83 equaled both objective-call counts and reported evaluations |
| Boundary handling | Every evaluated point and the returned best position remained within heterogeneous bounds |
| Minimization result | The returned value and position equaled the smallest objective observation made during the run |
| Constructor errors | Invalid dimension, population, budget, bound shape, finite-bound, and bound-order cases raised `ValueError` |
| Objective errors | Non-finite and non-scalar objective values raised `ValueError` |
| Quick start | Completed and reported a best value, best position, and 600 evaluations |

The final suite results were:

```text
Python 3.8 source-tree check: 25 passed in 0.64s
Python 3.11 release check: 25 passed in 0.52s
```

The isolated Python 3.11 installation completed, the installed-package smoke
call completed with 41 counted evaluations, and the quick start completed.

### 2.4 Corrections made during validation

Pre-test interface inspection found that the release base accepted bound
vectors with an incorrect shape, non-finite bounds, reversed bounds, and
non-finite or non-scalar objective values without an explicit interface
error. `srgfade/base.py` now validates these cases before they can enter the
search loop. The change does not affect valid regression inputs, as confirmed
by the numeric comparisons above.

Terminology cross-checking also found a shortened name for the fourth
mechanism in the README and module documentation. These descriptions now use
the paper-aligned term `restricted simulated-annealing acceptance`. No
algorithmic statement or numeric operation was changed by this correction.

No test failed in the recorded final runs. The number of unresolved failures
is zero.

### 2.5 Release-content checks

The runtime package, README, example, and self-contained public tests contain
no historical algorithm identifier, historical mechanism wording,
control-layer phrases, credential markers, personal absolute paths, or
unfinished-work markers. The separate authoritative comparison harness mapped
the differing perturbation argument without exposing it in the public package.

No cache directory, nested Git metadata, or file larger than 1 MiB remained
in the release directory after cleanup. The inspected Python and test files
used UTF-8 without a byte-order mark and LF line endings. `LICENSE`,
`CITATION.cff`, package metadata, the example, and both test modules were
present.

## 3. Criteria

| Gate | Acceptance criterion | Result |
| --- | --- | --- |
| Numeric equivalence | Best value and position within the fixed tolerances; evaluations equal | passed |
| Repeatability | Same seed and instance reuse produce equal observable numeric results | passed |
| Budget | Reported evaluations do not exceed the requested budget and equal objective calls | passed |
| Bounds | All evaluated and returned positions remain in the supplied box | passed |
| Minimization interface | Result represents the smallest value observed | passed |
| Invalid input | Defined malformed inputs fail explicitly | passed |
| Quick start | Example completes through the public import surface | passed |
| Isolated installation | Non-editable installation, smoke call, and example complete in a new environment | passed |
| Release content | Terminology, sensitive-pattern, cache, metadata, size, encoding, and license checks pass | passed |

## 4. Conclusion

The public implementation met the fixed-seed numeric regression, import,
repeatability, budget, boundary, minimization, invalid-input, isolated-install,
and quick-start criteria under the recorded settings. All observed release
issues were corrected locally in the public copy, and zero unresolved
failures remain.
