from __future__ import annotations

import ast

FORBIDDEN_ROOTS = frozenset({"fastapi", "sqlalchemy", "langchain", "langgraph"})
MODULES_ROOT = ("time_agent", "modules")


def _absolute_imported_modules(source: str) -> frozenset[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            modules.add(node.module)
    return frozenset(modules)


def _relative_imported_modules(
    node: ast.ImportFrom,
    current_module: str,
    domain_subpackage_depth: int,
) -> tuple[str, ...]:
    source_package = [
        *MODULES_ROOT,
        current_module,
        "domain",
        *(["__subpackage__"] * domain_subpackage_depth),
    ]
    parent_levels = node.level - 1
    if parent_levels > len(source_package):
        return ()
    base_package = source_package[: len(source_package) - parent_levels]
    if node.module is not None:
        return (".".join([*base_package, node.module]),)
    return tuple(".".join([*base_package, alias.name]) for alias in node.names)


def find_forbidden_imports(source: str) -> frozenset[str]:
    roots = {module.partition(".")[0] for module in _absolute_imported_modules(source)}
    return frozenset(roots & FORBIDDEN_ROOTS)


def find_cross_module_imports(
    source: str,
    current_module: str,
    *,
    domain_subpackage_depth: int = 0,
) -> frozenset[str]:
    imported_modules: set[str] = set()
    modules = set(_absolute_imported_modules(source))
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            modules.update(
                _relative_imported_modules(node, current_module, domain_subpackage_depth)
            )
    for module in modules:
        parts = module.split(".")
        if len(parts) >= 3 and tuple(parts[:2]) == MODULES_ROOT:
            imported_module = parts[2]
            if imported_module != current_module:
                imported_modules.add(imported_module)
    return frozenset(imported_modules)
