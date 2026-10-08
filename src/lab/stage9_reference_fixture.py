"""Stage-9 fixture: inherits immutable Stage-8 software reference parameters."""
from __future__ import annotations

from i0.modules.causal_model import CausalModelConfig
from .stage8_reference_fixture import build_stage8_reference_runtime
from .stage9_runtime import Stage9Config, Stage9Runtime


def build_stage9_reference_runtime() -> Stage9Runtime:
    previous = build_stage8_reference_runtime()
    return Stage9Runtime(
        world_config=previous.world.config,
        layout=previous.world._layout,
        safety_config=previous.stage3.substrate.safety._config,
        safety_facts=previous.stage3.control._facts,
        protected_integrity_threshold=(
            previous.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage9Config(
            version="stage9-reference-v1",
            stage8=previous._stage8_config,
            causal=CausalModelConfig(
                version="p35-p36-stage9-reference-v1",
                n1=2, n2=2, n_sec=2, m_sec=2,
            ),
        ),
        equipment=previous.equipment,
    )
