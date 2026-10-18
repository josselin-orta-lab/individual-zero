#!/usr/bin/env python3
"""Exact I1 generated-artifact comparison against the last pre-M11 migration.

The reference is a pinned *current* I1 software commit immediately preceding
the native M11 move, not a historical broken experimental cohort or scientific
oracle. Verify all generated Python bytes and namespace identities. The source
manifest provenance is intentionally NOT compared: that is what migration
changes. No network requests, state mutation, or older living-world replay.
"""
from __future__ import annotations

import argparse
import difflib
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def _build(root: Path, output: Path) -> dict[str, str]:
    script = root / "scripts" / "build_i1_fork.py"
    if not script.is_file():
        raise RuntimeError(f"missing independent I1 builder: {script}")
    p = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=str(root), text=True, capture_output=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(
            f"I1 build failed ({root}):\n{p.stdout}\n{p.stderr}"
        )
    manifest = json.loads((output / "i1_build_manifest.json").read_text())
    observed = {}
    for rel, details in manifest["files"].items():
        path = output / rel
        if not path.is_file():
            raise AssertionError(f"manifest references missing module: {rel}")
        digest = sha256(path.read_bytes()).hexdigest()
        if digest != details["built_sha256"]:
            raise AssertionError(f"incorrect generated SHA256 for {rel}")
        observed[rel] = digest
    return observed



def _approved_stage10_initialization_move(before: bytes, after: bytes) -> bool:
    """Permit only #255's exact assignment move, not general stage10 drift."""
    line = b'        canonical = type(self).__name__ == "I1Runtime"\n'
    early = b'        coordinator = Stage10PublicationCoordinator(\n'
    late = b'        if ((not canonical and candidate.get("forms")\n'
    if (before.count(line) != 1 or after.count(line) != 1
            or before.count(early) != 1 or after.count(early) != 1
            or before.count(late) != 1 or after.count(late) != 1):
        return False
    if not (before.index(early) < before.index(line) < before.index(late)
            and after.index(line) < after.index(early) < after.index(late)):
        return False
    reconstructed = after.replace(line, b"", 1).replace(late, line + late, 1)
    return reconstructed == before


def _approved_local_capture_resource_optimization(before: bytes, after: bytes) -> bool:
    """Allow only the two reviewed WorldBody.capture_local resource blocks.

    Rejects every other generated-source drift; this is NOT a scientific
    equivalence assertion. Independent first-person differential tests apply.
    """
    old_a = "        def resource_kinds(position: Position) -> tuple[str, ...]:\n            return tuple(\n                sorted(\n                    kind\n                    for (resource_position, kind), quantity in self._resources.items()\n                    if resource_position == position and quantity > 0\n                )\n            )\n"
    new_a = "        # Stage-3 only sees the current cell and four cardinal neighbors.\n        # Inspect every resource once rather than re-scanning the entire world\n        # for each of those cells. This lookup is ephemeral observation work:\n        # it is never retained by the individual or populated from Oracle data.\n        local_positions = {self._position}\n        local_positions.update(\n            self._position.moved(direction)\n            for direction in (\"north\", \"south\", \"east\", \"west\")\n        )\n        local_resource_rows: dict[Position, list[tuple[str, int]]] = {}\n        for (position, kind), quantity in self._resources.items():\n            if position in local_positions and quantity > 0:\n                local_resource_rows.setdefault(position, []).append((kind, quantity))\n\n        def resource_kinds(position: Position) -> tuple[str, ...]:\n            return tuple(sorted(kind for kind, _ in local_resource_rows.get(position, ())))\n"
    old_b = "        for (position, kind), quantity in sorted(\n            self._resources.items(),\n            key=lambda row: (row[0][0].x, row[0][0].y, row[0][1]),\n        ):\n            if quantity <= 0:\n                continue\n            visible_entities.append(\n                VisibleEntity(\n                    entity_id=f\"{kind}:{position.x}:{position.y}\",\n                    entity_type=kind,\n                    position=position,\n                    properties={\"quantity\": quantity},\n                )\n            )\n"
    new_b = "        # Visible resources already belong to the local field. Their final\n        # entity order is established below by (entity_type, entity_id), so\n        # sorting remote resource cells cannot influence the capture.\n        for position, resources in local_resource_rows.items():\n            for kind, quantity in resources:\n                visible_entities.append(\n                    VisibleEntity(\n                        entity_id=f\"{kind}:{position.x}:{position.y}\",\n                        entity_type=kind,\n                        position=position,\n                        properties={\"quantity\": quantity},\n                    )\n                )\n"
    original = before.decode("utf-8")
    candidate = after.decode("utf-8")
    if any(original.count(block) != 1 for block in (old_a, old_b)):
        return False
    if any(candidate.count(block) != 1 for block in (new_a, new_b)):
        return False
    intermediate = original.replace(old_a, new_a, 1).replace(old_b, new_b, 1)
    filters = [["        for index, position in enumerate(sorted(self._water_sources)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._water_sources)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("],["        for index, position in enumerate(sorted(self._creatures)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._creatures)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("],["        for index, position in enumerate(sorted(self._shelters)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._shelters)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("]]
    for old, new in filters:
        # The final candidate has its entity-loop headers rewritten again in
        # the next approved transformation. Check the intermediate before
        # applying that second change, then compare final bytes exactly.
        if intermediate.count(old) != 1:
            return False
        intermediate = intermediate.replace(old, new, 1)
    for old, new in [["        for index, position in enumerate(sorted(self._water_sources)):\n            # Keep the globally ranked entity ID, but allocate only entities","        for index, position in enumerate(\n            sorted(self._water_sources)\n            if not self._water_sources.isdisjoint(local_positions) else ()\n        ):\n            # Keep the globally ranked entity ID, but allocate only entities"],["        for index, position in enumerate(sorted(self._creatures)):\n            # Keep the globally ranked entity ID, but allocate only entities","        for index, position in enumerate(\n            sorted(self._creatures)\n            if not self._creatures.isdisjoint(local_positions) else ()\n        ):\n            # Keep the globally ranked entity ID, but allocate only entities"],["        for index, position in enumerate(sorted(self._shelters)):\n            # Keep the globally ranked entity ID, but allocate only entities","        for index, position in enumerate(\n            sorted(self._shelters)\n            if not self._shelters.isdisjoint(local_positions) else ()\n        ):\n            # Keep the globally ranked entity ID, but allocate only entities"]]:
        if intermediate.count(old) != 1 or candidate.count(new) != 1:
            return False
        intermediate = intermediate.replace(old, new, 1)
    return intermediate == candidate


def _approved_pending_index_cursor(before: bytes, after: bytes) -> bool:
    """Only allow five reviewed P-42 indexing transformations."""
    old = before.decode('utf-8')
    new = after.decode('utf-8')
    pairs = [["        self._pending: dict[str, dict] = {}\n        self._cut: ConsolidationCut | None = None","        self._pending: dict[str, dict] = {}\n        # Derived insertion-order key index: built only from already charged\n        # discovered episodes; never exported as another causal-state owner.\n        # Constant-time cursor access avoids rewalking all earlier episodes\n        # on every UC-priced rank slice. Restored from authenticated _pending.\n        self._pending_order: list[str] = []\n        self._cut: ConsolidationCut | None = None"],["            for payload in staged:\n                self._pending[payload[\"id\"]] = payload\n            self._seen_count += count","            for payload in staged:\n                ref = payload[\"id\"]\n                self._pending[ref] = payload\n                self._pending_order.append(ref)\n            self._seen_count += count"],["        inspected = list(islice(\n            self._pending.values(), self._rank_cursor, self._rank_cursor + count))\n        if len(inspected) != count:\n            raise RuntimeError(\"index changed during frozen paid selection\")","        refs = self._pending_order[self._rank_cursor:self._rank_cursor + count]\n        if len(refs) != count or len(self._pending_order) != len(self._pending):\n            raise RuntimeError(\"index changed during frozen paid selection\")\n        inspected = [self._pending[ref] for ref in refs]"],["        for ref in refs:\n            del self._pending[ref]\n        self._history_version = new_version","        for ref in refs:\n            del self._pending[ref]\n        # This maintenance occurs after the already UC-priced retirement;\n        # future ranks retain the exact original insertion order.\n        removed = set(refs)\n        self._pending_order = [\n            ref for ref in self._pending_order if ref not in removed\n        ]\n        self._history_version = new_version"],["        self._pending = check\n        self._cut, self._target = cut, target","        self._pending = check\n        self._pending_order = list(check)\n        self._cut, self._target = cut, target"]]
    for prior, replacement in pairs:
        if old.count(prior) != 1 or new.count(replacement) != 1:
            return False
        old = old.replace(prior, replacement, 1)
    return old == new

def _approved_memory_overlap(before: bytes, after: bytes) -> bool:
    """Allow only the reviewed Stage7 exact reference-overlap replacement."""
    original = before.decode("utf-8")
    candidate = after.decode("utf-8")
    former = "        if any(ref in current_refs for ref in episode.event_refs):\n            return 1.0"
    improved = "        # Exact overlap in C avoids one Python-level membership test per\n        # episode event. Neither recall eligibility nor subjective inputs change.\n        if not current_refs.isdisjoint(episode.event_refs):\n            return 1.0"
    return (original.count(former) == 1 and candidate.count(improved) == 1
            and original.replace(former, improved, 1) == candidate)


def _approved_stage9_episode_slice(before: bytes, after: bytes) -> bool:
    """Permit only the count-and-bounded-slice Stage9 substitution."""
    former = "            before = len(self.memory.episodes)\n            original_memory(_ctx)\n            newly_closed = self.memory.episodes[before:]"
    newer = "            # Count-only checkpoint: do not materialize the full lifetime\n            # episode tuple twice during every waking cognitive cycle.\n            before = self.memory.episode_count\n            original_memory(_ctx)\n            newly_closed = self.memory.read_episodes_range(\n                before, self.memory.episode_count,\n            )"
    prior = before.decode("utf-8")
    current = after.decode("utf-8")
    return (prior.count(former) == 1 and current.count(newer) == 1
            and prior.replace(former, newer, 1) == current)


def _approved_autobiographical_policy_fastpath(before: bytes, after: bytes) -> bool:
    """Only permit reviewed first-person policy-validation transformations."""
    prior, current = before.decode("utf-8"), after.decode("utf-8")
    for old, new in [["        self.validate()\n        kind = event.causal_event.get(\"kind\")\n        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:","        self.validate()\n        return self._project_validated(event)\n\n    def _project_validated(self, event: JournalEntry) -> dict[str, object]:\n        \"\"\"Internal fast path: caller validated this exact policy already.\n\n        No exemption from the event-kind or lived-field epistemic guards.\n        Direct callers must keep using project(), which always validates.\n        \"\"\"\n        kind = event.causal_event.get(\"kind\")\n        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:"],["            policy.project(entry)\n            validated.append(event_ref)","            if type(policy) is AutobiographicalPolicy:\n                policy._project_validated(entry)\n            else:\n                policy.project(entry)\n            validated.append(event_ref)"],["        projected: list[dict[str, object]] = []\n\n        for commit_event_id in self._commit_event_ids:","        projected: list[dict[str, object]] = []\n        # Exact built-in immutable policies can be validated once per read;\n        # custom policy subclasses keep their original validation cadence.\n        validated_versions: set[str] = set()\n\n        for commit_event_id in self._commit_event_ids:"],["            policy.validate()\n\n            for event_ref in refs:","            if type(policy) is AutobiographicalPolicy:\n                if version not in validated_versions:\n                    policy.validate()\n                    validated_versions.add(version)\n            else:\n                policy.validate()\n\n            for event_ref in refs:"],["                    projected.append(policy.project(source))","                    projected.append(\n                        policy._project_validated(source)\n                        if type(policy) is AutobiographicalPolicy\n                        else policy.project(source)\n                    )"]]:
        if prior.count(old) != 1 or current.count(new) != 1:
            return False
        prior = prior.replace(old, new, 1)
    return prior == current


def _approved_local_visible_entity_filter(before: bytes, after: bytes) -> bool:
    """Allow only the three reviewed remote-entity preallocation filters."""
    prior, current = before.decode("utf-8"), after.decode("utf-8")
    for old, new in [["        for index, position in enumerate(sorted(self._water_sources)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._water_sources)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("],["        for index, position in enumerate(sorted(self._creatures)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._creatures)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("],["        for index, position in enumerate(sorted(self._shelters)):\n            visible_entities.append(","        for index, position in enumerate(sorted(self._shelters)):\n            # Keep the globally ranked entity ID, but allocate only entities\n            # inside the first-person perceptual field.\n            if position not in local_positions:\n                continue\n            visible_entities.append("]]:
        if prior.count(old) != 1 or current.count(new) != 1:
            return False
        prior = prior.replace(old, new, 1)
    return prior == current


def _approved_autobio_index_rehydration(before: bytes, after: bytes) -> bool:
    """Verify the exact reviewed JournalViews index construction only."""
    old = "        self._commit_event_ids = [\n            entry.event_id\n            for entry in journal.entries\n            if entry.causal_event.get(\"kind\") == \"auto_segment_commit\"\n        ]"
    new = "        # Rehydrate in journal order without materializing the complete\n        # technical history. The reverse iterator is read-only and covers\n        # every original occurrence; only committed autobiographical IDs\n        # are retained, in their original chronological order.\n        self._commit_event_ids = [\n            entry.event_id\n            for entry in journal.iter_entries_reversed()\n            if entry.causal_event.get(\"kind\") == \"auto_segment_commit\"\n        ]\n        self._commit_event_ids.reverse()"
    source, candidate = before.decode("utf-8"), after.decode("utf-8")
    return source.count(old) == 1 and candidate.count(new) == 1 and source.replace(old, new, 1) == candidate


def _reference_autobio_fastpath(before: bytes) -> bytes:
    """Construct the exact reviewed earlier JournalViews intermediate."""
    from_source = before.decode("utf-8")
    pairs = [["        self.validate()\n        kind = event.causal_event.get(\"kind\")\n        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:","        self.validate()\n        return self._project_validated(event)\n\n    def _project_validated(self, event: JournalEntry) -> dict[str, object]:\n        \"\"\"Internal fast path: caller validated this exact policy already.\n\n        No exemption from the event-kind or lived-field epistemic guards.\n        Direct callers must keep using project(), which always validates.\n        \"\"\"\n        kind = event.causal_event.get(\"kind\")\n        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:"],["            policy.project(entry)\n            validated.append(event_ref)","            if type(policy) is AutobiographicalPolicy:\n                policy._project_validated(entry)\n            else:\n                policy.project(entry)\n            validated.append(event_ref)"],["        projected: list[dict[str, object]] = []\n\n        for commit_event_id in self._commit_event_ids:","        projected: list[dict[str, object]] = []\n        # Exact built-in immutable policies can be validated once per read;\n        # custom policy subclasses keep their original validation cadence.\n        validated_versions: set[str] = set()\n\n        for commit_event_id in self._commit_event_ids:"],["            policy.validate()\n\n            for event_ref in refs:","            if type(policy) is AutobiographicalPolicy:\n                if version not in validated_versions:\n                    policy.validate()\n                    validated_versions.add(version)\n            else:\n                policy.validate()\n\n            for event_ref in refs:"],["                    projected.append(policy.project(source))","                    projected.append(\n                        policy._project_validated(source)\n                        if type(policy) is AutobiographicalPolicy\n                        else policy.project(source)\n                    )"]]
    for old, new in pairs:
        if from_source.count(old) != 1:
            raise ValueError("earlier JournalViews reference drifted")
        from_source = from_source.replace(old, new, 1)
    return from_source.encode("utf-8")


def _approved_stage2_operator_closure(before: bytes, after: bytes) -> bool:
    """Approve only two exact operator-side full-journal copy removals."""
    source, changed = before.decode("utf-8"), after.decode("utf-8")
    pairs = [["        entries = self.journal.entries\n        if not entries:\n            raise RuntimeError(\"no journaled closure\")\n        closure = entries[-1]","        # Operator-only read: inspect the last immutable occurrence without\n        # copying the entire technical journal at every closed world step.\n        closure = next(self.journal.iter_entries_reversed(), None)\n        if closure is None:\n            raise RuntimeError(\"no journaled closure\")"],["            \"journal_event_count\": len(entries),","            \"journal_event_count\": self.journal.entry_count,"]]
    for old, new in pairs:
        if source.count(old) != 1 or changed.count(new) != 1:
            return False
        source = source.replace(old, new, 1)
    return source == changed


def _approved_wal_streaming(before: bytes, after: bytes) -> bool:
    """Only the source-inspected WAL streaming body, not weaker auditing."""
    original = before.decode("utf-8")
    current = after.decode("utf-8")
    former = "        with open(path, \"rb\") as stream:\n            contents = stream.read()\n        if contents and not contents.endswith(b\"\\n\"):\n            raise ValueError(\"unterminated durable journal record\")\n        replay = HashChainedJournal()\n        for raw in contents.splitlines():"
    newer = "        replay = HashChainedJournal()\n        with open(path, \"rb\") as stream:\n            for record in stream:\n                if not record.endswith(b\"\\n\"):\n                    raise ValueError(\"unterminated durable journal record\")\n                raw = record[:-1]\n                # Match bytes.splitlines() for the previously accepted CRLF\n                # separator, without relaxing canonical JSON record checks.\n                if raw.endswith(b\"\\r\"):\n                    raw = raw[:-1]"
    # Docstring change is explicitly reviewed as part of the same method.
    old_doc = "Verify a complete durable file offline; never resurrect an individual.\n\n        A torn last record or any rewritten, duplicated or reordered event\n        fails closed. Only an attestation is returned, not a runnable journal."
    new_doc = "Verify an entire durable WAL offline without buffering the file.\n\n        The replay still performs every canonical-byte, occurrence-order,\n        SHA-256 chain and terminal-state check. Only the transient full-file\n        byte buffer and splitlines list are removed. This never recovers life."
    if (original.count(former) != 1 or current.count(newer) != 1
            or original.count(old_doc) != 1 or current.count(new_doc) != 1):
        return False
    candidate = original.replace(old_doc, new_doc, 1).replace(former, newer, 1)
    # All lines in the streaming loop's old body become four spaces deeper.
    start = candidate.index("            if not raw:")
    end = candidate.index("        if not replay.verify():", start)
    candidate = candidate[:start] + "".join(
        "    " + line if line.strip() else line
        for line in candidate[start:end].splitlines(keepends=True)
    ) + candidate[end:]
    return candidate == current


def _approved_stage6_bfs_deque(before: bytes, after: bytes) -> bool:
    """Only the three reviewed FIFO queue transformations."""
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    for old, new in [["from dataclasses import dataclass","from collections import deque\nfrom dataclasses import dataclass"],["        queue: list[_Node] = [\n            _Node(\n                state=initial_state,\n                commands=(),\n                predictions=(),\n            )\n        ]","        queue = deque([\n            _Node(\n                state=initial_state,\n                commands=(),\n                predictions=(),\n            )\n        ])"],["            node = queue.pop(0)","            node = queue.popleft()"]]:
        if original.count(old) != 1 or candidate.count(new) != 1:
            return False
        original = original.replace(old, new, 1)
    return original == candidate


def _approved_agency_evidence_index(before: bytes, after: bytes) -> bool:
    """Only two exact reviewed adaptive index blocks."""
    old, new = before.decode("utf-8"), after.decode("utf-8")
    for prior, replacement in [["        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):","        # Ephemeral published evidence view. The first two admissible\n        # lookups scan it directly; only a third lookup pays for an index.\n        # No persistent cache, extra causal owner or hidden information.\n        published_reports: tuple[AgencyEvidence, ...] | None = None\n        published_by_action: dict[\n            tuple[str, int, int], list[AgencyEvidence]\n        ] | None = None\n        eligible_lookups = 0\n\n        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"],["            for report in self.published_agency_evidence():\n                if (\n                    report.option_ref != witness.option_ref\n                    or report.sent_t_monde != witness.sent_t_monde\n                    or report.observed_t_monde != witness.observed_t_monde\n                ):\n                    continue\n                compatible = any(","            if published_reports is None:\n                published_reports = self.published_agency_evidence()\n            eligible_lookups += 1\n            if eligible_lookups == 3:\n                published_by_action = {}\n                for report in published_reports:\n                    key = (\n                        report.option_ref, report.sent_t_monde,\n                        report.observed_t_monde,\n                    )\n                    published_by_action.setdefault(key, []).append(report)\n\n            # Preserve the original direct scan for small histories; do\n            # not allocate a filtering generator for one or two witnesses.\n            matching_reports = (\n                published_reports if published_by_action is None\n                else published_by_action.get(\n                    (witness.option_ref, witness.sent_t_monde,\n                     witness.observed_t_monde), ()\n                )\n            )\n            for report in matching_reports:\n                if (\n                    report.option_ref != witness.option_ref\n                    or report.sent_t_monde != witness.sent_t_monde\n                    or report.observed_t_monde != witness.observed_t_monde\n                ):\n                    continue\n                compatible = any("]]:
        if old.count(prior) != 1 or new.count(replacement) != 1:
            return False
        old = old.replace(prior, replacement, 1)
    return old == new


def _approved_agency_publication_duplicate_index(before: bytes, after: bytes) -> bool:
    """Permit the exact transient duplicate-physical-reference lookup."""
    old = "        agency = dict(self._agency_evidence)\n        for report in sorted(\n            self._pending_agency_evidence,\n            key=lambda value: (value.observed_t_monde, value.event_ref),\n        ):\n            if report.event_ref in {v.event_ref for v in agency.values()}:\n                raise ValueError(\"duplicate published physical agency observation\")\n            agency[report.identifier] = report"
    new = "        agency = dict(self._agency_evidence)\n        # Build an ephemeral index of physical references present in the\n        # current mapping. Identifier replacements must not leave stale refs.\n        agency_event_refs = {report.event_ref for report in agency.values()}\n        for report in sorted(\n            self._pending_agency_evidence,\n            key=lambda value: (value.observed_t_monde, value.event_ref),\n        ):\n            if report.event_ref in agency_event_refs:\n                raise ValueError(\"duplicate published physical agency observation\")\n            displaced = agency.get(report.identifier)\n            if displaced is not None and not any(\n                other.event_ref == displaced.event_ref\n                for key, other in agency.items()\n                if key != report.identifier\n            ):\n                # An overwritten report no longer occupies its old source.\n                # This rare fallback preserves exact previous semantics.\n                agency_event_refs.discard(displaced.event_ref)\n            agency[report.identifier] = report\n            agency_event_refs.add(report.event_ref)"
    original, changed = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and changed.count(new) == 1
            and original.replace(old, new, 1) == changed)


def _reference_causal_minimum(before: bytes) -> bytes:
    """Reconstruct the #261 exact stable intervention witness change."""
    old_one = "            if len(matching_contexts) < self.config.n2:\n                continue\n\n            if published_reports is None:"
    new_one = "            if len(matching_contexts) < self.config.n2:\n                continue\n            # This provenance witness is constant for this numeric outcome.\n            # Compute it once, not once for each compatible P-47 report.\n            intervention_ref = min(trial.identifier for trial in active_trials)\n\n            if published_reports is None:"
    old_two = "                    intervention_ref=min(\n                        trial.identifier for trial in active_trials\n                    ),"
    new_two = "                    intervention_ref=intervention_ref,"
    text = before.decode("utf-8")
    if text.count(old_one) != 1 or text.count(old_two) != 1:
        raise ValueError("causal minimum reference drift")
    return text.replace(old_one, new_one, 1).replace(old_two, new_two, 1).encode("utf-8")


def _reference_approved_active_context_cache(before: bytes) -> bytes:
    """Reconstruct the approved #264 exact source optimization."""
    old_a = "        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    new_a = "        # Query-local eligibility cache: every numeric witness of the same\n        # published contingency shares the same revision and interventions.\n        # Never persist this index or grant another owner causal authority.\n        active_by_contingency: dict[str, tuple[str, ...] | None] = {}\n        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    old_b = "            active_trials = tuple(\n                trial for trial in trials\n                if trial.observed_step > revision\n            )\n            matching_contexts = {\n                trial.context_signature for trial in active_trials\n            }\n            if len(matching_contexts) < self.config.n2:\n                continue\n            # This provenance witness is constant for this numeric outcome.\n            # Compute it once, not once for each compatible P-47 report.\n            intervention_ref = min(trial.identifier for trial in active_trials)"
    new_b = "            if contingency.ref not in active_by_contingency:\n                active_trials = tuple(\n                    trial for trial in trials\n                    if trial.observed_step > revision\n                )\n                matching_contexts = {\n                    trial.context_signature for trial in active_trials\n                }\n                active_by_contingency[contingency.ref] = (\n                    (min(trial.identifier for trial in active_trials),)\n                    if len(matching_contexts) >= self.config.n2\n                    else None\n                )\n            selected = active_by_contingency[contingency.ref]\n            if selected is None:\n                continue\n            intervention_ref = selected[0]"
    content = before.decode("utf-8")
    if content.count(old_a) != 1 or content.count(old_b) != 1:
        raise ValueError("previous causal cache source drift")
    return content.replace(old_a, new_a, 1).replace(old_b, new_b, 1).encode("utf-8")


def _reference_approved_physical_alias(before: bytes) -> bytes:
    """Reconstruct the approved #265 exact alias-index transformation."""
    old = "        # Batch arrival never bypasses the prior published lifecycle level.\n        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):\n            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:\n                raise ValueError(\"unregistered causal predicate\")\n            key = (o.contingency_ref, o.observation_ref, \"observation\")\n            same_physical = (\n                v for v in observations.values()\n                if v.contingency_ref == o.contingency_ref\n                and v.observation_ref == o.observation_ref\n            )\n            for existing in same_physical:\n                # A second identifier for the same physical transition is\n                # harmless only if every claim about its provenance and\n                # observation matches. Merely comparing cause/effect labels\n                # would silently discard a contradictory world step or\n                # Memory episode, contaminating n1 provenance. Distinct\n                # physical references remain independent even when an\n                # autobiographical episode contains multiple transitions.\n                if replace(existing, identifier=o.identifier) != o:\n                    raise ValueError(\n                        \"conflicting causal labels for one physical observation\"\n                    )\n                break\n            else:\n                if key in credits:\n                    # Credits are always paired to accepted observations.\n                    # A lone credit cannot justify silently losing a row.\n                    raise ValueError(\"causal observation credit lacks its source\")\n                old = published.get(o.contingency_ref)\n                if old is None:\n                    old = CanonicalContingency(\n                        ref=o.contingency_ref, version=1, predicate=o.predicate,\n                        subject_ref=o.subject_ref, context_signature=o.application_context,\n                        causal_status=\"aucun\", safety_status=\"aucun\",\n                        evidence_refs=(), harmful_episodes=(), harmless_episodes=(),\n                    )\n                elif (old.predicate, old.subject_ref, old.context_signature) != (\n                    o.predicate, o.subject_ref, o.application_context\n                ):\n                    raise ValueError(\"observation mismatches canonical contingency\")\n                credits.add(key)\n                observations[o.identifier] = o\n                published[o.contingency_ref] = old\n                continue\n            # An identical physical alias has no second P-35 credit.\n            continue"
    new = "        # Most publication cycles have zero or one new observation. Build\n        # this transient index only for batches large enough to amortize it.\n        # It is not persistent evidence, memory or another causal owner.\n        index_physical_sources = len(self._pending_causal_observations) >= 3\n        first_physical: dict[tuple[str, str], CausalObservation] = {}\n        if index_physical_sources:\n            for prior in observations.values():\n                first_physical.setdefault(\n                    (prior.contingency_ref, prior.observation_ref), prior\n                )\n\n        # Batch arrival never bypasses the prior published lifecycle level.\n        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):\n            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:\n                raise ValueError(\"unregistered causal predicate\")\n            key = (o.contingency_ref, o.observation_ref, \"observation\")\n            # A colliding identifier may replace an earlier physical\n            # source in the mapping. Keep exact old scan semantics for the\n            # rest of this batch instead of retaining a stale indexed row.\n            if index_physical_sources and o.identifier in observations:\n                index_physical_sources = False\n            if index_physical_sources:\n                first = first_physical.get((o.contingency_ref, o.observation_ref))\n                same_physical = (first,) if first is not None else ()\n            else:\n                same_physical = (\n                    v for v in observations.values()\n                    if v.contingency_ref == o.contingency_ref\n                    and v.observation_ref == o.observation_ref\n                )\n            for existing in same_physical:\n                # A second identifier for the same physical transition is\n                # harmless only if every claim about its provenance and\n                # observation matches. Merely comparing cause/effect labels\n                # would silently discard a contradictory world step or\n                # Memory episode, contaminating n1 provenance. Distinct\n                # physical references remain independent even when an\n                # autobiographical episode contains multiple transitions.\n                if replace(existing, identifier=o.identifier) != o:\n                    raise ValueError(\n                        \"conflicting causal labels for one physical observation\"\n                    )\n                break\n            else:\n                if key in credits:\n                    # Credits are always paired to accepted observations.\n                    # A lone credit cannot justify silently losing a row.\n                    raise ValueError(\"causal observation credit lacks its source\")\n                old = published.get(o.contingency_ref)\n                if old is None:\n                    old = CanonicalContingency(\n                        ref=o.contingency_ref, version=1, predicate=o.predicate,\n                        subject_ref=o.subject_ref, context_signature=o.application_context,\n                        causal_status=\"aucun\", safety_status=\"aucun\",\n                        evidence_refs=(), harmful_episodes=(), harmless_episodes=(),\n                    )\n                elif (old.predicate, old.subject_ref, old.context_signature) != (\n                    o.predicate, o.subject_ref, o.application_context\n                ):\n                    raise ValueError(\"observation mismatches canonical contingency\")\n                credits.add(key)\n                observations[o.identifier] = o\n                if index_physical_sources:\n                    first_physical.setdefault(\n                        (o.contingency_ref, o.observation_ref), o\n                    )\n                published[o.contingency_ref] = old\n                continue\n            # An identical physical alias has no second P-35 credit.\n            continue"
    original = before.decode("utf-8")
    if original.count(old) != 1:
        raise ValueError("source-alias reference drift")
    return original.replace(old, new, 1).encode("utf-8")


def _reference_approved_confirmed_count(before: bytes) -> bytes:
    """Reconstruct the exact already approved P-35 count optimization."""
    old = "            if sum(x.effect_present for x in e.values()) * len(b) <= (\n                sum(y.effect_present for y in b.values()) * len(e)\n            ):"
    new = "            # Already counted distinct positive exposed identifiers above.\n            if len(confirmed) * len(b) <= (\n                sum(y.effect_present for y in b.values()) * len(e)\n            ):"
    original = before.decode("utf-8")
    if original.count(old) != 1:
        raise ValueError("P-35 confirmed-count reference drift")
    return original.replace(old, new, 1).encode("utf-8")


def _reference_lived_review_dispatch(before: bytes) -> bytes:
    """Reconstruct exactly the already approved #267 transformation."""
    old = "            for review in (\n                self._lived_food_hypothesis_review(record, observations),\n                self._lived_hydration_hypothesis_review(record, observations),\n            )"
    new = "            # Each reviewer requires a distinct predicate. Never invoke\n            # both expensive observation scans for the same contingency.\n            for review in (\n                (\n                    self._lived_food_hypothesis_review(record, observations)\n                    if record.predicate == \"toxic_item\" else\n                    self._lived_hydration_hypothesis_review(record, observations)\n                    if record.predicate == \"hydration_effect\" else None\n                ),\n            )"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("review dispatch reference drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_approved_stream_noncanonical_pairs(before: bytes) -> bytes:
    """Reconstruct the approved #268 exact causal-control projection."""
    old = "                matched = [\n                    (x, y) for x in exposed for y in control\n                    if x.observation_context == y.observation_context\n                    and x.controlled_variables == y.controlled_variables\n                ]\n                if not matched:\n                    continue\n                e = {x.identifier: x for x, _ in matched}\n                b = {y.identifier: y for _, y in matched}"
    new = "                e = {}\n                b = {}\n                for x in exposed:\n                    for y in control:\n                        if (\n                            x.observation_context == y.observation_context\n                            and x.controlled_variables == y.controlled_variables\n                        ):\n                            e[x.identifier] = x\n                            b[y.identifier] = y\n                if not e:\n                    continue"
    content = before.decode("utf-8")
    if content.count(old) != 1:
        raise ValueError("previous P-35 noncanonical source drift")
    return content.replace(old, new, 1).encode("utf-8")


def _reference_approved_revision_contexts(before: bytes) -> bytes:
    """Reconstruct only the already approved #269 source transformations."""
    old_a = "        positive_by_ref = defaultdict(list)\n\n        def index_admitted_trial(item: CausalIntervention) -> None:"
    new_a = "        positive_by_ref = defaultdict(list)\n        # One transient context set per contingency/revision, enabled only\n        # for larger batches. Refutation invalidates every pre-boundary count.\n        reuse_positive_contexts = len(self._pending_causal_interventions) >= 3\n        positive_contexts_by_ref: dict[str, tuple[int, set[str]]] = {}\n\n        def index_admitted_trial(item: CausalIntervention) -> None:"
    old_b = "            if item.observed_effect and item.attribution == \"self_compatible\":\n                positive_by_ref[item.contingency_ref].append(item)"
    new_b = "            if item.observed_effect and item.attribution == \"self_compatible\":\n                positive_by_ref[item.contingency_ref].append(item)\n                # Only already admitted physical evidence may extend an\n                # existing context view, and only beyond its revision bound.\n                if reuse_positive_contexts:\n                    cached = positive_contexts_by_ref.get(item.contingency_ref)\n                    if cached is not None and item.observed_step > cached[0]:\n                        cached[1].add(item.context_signature)"
    old_c = "                if trial.observed_step > previous_boundary:\n                    revisions[old.ref] = (trial.observed_step, trial.identifier)"
    new_c = "                if trial.observed_step > previous_boundary:\n                    revisions[old.ref] = (trial.observed_step, trial.identifier)\n                    # Old positive contexts can no longer establish the claim.\n                    if reuse_positive_contexts:\n                        positive_contexts_by_ref.pop(old.ref, None)"
    old_d = "                # Check only positive, self-compatible interventions of\n                # this contingency, including earlier accepted batch rows.\n                contexts = {\n                    x.context_signature for x in positive_by_ref.get(old.ref, ())\n                    if x.observed_step > boundary\n                }"
    new_d = "                # Check only positive, self-compatible interventions of\n                # this contingency, including earlier accepted batch rows.\n                # The source list stays authoritative. Cached context sets\n                # are local to this publication and this exact revision.\n                cached = (\n                    positive_contexts_by_ref.get(old.ref)\n                    if reuse_positive_contexts else None\n                )\n                if cached is None or cached[0] != boundary:\n                    contexts = {\n                        x.context_signature for x in positive_by_ref.get(old.ref, ())\n                        if x.observed_step > boundary\n                    }\n                    if reuse_positive_contexts:\n                        positive_contexts_by_ref[old.ref] = (boundary, contexts)\n                else:\n                    contexts = cached[1]"
    source = before.decode("utf-8")
    for old, new in (
        (old_a, new_a),
        (old_b, new_b),
        (old_c, new_c),
        (old_d, new_d),
    ):
        if source.count(old) != 1:
            raise ValueError("approved revision-context source drift")
        source = source.replace(old, new, 1)
    return source.encode("utf-8")


def _reference_approved_physical_prior_buckets(before: bytes) -> bytes:
    """Rebuild the exact reviewed #270 optimization."""
    old_a = "            prior_uses = tuple(chain(\n                prior_by_physical.get(trial.observation_ref, ()),\n                prior_by_comparator.get(\n                    (trial.contingency_ref, trial.comparator_ref), ()\n                ),\n                prior_by_emitted.get(\n                    (trial.contingency_ref, trial.emitted_step), ()\n                ),\n                prior_by_observed.get(\n                    (trial.contingency_ref, trial.observed_step), ()\n                ),\n            ))"
    new_a = "            # Keep the four existing buckets by reference, not a tuple\n            # materializing their concatenation (which may repeat a trial).\n            prior_use_buckets = (\n                prior_by_physical.get(trial.observation_ref, ()),\n                prior_by_comparator.get(\n                    (trial.contingency_ref, trial.comparator_ref), ()\n                ),\n                prior_by_emitted.get(\n                    (trial.contingency_ref, trial.emitted_step), ()\n                ),\n                prior_by_observed.get(\n                    (trial.contingency_ref, trial.observed_step), ()\n                ),\n            )"
    old_b = "                for other in prior_uses\n            ):"
    new_b = "                for bucket in prior_use_buckets\n                for other in bucket\n            ):"
    old_c = "            if key in credits or prior_uses:\n                continue"
    new_c = "            if key in credits or any(prior_use_buckets):\n                continue"
    text = before.decode("utf-8")
    for old, new in ((old_a,new_a), (old_b,new_b), (old_c,new_c)):
        if text.count(old) != 1:
            raise ValueError("prior intervention source drift")
        text = text.replace(old, new, 1)
    return text.encode("utf-8")


def _reference_deferred_single_scan(before: bytes) -> bytes:
    """Reapply precisely the reviewed #271 source transformation."""
    old = "            successful = [\n                item for item in positive_by_ref.get(ref, ())\n                if item.observed_step > boundary\n            ]\n            if len({item.context_signature for item in successful}) < self.config.n2:\n                continue\n            current = published[ref]\n            # The previous sorted(...)[-1] chose the greatest observed\n            # (world-step, identifier) pair. Select the same witness without\n            # sorting every historical success of this contingency.\n            witness = max(\n                successful, key=lambda item: (item.observed_step, item.identifier)\n            )"
    new = "            # Accumulate independent contexts and the same maximal physical\n            # witness in one scan, without retaining another history list.\n            contexts: set[str] = set()\n            witness = None\n            for item in positive_by_ref.get(ref, ()):\n                if item.observed_step <= boundary:\n                    continue\n                contexts.add(item.context_signature)\n                if witness is None or (\n                    item.observed_step, item.identifier\n                ) > (witness.observed_step, witness.identifier):\n                    witness = item\n            if len(contexts) < self.config.n2:\n                continue\n            current = published[ref]"
    value = before.decode("utf-8")
    if value.count(old) != 1:
        raise ValueError("reviewed deferred selection drift")
    return value.replace(old, new, 1).encode("utf-8")


def _reference_hydration_classification(before: bytes) -> bytes:
    """Reconstruct the exact #272 reviewed classification."""
    old = "        observed = [\n            value for value in observations.values()\n            if value.identifier in self._hydration_observation_witnesses\n            and value.contingency_ref == contingency.ref\n            and value.predicate == contingency.predicate\n            and value.application_context == contingency.context_signature\n            and value.observation_context == \"water_source\"\n            and value.controlled_variables\n        ]\n        treated = sorted(\n            (value for value in observed if value.cause_present\n             and value.effect_present),\n            key=lambda value: value.identifier,\n        )\n        controls = sorted(\n            (value for value in observed if not value.cause_present\n             and not value.effect_present),\n            key=lambda value: value.identifier,\n        )"
    new = "        treated = []\n        controls = []\n        for value in observations.values():\n            if (\n                value.identifier not in self._hydration_observation_witnesses\n                or value.contingency_ref != contingency.ref\n                or value.predicate != contingency.predicate\n                or value.application_context != contingency.context_signature\n                or value.observation_context != \"water_source\"\n                or not value.controlled_variables\n            ):\n                continue\n            if value.cause_present and value.effect_present:\n                treated.append(value)\n            elif not value.cause_present and not value.effect_present:\n                controls.append(value)\n        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("hydration classification source drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_hydration_empty_arm(before: bytes) -> bytes:
    """Reapply only the reviewed #273 return guard."""
    old = "        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)\n        # Recovered or directly validated observations may contain lists:"
    new = "        # Both physical arms are necessary for any contrasting pair.\n        # Avoid sorting and indexing when one arm was never observed.\n        if not treated or not controls:\n            return None\n        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)\n        # Recovered or directly validated observations may contain lists:"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("prior hydration shortcut source drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_food_empty_arm(before: bytes) -> bytes:
    """Reconstruct the reviewed #274 source shortcut exactly."""
    old = "        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)"
    new = "        # A matched physical pair requires both arms. Empty groups could\n        # never pass the existing comparison loop, so skip its sorting.\n        if not exposed or not controls:\n            return None\n        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)"
    content = before.decode("utf-8")
    if content.count(old) != 1:
        raise ValueError("food empty-arm source drift")
    return content.replace(old, new, 1).encode("utf-8")


def _reference_agency_projection_stream(before: bytes) -> bytes:
    """Rebuild the reviewed #275 source optimization."""
    old = "        agency_projection_refs = [\n            event[\"event_id\"] for event in closed_events\n            if event[\"event_id\"] in agency_source_refs\n        ]\n        if len(agency_projection_refs) != len(set(agency_projection_refs)):\n            raise ValueError(\"duplicate closed Memory agency event projection\")"
    new = "        # Detect projection aliases without allocating a second list\n        # and then a second set of the same closed Memory identifiers.\n        seen_agency_projections: set[str] = set()\n        for event in closed_events:\n            ref = event[\"event_id\"]\n            if ref not in agency_source_refs:\n                continue\n            if ref in seen_agency_projections:\n                raise ValueError(\"duplicate closed Memory agency event projection\")\n            seen_agency_projections.add(ref)"
    data = before.decode("utf-8")
    if data.count(old) != 1:
        raise ValueError("agency projection reference drift")
    return data.replace(old, new, 1).encode("utf-8")


def _reference_numeric_no_concat(before: bytes) -> bytes:
    """Rebuild reviewed #276 source change."""
    old = "                    for old in (\n                        *self._numeric_witnesses.values(),\n                        *self._pending_numeric_witnesses,\n                    )"
    new = "                    for rows in (\n                        self._numeric_witnesses.values(),\n                        self._pending_numeric_witnesses,\n                    )\n                    for old in rows"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("numeric preflight reference drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_published_agency_sorted_items(before: bytes) -> bytes:
    """Reconstruct reviewed #277 agency reading change."""
    old = "        return tuple(self._agency_evidence[key] for key in sorted(self._agency_evidence))"
    new = "        return tuple(value for _, value in sorted(self._agency_evidence.items()))"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("agency mapping read reference drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_empty_agency_preflight(before: bytes) -> bytes:
    """Reconstruct the exact reviewed #278 source change."""
    old = "        # Preflight the whole episode; no partial causal buffering if one\n        # observation is duplicate or has inconsistent physical provenance.\n        historical_refs = {v.event_ref for v in self._agency_evidence.values()}"
    new = "        # No newly decoded agency comparison can collide or be buffered.\n        # Avoid scanning the entire published history on unrelated episodes.\n        if not admitted:\n            return ()\n        # Preflight the whole episode; no partial causal buffering if one\n        # observation is duplicate or has inconsistent physical provenance.\n        historical_refs = {v.event_ref for v in self._agency_evidence.values()}"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("empty agency preflight source drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_food_control_index_loop(before: bytes) -> bytes:
    """Reconstruct the reviewed #279 single-view food-control generation."""
    old = "        for observed in tuple(causal_observations):\n            for treatment, control in self.config.food_control_pairs:"
    new = "        # Iterate only the initial observed exposures. Appended controls\n        # must never be recycled as independent physical observations.\n        original_observation_count = len(causal_observations)\n        for index in range(original_observation_count):\n            observed = causal_observations[index]\n            for treatment, control in self.config.food_control_pairs:"
    original = before.decode("utf-8")
    if original.count(old) != 1:
        raise ValueError("prior food-control source drift")
    return original.replace(old, new, 1).encode("utf-8")


def _approved_numeric_episode_ref_index(before: bytes, after: bytes) -> bool:
    """Only allow a read-only per-episode physical witness reference set."""
    old = "        for witness in numeric_witnesses:\n            witness.validate()\n            if (\n                witness.identifier in self._numeric_witnesses\n                or any(\n                    old.transition_event_ref == witness.transition_event_ref\n                    for rows in (\n                        self._numeric_witnesses.values(),\n                        self._pending_numeric_witnesses,\n                    )\n                    for old in rows\n                )\n            ):\n                raise ValueError(\"duplicated closed physical numeric outcome\")"
    new = "        # Most closed episodes contain no numeric witnesses. Avoid paying\n        # for an all-history index in empty or very small batches.\n        # Existing history is immutable throughout this admission preflight.\n        existing_numeric_transition_refs = (\n            {\n                old.transition_event_ref\n                for rows in (\n                    self._numeric_witnesses.values(),\n                    self._pending_numeric_witnesses,\n                )\n                for old in rows\n            } if len(numeric_witnesses) >= 3 else None\n        )\n        for witness in numeric_witnesses:\n            witness.validate()\n            if (\n                witness.identifier in self._numeric_witnesses\n                or (\n                    witness.transition_event_ref in existing_numeric_transition_refs\n                    if existing_numeric_transition_refs is not None\n                    else any(\n                        old.transition_event_ref == witness.transition_event_ref\n                        for rows in (\n                            self._numeric_witnesses.values(),\n                            self._pending_numeric_witnesses,\n                        )\n                        for old in rows\n                    )\n                )\n            ):\n                raise ValueError(\"duplicated closed physical numeric outcome\")"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_food_control_index_loop(before: bytes, after: bytes) -> bool:
    """Allow only index-bounded traversal of original food observations."""
    old = "        for observed in tuple(causal_observations):\n            for treatment, control in self.config.food_control_pairs:"
    new = "        # Iterate only the initial observed exposures. Appended controls\n        # must never be recycled as independent physical observations.\n        original_observation_count = len(causal_observations)\n        for index in range(original_observation_count):\n            observed = causal_observations[index]\n            for treatment, control in self.config.food_control_pairs:"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_empty_agency_preflight(before: bytes, after: bytes) -> bool:
    """Only bypass redundant historical scans with no accepted comparisons."""
    old = "        # Preflight the whole episode; no partial causal buffering if one\n        # observation is duplicate or has inconsistent physical provenance.\n        historical_refs = {v.event_ref for v in self._agency_evidence.values()}"
    new = "        # No newly decoded agency comparison can collide or be buffered.\n        # Avoid scanning the entire published history on unrelated episodes.\n        if not admitted:\n            return ()\n        # Preflight the whole episode; no partial causal buffering if one\n        # observation is duplicate or has inconsistent physical provenance.\n        historical_refs = {v.event_ref for v in self._agency_evidence.values()}"
    reference, candidate = before.decode("utf-8"), after.decode("utf-8")
    return reference.count(old) == 1 and candidate.count(new) == 1 and reference.replace(old, new, 1) == candidate


def _approved_published_agency_sorted_items(before: bytes, after: bytes) -> bool:
    """Only remove redundant dictionary lookup after sorting keys."""
    old = "        return tuple(self._agency_evidence[key] for key in sorted(self._agency_evidence))"
    new = "        return tuple(value for _, value in sorted(self._agency_evidence.items()))"
    source, candidate = before.decode("utf-8"), after.decode("utf-8")
    return source.count(old) == 1 and candidate.count(new) == 1 and source.replace(old, new, 1) == candidate


def _approved_numeric_witness_no_concat(before: bytes, after: bytes) -> bool:
    """Admit only non-materializing ordered witness duplicate validation."""
    old = "                    for old in (\n                        *self._numeric_witnesses.values(),\n                        *self._pending_numeric_witnesses,\n                    )"
    new = "                    for rows in (\n                        self._numeric_witnesses.values(),\n                        self._pending_numeric_witnesses,\n                    )\n                    for old in rows"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_stream_agency_projection_check(before: bytes, after: bytes) -> bool:
    """Only permit a one-pass alias detector for closed Memory IDs."""
    old = "        agency_projection_refs = [\n            event[\"event_id\"] for event in closed_events\n            if event[\"event_id\"] in agency_source_refs\n        ]\n        if len(agency_projection_refs) != len(set(agency_projection_refs)):\n            raise ValueError(\"duplicate closed Memory agency event projection\")"
    new = "        # Detect projection aliases without allocating a second list\n        # and then a second set of the same closed Memory identifiers.\n        seen_agency_projections: set[str] = set()\n        for event in closed_events:\n            ref = event[\"event_id\"]\n            if ref not in agency_source_refs:\n                continue\n            if ref in seen_agency_projections:\n                raise ValueError(\"duplicate closed Memory agency event projection\")\n            seen_agency_projections.add(ref)"
    source, candidate = before.decode("utf-8"), after.decode("utf-8")
    return source.count(old) == 1 and candidate.count(new) == 1 and source.replace(old, new, 1) == candidate


def _approved_food_empty_arm(before: bytes, after: bytes) -> bool:
    """Allow only a no-physical-pair food review shortcut."""
    old = "        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)"
    new = "        # A matched physical pair requires both arms. Empty groups could\n        # never pass the existing comparison loop, so skip its sorting.\n        if not exposed or not controls:\n            return None\n        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_hydration_empty_arm_shortcut(before: bytes, after: bytes) -> bool:
    """Allow only the empty treated/control arm early return."""
    old = "        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)\n        # Recovered or directly validated observations may contain lists:"
    new = "        # Both physical arms are necessary for any contrasting pair.\n        # Avoid sorting and indexing when one arm was never observed.\n        if not treated or not controls:\n            return None\n        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)\n        # Recovered or directly validated observations may contain lists:"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_hydration_single_classification(before: bytes, after: bytes) -> bool:
    """Allow only stream classification before existing lexical sorts."""
    old = "        observed = [\n            value for value in observations.values()\n            if value.identifier in self._hydration_observation_witnesses\n            and value.contingency_ref == contingency.ref\n            and value.predicate == contingency.predicate\n            and value.application_context == contingency.context_signature\n            and value.observation_context == \"water_source\"\n            and value.controlled_variables\n        ]\n        treated = sorted(\n            (value for value in observed if value.cause_present\n             and value.effect_present),\n            key=lambda value: value.identifier,\n        )\n        controls = sorted(\n            (value for value in observed if not value.cause_present\n             and not value.effect_present),\n            key=lambda value: value.identifier,\n        )"
    new = "        treated = []\n        controls = []\n        for value in observations.values():\n            if (\n                value.identifier not in self._hydration_observation_witnesses\n                or value.contingency_ref != contingency.ref\n                or value.predicate != contingency.predicate\n                or value.application_context != contingency.context_signature\n                or value.observation_context != \"water_source\"\n                or not value.controlled_variables\n            ):\n                continue\n            if value.cause_present and value.effect_present:\n                treated.append(value)\n            elif not value.cause_present and not value.effect_present:\n                controls.append(value)\n        treated.sort(key=lambda value: value.identifier)\n        controls.sort(key=lambda value: value.identifier)"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_deferred_single_scan(before: bytes, after: bytes) -> bool:
    """Allow only single-pass positive history witness selection."""
    old = "            successful = [\n                item for item in positive_by_ref.get(ref, ())\n                if item.observed_step > boundary\n            ]\n            if len({item.context_signature for item in successful}) < self.config.n2:\n                continue\n            current = published[ref]\n            # The previous sorted(...)[-1] chose the greatest observed\n            # (world-step, identifier) pair. Select the same witness without\n            # sorting every historical success of this contingency.\n            witness = max(\n                successful, key=lambda item: (item.observed_step, item.identifier)\n            )"
    new = "            # Accumulate independent contexts and the same maximal physical\n            # witness in one scan, without retaining another history list.\n            contexts: set[str] = set()\n            witness = None\n            for item in positive_by_ref.get(ref, ()):\n                if item.observed_step <= boundary:\n                    continue\n                contexts.add(item.context_signature)\n                if witness is None or (\n                    item.observed_step, item.identifier\n                ) > (witness.observed_step, witness.identifier):\n                    witness = item\n            if len(contexts) < self.config.n2:\n                continue\n            current = published[ref]"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return original.count(old) == 1 and candidate.count(new) == 1 and original.replace(old, new, 1) == candidate


def _approved_physical_prior_buckets(before: bytes, after: bytes) -> bool:
    """Allow only grouping existing physical-index lists by reference."""
    old_a = "            prior_uses = tuple(chain(\n                prior_by_physical.get(trial.observation_ref, ()),\n                prior_by_comparator.get(\n                    (trial.contingency_ref, trial.comparator_ref), ()\n                ),\n                prior_by_emitted.get(\n                    (trial.contingency_ref, trial.emitted_step), ()\n                ),\n                prior_by_observed.get(\n                    (trial.contingency_ref, trial.observed_step), ()\n                ),\n            ))"
    new_a = "            # Keep the four existing buckets by reference, not a tuple\n            # materializing their concatenation (which may repeat a trial).\n            prior_use_buckets = (\n                prior_by_physical.get(trial.observation_ref, ()),\n                prior_by_comparator.get(\n                    (trial.contingency_ref, trial.comparator_ref), ()\n                ),\n                prior_by_emitted.get(\n                    (trial.contingency_ref, trial.emitted_step), ()\n                ),\n                prior_by_observed.get(\n                    (trial.contingency_ref, trial.observed_step), ()\n                ),\n            )"
    old_b = "                for other in prior_uses\n            ):"
    new_b = "                for bucket in prior_use_buckets\n                for other in bucket\n            ):"
    old_c = "            if key in credits or prior_uses:\n                continue"
    new_c = "            if key in credits or any(prior_use_buckets):\n                continue"
    source, candidate = before.decode("utf-8"), after.decode("utf-8")
    for old, new in (
        (old_a, new_a),
        (old_b, new_b),
        (old_c, new_c),
    ):
        if source.count(old) != 1 or candidate.count(new) != 1:
            return False
        source = source.replace(old, new, 1)
    return source == candidate


def _approved_revision_bounded_context_cache(before: bytes, after: bytes) -> bool:
    """Allow only this query-local revision-scoped context-set change."""
    old_a = "        positive_by_ref = defaultdict(list)\n\n        def index_admitted_trial(item: CausalIntervention) -> None:"
    new_a = "        positive_by_ref = defaultdict(list)\n        # One transient context set per contingency/revision, enabled only\n        # for larger batches. Refutation invalidates every pre-boundary count.\n        reuse_positive_contexts = len(self._pending_causal_interventions) >= 3\n        positive_contexts_by_ref: dict[str, tuple[int, set[str]]] = {}\n\n        def index_admitted_trial(item: CausalIntervention) -> None:"
    old_b = "            if item.observed_effect and item.attribution == \"self_compatible\":\n                positive_by_ref[item.contingency_ref].append(item)"
    new_b = "            if item.observed_effect and item.attribution == \"self_compatible\":\n                positive_by_ref[item.contingency_ref].append(item)\n                # Only already admitted physical evidence may extend an\n                # existing context view, and only beyond its revision bound.\n                if reuse_positive_contexts:\n                    cached = positive_contexts_by_ref.get(item.contingency_ref)\n                    if cached is not None and item.observed_step > cached[0]:\n                        cached[1].add(item.context_signature)"
    old_c = "                if trial.observed_step > previous_boundary:\n                    revisions[old.ref] = (trial.observed_step, trial.identifier)"
    new_c = "                if trial.observed_step > previous_boundary:\n                    revisions[old.ref] = (trial.observed_step, trial.identifier)\n                    # Old positive contexts can no longer establish the claim.\n                    if reuse_positive_contexts:\n                        positive_contexts_by_ref.pop(old.ref, None)"
    old_d = "                # Check only positive, self-compatible interventions of\n                # this contingency, including earlier accepted batch rows.\n                contexts = {\n                    x.context_signature for x in positive_by_ref.get(old.ref, ())\n                    if x.observed_step > boundary\n                }"
    new_d = "                # Check only positive, self-compatible interventions of\n                # this contingency, including earlier accepted batch rows.\n                # The source list stays authoritative. Cached context sets\n                # are local to this publication and this exact revision.\n                cached = (\n                    positive_contexts_by_ref.get(old.ref)\n                    if reuse_positive_contexts else None\n                )\n                if cached is None or cached[0] != boundary:\n                    contexts = {\n                        x.context_signature for x in positive_by_ref.get(old.ref, ())\n                        if x.observed_step > boundary\n                    }\n                    if reuse_positive_contexts:\n                        positive_contexts_by_ref[old.ref] = (boundary, contexts)\n                else:\n                    contexts = cached[1]"
    expected, candidate = before.decode("utf-8"), after.decode("utf-8")
    for old, new in (
        (old_a, new_a),
        (old_b, new_b),
        (old_c, new_c),
        (old_d, new_d),
    ):
        if expected.count(old) != 1 or candidate.count(new) != 1:
            return False
        expected = expected.replace(old, new, 1)
    return expected == candidate


def _approved_stream_noncanonical_pairs(before: bytes, after: bytes) -> bool:
    """Only replace list materialization with ordered matching projections."""
    old = "                matched = [\n                    (x, y) for x in exposed for y in control\n                    if x.observation_context == y.observation_context\n                    and x.controlled_variables == y.controlled_variables\n                ]\n                if not matched:\n                    continue\n                e = {x.identifier: x for x, _ in matched}\n                b = {y.identifier: y for _, y in matched}"
    new = "                e = {}\n                b = {}\n                for x in exposed:\n                    for y in control:\n                        if (\n                            x.observation_context == y.observation_context\n                            and x.controlled_variables == y.controlled_variables\n                        ):\n                            e[x.identifier] = x\n                            b[y.identifier] = y\n                if not e:\n                    continue"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _approved_lived_review_predicate_dispatch(before: bytes, after: bytes) -> bool:
    """Allow only mutually exclusive lived-review calls, preserving order."""
    old = "            for review in (\n                self._lived_food_hypothesis_review(record, observations),\n                self._lived_hydration_hypothesis_review(record, observations),\n            )"
    new = "            # Each reviewer requires a distinct predicate. Never invoke\n            # both expensive observation scans for the same contingency.\n            for review in (\n                (\n                    self._lived_food_hypothesis_review(record, observations)\n                    if record.predicate == \"toxic_item\" else\n                    self._lived_hydration_hypothesis_review(record, observations)\n                    if record.predicate == \"hydration_effect\" else None\n                ),\n            )"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _approved_confirmed_count_reuse(before: bytes, after: bytes) -> bool:
    """Only reuse the already built distinct positive-ID set count."""
    old = "            if sum(x.effect_present for x in e.values()) * len(b) <= (\n                sum(y.effect_present for y in b.values()) * len(e)\n            ):"
    new = "            # Already counted distinct positive exposed identifiers above.\n            if len(confirmed) * len(b) <= (\n                sum(y.effect_present for y in b.values()) * len(e)\n            ):"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _approved_physical_observation_index(before: bytes, after: bytes) -> bool:
    """Only allow an ephemeral alias lookup with collision-safe fallback."""
    old = "        # Batch arrival never bypasses the prior published lifecycle level.\n        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):\n            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:\n                raise ValueError(\"unregistered causal predicate\")\n            key = (o.contingency_ref, o.observation_ref, \"observation\")\n            same_physical = (\n                v for v in observations.values()\n                if v.contingency_ref == o.contingency_ref\n                and v.observation_ref == o.observation_ref\n            )\n            for existing in same_physical:\n                # A second identifier for the same physical transition is\n                # harmless only if every claim about its provenance and\n                # observation matches. Merely comparing cause/effect labels\n                # would silently discard a contradictory world step or\n                # Memory episode, contaminating n1 provenance. Distinct\n                # physical references remain independent even when an\n                # autobiographical episode contains multiple transitions.\n                if replace(existing, identifier=o.identifier) != o:\n                    raise ValueError(\n                        \"conflicting causal labels for one physical observation\"\n                    )\n                break\n            else:\n                if key in credits:\n                    # Credits are always paired to accepted observations.\n                    # A lone credit cannot justify silently losing a row.\n                    raise ValueError(\"causal observation credit lacks its source\")\n                old = published.get(o.contingency_ref)\n                if old is None:\n                    old = CanonicalContingency(\n                        ref=o.contingency_ref, version=1, predicate=o.predicate,\n                        subject_ref=o.subject_ref, context_signature=o.application_context,\n                        causal_status=\"aucun\", safety_status=\"aucun\",\n                        evidence_refs=(), harmful_episodes=(), harmless_episodes=(),\n                    )\n                elif (old.predicate, old.subject_ref, old.context_signature) != (\n                    o.predicate, o.subject_ref, o.application_context\n                ):\n                    raise ValueError(\"observation mismatches canonical contingency\")\n                credits.add(key)\n                observations[o.identifier] = o\n                published[o.contingency_ref] = old\n                continue\n            # An identical physical alias has no second P-35 credit.\n            continue"
    new = "        # Most publication cycles have zero or one new observation. Build\n        # this transient index only for batches large enough to amortize it.\n        # It is not persistent evidence, memory or another causal owner.\n        index_physical_sources = len(self._pending_causal_observations) >= 3\n        first_physical: dict[tuple[str, str], CausalObservation] = {}\n        if index_physical_sources:\n            for prior in observations.values():\n                first_physical.setdefault(\n                    (prior.contingency_ref, prior.observation_ref), prior\n                )\n\n        # Batch arrival never bypasses the prior published lifecycle level.\n        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):\n            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:\n                raise ValueError(\"unregistered causal predicate\")\n            key = (o.contingency_ref, o.observation_ref, \"observation\")\n            # A colliding identifier may replace an earlier physical\n            # source in the mapping. Keep exact old scan semantics for the\n            # rest of this batch instead of retaining a stale indexed row.\n            if index_physical_sources and o.identifier in observations:\n                index_physical_sources = False\n            if index_physical_sources:\n                first = first_physical.get((o.contingency_ref, o.observation_ref))\n                same_physical = (first,) if first is not None else ()\n            else:\n                same_physical = (\n                    v for v in observations.values()\n                    if v.contingency_ref == o.contingency_ref\n                    and v.observation_ref == o.observation_ref\n                )\n            for existing in same_physical:\n                # A second identifier for the same physical transition is\n                # harmless only if every claim about its provenance and\n                # observation matches. Merely comparing cause/effect labels\n                # would silently discard a contradictory world step or\n                # Memory episode, contaminating n1 provenance. Distinct\n                # physical references remain independent even when an\n                # autobiographical episode contains multiple transitions.\n                if replace(existing, identifier=o.identifier) != o:\n                    raise ValueError(\n                        \"conflicting causal labels for one physical observation\"\n                    )\n                break\n            else:\n                if key in credits:\n                    # Credits are always paired to accepted observations.\n                    # A lone credit cannot justify silently losing a row.\n                    raise ValueError(\"causal observation credit lacks its source\")\n                old = published.get(o.contingency_ref)\n                if old is None:\n                    old = CanonicalContingency(\n                        ref=o.contingency_ref, version=1, predicate=o.predicate,\n                        subject_ref=o.subject_ref, context_signature=o.application_context,\n                        causal_status=\"aucun\", safety_status=\"aucun\",\n                        evidence_refs=(), harmful_episodes=(), harmless_episodes=(),\n                    )\n                elif (old.predicate, old.subject_ref, old.context_signature) != (\n                    o.predicate, o.subject_ref, o.application_context\n                ):\n                    raise ValueError(\"observation mismatches canonical contingency\")\n                credits.add(key)\n                observations[o.identifier] = o\n                if index_physical_sources:\n                    first_physical.setdefault(\n                        (o.contingency_ref, o.observation_ref), o\n                    )\n                published[o.contingency_ref] = old\n                continue\n            # An identical physical alias has no second P-35 credit.\n            continue"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _approved_active_context_cache(before: bytes, after: bytes) -> bool:
    """Only allow the exact request-local revision-invariant cache."""
    old_a = "        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    new_a = "        # Query-local eligibility cache: every numeric witness of the same\n        # published contingency shares the same revision and interventions.\n        # Never persist this index or grant another owner causal authority.\n        active_by_contingency: dict[str, tuple[str, ...] | None] = {}\n        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    old_b = "            active_trials = tuple(\n                trial for trial in trials\n                if trial.observed_step > revision\n            )\n            matching_contexts = {\n                trial.context_signature for trial in active_trials\n            }\n            if len(matching_contexts) < self.config.n2:\n                continue\n            # This provenance witness is constant for this numeric outcome.\n            # Compute it once, not once for each compatible P-47 report.\n            intervention_ref = min(trial.identifier for trial in active_trials)"
    new_b = "            if contingency.ref not in active_by_contingency:\n                active_trials = tuple(\n                    trial for trial in trials\n                    if trial.observed_step > revision\n                )\n                matching_contexts = {\n                    trial.context_signature for trial in active_trials\n                }\n                active_by_contingency[contingency.ref] = (\n                    (min(trial.identifier for trial in active_trials),)\n                    if len(matching_contexts) >= self.config.n2\n                    else None\n                )\n            selected = active_by_contingency[contingency.ref]\n            if selected is None:\n                continue\n            intervention_ref = selected[0]"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old_a) == original.count(old_b) == 1
            and candidate.count(new_a) == candidate.count(new_b) == 1
            and original.replace(old_a, new_a, 1).replace(old_b, new_b, 1) == candidate)


def _reference_hydration_control_lookup(before: bytes) -> bytes:
    """Reconstruct the exact already reviewed #263 hydration transformation."""
    old = "        for effect in treated:\n            for baseline in controls:\n                if (\n                    effect.observation_ref == baseline.observation_ref\n                    or effect.observed_step == baseline.observed_step\n                    or effect.controlled_variables != baseline.controlled_variables\n                    or effect.observation_context != baseline.observation_context\n                ):\n                    continue"
    new = "        # Recovered or directly validated observations may contain lists:\n        # equality comparisons worked for them, but list-backed controls\n        # cannot be used as dictionary keys. Never silently normalize proof.\n        # Preserve the original ordered scan for these uncommon inputs.\n        canonical_controls = all(\n            type(row.controlled_variables) is tuple\n            and all(type(pair) is tuple for pair in row.controlled_variables)\n            for rows in (treated, controls) for row in rows\n        )\n        controls_by_context: dict[\n            tuple[str, tuple[tuple[str, str], ...]], list[CausalObservation]\n        ] = {}\n        if canonical_controls:\n            for baseline in controls:\n                key = (baseline.observation_context, baseline.controlled_variables)\n                controls_by_context.setdefault(key, []).append(baseline)\n        for effect in treated:\n            comparable = (\n                controls_by_context.get(\n                    (effect.observation_context, effect.controlled_variables), ()\n                ) if canonical_controls else controls\n            )\n            for baseline in comparable:\n                if (\n                    effect.observation_ref == baseline.observation_ref\n                    or effect.observed_step == baseline.observed_step\n                    or effect.controlled_variables != baseline.controlled_variables\n                    or effect.observation_context != baseline.observation_context\n                ):\n                    continue"
    content = before.decode("utf-8")
    if content.count(old) != 1:
        raise ValueError("hydration reference drift")
    return content.replace(old, new, 1).encode("utf-8")


def _approved_hydration_control_lookup(before: bytes, after: bytes) -> bool:
    """Only permit the context-keyed, order-preserving hydration control lookup."""
    old = "        for effect in treated:\n            for baseline in controls:\n                if (\n                    effect.observation_ref == baseline.observation_ref\n                    or effect.observed_step == baseline.observed_step\n                    or effect.controlled_variables != baseline.controlled_variables\n                    or effect.observation_context != baseline.observation_context\n                ):\n                    continue"
    new = "        # Recovered or directly validated observations may contain lists:\n        # equality comparisons worked for them, but list-backed controls\n        # cannot be used as dictionary keys. Never silently normalize proof.\n        # Preserve the original ordered scan for these uncommon inputs.\n        canonical_controls = all(\n            type(row.controlled_variables) is tuple\n            and all(type(pair) is tuple for pair in row.controlled_variables)\n            for rows in (treated, controls) for row in rows\n        )\n        controls_by_context: dict[\n            tuple[str, tuple[tuple[str, str], ...]], list[CausalObservation]\n        ] = {}\n        if canonical_controls:\n            for baseline in controls:\n                key = (baseline.observation_context, baseline.controlled_variables)\n                controls_by_context.setdefault(key, []).append(baseline)\n        for effect in treated:\n            comparable = (\n                controls_by_context.get(\n                    (effect.observation_context, effect.controlled_variables), ()\n                ) if canonical_controls else controls\n            )\n            for baseline in comparable:\n                if (\n                    effect.observation_ref == baseline.observation_ref\n                    or effect.observed_step == baseline.observed_step\n                    or effect.controlled_variables != baseline.controlled_variables\n                    or effect.observation_context != baseline.observation_context\n                ):\n                    continue"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _reference_food_control_sort(before: bytes) -> bytes:
    """Reconstruct the approved #262 sorted food-controls transformation."""
    old = "        for present in sorted(exposed, key=lambda row: row.identifier):\n            for absent in sorted(controls, key=lambda row: row.identifier):"
    new = "        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)\n        for present in sorted(exposed, key=lambda row: row.identifier):\n            for absent in sorted_controls:"
    original = before.decode("utf-8")
    if original.count(old) != 1:
        raise ValueError("food controls reference drift")
    return original.replace(old, new, 1).encode("utf-8")


def _approved_food_review_control_sort(before: bytes, after: bytes) -> bool:
    """Only hoist an invariant food-control sort out of the exposed loop."""
    old = "        for present in sorted(exposed, key=lambda row: row.identifier):\n            for absent in sorted(controls, key=lambda row: row.identifier):"
    new = "        # The sorted controls are invariant across all exposed observations.\n        # Sorting once preserves the exact first admissible pair and ranking.\n        sorted_controls = sorted(controls, key=lambda row: row.identifier)\n        for present in sorted(exposed, key=lambda row: row.identifier):\n            for absent in sorted_controls:"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _reference_approved_numeric_index(before: bytes) -> bytes:
    """Recreate the existing #260 exact numeric publication transformation."""
    old = "        numeric = dict(self._numeric_witnesses)\n        for witness in sorted(\n            self._pending_numeric_witnesses, key=lambda row: row.identifier,\n        ):\n            witness.validate()\n            if (\n                witness.identifier in numeric\n                or any(\n                    prior.transition_event_ref == witness.transition_event_ref\n                    for prior in numeric.values()\n                )\n            ):\n                raise ValueError(\"duplicate published physical numeric witness\")\n            numeric[witness.identifier] = witness"
    new = "        numeric = dict(self._numeric_witnesses)\n        # One transient index per publication. The identifier guard rejects\n        # overwrites, so every accepted physical reference stays present.\n        numeric_transition_refs = {\n            prior.transition_event_ref for prior in numeric.values()\n        }\n        for witness in sorted(\n            self._pending_numeric_witnesses, key=lambda row: row.identifier,\n        ):\n            witness.validate()\n            if (\n                witness.identifier in numeric\n                or witness.transition_event_ref in numeric_transition_refs\n            ):\n                raise ValueError(\"duplicate published physical numeric witness\")\n            numeric[witness.identifier] = witness\n            numeric_transition_refs.add(witness.transition_event_ref)"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("numeric publication reference drift")
    return text.replace(old, new, 1).encode("utf-8")


def _approved_causal_intervention_min_index(before: bytes, after: bytes) -> bool:
    """Constrain the new invariant-preserving two-block calculation move."""
    old_one = "            if len(matching_contexts) < self.config.n2:\n                continue\n\n            if published_reports is None:"
    new_one = "            if len(matching_contexts) < self.config.n2:\n                continue\n            # This provenance witness is constant for this numeric outcome.\n            # Compute it once, not once for each compatible P-47 report.\n            intervention_ref = min(trial.identifier for trial in active_trials)\n\n            if published_reports is None:"
    old_two = "                    intervention_ref=min(\n                        trial.identifier for trial in active_trials\n                    ),"
    new_two = "                    intervention_ref=intervention_ref,"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    if any(original.count(v) != 1 for v in (old_one, old_two)):
        return False
    if any(candidate.count(v) != 1 for v in (new_one, new_two)):
        return False
    return (original.replace(old_one, new_one, 1)
                    .replace(old_two, new_two, 1) == candidate)


def _approved_numeric_publication_index(before: bytes, after: bytes) -> bool:
    """Allow exactly the transient numeric physical-reference index."""
    old = "        numeric = dict(self._numeric_witnesses)\n        for witness in sorted(\n            self._pending_numeric_witnesses, key=lambda row: row.identifier,\n        ):\n            witness.validate()\n            if (\n                witness.identifier in numeric\n                or any(\n                    prior.transition_event_ref == witness.transition_event_ref\n                    for prior in numeric.values()\n                )\n            ):\n                raise ValueError(\"duplicate published physical numeric witness\")\n            numeric[witness.identifier] = witness"
    new = "        numeric = dict(self._numeric_witnesses)\n        # One transient index per publication. The identifier guard rejects\n        # overwrites, so every accepted physical reference stays present.\n        numeric_transition_refs = {\n            prior.transition_event_ref for prior in numeric.values()\n        }\n        for witness in sorted(\n            self._pending_numeric_witnesses, key=lambda row: row.identifier,\n        ):\n            witness.validate()\n            if (\n                witness.identifier in numeric\n                or witness.transition_event_ref in numeric_transition_refs\n            ):\n                raise ValueError(\"duplicate published physical numeric witness\")\n            numeric[witness.identifier] = witness\n            numeric_transition_refs.add(witness.transition_event_ref)"
    original, candidate = before.decode("utf-8"), after.decode("utf-8")
    return (original.count(old) == 1 and candidate.count(new) == 1
            and original.replace(old, new, 1) == candidate)


def _reference_numeric_publication(before: bytes) -> bytes:
    """Reconstruct the already approved agency publication index exactly."""
    # The previous migration exception still constrains the historical block.
    old = "        agency = dict(self._agency_evidence)\n        for report in sorted(\n            self._pending_agency_evidence,\n            key=lambda value: (value.observed_t_monde, value.event_ref),\n        ):\n            if report.event_ref in {v.event_ref for v in agency.values()}:\n                raise ValueError(\"duplicate published physical agency observation\")\n            agency[report.identifier] = report"
    new = "        agency = dict(self._agency_evidence)\n        # Build an ephemeral index of physical references present in the\n        # current mapping. Identifier replacements must not leave stale refs.\n        agency_event_refs = {report.event_ref for report in agency.values()}\n        for report in sorted(\n            self._pending_agency_evidence,\n            key=lambda value: (value.observed_t_monde, value.event_ref),\n        ):\n            if report.event_ref in agency_event_refs:\n                raise ValueError(\"duplicate published physical agency observation\")\n            displaced = agency.get(report.identifier)\n            if displaced is not None and not any(\n                other.event_ref == displaced.event_ref\n                for key, other in agency.items()\n                if key != report.identifier\n            ):\n                # An overwritten report no longer occupies its old source.\n                # This rare fallback preserves exact previous semantics.\n                agency_event_refs.discard(displaced.event_ref)\n            agency[report.identifier] = report\n            agency_event_refs.add(report.event_ref)"
    text = before.decode("utf-8")
    if text.count(old) != 1:
        raise ValueError("agency publication reference drift")
    return text.replace(old, new, 1).encode("utf-8")


def _reference_agency_index(before: bytes) -> bytes:
    """Reconstruct the previously approved causal-query transformation."""
    source = before.decode("utf-8")
    old_a = "        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    old_b = "            for report in self.published_agency_evidence():\n                if (\n                    report.option_ref != witness.option_ref\n                    or report.sent_t_monde != witness.sent_t_monde\n                    or report.observed_t_monde != witness.observed_t_monde\n                ):\n                    continue\n                compatible = any("
    # Current I1 is the sole authoritative intermediate, reconstructed only
    # from two exact reviewed blocks verified against the pinned reference.
    first = "        # Ephemeral published evidence view. The first two admissible\n        # lookups scan it directly; only a third lookup pays for an index.\n        # No persistent cache, extra causal owner or hidden information.\n        published_reports: tuple[AgencyEvidence, ...] | None = None\n        published_by_action: dict[\n            tuple[str, int, int], list[AgencyEvidence]\n        ] | None = None\n        eligible_lookups = 0\n\n        rules: list[NumericPredictionCorrection] = []\n        for _, witness in sorted(self._numeric_witnesses.items()):"
    second = "            if published_reports is None:\n                published_reports = self.published_agency_evidence()\n            eligible_lookups += 1\n            if eligible_lookups == 3:\n                published_by_action = {}\n                for report in published_reports:\n                    key = (\n                        report.option_ref, report.sent_t_monde,\n                        report.observed_t_monde,\n                    )\n                    published_by_action.setdefault(key, []).append(report)\n\n            # Preserve the original direct scan for small histories; do\n            # not allocate a filtering generator for one or two witnesses.\n            matching_reports = (\n                published_reports if published_by_action is None\n                else published_by_action.get(\n                    (witness.option_ref, witness.sent_t_monde,\n                     witness.observed_t_monde), ()\n                )\n            )\n            for report in matching_reports:\n                if (\n                    report.option_ref != witness.option_ref\n                    or report.sent_t_monde != witness.sent_t_monde\n                    or report.observed_t_monde != witness.observed_t_monde\n                ):\n                    continue\n                compatible = any("
    for previous, replacement in ((old_a, first), (old_b, second)):
        if source.count(previous) != 1:
            raise ValueError("causal reference unexpectedly drifted")
        source = source.replace(previous, replacement, 1)
    return source.encode("utf-8")


def verify(reference_root: Path) -> None:
    reference_root = reference_root.resolve()
    if reference_root == ROOT.resolve():
        raise ValueError("reference root must be an independent checkout")
    with TemporaryDirectory(prefix="i1-parity-") as folder:
        old_root = Path(folder) / "reference"
        new_root = Path(folder) / "native"
        old = _build(reference_root, old_root)
        new = _build(ROOT, new_root)
        missing = sorted(set(old) - set(new))
        added = sorted(set(new) - set(old))
        changed = sorted(
            rel for rel in old.keys() & new.keys()
            if old[rel] != new[rel] and not (
                (rel == "i1lab/stage10_runtime.py"
                 and _approved_stage10_initialization_move(
                     (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                 ))
                or (rel == "i1lab/world.py"
                    and _approved_local_capture_resource_optimization(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1/modules/consolidation_pending_index.py"
                    and _approved_pending_index_cursor(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1/modules/causal_model.py"
                    and _approved_numeric_episode_ref_index(
                        _reference_food_control_index_loop(
                            _reference_empty_agency_preflight(
                                _reference_published_agency_sorted_items(
                                    _reference_numeric_no_concat(
                                        _reference_agency_projection_stream(
                                            _reference_food_empty_arm(
                                                _reference_hydration_empty_arm(
                                                    _reference_hydration_classification(
                                                        _reference_deferred_single_scan(
                                                            _reference_approved_physical_prior_buckets(
                                                                _reference_approved_revision_contexts(
                                                                    _reference_approved_stream_noncanonical_pairs(
                                                                        _reference_lived_review_dispatch(
                                                                            _reference_approved_confirmed_count(
                                                                                _reference_approved_physical_alias(
                                                                                    _reference_approved_active_context_cache(
                                                                                        _reference_hydration_control_lookup(
                                                                                            _reference_food_control_sort(
                                                                                                _reference_causal_minimum(
                                                                                                    _reference_approved_numeric_index(
                                                                                                        _reference_numeric_publication(
                                                                                                            _reference_agency_index(
                                                                                                                (old_root / rel).read_bytes()
                                                                                                            )
                                                                                                        )
                                                                                                    )
                                                                                                )
                                                                                            )
                                                                                        )
                                                                                    )
                                                                                )
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        (new_root / rel).read_bytes()
                    ))
                or (rel == "i1/modules/stage6_planning.py"
                    and _approved_stage6_bfs_deque(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1/modules/memory.py"
                    and _approved_memory_overlap(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1lab/journal.py"
                    and _approved_wal_streaming(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1lab/stage2_runtime.py"
                    and _approved_stage2_operator_closure(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1lab/stage9_runtime.py"
                    and _approved_stage9_episode_slice(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
                    ))
                or (rel == "i1lab/journal_views.py"
                    and _approved_autobio_index_rehydration(
                        _reference_autobio_fastpath((old_root / rel).read_bytes()),
                        (new_root / rel).read_bytes()
                    ))
            )
        )
        if missing or added or changed:
            print(f"I1 byte-parity FAIL: missing={missing} added={added}"
                  f" changed={changed}", file=sys.stderr)
            for rel in changed[:3]:
                former = (old_root / rel).read_text().splitlines(keepends=True)
                native = (new_root / rel).read_text().splitlines(keepends=True)
                diff = difflib.unified_diff(
                    former, native, fromfile=f"before/{rel}",
                    tofile=f"native/{rel}", n=3,
                )
                print("".join(list(diff)[:100]), file=sys.stderr)
            raise AssertionError("native migration changed generated I1 bytes")
        print(f"I1_GENERATED_PARITY_OK: {len(new)} files; only reviewed #255 and local-capture block transformations permitted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    args = parser.parse_args()
    verify(args.reference_root)


if __name__ == "__main__":
    main()
