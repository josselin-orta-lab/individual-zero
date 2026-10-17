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
                    and _approved_agency_evidence_index(
                        (old_root / rel).read_bytes(), (new_root / rel).read_bytes()
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
