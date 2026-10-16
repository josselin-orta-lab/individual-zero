"""Single canonical I1 birth entry point, without laboratory ablation arms.

The caller supplies an actual world, perception-safe layout, frozen Stage11
and Stage10 contracts, equipment and Stage12 diagnostic policy. All natural
I1 traits and capacities are installed by I1Runtime, not by experiment flags.
The resulting actor remains mortal and journalled by the existing executive.
"""
from __future__ import annotations

from .i1_natural_runtime import I1Runtime


def birth_i1(*, life_id: str, world_config, layout, safety_config,
             safety_facts, protected_integrity_threshold, stage11_config,
             stage10_config, equipment, detector_policy,
             wal_path: str, diagnostic_sample_cost_uc: int = 1,
             module_occupancy_cost_uc: int = 1) -> I1Runtime:
    if (type(life_id) is not str or not life_id.startswith("i1:")
            or not life_id.strip() or not wal_path):
        raise ValueError("ordinary I1 birth needs unique identity and durable WAL")
    return I1Runtime(
        birth_life_id=life_id,
        world_config=world_config, layout=layout,
        safety_config=safety_config, safety_facts=safety_facts,
        protected_integrity_threshold=protected_integrity_threshold,
        stage11_config=stage11_config, stage10_config=stage10_config,
        equipment=equipment, detector_policy=detector_policy,
        diagnostic_sample_cost_uc=diagnostic_sample_cost_uc,
        module_occupancy_cost_uc=module_occupancy_cost_uc,
        autonomous_mortal=True, wal_path=wal_path,
    )
