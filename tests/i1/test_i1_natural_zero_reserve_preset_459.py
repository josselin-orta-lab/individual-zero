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
    assert all(v["waking_capture_before_command"]
               for _, v in sleep_rows if v["provenance"] in (
                   "ordinary_awake_admission", "readmitted_after_wake"))
    assert all(v["wake_capture_after_control_boundary"]
               for _, v in sleep_rows
               if v["provenance"] == "readmitted_after_wake")
    assert all(not v["waking_capture_before_command"]
               and not v["wake_capture_after_control_boundary"]
               for _, v in sleep_rows
               if v["provenance"] == "reduced_sleep_continuation")
    # #495: verify dormant selector on real M11 source identities,
    # independent of the operator's wake label and with NO Memory write.
    assert all(v["dormant_wake_cue_eligible"]
               for _, v in sleep_rows
               if v["provenance"] == "readmitted_after_wake")
    assert all(not v["dormant_wake_cue_eligible"]
               for _, v in sleep_rows
               if v["provenance"] in (
                   "ordinary_awake_admission",
                   "reduced_sleep_continuation"))
    postwake = life["waking_perception_transition_custody_495"]
    assert len(postwake) >= len(classes["readmitted_after_wake"])
    assert {row["step"] for row in postwake} >= set(
        classes["readmitted_after_wake"])
    assert len({row["first_person_capture_ref"] for row in postwake}) == len(postwake)
    assert len({row["applied_transition_ref"] for row in postwake}) == len(postwake)
    for row in postwake:
        assert row["first_person_capture_ref"] != row["applied_transition_ref"]
        assert not row["capture_is_personal_memory"]
        assert not row["subjective_waking_boundary_proven"]
        assert not row["continuous_subjective_session_proven"]
        if row["transition_ingested_step"] is not None:
            assert row["transition_committed_step"] is not None
            assert row["transition_committed_step"] <= row["transition_ingested_step"]
    # #495 L2 custody: a personally permitted waking cue must not become
    # Memory-visible before its exact-source DC-09 commitment. Absence from
    # a closed episode is UNKNOWN, not fabricated continuous sleep memory.
    assert all(
        row["waking_autobiographical_ref"] is None
        or (row["waking_autobiographical_ref"]
            not in (row["first_person_capture_ref"],
                    row["applied_transition_ref"])
            and row["waking_commit_step"] is not None)
        for row in postwake
    )
    assert any(row["waking_autobiographical_ref"] is not None
               for row in postwake)
    for row in postwake:
        if row["waking_ingestion_step"] is not None:
            assert row["waking_commit_step"] <= row["waking_ingestion_step"]
        if row["waking_closed_episode_ref"] is not None:
            assert row["waking_ingestion_step"] is not None
    print("I1_495_WAKING_MEMORY_SOURCE_CUSTODY",
          "committed", sum(x["waking_commit_step"] is not None
                           for x in postwake),
          "ingested", sum(x["waking_ingestion_step"] is not None
                          for x in postwake),
          "closed", sum(x["waking_closed_episode_ref"] is not None
                        for x in postwake))
    print("I1_495_NATURAL_WAKE_TRANSITION_CUSTODY",
          "perceived", len(postwake),
          "committed", sum(x["transition_committed_step"] is not None
                           for x in postwake),
          "ingested", sum(x["transition_ingested_step"] is not None
                          for x in postwake),
          "closed", sum(x["closed_episode_ref"] is not None
                        for x in postwake))
    # A terminal physical transition is perceptible before death, but the
    # mortal boundary MUST NOT create a subsequent autobiographical commit.
    assert all(
        v["waking_dc09_committed"]
        or (v["waking_dc09_terminal_uncommitted"]
            and step == last["world_step"] and life["lifecycle"] == "dead")
        for step, v in sleep_rows
        if v["provenance"] == "readmitted_after_wake"
    )
    assert all(not v["waking_dc09_committed"]
               for _, v in sleep_rows
               if v["provenance"] in (
                   "ordinary_awake_admission",
                   "reduced_sleep_continuation"))
    assert sum(v["waking_dc09_terminal_uncommitted"]
               for _, v in sleep_rows) <= 1
    assert all(not v["waking_dc09_committed"]
               for _, v in sleep_rows if v["waking_dc09_terminal_uncommitted"])

    print("I1_495_NATIVE_WAKING_DC09",
          sum(v["waking_dc09_committed"] for _, v in sleep_rows),
          "postwake committed cues")
    print("I1_495_NATURAL_DORMANT_WAKE_ELIGIBILITY",
          sum(v["dormant_wake_cue_eligible"]
              for _, v in sleep_rows),
          "true_postwake_readmissions")
    print("I1_490_AUTHENTIC_WAKING_PERCEPTION",
          sum(v["wake_capture_after_control_boundary"]
              for _, v in sleep_rows),
          "woken_readmissions")
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
    # #474: actual cognitive access proof, not a manufactured sleep benefit.
    # Only previously closed, committed sources may appear in a recalled row.
    recall_rows = [row["sleep_site_recall_custody_467"]
                   for row in life["steps"]]
    paid = sum(row["paid_uc"] for row in recall_rows)
    reads = sum(row["read_count"] for row in recall_rows)
    witnesses = sum(row["witness_count"] for row in recall_rows)
    assert paid >= reads
    # #495: only links from already paid closed-source recall are reported.
    # No link or waking cue is inferred from technical wake markers.
    assert all(row["published_evidence"] is False for row in recall_rows)
    assert all(row["waking_link_count"] == len(row["waking_links"])
               for row in recall_rows)
    assert all(row["waking_link_count"] <= row["witness_count"]
               for row in recall_rows)
    assert all(row["waking_link_count"] == 0
               for row in recall_rows if not row["read_count"])
    for recall in recall_rows:
        for link in recall["waking_links"]:
            assert link["relation"] == "immediate_next_step_only"
            assert link["waking_step"] == link["sleep_step"] + 1
            assert len(link["sleep_source_refs"]) == 2
            assert all(ref in recall["source_event_refs"]
                       for ref in link["sleep_source_refs"])
            assert all(type(link[k]) is str and link[k]
                       for k in ("waking_cue_ref", "waking_cue_episode_ref",
                                 "waking_applied_command_ref",
                                 "waking_applied_transition_ref",
                                 "waking_applied_primitive"))
            assert len({link["waking_cue_ref"],
                        link["waking_applied_command_ref"],
                        link["waking_applied_transition_ref"]}) == 3
    distinct = life["distinct_paid_waking_links_audit_495"]
    assert distinct["paid_read_count"] == reads
    assert distinct["consulted_occurrences"] == sum(
        row["waking_link_count"] for row in recall_rows)
    assert 0 <= distinct["distinct_source_links"] <= distinct["consulted_occurrences"]
    assert distinct["repeated_consultations"] == (
        distinct["consulted_occurrences"] - distinct["distinct_source_links"])
    assert distinct["continuous_subjective_session_proven"] is False
    assert distinct["decision_influence_proven"] is False
    assert distinct["distinct_source_links"] > 0, distinct
    print("I1_495_DISTINCT_WAKING_LINKS", distinct)
    # #510: a naturally evaluated sleep candidate can see personally
    # recalled context at the pre-Competition boundary without a second Q,
    # Stage6, P-40 or Competition score.
    contexts = [step["sleep_site_stage8_context_custody_510"]
                for step in life["steps"]]
    assert all(row["read_count"] in (0, 1) and
               row["score_applied"] is False for row in contexts)
    assert all(context["read_count"] <= recall["read_count"]
               for context, recall in zip(contexts, recall_rows))
    assert all(context["source_refs"] == recall["source_event_refs"]
               for context, recall in zip(contexts, recall_rows)
               if context["read_count"])
    assert sum(row["read_count"] for row in contexts) > 0
    # #512: natural Q is explicitly spatial, so old personal experience
    # cannot be added a second time as an untested Memory site bonus.
    assert all(row["q_spatial_features_present"] is True for row in contexts)
    assert all({"x", "y", "energy", "food", "water", "integrity"}
               <= set(row["q_feature_names"]) for row in contexts)
    assert all(row["q_signature_general"] == "primitive:dormir"
               and row["independent_context_value_established"] is False
               for row in contexts)
    print("I1_512_NATURAL_SLEEP_Q_SPATIAL_OVERLAP",
          "observed", sum(x["read_count"] for x in contexts))
    print("I1_510_PAID_STAGE8_SLEEP_CONTEXT",
          "observed", sum(row["read_count"] for row in contexts),
          "paid_reads", reads)
    print("I1_495_PAID_WAKING_LINKS",
          "reads", reads,
          "links", sum(x["waking_link_count"] for x in recall_rows))
    assert all(len(row["source_event_refs"]) == 2 * row["witness_count"]
               for row in recall_rows)
    assert all(row["read_count"] in (0, 1) for row in recall_rows)
    # The actual natural scenario must demonstrate nonempty charged recall;
    # a green structural test alone does not establish runtime activation.
    assert reads > 0 and witnesses > 0, (reads, witnesses, paid)
    print("I1_474_PAID_SLEEP_RECALL", "reads", reads,
          "uc", paid, "witnesses", witnesses)
    # #478: natural paid read must reveal at least one genuinely known
    # adjacent after-state direction, not only unknown first-step deltas.
    balances = [row["site_balance"] for row in recall_rows
                if row["read_count"]]
    known = sum(
        counts["increase"] + counts["decrease"] + counts["stable"]
        for balance in balances for counts in balance.values()
    )
    assert known > 0, (reads, witnesses, balances)
    assert all(sum(counts.values()) == row["witness_count"]
               for row in recall_rows if row["read_count"]
               for counts in row["site_balance"].values())
    print("I1_478_NATURAL_SLEEP_BALANCE", "known", known,
          "paid_reads", reads)
    # #467: independent read-only concordance is a measurement, NOT a
    # subjective memory. Reduced sleep has no fresh waking capture.
    concordance = [step["prebody_concordance_audit_467"]
                   for step in life["steps"]]
    assert all(not row["autobiographical_policy_activated"]
               and not row["memory_wrote_prebody"]
               for row in concordance)
    assert all(row["physical_before_present"]
               for row in concordance
               if row["status"] != "no_physical_transition")
    assert any(row["status"] == "capture_matches_physical_before"
               for row in concordance)
    assert all(row["status"] in {
        "capture_matches_physical_before",
        "capture_physical_divergence",
        "no_current_waking_capture",
        "no_physical_transition",
    } for row in concordance)
    print("I1_467_M11_PREBODY_CONCORDANCE", {
        status: sum(row["status"] == status for row in concordance)
        for status in {row["status"] for row in concordance}
    })
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
    # #471: operator-side proof that chronologically adjacent real
    # sleeping steps can span multiple closed autobiographical episodes.
    runs = life["sleep_episode_link_audit_471"]
    assert runs and sum(x["steps"] for x in runs) == sleep_count
    assert all(x["source_count"] == 2 * x["steps"] for x in runs)
    assert all(x["sources_in_closed_episodes"] <=
               x["sources_seen_by_memory"] <= x["source_count"]
               for x in runs)
    assert all(x["end_step"] - x["start_step"] + 1 == x["steps"]
               for x in runs)
    assert all(x["body_delta"] ==
               {k: x["body_after"][k] - x["body_before"][k]
                for k in x["body_before"]} for x in runs)
    assert all(x["all_sources_in_closed_episodes"] ==
               (x["sources_in_closed_episodes"] == x["source_count"])
               for x in runs)
    expected_provenance = {"ordinary_awake_admission": 3,
                           "readmitted_after_wake": 31,
                           "reduced_sleep_continuation": 9}
    assert {kind: sum(x["provenance_counts"][kind] for x in runs)
            for kind in expected_provenance} == expected_provenance
    assert [x["provenance_counts"]["readmitted_after_wake"] for x in runs] == [0, 0, 31]
    assert len(runs) <= sleep_count
    decisions = life["sleep_decision_custody_audit_490"]
    assert len(decisions) == 34, len(decisions)
    assert sum(x["physical_command_count"] for x in decisions) == sleep_count
    assert sum(x["source_count"] for x in decisions) == 2 * sleep_count
    assert sum(x["admission_class"] == "readmitted_after_wake"
               for x in decisions) == 31
    assert sum(x["admission_class"] == "ordinary_awake_admission"
               for x in decisions) == 3
    assert any(x["physical_command_count"] > 1 for x in decisions)
    assert all(x["physical_steps"][0] == x["decision_step"] for x in decisions)
    assert all(x["sources_in_closed_episodes"] <= x["ingested_sources"]
               <= x["committed_sources"] <= x["source_count"]
               for x in decisions)
    assert all(x["continuous_subjective_session_proven"] is False
               and x["decision_influence_proven"] is False
               for x in decisions)
    print("I1_490_SLEEP_DECISION_CUSTODY",
          "distinct_decisions", len(decisions),
          "physical_sleep_steps", sleep_count,
          "owned_sources", sum(x["sources_in_closed_episodes"] for x in decisions))
    print("I1_471_SLEEP_EPISODE_LINK",
          "runs", len(runs),
          "lengths", [x["steps"] for x in runs],
          "closed_episode_counts", [len(x["distinct_closed_episode_refs"])
                                    for x in runs],
          "runs_with_all_sources_closed", sum(
              x["all_sources_in_closed_episodes"] for x in runs),
          "provenance", [x["provenance_counts"] for x in runs],
          "sources_in_closed_episodes",
          sum(x["sources_in_closed_episodes"] for x in runs),
          "total_sources", sum(x["source_count"] for x in runs))
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
