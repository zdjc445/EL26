from pathlib import Path

from tests.architecture.rules import find_cross_module_imports, find_forbidden_imports

MODULES = Path(__file__).resolve().parents[2] / "src" / "time_agent" / "modules"


def test_rule_detects_framework_imports() -> None:
    source = "from fastapi import APIRouter\nimport sqlalchemy.orm\n"

    assert find_forbidden_imports(source) == frozenset({"fastapi", "sqlalchemy"})


def test_rule_allows_standard_library_and_own_domain_imports() -> None:
    source = (
        "from dataclasses import dataclass\nfrom time_agent.modules.calendar.domain import Event\n"
    )

    assert find_forbidden_imports(source) == frozenset()
    assert find_cross_module_imports(source, current_module="calendar") == frozenset()


def test_rule_detects_cross_module_internal_imports() -> None:
    source = "from time_agent.modules.knowledge.domain import Document\n"

    assert find_cross_module_imports(source, current_module="calendar") == frozenset({"knowledge"})


def test_repository_domain_files_respect_module_boundaries() -> None:
    violations: dict[str, dict[str, frozenset[str]]] = {}
    for module_path in (path for path in MODULES.iterdir() if path.is_dir()):
        for path in (module_path / "domain").glob("**/*.py"):
            source = path.read_text(encoding="utf-8")
            frameworks = find_forbidden_imports(source)
            cross_module = find_cross_module_imports(source, current_module=module_path.name)
            if frameworks or cross_module:
                violations[str(path.relative_to(MODULES))] = {
                    "frameworks": frameworks,
                    "cross_module": cross_module,
                }

    assert violations == {}
