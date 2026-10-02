"""Tests for the project's dependency manifest.

Task R1-1 asks for requirements to be pinned to exact versions (and for any
missing transitive dependencies to be declared) for packages used by the
loyalty discount feature (``app/order.py`` and ``app/loyalty.py``), instead
of loose/unpinned entries.

The project currently declares its dependencies in ``pyproject.toml``
(``[project.dependencies]``) rather than a ``requirements.txt``. These tests
guard the acceptance criteria regardless of which manifest file is used:

* any declared runtime dependency must be pinned to an exact version
  (``==``), never a loose/unbounded spec (bare name, ``>=``, ``~=``, ``*``...);
* the modules that implement the loyalty discount feature must not import
  any third-party package that is not declared in the manifest -- i.e. no
  missing transitive dependency for the feature this task is about.
"""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"

LOOSE_MARKERS = (">=", "<=", "~=", "!=", ">", "<")


def _load_pyproject() -> dict:
    with PYPROJECT_PATH.open("rb") as fh:
        return tomllib.load(fh)


def _is_exact_pin(spec: str) -> bool:
    """Return True if a dependency spec pins an exact version with '=='."""
    return "==" in spec


def _split_requirements_line(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    return line


# --- happy path / manifest shape ---------------------------------------


def test_pyproject_exists_and_is_parseable():
    assert PYPROJECT_PATH.exists()
    data = _load_pyproject()
    assert "project" in data


def test_declared_runtime_dependencies_are_exactly_pinned():
    """Every runtime dependency declared in pyproject.toml must use an
    exact '==' pin, never a loose/unbounded specifier."""
    data = _load_pyproject()
    dependencies = data.get("project", {}).get("dependencies", [])
    assert isinstance(dependencies, list)
    for dep in dependencies:
        assert _is_exact_pin(dep), f"dependency {dep!r} is not pinned to an exact version"
        for marker in LOOSE_MARKERS:
            assert marker not in dep.replace("==", ""), (
                f"dependency {dep!r} looks like a loose/range specifier, not an exact pin"
            )


def test_declared_runtime_dependencies_have_no_bare_unversioned_entries():
    """No runtime dependency may be a bare package name with no version
    constraint at all (e.g. 'requests')."""
    data = _load_pyproject()
    dependencies = data.get("project", {}).get("dependencies", [])
    for dep in dependencies:
        assert any(c in dep for c in ("==", ">=", "<=", "~=", "!=", ">", "<")), (
            f"dependency {dep!r} has no version specifier at all"
        )


def test_requirements_txt_if_present_is_fully_pinned():
    """If a requirements.txt exists alongside pyproject.toml, every
    non-comment, non-blank entry must be an exact pin."""
    if not REQUIREMENTS_PATH.exists():
        pytest_skip_reason = "no requirements.txt in this project"
        import pytest

        pytest.skip(pytest_skip_reason)

    lines = [
        parsed
        for raw in REQUIREMENTS_PATH.read_text().splitlines()
        if (parsed := _split_requirements_line(raw)) is not None
    ]
    for entry in lines:
        assert _is_exact_pin(entry), f"requirements.txt entry {entry!r} is not pinned (needs '==')"


# --- no missing transitive dependencies for the loyalty discount feature --


def _third_party_imports(path: Path) -> set[str]:
    """Return the set of top-level module names imported by the file at
    `path` that are not part of the Python standard library and not the
    project's own `app` package."""
    tree = ast.parse(path.read_text(), filename=str(path))
    stdlib = set(sys.stdlib_module_names)
    third_party: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in stdlib and top != "app":
                    third_party.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            top = node.module.split(".")[0]
            if top not in stdlib and top != "app":
                third_party.add(top)
    return third_party


def test_loyalty_discount_feature_has_no_undeclared_third_party_imports():
    """app/order.py and app/loyalty.py implement the loyalty discount
    feature this task's requirements pinning is about. They must not rely
    on any third-party package that isn't declared (and pinned) in the
    project's dependency manifest -- i.e. no missing transitive
    dependency."""
    data = _load_pyproject()
    declared = data.get("project", {}).get("dependencies", [])
    declared_names = {dep.split("==")[0].strip().lower() for dep in declared}

    feature_files = [REPO_ROOT / "app" / "order.py", REPO_ROOT / "app" / "loyalty.py"]
    for file_path in feature_files:
        assert file_path.exists()
        third_party = _third_party_imports(file_path)
        undeclared = {name for name in third_party if name.lower() not in declared_names}
        assert not undeclared, (
            f"{file_path} imports third-party package(s) {undeclared} "
            "that are not declared in pyproject.toml dependencies"
        )
