---
name: test-writer
description: "Write pytest tests for the eve-sd project. Use when asked to write, add, create, or generate tests; implement TDD red/green cycle; test a function, class, or module; add test coverage; write unit tests or integration tests. Covers: test file layout, fixtures, markers, test data, conftest patterns, and project conventions."
argument-hint: "describe the function, class, or module to test"
---

# Test Writer

## Project Test Conventions

- **Framework**: pytest with `pytest-cov`
- **Test root**: `tests/`
- **Mirror layout**: test files mirror `src/eve_sd/` — e.g., `src/eve_sd/helpers/json_io.py` → `tests/eve_sd/helpers/test_json_io.py`
- **Naming**: test files are `test_<module>.py`; test functions are `test_<description>()`
- **Python**: 3.14 syntax, full type hints, Google-style docstrings
- **Style**: formatted/linted with `ruff` (88-char line limit, PEP 8)
- **TDD**: red/green cycle — write the failing test first, then implement

## Test Data

SDE test data lives in `tests/resources/sde_data/`:
- `tests/resources/sde_data/__init__.py` — shared constants / data helpers
- `tests/resources/sde_data/jsonl/` — sample `.jsonl` files (first ~3 rows of real data)
- `tests/resources/sde_data/yaml/` — sample YAML equivalents

Import test data like:
```python
from importlib.resources import files as resource_files

```

## Conftest & Fixtures

Root `conftest.py` (`tests/conftest.py`) provides:
- `test_output_dir` (session-scoped `tmp_path_factory`) — use for output file tests
- `--runslow` CLI flag — gate expensive tests with `@pytest.mark.slow`

Add module-level fixtures to the nearest `conftest.py` for that subtree.

## Markers

| Marker | Usage |
|--------|-------|
| `@pytest.mark.slow` | Tests that hit network, disk, or take > 1 s |

```python
@pytest.mark.slow
def test_download_sde() -> None: ...
```

## Standard Test File Template

```python
"""Tests for <module path>."""

import pytest

from eve_sd.<module_path> import <SymbolUnderTest>


class TestSymbolUnderTest:
    """Tests for <SymbolUnderTest>."""

    def test_happy_path(self) -> None:
        """<SymbolUnderTest> returns expected result for valid input."""
        result = <SymbolUnderTest>(...)
        assert result == ...

    def test_edge_case_empty_input(self) -> None:
        """<SymbolUnderTest> handles empty input correctly."""
        ...

    def test_raises_on_invalid_input(self) -> None:
        """<SymbolUnderTest> raises ValueError for invalid input."""
        with pytest.raises(ValueError):
            <SymbolUnderTest>(invalid_arg)
```

## Procedure

1. **Identify the target** — module path, class/function name, public API surface.
2. **Read the source file** — understand inputs, outputs, side-effects, and error conditions.
3. **Determine the test file path** — mirror the source path under `tests/eve_sd/`.
4. **Check for existing tests** — read the test file if it exists; don't duplicate.
5. **List test cases** — happy path, edge cases, error paths, slow/integration tests.
6. **Write failing tests first** (red) — import and call; assert expected outcomes.
7. **Verify tests fail** — run `pytest <test_file> -v` in the `.venv`.
8. **Implement or confirm implementation** — only fix source if asked.
9. **Verify tests pass** (green) — run pytest again.
10. **Check coverage** if needed: `pytest --cov=eve_sd <test_file>`.

## Running Tests

```bash
# All tests (fast)
pytest

# All tests including slow
pytest --runslow

# Single file
pytest tests/eve_sd/helpers/test_json_io.py -v

# With coverage
pytest --cov=eve_sd --cov-report=term-missing
```

The virtual environment is at `.venv/` in the project root. Tests are run from the project root.
