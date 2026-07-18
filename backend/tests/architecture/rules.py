from __future__ import annotations

import ast

FORBIDDEN_ROOTS = frozenset({"fastapi", "sqlalchemy", "langchain", "langgraph"})


def _imported_modules(source: str) -> frozenset[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return frozenset(modules)


def find_forbidden_imports(source: str) -> frozenset[str]:
    roots = {module.partition(".")[0] for module in _imported_modules(source)}
    return frozenset(roots & FORBIDDEN_ROOTS)


def find_cross_module_imports(source: str, current_module: str) -> frozenset[str]:
    imported_modules: set[str] = set()
    for module in _imported_modules(source):
        parts = module.split(".")
        if len(parts) >= 3 and parts[:2] == ["time_agent", "modules"]:
            imported_module = parts[2]
            if imported_module != current_module:
                imported_modules.add(imported_module)
    return frozenset(imported_modules)
