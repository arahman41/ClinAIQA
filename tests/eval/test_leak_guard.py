"""
Leak guard: verify that tuning and scoring modules do NOT import a held-out loader.

The held-out set is only accessed in report_metrics.py. Importing either held-out
loader anywhere else in the evaluation or tuning pipeline invalidates the precision
and recall metric, which is the single most important discipline in this project
(see agent_docs/testing.md).
"""
from __future__ import annotations

import ast
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).parents[2]

# Both the in-memory split loader and the DB-backed loader are forbidden in
# tuning code. Either one leaking into the tuning path corrupts the metric.
_FORBIDDEN_SYMBOLS = (
    "load_heldout_for_final_report",
    "load_heldout_from_db_for_final_report",
)

_GUARDED_MODULES = [
    "clinaiqa/eval/rubric.py",
    "clinaiqa/eval/scorer.py",
    "clinaiqa/eval/runner.py",
    "clinaiqa/eval/metrics.py",
    "clinaiqa/eval/db_loader.py",
    "clinaiqa/data/split.py",
]


def _imported_symbols(path: pathlib.Path) -> set[str]:
    """Return the set of names this module imports (both `import x` and `from y import x`)."""
    src = path.read_text(encoding="utf-8")
    names: set[str] = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.name)
                if alias.asname:
                    names.add(alias.asname)
    return names


@pytest.mark.harness
@pytest.mark.parametrize("module_path", _GUARDED_MODULES)
def test_guarded_module_does_not_import_heldout_loader(module_path: str):
    full_path = _REPO_ROOT / module_path
    if not full_path.exists():
        pytest.skip(f"{module_path} not yet created")
    imported = _imported_symbols(full_path)
    leaked = imported & set(_FORBIDDEN_SYMBOLS)
    assert not leaked, (
        f"{module_path} must not import {sorted(leaked)}. "
        "A held-out loader is only allowed in report_metrics.py."
    )
