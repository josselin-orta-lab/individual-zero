"""Stage-9 raw artifact custody fixtures are synthetic, never heldout results."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.stage9_heldout_artifact_custody import (
    INDEX_VERSION, audit_heldout_raw_artifacts, load_raw_artifact_index,
)
from lab.stage9_scientific_preregistration import validate_registration
from lab.journal import HashChainedJournal
from lab.determinism import canonical_causal_bytes
from tests.test_stage9_scientific_assessment import make_report, sealed
from tests.test_stage9_scientific_preregistration import example_draft


def _prepared(root: Path):
    registration = example_draft()
    report = make_report(registration, candidates=20)
    index_runs = []
    for i, run in enumerate(report["runs"]):
        name = f"run{i}"
        folder = root / name
        folder.mkdir()
        # These journal entries are deliberately synthetic parser fixtures.
        # They exercise source-link integrity but DO NOT represent real
        # WorldBody transitions or closed Memory episodes.
        journal_builder = HashChainedJournal()
        observations = (
            run["known_cause_cases"]
            + run["naturally_acquired_false_candidates"]
        )
        memory_episodes = []
        memory_seen_events = set()
        for step, observation in enumerate(observations, start=1):
            attempt = f"synthetic-attempt:{i}:{step}"
            command_id = f"command:{i}:{step}"
            transition_id = observation["observation_ref"]
            journal_builder.append(
                event_id=command_id,
                causal_event={
                    "kind": "command_experienced",
                    "attempt_ref": attempt, "t_monde": step,
                    "primitive": "attendre", "parameters": {},
                },
            )
            journal_builder.append(
                event_id=transition_id,
                causal_event={
                    "kind": "world_transition_experienced",
                    "attempt_ref": attempt, "t_monde": step,
                    "effects": {"rest": "attendre"},
                },
            )
            memory_episodes.append({
                "id": observation["episode_ref"],
                "start_t_monde": step,
                "end_t_monde": step,
                "event_refs": [command_id, transition_id],
                "boundary_type": "max_length",
            })
            memory_seen_events.update((command_id, transition_id))
            journal_builder.append(
                event_id=f"commit:{i}:{step}",
                causal_event={
                    "kind": "auto_segment_commit",
                    "attempt_ref": attempt, "t_monde": step,
                    "event_refs": [command_id, transition_id],
                    "filter_version": "stage9-synthetic-parser-fixture",
                },
            )
        self_audit = journal_builder.verify()
        if not self_audit:
            raise AssertionError("synthetic fixture's journal must be consistent")
        journal = journal_builder.canonical_bytes()
        # A *synthetic* canonical owner-state envelope, not a lived Memory
        # or scientific heldout run. The new audit checks exact references
        # against the serialized Memory owner after journal verification.
        state = canonical_causal_bytes({
            "memory": {
                "config_version": "stage9-synthetic-parser-fixture",
                "episodes": memory_episodes,
                "seen_event_refs": sorted(memory_seen_events),
                "episode_sequence": len(memory_episodes),
            },
            "causal_model": {"published": [
                {
                    "ref": entry["contingency_ref"],
                    "causal_status": entry["causal_status"],
                }
                for entry in run["naturally_acquired_false_candidates"]
            ], "causal_observations": [],
                "causal_interventions": [], "causal_credits": []},
        })
        files = {
            "journal_path": (f"{name}/original.jsonl", journal),
            "replay_journal_path": (f"{name}/replay.jsonl", journal),
            "causal_state_path": (f"{name}/state.json", state),
            "replay_causal_state_path": (f"{name}/replay-state.json", state),
        }
        row = {"world_id": run["world_id"], "seed": run["seed"]}
        for key, (relative, payload) in files.items():
            (root / relative).write_bytes(payload)
            row[key] = relative
        run["journal_sha256"] = sha256(journal).hexdigest()
        run["replay_journal_sha256"] = sha256(journal).hexdigest()
        run["causal_state_sha256"] = sha256(state).hexdigest()
        run["replay_causal_state_sha256"] = sha256(state).hexdigest()
        index_runs.append(row)
    report = sealed(report)
    index = {
        "protocol_version": INDEX_VERSION,
        "registration_digest": validate_registration(registration),
        "evidence_sha256": report["evidence_sha256"],
        "runs": index_runs,
    }
    return registration, report, index


def _replace_journal_bytes(
    root: Path, evidence: dict[str, object], index: dict[str, object],
    payload: bytes, *, run_index: int = 0,
):
    """Re-seal forged *metadata*, proving SHA agreement is not authenticity."""
    revised = deepcopy(evidence)
    for key, sha_key in (
        ("journal_path", "journal_sha256"),
        ("replay_journal_path", "replay_journal_sha256"),
    ):
        (root / index["runs"][run_index][key]).write_bytes(payload)
        revised["runs"][run_index][sha_key] = sha256(payload).hexdigest()
    revised = sealed(revised)
    index["evidence_sha256"] = revised["evidence_sha256"]
    return revised


def _replace_causal_state_bytes(
    root: Path, evidence: dict[str, object], index: dict[str, object],
    payload: bytes, *, run_index: int = 0,
):
    """Reseal both claimed owner-state checksums and the evidence manifest."""
    revised = deepcopy(evidence)
    for key, sha_key in (
        ("causal_state_path", "causal_state_sha256"),
        ("replay_causal_state_path", "replay_causal_state_sha256"),
    ):
        (root / index["runs"][run_index][key]).write_bytes(payload)
        revised["runs"][run_index][sha_key] = sha256(payload).hexdigest()
    revised = sealed(revised)
    index["evidence_sha256"] = revised["evidence_sha256"]
    return revised


def _rewrite_chain(
    payload: bytes, *,
    rename_observation: str,
) -> bytes:
    fresh = HashChainedJournal()
    for line in payload.split(b"\n"):
        record = json.loads(line)
        identifier = record["event_id"]
        event = record["causal_event"]
        if rename_observation == identifier:
            identifier = "synthetic-renamed-physical-transition"
        if event.get("kind") == "auto_segment_commit":
            refs = event["event_refs"]
            if rename_observation in refs:
                event["event_refs"] = [
                    "synthetic-renamed-physical-transition"
                    if r == rename_observation else r for r in refs
                ]
        fresh.append(event_id=identifier, causal_event=event)
    if not fresh.verify():
        raise AssertionError("forged synthetic chain must be internally valid")
    return fresh.canonical_bytes()


def _append_rehashed_event(
    original: bytes, *, event_id: str, causal_event: dict[str, object],
) -> bytes:
    """Make a valid SHA-linked *forgery*, not a physical execution."""
    journal = HashChainedJournal()
    for line in original.split(b"\n"):
        record = json.loads(line)
        journal.append(
            event_id=record["event_id"],
            causal_event=record["causal_event"],
        )
    journal.append(event_id=event_id, causal_event=causal_event)
    if not journal.verify():
        raise AssertionError("forgery fixture must have an intact hash chain")
    return journal.canonical_bytes()


class Stage9RawArtifactCustodyTests(unittest.TestCase):
    def test_real_bytes_match_declared_digests_but_are_not_scientific_proof(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            result = audit_heldout_raw_artifacts(
                registration=registration, evidence=report,
                index=index, artifact_root=root,
            )
            self.assertEqual(result["runs_checked"], 4)
            self.assertEqual(result["raw_files_checked"], 16)
            self.assertTrue(result["original_replay_bytes_identical"])
            self.assertTrue(result["journal_chain_integrity_verified"])
            self.assertEqual(result["journal_events_checked"], 132)
            self.assertEqual(result["committed_physical_sources_checked"], 44)
            self.assertFalse(result["physical_truth_attested"])
            self.assertFalse(result["memory_episode_closure_attested"])
            self.assertTrue(result["archived_causal_owner_state_canonical"])
            self.assertTrue(result["closed_episode_membership_structurally_verified"])
            self.assertEqual(result["closed_memory_episodes_scanned"], 44)
            self.assertEqual(result["claimed_closed_memory_sources_checked"], 44)
            self.assertFalse(result["memory_runtime_attested"])
            self.assertGreater(result["total_bytes_checked"], 0)
            self.assertEqual(len(result["index_sha256"]), 64)
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertTrue(result["outstanding"])
            self.assertNotEqual(result["provisional_metric_assessment"], "accepted")

    def test_rehashed_invalid_or_noncanonical_owner_state_is_rejected(self):
        for scenario in ("invalid_json", "noncanonical", "missing_memory"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, report, index = _prepared(root)
                    original = (
                        root / index["runs"][0]["causal_state_path"]
                    ).read_bytes()
                    if scenario == "invalid_json":
                        forged_bytes = b"not an owner snapshot"
                        failure = "invalid archived causal owner-state JSON"
                    elif scenario == "noncanonical":
                        forged_bytes = b" " + original
                        failure = "not byte-canonical"
                    else:
                        forged_bytes = canonical_causal_bytes(
                            {"causal_model": {"published": [], "causal_observations": [],
                                              "causal_interventions": [], "causal_credits": []}},
                        )
                        failure = "lacks Memory owner"
                    forged = _replace_causal_state_bytes(
                        root, report, index, forged_bytes,
                    )
                    with self.assertRaisesRegex(ValueError, failure):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=forged,
                            index=index, artifact_root=root,
                        )

    def test_rehashed_missing_or_forged_memory_closure_is_rejected(self):
        for scenario in (
            "missing_episode", "misnamed_episode", "omitted_command",
            "wrong_step", "unseen_event", "reused_event",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, report, index = _prepared(root)
                    state = json.loads((
                        root / index["runs"][0]["causal_state_path"]
                    ).read_bytes())
                    episodes = state["memory"]["episodes"]
                    command_ref = episodes[0]["event_refs"][0]
                    if scenario == "missing_episode":
                        episodes.pop(0)
                        failure = "not archived as closed"
                    elif scenario == "misnamed_episode":
                        episodes[0]["id"] = "forged-closed-episode"
                        failure = "not archived as closed"
                    elif scenario == "omitted_command":
                        episodes[0]["event_refs"].remove(command_ref)
                        failure = "not in one closed Memory episode"
                    elif scenario == "wrong_step":
                        episodes[0]["start_t_monde"] = 0
                        episodes[0]["end_t_monde"] = 0
                        failure = "not in one closed Memory episode"
                    elif scenario == "unseen_event":
                        state["memory"]["seen_event_refs"].remove(command_ref)
                        failure = "reused or unseen event"
                    else:
                        # Some positive runs have only one closed episode:
                        # explicitly forge another closed episode that
                        # reuses the *same* physical Memory event.
                        duplicate = deepcopy(episodes[0])
                        duplicate["id"] = "forged-second-closed-episode"
                        episodes.append(duplicate)
                        failure = "reused or unseen event"
                    forged = _replace_causal_state_bytes(
                        root, report, index, canonical_causal_bytes(state),
                        run_index=0,
                    )
                    with self.assertRaisesRegex(ValueError, failure):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=forged,
                            index=index, artifact_root=root,
                        )

    def test_symlinked_artifact_root_is_rejected(self):
        with TemporaryDirectory() as folder:
            parent = Path(folder)
            root = parent / "raw"
            root.mkdir()
            reg, report, index = _prepared(root)
            alias = parent / "swappable-root"
            try:
                alias.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "root or ancestor may not be a symlink"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=report,
                    index=index, artifact_root=alias,
                )

    def test_symlinked_artifact_root_ancestor_is_rejected(self):
        with TemporaryDirectory() as folder:
            parent = Path(folder)
            physical_parent = parent / "physical-parent"
            physical_parent.mkdir()
            root = physical_parent / "raw"
            root.mkdir()
            reg, report, index = _prepared(root)
            alias = parent / "alias-parent"
            try:
                alias.symlink_to(physical_parent, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "root or ancestor may not be a symlink"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=report,
                    index=index, artifact_root=alias / "raw",
                )

    def test_mutation_after_structural_journal_audit_is_rejected(self):
        from lab.stage9_canonical_journal_audit import audit_raw_causal_journal

        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = root / index["runs"][0]["journal_path"]

            def tamper_after_parse(*args, **kwargs):
                outcome = audit_raw_causal_journal(*args, **kwargs)
                original.write_bytes(original.read_bytes() + b"forged")
                return outcome

            with patch(
                "lab.stage9_heldout_artifact_custody.audit_raw_causal_journal",
                side_effect=tamper_after_parse,
            ):
                with self.assertRaisesRegex(ValueError, "changed during custody audit"):
                    audit_heldout_raw_artifacts(
                        registration=reg, evidence=report,
                        index=index, artifact_root=root,
                    )

    def test_later_run_cannot_modify_previously_verified_artifact(self):
        from lab.stage9_memory_custody import audit_archived_closed_memory_sources

        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            first_journal = root / index["runs"][0]["journal_path"]
            calls = 0

            def tamper_on_later_run(*args, **kwargs):
                nonlocal calls
                result = audit_archived_closed_memory_sources(*args, **kwargs)
                calls += 1
                if calls == 2:
                    first_journal.write_bytes(first_journal.read_bytes() + b"forged")
                return result

            with patch(
                "lab.stage9_heldout_artifact_custody.audit_archived_closed_memory_sources",
                side_effect=tamper_on_later_run,
            ):
                with self.assertRaisesRegex(ValueError, "changed before custody audit completion"):
                    audit_heldout_raw_artifacts(
                        registration=reg, evidence=report,
                        index=index, artifact_root=root,
                    )

    def test_rehashed_report_cannot_invent_archived_established_rule(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run = next(
                (row for row in report["runs"]
                 if row["naturally_acquired_false_candidates"]),
                None,
            )
            self.assertIsNotNone(run)
            candidate = run["naturally_acquired_false_candidates"][0]
            item = next(
                item for item in index["runs"]
                if (item["world_id"], item["seed"])
                == (run["world_id"], run["seed"])
            )
            state = json.loads((root / item["causal_state_path"]).read_bytes())
            status = next(
                row for row in state["causal_model"]["published"]
                if row["ref"] == candidate["contingency_ref"]
            )
            status["causal_status"] = (
                "etablie" if candidate["causal_status"] != "etablie"
                else "hypothese_causale"
            )
            replacement = canonical_causal_bytes(state)
            altered = _replace_causal_state_bytes(
                root, report, index, replacement,
                run_index=index["runs"].index(item),
            )
            with self.assertRaisesRegex(ValueError, "disagrees with archived causal status"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_rehashed_physical_observation_cannot_credit_two_rules(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run = next(
                row for row in report["runs"]
                if len(row["naturally_acquired_false_candidates"]) >= 2
            )
            item = next(
                row for row in index["runs"]
                if (row["world_id"], row["seed"]) == (run["world_id"], run["seed"])
            )
            run_index = index["runs"].index(item)
            state = json.loads((root / item["causal_state_path"]).read_bytes())
            candidates = run["naturally_acquired_false_candidates"]
            observation_ref = candidates[0]["observation_ref"]
            for candidate in candidates[:2]:
                state["causal_model"]["causal_observations"].append({
                    "contingency_ref": candidate["contingency_ref"],
                    "observation_ref": observation_ref,
                    "episode_ref": candidates[0]["episode_ref"],
                    "observed_step": 1 + len(run["known_cause_cases"]),
                })
                state["causal_model"]["causal_credits"].append([
                    candidate["contingency_ref"], observation_ref, "observation",
                ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
                run_index=run_index,
            )
            with self.assertRaisesRegex(
                ValueError, "physical observation reused across causal evidence credits",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_rehashed_causal_credit_cannot_reference_unpublished_rule(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            state = json.loads(
                (root / index["runs"][0]["causal_state_path"]).read_bytes()
            )
            physical = report["runs"][0]["known_cause_cases"][0]
            state["causal_model"]["causal_observations"].append({
                "contingency_ref": "invented:unpublished",
                "observation_ref": physical["observation_ref"],
                "episode_ref": physical["episode_ref"],
            })
            state["causal_model"]["causal_credits"].append([
                "invented:unpublished", physical["observation_ref"], "observation",
            ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
            )
            with self.assertRaisesRegex(
                ValueError, "evidence refers to unpublished contingency",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_unreported_intervention_requires_real_physical_transition(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run = next(row for row in report["runs"] if row["naturally_acquired_false_candidates"])
            item = next(row for row in index["runs"] if
                        (row["world_id"], row["seed"]) == (run["world_id"], run["seed"]))
            candidate = run["naturally_acquired_false_candidates"][0]
            state = json.loads((root / item["causal_state_path"]).read_bytes())
            state["causal_model"]["causal_interventions"].append({
                "contingency_ref": candidate["contingency_ref"],
                "observation_ref": "forged:unreported-physical-transition",
                "episode_ref": candidate["episode_ref"],
                "command_ref": "forged:command",
                "observed_step": 1,
            })
            state["causal_model"]["causal_credits"].append([
                candidate["contingency_ref"], "forged:unreported-physical-transition", "intervention",
            ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
                run_index=index["runs"].index(item),
            )
            with self.assertRaisesRegex(ValueError, "physical transition absent from raw journal"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered, index=index, artifact_root=root,
                )

    def test_rehashed_causal_observation_cannot_forge_world_step(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run = next(
                row for row in report["runs"]
                if row["naturally_acquired_false_candidates"]
            )
            item = next(
                row for row in index["runs"]
                if (row["world_id"], row["seed"]) == (run["world_id"], run["seed"])
            )
            candidate = run["naturally_acquired_false_candidates"][0]
            state = json.loads((root / item["causal_state_path"]).read_bytes())
            state["causal_model"]["causal_observations"].append({
                "contingency_ref": candidate["contingency_ref"],
                "observation_ref": candidate["observation_ref"],
                "episode_ref": candidate["episode_ref"],
                "observed_step": 999,
            })
            state["causal_model"]["causal_credits"].append([
                candidate["contingency_ref"], candidate["observation_ref"],
                "observation",
            ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
                run_index=index["runs"].index(item),
            )
            with self.assertRaisesRegex(
                ValueError, "causal evidence world step disagrees with physical source",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_rehashed_intervention_cannot_forge_committed_command(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run = next(
                row for row in report["runs"]
                if row["naturally_acquired_false_candidates"]
            )
            item = next(
                row for row in index["runs"]
                if (row["world_id"], row["seed"]) == (run["world_id"], run["seed"])
            )
            candidate = run["naturally_acquired_false_candidates"][0]
            state = json.loads((root / item["causal_state_path"]).read_bytes())
            state["causal_model"]["causal_interventions"].append({
                "contingency_ref": candidate["contingency_ref"],
                "observation_ref": candidate["observation_ref"],
                "episode_ref": candidate["episode_ref"],
                "command_ref": "forged:applied-command",
                "observed_step": 1 + len(run["known_cause_cases"]),
            })
            state["causal_model"]["causal_credits"].append([
                candidate["contingency_ref"], candidate["observation_ref"],
                "intervention",
            ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
                run_index=index["runs"].index(item),
            )
            with self.assertRaisesRegex(
                ValueError, "intervention disagrees with physical source",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_rehashed_forged_causal_credit_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            state = json.loads(
                (root / index["runs"][0]["causal_state_path"]).read_bytes()
            )
            state["causal_model"]["causal_credits"].append([
                "forged:contingency", "forged:observation", "intervention",
            ])
            altered = _replace_causal_state_bytes(
                root, report, index, canonical_causal_bytes(state),
            )
            with self.assertRaisesRegex(
                ValueError, "causal credits disagree with admitted evidence",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=altered,
                    index=index, artifact_root=root,
                )

    def test_rehashed_missing_or_duplicate_canonical_rule_is_rejected(self):
        for scenario in ("missing", "duplicate"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, report, index = _prepared(root)
                    item = next(
                        entry for entry in index["runs"]
                        if any(
                            r["world_id"] == entry["world_id"]
                            and r["seed"] == entry["seed"]
                            and r["naturally_acquired_false_candidates"]
                            for r in report["runs"]
                        )
                    )
                    state = json.loads(
                        (root / item["causal_state_path"]).read_bytes()
                    )
                    published = state["causal_model"]["published"]
                    self.assertTrue(published)
                    if scenario == "missing":
                        published.pop(0)
                        reason = "disagrees with archived causal status"
                    else:
                        published.append(deepcopy(published[0]))
                        reason = "duplicate archived causal contingency"
                    altered = _replace_causal_state_bytes(
                        root, report, index, canonical_causal_bytes(state),
                        run_index=index["runs"].index(item),
                    )
                    with self.assertRaisesRegex(ValueError, reason):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=altered,
                            index=index, artifact_root=root,
                        )

    def test_tampering_with_actual_journal_or_replay_fails(self):
        for key in ("journal_path", "replay_journal_path",
                    "causal_state_path", "replay_causal_state_path"):
            with self.subTest(key=key):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    path = root / index["runs"][0][key]
                    path.write_bytes(path.read_bytes() + b"forged")
                    with self.assertRaisesRegex(ValueError, "raw artifact digest"):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_empty_reported_journal_is_not_accepted_as_execution(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            reported = deepcopy(evidence)
            empty_sha = sha256(b"").hexdigest()
            reported["runs"][0]["journal_sha256"] = empty_sha
            reported["runs"][0]["replay_journal_sha256"] = empty_sha
            reported = sealed(reported)
            index["evidence_sha256"] = reported["evidence_sha256"]
            for key in ("journal_path", "replay_journal_path"):
                (root / index["runs"][0][key]).write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "empty raw artifact"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=reported,
                    index=index, artifact_root=root,
                )

    def test_metadata_rehashed_but_broken_raw_hash_chain_is_detected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = root / index["runs"][0]["journal_path"]
            records = original.read_bytes().split(b"\n")
            first = json.loads(records[0])
            first["event_hash"] = "0" * 64
            records[0] = canonical_causal_bytes(first)
            forged = _replace_journal_bytes(root, report, index, b"\n".join(records))
            with self.assertRaisesRegex(ValueError, "broken causal journal event hash"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_valid_rehashed_chain_cannot_hide_missing_physical_observation(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            physical = report["runs"][0]["known_cause_cases"][0]["observation_ref"]
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            payload = _rewrite_chain(
                original, rename_observation=physical,
            )
            forged = _replace_journal_bytes(root, report, index, payload)
            with self.assertRaisesRegex(ValueError, "physical transition absent"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_journal_without_applied_command_commit_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            physical = report["runs"][0]["known_cause_cases"][0]["observation_ref"]
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            # Preserve the physical source ID while removing the matching
            # command from its otherwise correctly re-hashed closure.
            source = HashChainedJournal()
            for line in original.split(b"\n"):
                entry = json.loads(line)
                event = entry["causal_event"]
                if event.get("kind") == "auto_segment_commit" and physical in event["event_refs"]:
                    event["event_refs"] = [physical]
                source.append(event_id=entry["event_id"], causal_event=event)
            forged = _replace_journal_bytes(
                root, report, index, source.canonical_bytes(),
            )
            with self.assertRaisesRegex(ValueError, "unique committed same-attempt"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_noncanonical_journal_bytes_are_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            forged = _replace_journal_bytes(root, report, index, b" " + original)
            with self.assertRaisesRegex(ValueError, "not byte-canonical"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_duplicate_journal_event_id_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            records = [
                json.loads(line) for line in original.split(b"\n")
            ]
            duplicate_id = records[0]["event_id"]
            event = {"kind": "synthetic_duplicate_id"}
            previous_hash = records[-1]["event_hash"]
            # Forge a cryptographically linked record without going through
            # HashChainedJournal.append, which rejects duplicate IDs.
            records.append({
                "index": len(records),
                "event_id": duplicate_id,
                "previous_hash": previous_hash,
                "causal_event": event,
                "event_hash": sha256(
                    bytes.fromhex(previous_hash)
                    + canonical_causal_bytes({
                        "event_id": duplicate_id, "causal_event": event,
                    })
                ).hexdigest(),
            })
            forged = _replace_journal_bytes(
                root, report, index,
                b"\n".join(canonical_causal_bytes(row) for row in records),
            )
            with self.assertRaisesRegex(ValueError, "repeated canonical journal"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_extra_physical_command_or_advancement_is_rejected(self):
        # Previously, an unreferenced duplicate in the *same applied
        # attempt* could be hidden outside the selected AutoSegmentCommit.
        for kind in ("command_experienced", "world_transition_experienced"):
            with self.subTest(kind=kind):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, report, index = _prepared(root)
                    journal = (root / index["runs"][0]["journal_path"]).read_bytes()
                    extra = {
                        "kind": kind,
                        "attempt_ref": "synthetic-attempt:0:1",
                        "t_monde": 1,
                    }
                    forged = _replace_journal_bytes(
                        root, report, index,
                        _append_rehashed_event(
                            journal,
                            event_id=f"uncommitted-extra:{kind}",
                            causal_event=extra,
                        ),
                    )
                    with self.assertRaisesRegex(
                        ValueError, "nonunique command or world advancement",
                    ):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=forged,
                            index=index, artifact_root=root,
                        )

    def test_rehashed_second_memory_commit_cannot_reuse_an_observation(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            physical = report["runs"][0]["known_cause_cases"][0]["observation_ref"]
            forged = _replace_journal_bytes(
                root, report, index,
                _append_rehashed_event(
                    original,
                    event_id="second-commit-for-same-attempt",
                    causal_event={
                        "kind": "auto_segment_commit",
                        "attempt_ref": "synthetic-attempt:0:1",
                        "t_monde": 1,
                        "event_refs": ["command:0:1", physical],
                        "filter_version": "stage9-synthetic-parser-fixture",
                    },
                ),
            )
            with self.assertRaisesRegex(
                ValueError, "unique same-attempt Memory commit",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_commit_rejects_wrong_step_with_same_attempt(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            forged_journal = HashChainedJournal()
            for line in original.split(b"\n"):
                record = json.loads(line)
                event = record["causal_event"]
                if record["event_id"] == "command:0:1":
                    event["t_monde"] = 99
                forged_journal.append(
                    event_id=record["event_id"], causal_event=event,
                )
            self.assertTrue(forged_journal.verify())
            forged = _replace_journal_bytes(
                root, report, index, forged_journal.canonical_bytes(),
            )
            with self.assertRaisesRegex(
                ValueError, "attempt reused across world steps",
            ):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_attempt_cannot_span_multiple_world_steps(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            run_index = next(
                i for i, row in enumerate(report["runs"])
                if len(row["known_cause_cases"] + row["naturally_acquired_false_candidates"]) >= 2
            )
            original = (root / index["runs"][run_index]["journal_path"]).read_bytes()
            forged_journal = HashChainedJournal()
            for line in original.split(b"\n"):
                record = json.loads(line)
                event = record["causal_event"]
                if (
                    event.get("attempt_ref") == f"synthetic-attempt:{run_index}:2"
                    and event.get("kind") in {
                        "command_experienced", "world_transition_experienced",
                        "auto_segment_commit",
                    }
                ):
                    event["attempt_ref"] = f"synthetic-attempt:{run_index}:1"
                forged_journal.append(
                    event_id=record["event_id"], causal_event=event,
                )
            self.assertTrue(forged_journal.verify())
            forged = _replace_journal_bytes(
                root, report, index, forged_journal.canonical_bytes(),
                run_index=run_index,
            )
            with self.assertRaisesRegex(ValueError, "attempt reused across world steps"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=forged,
                    index=index, artifact_root=root,
                )

    def test_rehashed_commit_cannot_launder_foreign_or_future_source(self):
        for scenario in ("future_foreign", "repeated_ref"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, report, index = _prepared(root)
                    original = (root / index["runs"][0]["journal_path"]).read_bytes()
                    forged_journal = HashChainedJournal()
                    for line in original.split(b"\n"):
                        record = json.loads(line)
                        event = record["causal_event"]
                        if record["event_id"] == "commit:0:1":
                            event["event_refs"].append(
                                "command:0:2"
                                if scenario == "future_foreign"
                                else "command:0:1"
                            )
                        forged_journal.append(
                            event_id=record["event_id"], causal_event=event,
                        )
                    self.assertTrue(forged_journal.verify())
                    forged = _replace_journal_bytes(
                        root, report, index, forged_journal.canonical_bytes(),
                    )
                    with self.assertRaisesRegex(
                        ValueError,
                        "foreign or future event|unique committed same-attempt",
                    ):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=forged,
                            index=index, artifact_root=root,
                        )

    def test_cancelled_attempt_at_same_world_step_is_not_double_counted(self):
        # A rollback may reuse the world step, but has a *distinct attempt*
        # and no autobiographical commit. INV-44 forbids counting it.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            original = (root / index["runs"][0]["journal_path"]).read_bytes()
            command = _append_rehashed_event(
                original, event_id="cancelled-command",
                causal_event={
                    "kind": "command_experienced",
                    "attempt_ref": "cancelled-attempt:0:1",
                    "t_monde": 1,
                },
            )
            cancelled = _append_rehashed_event(
                command, event_id="cancelled-transition",
                causal_event={
                    "kind": "world_transition_experienced",
                    "attempt_ref": "cancelled-attempt:0:1",
                    "t_monde": 1,
                },
            )
            forged = _replace_journal_bytes(root, report, index, cancelled)
            result = audit_heldout_raw_artifacts(
                registration=reg, evidence=forged,
                index=index, artifact_root=root,
            )
            self.assertEqual(result["committed_physical_sources_checked"], 44)
            self.assertEqual(result["journal_events_checked"], 134)
            self.assertFalse(result["physical_truth_attested"])

    def test_digest_can_not_be_forged_in_report_or_index(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            changed = deepcopy(evidence)
            changed["runs"][0]["journal_sha256"] = "f" * 64
            changed["runs"][0]["replay_journal_sha256"] = "f" * 64
            changed = sealed(changed)
            index["evidence_sha256"] = changed["evidence_sha256"]
            with self.assertRaisesRegex(ValueError, "raw artifact digest"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=changed,
                    index=index, artifact_root=root,
                )
            index["evidence_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "not bound"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_missing_or_duplicate_run_index_is_rejected(self):
        for modification in ("missing", "duplicate", "foreign"):
            with self.subTest(modification=modification):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    if modification == "missing":
                        index["runs"].pop()
                    elif modification == "duplicate":
                        index["runs"][1] = deepcopy(index["runs"][0])
                    else:
                        index["runs"][0]["world_id"] = "unregistered-world"
                    with self.assertRaises(ValueError):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_same_raw_file_cannot_masquerade_as_independent_replay(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            index["runs"][0]["replay_journal_path"] = (
                index["runs"][0]["journal_path"]
            )
            with self.assertRaisesRegex(ValueError, "reused"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_hardlinked_original_and_replay_are_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            first = root / index["runs"][0]["journal_path"]
            replay = root / index["runs"][0]["replay_journal_path"]
            replay.unlink()
            os.link(first, replay)
            with self.assertRaisesRegex(ValueError, "reused"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_path_escape_and_symlink_do_not_access_outside_file(self):
        for scenario in ("traversal", "symlink"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    original = root / index["runs"][0]["journal_path"]
                    if scenario == "traversal":
                        index["runs"][0]["journal_path"] = "../../outside"
                    else:
                        link = root / "shortcut.jsonl"
                        link.symlink_to(original)
                        index["runs"][0]["journal_path"] = link.name
                    with self.assertRaisesRegex(ValueError, "traversal|symlink"):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_older_v2_index_does_not_claim_stronger_v3_provenance(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, report, index = _prepared(root)
            index["protocol_version"] = "stage9-heldout-raw-artifact-index-v2"
            with self.assertRaisesRegex(ValueError, "schema mismatch"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=report,
                    index=index, artifact_root=root,
                )

    def test_ambiguous_json_and_invalid_schema_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            manifest = root / "index.json"
            manifest.write_text('{"protocol_version":"a","protocol_version":"b"}')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_raw_artifact_index(manifest)
            manifest.write_text('{"runs":[NaN]}')
            with self.assertRaisesRegex(ValueError, "non-finite"):
                load_raw_artifact_index(manifest)
            index["protocol_version"] = "obsolete"
            with self.assertRaisesRegex(ValueError, "schema"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )


if __name__ == "__main__":
    unittest.main()
