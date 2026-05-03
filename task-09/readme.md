## Plugin Architecture with Dynamic Module Loading

**Description:** Design an application core that discovers, loads, and manages plugins at runtime. Support lifecycle hooks, dependency resolution, and sandboxed execution.

**Prerequisites:**

- `importlib` and `importlib.metadata`
- Abstract base classes (`abc.ABC`, `@abstractmethod`)
- Decorators and class registries
- `pyproject.toml` entry points
- Dependency graph resolution (topological sort)
- Error handling and graceful degradation

