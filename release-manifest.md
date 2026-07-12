# SRGFADE release manifest

Publication time: 2026-07-12T08:31:17Z

Rigor-audit refresh: 2026-07-12T08:57:09Z

Public repository: https://github.com/cxbrucewayen/SRGFADE

## Git references

| Item | Local commit SHA | Remote commit SHA | Reference |
| --- | --- | --- | --- |
| Version 1.0.0 release payload | `700813feeb5cb7aabdfe77ce7db67e0d1ea13926` | `700813feeb5cb7aabdfe77ce7db67e0d1ea13926` | `refs/tags/v1.0.0` |

The `v1.0.0` tag fixes the release payload at the commit shown above. The
`main` branch contains the same payload and this manifest. The current `main`
commit is available from the public Git reference because a commit cannot
embed its own SHA in a file that contributes to that SHA.

The refresh changes only the baseline table labels and file-name presentation,
removing private workspace directory prefixes. The frozen source hashes,
package implementation, interface, examples, and tests are unchanged.

## Repository whitelist

The `main` branch contains exactly these files:

- `.gitignore`
- `BASELINE.md`
- `CITATION.cff`
- `LICENSE`
- `MANIFEST.in`
- `README.md`
- `examples/README.md`
- `examples/quick_start.py`
- `pyproject.toml`
- `release-manifest.md`
- `release-readiness-audit.md`
- `release-validation.md`
- `release-verification.md`
- `requirements.txt`
- `srgfade/__init__.py`
- `srgfade/base.py`
- `srgfade/core.py`
- `tests/README.md`
- `tests/test_regression.py`
- `tests/test_smoke.py`
