# SRGFADE anonymous release verification

Verification completed: 2026-07-12T08:33:46Z

Publication-rigor refresh verified: 2026-07-12T08:57:09Z

Public repository: https://github.com/cxbrucewayen/SRGFADE

## 1. Scope and anonymous access

The verification used public HTTPS endpoints and a new clone outside the
release directory. Git terminal prompting was disabled and the credential
helper was disabled for remote reads and cloning. No credential was supplied,
printed, or stored by the verification commands.

The cold environment used Windows 10 Professional 10.0.19045, Git 2.48.1,
Python 3.11.5, pip 26.1.2, NumPy 2.4.6, and pytest 9.1.1. The clone and its
virtual environment were created below the system temporary directory.

## 2. Public URL observations

| Resource | URL | HTTP result | Observed page or content |
| --- | --- | ---: | --- |
| Repository | https://github.com/cxbrucewayen/SRGFADE | 200 | Page title identified `cxbrucewayen/SRGFADE` |
| Licence page | https://github.com/cxbrucewayen/SRGFADE/blob/main/LICENSE | 200 | Page title identified `SRGFADE/LICENSE at main` |
| Citation page | https://github.com/cxbrucewayen/SRGFADE/blob/main/CITATION.cff | 200 | Page title identified `SRGFADE/CITATION.cff at main` |
| Release page | https://github.com/cxbrucewayen/SRGFADE/releases/tag/v1.0.0 | 200 | Page title identified `Release v1.0.0` |
| Raw licence | https://raw.githubusercontent.com/cxbrucewayen/SRGFADE/main/LICENSE | 200 | SHA-256 `acb13d90090f25a88f27b66ba8f7963799c09b8df2a16dc33ff0b567dc965b66` |
| Raw citation metadata | https://raw.githubusercontent.com/cxbrucewayen/SRGFADE/main/CITATION.cff | 200 | SHA-256 `590b7b58538daaf8831d1ae401f593ec2f3fe696444a4f9862924c7d3f386b3c` |

The two raw-file hashes equal the hashes of the retained local release files.

## 3. Git references and payload relation

Anonymous `git ls-remote` and the cold clone returned these references:

| Reference | Remote SHA | Cold-clone SHA | Result |
| --- | --- | --- | --- |
| `refs/heads/main` | `ec06544ac9e473e2aaba20b49e23cd87c7543c25` | `ec06544ac9e473e2aaba20b49e23cd87c7543c25` | matched |
| `refs/tags/v1.0.0` | `700813feeb5cb7aabdfe77ce7db67e0d1ea13926` | `700813feeb5cb7aabdfe77ce7db67e0d1ea13926` | matched |

The tag fixes the version 1.0.0 release payload. A name-status comparison from
`v1.0.0` to the verified `main` commit reported only
`A release-manifest.md` and `A release-verification.md`. The package, README,
licence, citation metadata, example, baseline record, and tests were identical
between the two references.

A later documentation-only commit on `main` adds this report and its manifest
whitelist entry. That commit does not change the version 1.0.0 payload.

## 4. Commands and results

The anonymous clone used:

```text
git -c credential.helper= clone --no-local https://github.com/cxbrucewayen/SRGFADE.git <temporary-directory>/SRGFADE
```

The isolated installation and reader-facing checks followed the README:

```text
py -3.11 -m venv <temporary-directory>/.venv
<temporary-python> -m pip install --upgrade pip
<temporary-python> -m pip install -e ".[test]"
<temporary-python> -m pytest -rs
<temporary-python> examples/quick_start.py
git checkout --detach v1.0.0
<temporary-python> -m pip install -e ".[test]"
<temporary-python> -m pytest -rs
<temporary-python> examples/quick_start.py
```

| Checkout | Installation | Complete test suite | Quick start |
| --- | --- | --- | --- |
| `main` at `ec06544ac9e473e2aaba20b49e23cd87c7543c25` | completed | 28 passed, 0 skipped, 0 failed | completed; best fitness `0.149317796824`, 600 evaluations |
| `v1.0.0` at `700813feeb5cb7aabdfe77ce7db67e0d1ea13926` | completed | 28 passed, 0 skipped, 0 failed | completed; best fitness `0.149317796824`, 600 evaluations |

Both quick-start runs returned the same best position:

```text
[-0.24566152  0.07143378  0.01647773 -0.12203361  0.26211012]
```

## 5. Correction and rerun

The first cold-clone run on the preceding release payload collected 28 tests,
passed 23, and skipped five regression cases because they attempted to read an
authoritative source tree outside the public repository. This did not satisfy
the cold-clone criterion that the complete public suite run without private
workspace files.

The public regression module was changed to check five frozen result
observations established by the earlier authoritative comparison. The tests
now retain the fixed seeds, dimensions, budgets, default and nondefault
perturbation coefficients, objective values, positions, and evaluation-count
checks without accessing external source files. The updated suite was
committed, the `v1.0.0` payload was updated, and the full anonymous procedure
was repeated from a new clone and environment. The final results are those in
Section 4.

## 6. Publication-rigor refresh

A publication-rigor scan found two private workspace directory prefixes in the
baseline table. The table now identifies the frozen files by file name only;
the recorded SHA-256 values and byte counts are unchanged. The correction was
applied independently to `main` and the `v1.0.0` payload. A new anonymous clone
confirmed zero matches for private directory names, absolute local paths,
email addresses, legacy terminology, or credential-related terms on both
references. Both references again passed all 28 tests and produced identical
quick-start output.

## 7. Result and cleanup

The public repository pages, raw licence, raw citation metadata, anonymous Git
references, cold clone, README installation, complete tests, and quick start
all met their recorded criteria. The final verification has zero skipped
tests, zero failed tests, and zero unresolved release failures.

The temporary clone and virtual environment were deleted after the recorded
checks. The retained artifacts are the public repository, this report, and the
other release records in the repository.
