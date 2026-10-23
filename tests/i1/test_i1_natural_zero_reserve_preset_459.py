"""#459: read-only natural M11 depletion postmortem, no scripted commands."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalM11Depletion459(unittest.TestCase):
    def test_registered_empty_land_after_physical_exhaustion(self):
        with TemporaryDirectory(prefix="i1-459-") as temp:
            code = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import execute

with TemporaryDirectory(prefix="i1-459-empty-") as d:
    output = Path(d) / "natural-m11"
    report = execute(
        preset_name="empty-land", seed=246, steps=55,
        lives=1, custody="m11", output_dir=output,
    )
    assert report["status"] == "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT", report
    assert report["environment"]["world_physics_digest_kind"] == "input_prebirth_config"
    life = report["lives"][0]
    assert life["effective_birth_physics"]["zero_reserve_lethal"] is True
    assert "v4-metabolic-coupling" in life["effective_birth_physics"]["version"]
    assert life["effective_birth_physics"]["digest"] != report["environment"]["world_physics_digest"]
    assert life["steps"]
    assert len(life["steps"]) <= 55
    assert [row["generation"] for row in life["steps"]] == list(
        range(1, len(life["steps"]) + 1))
    assert all(row["body_after"]["integrity"] > 0 for row in life["steps"])
    assert all(row["terminal_reasons"] == [] for row in life["steps"][:-1])
    last = life["steps"][-1]
    physical = [x["physical_journal_observation"] for x in life["steps"]]
    assert all(x is not None for x in physical), (
        "unadmitted physical step is not a metabolic observation")
    assert all(x["body_after"] == life["steps"][i]["body_after"]
               for i, x in enumerate(physical))
    sleep_count = sum(x["primitive"] == "dormir" for x in physical)
    energy_gain = sum(max(0.0, x["body_after"]["energy"] -
                          x["body_before"]["energy"]) for x in physical)
    food_consumed = sum(x["body_before"]["food"] -
                        x["body_after"]["food"] for x in physical)
    assert sleep_count > 0
    assert food_consumed > 0
    assert all(x["body_after"]["water"] <= x["body_before"]["water"]
               for x in physical)
    assert all(x["body_after"]["food"] <= x["body_before"]["food"]
               for x in physical)
    print("I1_463_M11_METABOLIC_FLOW", sleep_count, energy_gain,
          food_consumed, "decisions", len(physical))
    # #465: 43 physical dormir steps are not 43 choices. Verify strict
    # provenance using already paid first-person journals and M11 receipts.
    sleep_rows = [
        (row["world_step"], row["sleep_custody_observation"])
        for row in life["steps"] if row["physical_journal_observation"][
            "primitive"] == "dormir"
    ]
    classes = {name: [step for step, val in sleep_rows
                      if val["provenance"] == name]
               for name in ("ordinary_awake_admission",
                            "readmitted_after_wake",
                            "reduced_sleep_continuation")}
    assert sum(map(len, classes.values())) == sleep_count
    assert all(life["steps"][step-1]["sleep_custody_observation"][
               "paid_competition_cycles"] == 0
               for step in classes["reduced_sleep_continuation"])
    assert all(life["steps"][step-1]["sleep_custody_observation"][
               "paid_competition_cycles"] > 0
               for step in classes["ordinary_awake_admission"]
               + classes["readmitted_after_wake"])
    assert all(v["pressure"] is not None for _, v in sleep_rows)
    assert all(v["wake_reason"] is not None for _, v in sleep_rows
               if v["provenance"] == "readmitted_after_wake")
    near_full = [step for step, _ in sleep_rows if physical[step - 1][
        "body_before"]["energy"] >= 99.0]
    no_recovery = [step for step, _ in sleep_rows if physical[step - 1][
        "body_after"]["energy"] <= physical[step - 1][
        "body_before"]["energy"]]
    critical_dormir = [step for step, v in sleep_rows
                       if v["reduced_critical_channels"] and "water" in
                       v["reduced_critical_channels"]]
    # #467: prove which genuine physical steps became Memory-visible.
    # An AutoSegmentCommit after dispatch is not retroactive ingestion
    # during a reduced sleep step. Never count raw technical journal rows
    # as recalled episodes or claimed consolidation.
    memory_rows = [
        (row["world_step"], row["autobiographical_sleep_custody_467"])
        for row in life["steps"]
    ]
    physically_committed = sum(
        bool(x["auto_commit_count"]) for _, x in memory_rows)
    reduced_with_autobio = sum(
        bool(x["auto_commit_count"])
        for i, (_, x) in enumerate(memory_rows)
        if life["steps"][i]["sleep_custody_observation"]["provenance"]
        == "reduced_sleep_continuation")
    sleep_without_memory_ingestion = sum(
        x["physical_refs_seen_by_memory_after_commit"] == 0
        for i, (_, x) in enumerate(memory_rows)
        if physical[i]["primitive"] == "dormir")
    closed_episodes = sum(len(x["episodes_closed_during_step"])
                          for _, x in memory_rows)
    latest_h = memory_rows[-1][1]["slow_history_version"]
    assert physically_committed > 0
    assert sleep_without_memory_ingestion >= 0
    # #469: compare real first-person physical source custody without
    # assuming an immediate Memory ingestion or a future replay.
    ref_rows = life["physical_memory_custody_469"]
    assert len(ref_rows) == 2 * len(physical)
    assert len({x["source_ref"] for x in ref_rows}) == len(ref_rows)
    sleep_refs = [x for x in ref_rows if x["primitive"] == "dormir"]
    assert len(sleep_refs) == 2 * sleep_count
    assert all(x["memory_ingestion_step"] is None
               or x["memory_ingestion_step"] >= x["step"]
               for x in ref_rows)
    assert all(x["autobiographical_commit_step"] is None
               or x["autobiographical_commit_step"] >= x["step"]
               for x in ref_rows)
    assert all(x["memory_ingestion_step"] is None
               or x["autobiographical_commit_step"] is not None
               for x in ref_rows)
    missing_commit = sum(x["autobiographical_commit_step"] is None
                         for x in sleep_refs)
    missing_ingestion = sum(x["memory_ingestion_step"] is None
                            for x in sleep_refs)
    lagged = [x["memory_ingestion_step"] - x["step"]
              for x in sleep_refs if x["memory_ingestion_step"] is not None]
    print("I1_469_SLEEP_MEMORY_LAG",
          "source_refs", len(sleep_refs),
          "without_commit", missing_commit,
          "without_ingestion_by_death", missing_ingestion,
          "ingestion_delays", sorted(set(lagged)),
          "max_delay", max(lagged, default=None))
    print("I1_467_SLEEP_MEMORY_CUSTODY",
          "physical_autobiographical_commits", physically_committed,
          "reduced_autobiographical_commits", reduced_with_autobio,
          "sleep_steps_without_immediate_memory_ingestion",
          sleep_without_memory_ingestion,
          "closed_episodes", closed_episodes,
          "last_h", latest_h)
    print("I1_465_SLEEP_PROVENANCE", classes,
          "at_energy_99", near_full, "without_energy_gain", no_recovery,
          "water_critical_reduced", critical_dormir,
          "paid_consolidation_commits", sum(
              x["sleep_custody_observation"]["consolidation_commits"]
              for x in life["steps"]),
          "paid_consolidation_passes", sum(
              x["sleep_custody_observation"][
                  "consolidation_pass_checkpoints"]
              for x in life["steps"]))
    from i1lab.sqlite_life_store import SQLiteLifeLedger
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(output / life["custody_file"]),
        expected_individual_id=life["individual_id"],
    )
    assert audit.generation == len(life["steps"])
    assert audit.journal_head == life["journal_head"]
    if life["lifecycle"] == "dead":
        assert last["lifecycle"] == "dead"
        assert any(x in last["terminal_reasons"]
                   for x in ("zero_water", "zero_food")), last
        assert (last["body_after"]["water"] == 0
                or last["body_after"]["food"] == 0)
        assert not audit.may_recover
    else:
        # Missing physical exposure is not a false forced death.
        assert life["lifecycle"] == "active"
        assert all(row["body_after"]["water"] > 0
                   and row["body_after"]["food"] > 0
                   for row in life["steps"])
    print("I1_459_M11_OBSERVED", life["lifecycle"], len(life["steps"]),
          last["terminal_reasons"], last["body_after"])
"""
            # The world runner creates its own generated I1 fork.
            process = subprocess.run(
                [sys.executable, "-B", "-c", code],
                env={"PYTHONPATH": str(ROOT / "tools") + ":" + str(ROOT / "src")},
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("I1_459_M11_OBSERVED", process.stdout)
            # The real observed status is surfaced in CI instead of hidden
            # inside the subprocess. This cannot influence the living agent.
            print(process.stdout.strip(), flush=True)


if __name__ == "__main__":
    unittest.main()
