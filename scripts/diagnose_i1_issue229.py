"""#229 development diagnostic: independent living I1, no commanded food actions.

This is an *exploratory diagnostic*, not A2.39 confirmation or a prospective
effect-size estimate. The three direct WorldBody commands are technician-only
physical controls, explicitly excluded from autonomous I1 action counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from build_i1_fork import generate
from i1_a238_fixtures import references
from i1_a238_model import sealed_model
from i1_a239_fixtures import world_case, factor_flags


def main(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="i1-229-diagnosis-") as temporary:
        generated = Path(temporary) / "built"
        generate(generated)
        sys.path.insert(0, str(generated))
        from i1lab.i1_a239_runtime import I1A239ExperimentalRuntime
        from i1lab.world import WorldBody
        from i1lab.journal import HashChainedJournal
        from i1.modules.simulator import state_from_capture
        from i1.interfaces import PrimitiveCommand

        s11, c11, c10, policy = references()
        model, seal = sealed_model(Path(temporary) / "training")
        physical, layout, conf, _, _ = world_case(
            s11, c11, "ACQUIRE_THEN_EAT_LOCAL", 0, "H1_ONLY"
        )
        flags = factor_flags("H1_ONLY")
        life = I1A239ExperimentalRuntime(
            world_config=physical, layout=layout,
            safety_config=s11.stage3.substrate.safety._config,
            safety_facts=s11._canonical_safety._innate,
            protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
            stage11_config=conf, stage10_config=c10,
            equipment=s11.equipment, autonomous_mortal=True,
            wal_path=str((output / "baseline.wal").resolve()),
            birth_life_id="i1:issue229:diagnostic:baseline:00",
            detector_policy=policy, diagnostic_sample_cost_uc=1,
            module_occupancy_cost_uc=1,
            i1_model_enabled=True, i1_model=model, i1_forecast_cost_uc=2,
            i1_lived_recall_enabled=True, i1_recall_cost_uc=1,
            i1_water_probe_enabled=True, i1_water_learning_enabled=True,
            i1_water_consider_uc=2, i1_water_acquire_uc=2,
            i1_d2_prudence=True, i1_d2_review_uc=1, **flags,
            i1_a238_need_review_uc=1, i1_a238_move_review_uc=3,
            i1_a238_max_move_reviews=2
        )
        steps = []
        for _ in range(14):
            before = dict(life.world.telemetry())
            before_inv = dict(life.world.inventory())
            start = len(life.journal.entries)
            result = life.run_step()
            capture = life.stage3._capture
            if capture is None:
                raise AssertionError("I1 was not actually perceptually captured")
            state = state_from_capture(
                capture=capture, is_night=life.world.is_night(capture.t_monde)
            )
            candidates = [command.as_dict() for command in
                          life.planning.candidate_commands(state)]
            events = [dict(entry.causal_event)
                      for entry in life.journal.entries[start:]]
            steps.append({
                "t_monde": capture.t_monde,
                "body_before": before,
                "body_after": dict(life.world.telemetry()),
                "inventory_before": before_inv,
                "inventory_after": dict(life.world.inventory()),
                "perceived_inventory": dict(state.inventory),
                "perceived_local_resources": list(state.current_resources),
                "goal_pressure": life.goal_manager._latest_pressure.get(("eat", "food")),
                "active_goal": None if life.goal_manager.active_goal is None
                               else life.goal_manager.active_goal.goal_type,
                "candidate_commands": candidates,
                "planner_result": life.planning.last_search_diagnostic,
                "partial_options": [e["data"] for e in events
                                    if e.get("kind") ==
                                    "i1_partial_instrumental_option_proposed"],
                "competition_scores": [e["data"] for e in events
                                        if "competition" in e.get("kind", "")
                                        or e.get("kind") == "stage8_option_evaluation"],
                "rejection_reasons": [e for e in events
                                      if "reject" in e.get("kind", "")
                                      or "block" in e.get("kind", "")],
                "selected_option": result.option_ref,
                "admitted_command": [e["data"] for e in events
                                     if e.get("kind") == "command_admitted"],
                "executed_command": result.command_primitive,
                "execution_status": result.execution_status,
                "uc_charges": [e["data"] for e in events
                               if e.get("kind") == "compute_charge"],
                "physical_outcome": [e for e in events
                                     if "world" in e.get("kind", "")
                                     or "transition" in e.get("kind", "")],
                "memory_events": [e for e in events
                                  if "memory" in e.get("kind", "")
                                  or "episode" in e.get("kind", "")],
            })
            if result.execution_status != "applied":
                break

        # Physical controls: NEVER a command to the born individual above.
        empty = WorldBody(config=physical, layout=layout)
        empty_result = empty.apply(PrimitiveCommand("manger", {"target": "berry_b"}), t_monde=1)
        filled = WorldBody(config=physical, layout=layout)
        collection = filled.apply(PrimitiveCommand("collecter", {"target": "berry_b"}), t_monde=1)
        before_eating = filled.telemetry()["food"]
        consumption = filled.apply(PrimitiveCommand("manger", {"target": "berry_b"}), t_monde=2)
        toxic_layout = replace(layout, resources=((physical.initial_position, "berry_a", 1),))
        toxic = WorldBody(config=physical, layout=toxic_layout)
        toxic.apply(PrimitiveCommand("collecter", {"target": "berry_a"}), t_monde=1)
        toxic_result = toxic.apply(PrimitiveCommand("manger", {"target": "berry_a"}), t_monde=2)
        controls = {
            "operator_only": True,
            "empty_inventory_effect": empty_result.effects,
            "collection_effect": collection.effects,
            "ingestion_effect": consumption.effects,
            "ingestion_inventory_after": dict(filled.inventory()),
            "ingestion_positive_net_food": filled.telemetry()["food"] > before_eating,
            "toxic_ingestion_effect": toxic_result.effects,
            "toxic_ingestion_terminal": toxic_result.lethal,
        }
        assert life.journal.verify()
        audit = HashChainedJournal.audit_durable_wal(str((output / "baseline.wal").resolve()))
        assert audit["head_hash"] == life.journal.head_hash
        assert empty_result.effects["ate"] == "unavailable"
        assert controls["ingestion_positive_net_food"]
        assert toxic_result.lethal
        had_collection = any(s["executed_command"] == "collecter"
                             and s["inventory_after"]["berry_b"] > s["inventory_before"]["berry_b"]
                             for s in steps)
        had_postcollect_candidate = any(
            s["inventory_before"]["berry_b"] > 0
            and any(c["primitive"] == "manger" for c in s["candidate_commands"])
            for s in steps
        )
        assert had_collection, "historical failure not reproduced in this life"
        assert had_postcollect_candidate, "no observed postcollection decision state"
        report = {
            "schema": "i1-issue229-development-diagnosis-v1",
            "reference": "a239:af5006612b45b46d5ee2b2ed9e97b9cf6e104167",
            "model_corpus": seal,
            "autonomous_steps": steps,
            "operator_only_physical_controls": controls,
            "autonomous_collection": had_collection,
            "postcollection_manger_affordance": had_postcollect_candidate,
            "autonomous_ingestion_count": sum(s["executed_command"] == "manger"
                                               for s in steps),
            "journal_head_sha256": life.journal.head_hash,
            "wal_audit": {"head_matches_journal": True},
        }
        (output / "diagnosis.json").write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n"
        )
        print(json.dumps({
            "diagnosis": "COMPLETE", "collections": had_collection,
            "manger_candidate_postcollection": had_postcollect_candidate,
            "autonomous_ingestion_count": report["autonomous_ingestion_count"],
            "executed": [s["executed_command"] for s in steps],
            "wal_ok": True
        }, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output)
