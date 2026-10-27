"""Laboratory-only matched temperament projection, never a living-state clone.

A four-arm cohort may use the same pure temperament source while retaining
independent identities, personal memory, and immutable mortal WAL custody.
This utility only builds a configuration; it never births or steps an actor.
"""
from __future__ import annotations

from .i1_birth_temperament import configure_birth_temperament


def matched_temperament_configuration(stage11_config, *, life_id: str,
                                      world: str, seed: int):
    if type(world) is not str or not world or len(world)>64 or ":" in world:
        raise ValueError("bounded lab world name required")
    if type(seed) is not int or seed < 0:
        raise ValueError("nonnegative deterministic lab seed required")
    source=f"i1:research-twin:{world}:{seed}"
    return configure_birth_temperament(
        stage11_config,life_id=life_id,temperament_source_id=source,
    )
