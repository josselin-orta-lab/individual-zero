"""Stage-7 deterministic memory compatibility fixture.

P-34 values here are software-compatibility values, not campaign calibration.
"""

from __future__ import annotations

from i0.modules.memory import MemoryConfig

from .stage6_reference_fixture import build_stage6_reference_runtime
from .stage7_runtime import Stage7Config, Stage7Runtime


def build_stage7_reference_runtime(*, autonomous_mortal: bool = False) -> Stage7Runtime:
    stage6 = build_stage6_reference_runtime(autonomous_mortal=autonomous_mortal)
    return Stage7Runtime(
        world_config=stage6.world.config,
        layout=stage6.world._layout,
        safety_config=stage6.stage3.substrate.safety._config,
        safety_facts=stage6.stage3.control._facts,
        protected_integrity_threshold=(
            stage6.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage7Config(
            version="stage7-reference-v1",
            stage6=stage6.stage6_config,
            memory=MemoryConfig(
                version="p34-stage7-reference-v1",
                prediction_error_multiplier=2.0,
                max_episode_steps=2,
                link_delta_steps=2,
                recall_threshold=0.25,
                recall_weight_recency=0.5,
                recall_weight_importance=0.25,
                recall_weight_relevance=1.0,
                recall_recency_scale_steps=20,
                contribution_ttl_steps=4,
            ),
        ),
        equipment=stage6.equipment,
        autonomous_mortal=autonomous_mortal,
    )
