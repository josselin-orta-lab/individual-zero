"""Infrastructure de laboratoire, sans chargement implicite d'I0.

The public bootstrap symbols are exported lazily for backwards compatibility.
Importing independent journal auditing or Bench utilities must not import the
cognitive runtime, Oracle or scientific evaluation services as a side effect.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime import RunConfig, RunSummary, run_individual

__all__ = ["RunConfig", "RunSummary", "run_individual"]


def __getattr__(name: str):
    if name in __all__:
        from .runtime import RunConfig, RunSummary, run_individual

        return {
            "RunConfig": RunConfig,
            "RunSummary": RunSummary,
            "run_individual": run_individual,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
