"""Build a separately importable I1 descendant without editing I0 or lab.

The checked-in src/i1 tree is the exact source snapshot from the approved
I0 main SHA. This build mechanically namespaces that copy and the complete
laboratory runtime in a separate output directory. No src/i0 or src/lab file
is written. The I1-generated WorldBody alone receives versioned physical deprivation
by default, and the generated mortal Stage11Sleep entrypoint activates the
natural sleep policy for every new I1 birth. Reference I0 and Lab are unchanged.

Output is disposable build code, not an archived living individual.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tokenize

SOURCE_MAIN_SHA = "8ce8711b2d5f86b184d66fcee1d95a3e39f30836"
SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
GENERATED_SCHEMA = "i1-namespaced-source-build-v1"
IMPORTS = (
    (re.compile(r"(?m)^(\s*from\s+)i0(?=[.\s])"), r"\1i1"),
    (re.compile(r"(?m)^(\s*import\s+)i0(?=[.\s,])"), r"\1i1"),
    (re.compile(r"(?m)^(\s*from\s+)lab(?=[.\s])"), r"\1i1lab"),
    (re.compile(r"(?m)^(\s*import\s+)lab(?=[.\s,])"), r"\1i1lab"),
)
BIRTH_ID = re.compile(r'(?m)^(\s*individual_id\s*=\s*["\'])i0')


def rewrite(text: str) -> str:
    for pattern, replacement in IMPORTS:
        text = pattern.sub(replacement, text)
    return BIRTH_ID.sub(r"\1i1", text)



def i1_physiology_source(source: str) -> str:
    """Versioned I1-only physical deprivation, never applied to I0 or Lab.

    The generated copy owns the consequences; cognitive code sees only the
    same body telemetry on the next authorized capture. Rates are frozen
    constructor inputs, carried by the normal WorldPhysicsConfig / M11 digest.
    """
    patches = (
        (
            "    shelter_stones_required: int = 4\n",
            "    shelter_stones_required: int = 4\n"
            # The generated world type is shared by archived I1 ablations.
            # Merely extending its physical schema must not silently turn
            # deprivation ON for their explicitly chosen experimental worlds.
            # The canonical natural birth profile supplies positive defaults.
            "    starvation_integrity_damage_per_step: float = 0.0\n"
            "    dehydration_integrity_damage_per_step: float = 0.0\n"
        ),
        (
            "        self.tool_recipe.validate()\n",
            "        for damage in (self.starvation_integrity_damage_per_step,\n"
            "                       self.dehydration_integrity_damage_per_step):\n"
            "            if not 0.0 <= damage <= 100.0 or damage != damage:\n"
            "                raise ValueError('I1 deprivation rates must be finite in [0,100]')\n"
            "        self.tool_recipe.validate()\n"
        ),
        (
            '            "shelter_stones_required": self.shelter_stones_required,\n',
            '            "shelter_stones_required": self.shelter_stones_required,\n'
            '            "starvation_integrity_damage_per_step": self.starvation_integrity_damage_per_step,\n'
            '            "dehydration_integrity_damage_per_step": self.dehydration_integrity_damage_per_step,\n'
        ),
        (
            "        lethal_reasons: list[str] = []\n",
            "        # #231: apply *after* the actual action. Successful eating or\n"
            "        # drinking prevents same-step deprivation. Rest, a failed\n"
            "        # action, and physical hazards do not suspend metabolism.\n"
            "        starvation = (self._config.starvation_integrity_damage_per_step\n"
            "                      if body.food <= 0.0 else 0.0)\n"
            "        dehydration = (self._config.dehydration_integrity_damage_per_step\n"
            "                       if body.water <= 0.0 else 0.0)\n"
            "        if starvation or dehydration:\n"
            "            integrity_before = body.integrity\n"
            "            body = BodyState(\n"
            "                energy=body.energy, food=body.food, water=body.water,\n"
            "                integrity=self._clamp(integrity_before - starvation - dehydration),\n"
            "            )\n"
            "            effects['deprivation_integrity_damage'] = {\n"
            "                'starvation': starvation, 'dehydration': dehydration,\n"
            "                'actual_integrity_loss': integrity_before - body.integrity,\n"
            "            }\n"
            "        lethal_reasons: list[str] = []\n"
        ),
    )
    for original, replacement in patches:
        if source.count(original) != 1:
            raise ValueError("I1 deprivation source anchor changed")
        source = source.replace(original, replacement)
    return source

def i1_scoped_autobiographical_view_source(source: str) -> str:
    """Generated I1 only: project selected event payloads, validate ALL commits.

    Every AutoSegmentCommit and authorized source is still examined in order,
    including sources outside the chosen batch. The only saved work is
    projecting and storing irrelevant lived payloads. No uncommitted source
    can enter the scoped result and no cognitive P-42 charge is skipped.
    """
    definition = (
        '    def autobiographical(\n'
        '        self,\n'
        '        *,\n'
        '        policies: Mapping[str, AutobiographicalPolicy],\n'
        '    ) -> tuple[dict[str, object], ...]:\n'
    )
    expanded = (
        '    def autobiographical(\n'
        '        self,\n'
        '        *,\n'
        '        policies: Mapping[str, AutobiographicalPolicy],\n'
        '        selected_event_refs: frozenset[str] | None = None,\n'
        '    ) -> tuple[dict[str, object], ...]:\n'
        '        if selected_event_refs is not None and (\n'
        '                type(selected_event_refs) is not frozenset\n'
        '                or any(type(ref) is not str or not ref\n'
        '                       for ref in selected_event_refs)):\n'
        '            raise ValueError("invalid scoped autobiographical refs")\n'
    )
    if source.count(definition) != 1:
        raise ValueError("unreviewed generated JournalViews policy boundary")
    source = source.replace(definition, expanded)
    projection = '                projected.append(policy.project(source))\n'
    if source.count(projection) != 1:
        raise ValueError("unreviewed I1 autobiographical projected occurrence")
    return source.replace(
        projection,
        '                if (selected_event_refs is None\n'
        '                        or event_ref in selected_event_refs):\n'
        '                    projected.append(policy.project(source))\n',
    )


def i1_scoped_consolidation_evidence_source(source: str) -> str:
    """Generate bounded P-42-selected evidence without touching Lab source.

    The full technical hash-chain and EVERY autobiography commitment are
    validated just as before. Only already frozen episode event payloads
    are projected or retained for the semantic runner.
    """
    old = '        projection = views.autobiographical(policies=policies)\n'
    new = (
        '        episodes = transaction.frozen_episodes_copy()\n'
        '        selected = set()\n'
        '        for episode_ref in transaction.batch:\n'
        '            refs = episodes[episode_ref].get("event_refs")\n'
        '            if (type(refs) is not list or not refs\n'
        '                    or any(type(ref) is not str or not ref for ref in refs)\n'
        '                    or len(set(refs)) != len(refs)\n'
        '                    or selected.intersection(refs)):\n'
        '                raise ValueError("invalid or overlapping frozen episode refs")\n'
        '            selected.update(refs)\n'
        '        projection = views.autobiographical(\n'
        '            policies=policies, selected_event_refs=frozenset(selected),\n'
        '        )\n'
    )
    if source.count(old) != 1:
        raise ValueError("unreviewed verified evidence projection anchor")
    source = source.replace(old, new)
    committed = '                committed_before_cut.add(event_ref)\n'
    if source.count(committed) != 1:
        raise ValueError("unreviewed pre-cut authorization scan")
    source = source.replace(
        committed,
        '                if event_ref in selected:\n'
        '                    committed_before_cut.add(event_ref)\n',
    )
    duplicate = '        episodes = transaction.frozen_episodes_copy()\n'
    if source.count(duplicate) != 2:
        raise ValueError("missing scoped episode input or duplicate legacy copy")
    # Keep the first, already checked snapshot. Do not copy the entire
    # selected batch a second time before creating owned projections.
    prefix, suffix = source.split(duplicate, 1)
    if duplicate not in suffix:
        raise ValueError("unreviewed duplicate episode materialization")
    suffix = suffix.replace(duplicate, '', 1)
    rewritten = prefix + duplicate + suffix
    old_copy = "            projected[ref] = deepcopy(record)\n"
    if rewritten.count(old_copy) != 1:
        raise ValueError("unreviewed detached autobiography intermediate projection")
    # policy.project() already returns a private dict. The eventual episode
    # copy below remains the independent immutable evidence boundary.
    return rewritten.replace(old_copy, "            projected[ref] = record\n")


def i1_slow_history_preflight_no_full_birth_copy_source(source: str) -> str:
    """Preflight staged history without cloning the candidate twice.

    The temporary owner is never published. Its restore method still checks
    the complete staged history and creates an independent owned copy.
    """
    before = "        # Validate h before applying ANY owner states.\n        temp = SlowHistory(\n            birth_version=prepared.source_version,\n            birth_state=prepared.candidate_history,\n        )\n        temp.restore_causal_state(staged_history)\n"
    after = "        # Preflight exact staged state before touching any living owner.\n        # SlowHistory.restore_causal_state validates and detaches that state;\n        # the temporary constructor's birth payload is immediately discarded.\n        temp = SlowHistory(\n            birth_version=prepared.source_version,\n            birth_state={},\n        )\n        temp.restore_causal_state(staged_history)\n"
    if source.count(before) != 1:
        raise ValueError("unreviewed I1 SlowHistory preflight source")
    return source.replace(before, after)


def i1_publication_detached_candidate_source(source: str) -> str:
    """Avoid duplicate private-history materialization in generated I1 only.

    The validated transaction returns a detached tree, and the SlowHistory
    restore boundary validates and owns its own independent replacement.
    """
    changes = (
        ("        candidate = _copy_causal(transaction.validated_candidate(\n            validator=technical_validator))\n",
         "        # The transaction already validates and detaches its private candidate.\n        candidate = transaction.validated_candidate(\n            validator=technical_validator)\n"),
        ("        staged_history[\"current_state\"] = _copy_causal(prepared.candidate_history)\n",
         "        # SlowHistory.restore_causal_state independently validates and detaches\n        # this candidate before installing it as the current owned state.\n        staged_history[\"current_state\"] = prepared.candidate_history\n"),
        (
            "        staged_history = deepcopy(before_history)\n",
            "        # The committed history export already owns its nested state.\n        # Copy only the lineage list we append to; baseline checks retain the\n        # independent before_history and SlowHistory.restore still detaches.\n        staged_history = dict(before_history)\n        staged_history[\"lineage\"] = list(before_history[\"lineage\"])\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 Stage10 publication copy boundary")
        source = source.replace(before, after)
    return source


def i1_bounded_stage10_sleep_anchor_source(source: str) -> str:
    """Reverse-scan append-only frozen journal entries without allocating all."""
    old = "            e for e in reversed(self.journal.entries)\n"
    new = "            e for e in self.journal.iter_entries_reversed()\n"
    if source.count(old) != 1:
        raise ValueError("unreviewed I1 sleep-cut journal anchor")
    return source.replace(old, new)


def i1_no_meta_custody_rollback_source(source: str) -> str:
    """Do not save and reinstall previous living Meta/Health owner versions.

    The generated natural I1 runs under the mortal fail-stop boundary.
    A fresh authenticated M11 cold import is never allowed to rescue an
    incomplete owner graph. Keep both defensive input copies.
    """
    before = "        old_meta = self.meta.export_causal_state()\n        old_health = self.health.export_causal_state()\n        try:\n            self.meta.restore_causal_state(deepcopy(state[\"metacognition\"]))\n            self.health.restore_causal_state(deepcopy(state[\"sleep_health\"]))\n        except Exception:\n            self.meta.restore_causal_state(old_meta)\n            self.health.restore_causal_state(old_health)\n            raise\n"
    after = "        # No backup of living owners for a compensating rewind. If an\n        # installation fails, the mortal Stage10 step halts the individual;\n        # M11 cold installation instead aborts the unpublished new runtime.\n        self.meta.restore_causal_state(deepcopy(state[\"metacognition\"]))\n        self.health.restore_causal_state(deepcopy(state[\"sleep_health\"]))\n"
    if source.count(before) != 1:
        raise ValueError("unreviewed I1 metacognition/health no-rewind boundary")
    return source.replace(before, after)


def i1_stage10_publication_bounded_count_source(source: str) -> str:
    """Read journal cardinality without repeatedly allocating all entries.

    The generated I1lab journal has an exact O(1) entry_count view; full
    journal verification, append and owner/version checks are unchanged.
    """
    before = "len(self.journal.entries)"
    if source.count(before) != 3:
        raise ValueError("unreviewed I1 Stage10 publication occurrence count")
    return source.replace(before, "self.journal.entry_count")


def i1_no_live_publication_rollback_source(source: str) -> str:
    """Ban live owner rewind after attempted canonical I1 publication.

    Errors propagate to the already fail-stopped mortal Stage10.run_step and
    the independent M11 poison/uncertain-intent gate. The source lab and I0
    implementations are deliberately unchanged.
    """
    changes = (
        ("no owner changes until every candidate is valid, and a failed installation\nrestores the complete prior states before the Scheduler continues.\n", "all candidates are validated before owner installation. Any failed\ninstallation halts the mortal step without restoring earlier live states.\n"),
        ("        except Exception as error:\n            # A successful journal append is an irreversible publication\n            # boundary. If acknowledgement fails AFTER the append, rolling\n            # the active owners or h back would contradict the durable causal\n            # journal and permit a second publication of the same life.\n            #\n            # A failed fsync may have left a torn WAL: a poisoned journal\n            # likewise cannot authorize restoring active published forms.\n            journal_committed = (\n                len(self.journal.entries) != event_index\n                or self.journal.head_hash != prepared.postcut_slice.end_hash\n            )\n            if journal_committed or not self.journal.verify():\n                raise RuntimeError(\n                    \"irreversible consolidation journal fault after publication; \"\n                    \"halt the individual, never restore committed active state\"\n                ) from error\n            # Before the journal event exists, all states were private and\n            # the scheduler has not exposed an activation; safe to discard.\n            self.history.restore_causal_state(before_history)\n            for name in sorted(self.owners):\n                self.owners[name].restore_causal_state(\n                    deepcopy(prepared.baseline_owner_states[name]))\n            raise\n", "        except Exception as error:\n            # Installation of a newly published version may have mutated a\n            # live owner even if the journal event was not appended. I1 may\n            # never rewind such an owner. Stage10.run_step irreversibly halts\n            # the mortal identity on the propagated error, while M11 also\n            # refuses continuation of an uncertain private generation.\n            journal_committed = (\n                len(self.journal.entries) != event_index\n                or self.journal.head_hash != prepared.postcut_slice.end_hash\n            )\n            if journal_committed or not self.journal.verify():\n                raise RuntimeError(\n                    \"irreversible consolidation journal fault after publication; \"\n                    \"halt the individual, never restore committed active state\"\n                ) from error\n            raise RuntimeError(\n                \"incomplete consolidation owner publication; \"\n                \"halt the individual, never restore previous cognitive state\"\n            ) from error\n"),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 no-rollback Stage10 boundary")
        source = source.replace(before, after)
    return source


def i1_committed_history_metadata_source(source: str) -> str:
    """Generated I1-only SlowHistory: O(1) immutable committed-ref access.

    The cached frozenset is owned by the same SlowHistory instance, derived
    exclusively at the canonical birth and every checked restore. It is not
    a new writer, snapshot source, or cognitive read with different UC rules.
    """
    birth = '        self._lineage: list[dict[str, object]] = []\n'
    birth_new = (
        birth + '        self._i1_committed_refs = frozenset(\n'
        '            self._current_state["consolidated_episode_refs"]\n'
        '        )\n'
    )
    if source.count(birth) != 1:
        raise ValueError("unreviewed SlowHistory I1 birth metadata")
    source = source.replace(birth, birth_new)
    read = '    def read_committed(self) -> object:\n'
    method = (
        '    def committed_episode_refs(self) -> frozenset[str]:\n'
        '        """Read exact committed identifiers without copying private forms."""\n'
        '        return self._i1_committed_refs\n\n'
    )
    if source.count(read) != 1:
        raise ValueError("unreviewed SlowHistory committed-ref read")
    source = source.replace(read, method + read)
    restore = '        # Assign only after validating the entire replacement.\n'
    amended = (
        '        refs = current.get("consolidated_episode_refs")\n'
        '        if (type(refs) is not list\n'
        '                or any(type(ref) is not str or not ref for ref in refs)\n'
        '                or len(refs) != len(set(refs))):\n'
        '            raise ValueError("unverified consolidated episode references")\n'
        '        committed = frozenset(refs)\n'
        + restore
        + '        self._i1_committed_refs = committed\n'
    )
    if source.count(restore) != 1:
        raise ValueError("unreviewed SlowHistory committed-ref restore")
    return source.replace(restore, amended)


def i1_bounded_batch_selection_source(source: str) -> str:
    """Select the same P-42 best episodes without sorting the whole backlog."""
    import_anchor = "from dataclasses import dataclass\n"
    old = (
        "        priorities.sort(key=lambda item: (-item.score, -item.age_steps, item.episode_ref))\n"
        "        selected = tuple(priorities[:cfg.maximum_episodes])\n"
    )
    new = (
        "        # Full scores are still paid, computed and validated. Only the\n"
        "        # policy-bounded best group is sorted at the end.\n"
        "        selected = tuple(nsmallest(\n"
        "            cfg.maximum_episodes, priorities,\n"
        "            key=lambda item: (-item.score, -item.age_steps, item.episode_ref),\n"
        "        ))\n"
    )
    if source.count(import_anchor) != 1 or source.count(old) != 1:
        raise ValueError("unreviewed I1 bounded consolidation selection")
    return source.replace(
        import_anchor, import_anchor + "from heapq import nsmallest\n",
    ).replace(old, new)


def i1_pending_projection_copy_source(source: str) -> str:
    """Keep exactly one detached copy of a trusted, indexed episode.

    The private wrapper is consumed by ConsolidationBatchSelector._projection,
    which validates the returned raw mapping and deepcopies it. Never change
    the public Episode.as_dict contract or the paid pending-index ledger.
    """
    if source.count("class _IndexedEpisode:\n") != 1:
        raise ValueError("unreviewed I1 pending index projection type")
    old = "    def as_dict(self):\n        return deepcopy(self.payload)\n"
    new = (
        "    def as_dict(self):\n"
        "        # Private view only: selector._projection validates and then\n"
        "        # deepcopies this exact mapping before retaining it.\n"
        "        return self.payload\n"
    )
    if source.count(old) != 1:
        raise ValueError("unreviewed I1 pending projection copy site")
    return source.replace(old, new)


def i1_journal_bounded_view_source(source: str) -> str:
    """I1-only bounded journal reads; preserve all legacy .entries semantics."""
    anchor = (
        "    @property\n"
        "    def entries(self) -> tuple[JournalEntry, ...]:\n"
        "        return tuple(self._entries)\n"
    )
    addition = (
        "\n"
        "    @property\n"
        "    def entry_count(self) -> int:\n"
        "        \"\"\"Read append-only occurrence count without materializing a tuple.\"\"\"\n"
        "        return len(self._entries)\n"
        "\n"
        "    def entries_since(self, start: int) -> tuple[JournalEntry, ...]:\n"
        "        \"\"\"Detach only the append-only suffix requested by the caller.\"\"\"\n"
        "        if type(start) is not int or not 0 <= start <= len(self._entries):\n"
        "            raise ValueError(\"invalid journal suffix boundary\")\n"
        "        return tuple(self._entries[start:])\n"
        "\n"
        "    def iter_entries_reversed(self):\n"
        "        \"\"\"Iterate frozen append-only events without a full tuple.\"\"\"\n"
        "        return reversed(self._entries)\n"
    )
    if source.count(anchor) != 1 or source.count("len(replay.entries)") != 2:
        raise ValueError("unreviewed I1 technical journal read boundary")
    source = source.replace(anchor, anchor + addition)
    return source.replace("len(replay.entries)", "replay.entry_count")


def i1_postcut_bounded_verification_source(source: str) -> str:
    """Keep full postcut integrity checks without duplicate full history reads.

    Applies only to the generated I1lab journal coordinator, after the
    generated I1lab HashChainedJournal gains entry_count/entries_since.
    """
    replacements = (
        (
            "    def _verified(self) -> tuple:\n        if not self._journal.verify():\n            raise ValueError(\"hash-chained journal integrity failure\")\n        return self._journal.entries\n",
            "    def _verified(self) -> HashChainedJournal:\n        if not self._journal.verify():\n            raise ValueError(\"hash-chained journal integrity failure\")\n        return self._journal\n",
        ),
        (
            "    def _check_cut(self, cut: ConsolidationCut, entries: tuple) -> None:\n        cut.validate()\n        if cut.journal_index >= len(entries):\n            raise ValueError(\"cut journal occurrence is absent\")\n        original = entries[cut.journal_index]\n        if (original.event_id != cut.journal_event_id\n                or original.event_hash != cut.journal_hash):\n            raise ValueError(\"cut identity or head hash mismatches journal\")\n",
            "    def _check_cut(self, cut: ConsolidationCut, journal: HashChainedJournal) -> None:\n        cut.validate()\n        if cut.journal_index >= journal.entry_count:\n            raise ValueError(\"cut journal occurrence is absent\")\n        original = journal.get(cut.journal_event_id)\n        if (original is None or original.index != cut.journal_index\n                or original.event_hash != cut.journal_hash):\n            raise ValueError(\"cut identity or head hash mismatches journal\")\n",
        ),
        (
            "        entries = self._verified()\n        self._check_cut(cut, entries)\n        end_index = len(entries) - 1\n        end_hash = entries[-1].event_hash\n",
            "        journal = self._verified()\n        self._check_cut(cut, journal)\n        end_index = journal.entry_count - 1\n        end_hash = journal.head_hash\n",
        ),
        (
            "        for event in entries[cut.journal_index + 1:]:\n",
            "        for event in journal.entries_since(cut.journal_index + 1):\n",
        ),
        (
            "        entries = self._verified()\n        self._check_cut(frozen.cut, entries)\n        if (len(entries) - 1 != frozen.end_index\n                or self._journal.head_hash != frozen.end_hash):\n            raise ValueError(\"journal advanced after private rebase preparation\")\n        current = self.freeze(cut=frozen.cut)\n",
            "        # A single complete verification happens inside freeze(), which also\n        # rechecks the causal cut and builds the exact post-cut digest.\n        current = self.freeze(cut=frozen.cut)\n        if (current.end_index != frozen.end_index\n                or current.end_hash != frozen.end_hash):\n            raise ValueError(\"journal advanced after private rebase preparation\")\n",
        ),
        (
            "                t_monde=t, kind=kind, payload=deepcopy(dict(payload)),\n",
            "                t_monde=t, kind=kind, payload=dict(payload),\n",
        ),
    )
    for before, after in replacements:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 postcut journal verification boundary")
        source = source.replace(before, after)
    return source


def i1_journal_full_integrity_copy_source(source: str) -> str:
    """Keep SHA-256 verification but avoid copying already-owned nested events.

    This generator-only transformation leaves the public journal export and
    all I0/Lab source snapshots unchanged.
    """
    changes = (
        ("    def __len__(self) -> int:\n        return len(self.__contents)\n",
         "    def __len__(self) -> int:\n        return len(self.__contents)\n\n    def _canonical_occurrence_bytes(self, event_id: str) -> bytes:\n        \"\"\"Hash owned causal payload without exposing internal mutable values.\"\"\"\n        return canonical_causal_bytes({\n            \"event_id\": event_id, \"causal_event\": self.__contents,\n        })\n"),
        ("        seen_ids: set[str] = set()\n",
         ""),
        ("                or entry.event_id in seen_ids\n",
         ""),
        ("            seen_ids.add(entry.event_id)\n",
         ""),
        ("                or self._by_id.get(entry.event_id) is not entry\n",
         "                or self._by_id.get(entry.event_id) is not entry\n                or type(entry.causal_event) is not _DetachedCausalEvent\n"),
        ("            expected_hash = sha256_hex(\n                bytes.fromhex(previous_hash)\n                + canonical_causal_bytes(\n                    {\n                        \"event_id\": entry.event_id,\n                        \"causal_event\": entry.causal_event,\n                    }\n                )\n            )\n",
         "            expected_hash = sha256_hex(\n                bytes.fromhex(previous_hash)\n                + entry.causal_event._canonical_occurrence_bytes(entry.event_id)\n            )\n"),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 full-journal verification anchor")
        source = source.replace(before, after)
    return source


def i1_m11_bounded_journal_source(source: str) -> str:
    """Avoid whole-journal tuple materialization in I1 M11 and cold restore.

    Journal verification, hash checks, durable-intent fencing, state capture,
    commit ordering and published owner isolation remain unchanged.
    """
    substitutions = (
        (
            "        runtime.journal.append(\n",
            "        appended = runtime.journal.append(\n",
        ),
        (
            "        if runtime.journal.entries[-1].as_dict() != entry:\n",
            "        if appended.as_dict() != entry:\n",
        ),
        (
            'or len(runtime.journal.entries) != image["journal"]["count"]',
            'or runtime.journal.entry_count != image["journal"]["count"]',
        ),
        (
            "                or runtime.journal.entries\n",
            "                or runtime.journal.entry_count\n",
        ),
        (
            "                or base.journal_count != len(self._runtime.journal.entries)):\n",
            "                or base.journal_count != self._runtime.journal.entry_count):\n",
        ),
        (
            "                for event in candidate.journal.entries[base.journal_count:]\n",
            "                for event in candidate.journal.entries_since(base.journal_count)\n",
        ),
    )
    for before, after in substitutions:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 M11 journal-copy anchor")
        source = source.replace(before, after)
    return source


def i1_sqlite_life_audit_canonical_source(source: str) -> str:
    """Retain all full SQL and schema checks but avoid duplicate decoding.

    The exact old-current generation already carries a verified receipt;
    this is only for the generated I1lab SQLite ledger.
    """
    changes = (
        ("            if canonical_causal_bytes(decoded) != data:\n                raise ValueError(\"noncanonical state\")\n            _canonical_state(decoded, identity)\n",
         "            # _canonical_state performs the full schema and causal\n            # normalization checks; reuse its bytes for the exact comparison.\n            if _canonical_state(decoded, identity) != data:\n                raise ValueError(\"noncanonical state\")\n"),
        ("            old_bytes = self._db.execute(\n                \"SELECT state_bytes FROM life_current WHERE slot=1\"\n            ).fetchone()[0]\n            old_metadata = registered_current_metadata(json.loads(old_bytes))\n            new_metadata = registered_current_metadata(current_state)\n            if (old_metadata is None) != (new_metadata is None):\n                raise ValueError(\"current identity cannot switch registered custody contract\")\n            if (\n                old_metadata is not None\n                and new_metadata is not None\n                and old_metadata[0] != new_metadata[0]\n            ):\n                raise ValueError(\"registered causal owner roster changed within one identity\")\n",
         "            # The receipt came from a complete audit of the current SQL\n            # generation. Under BEGIN IMMEDIATE, _checked_current_anchor\n            # rechecks its state bytes and pinned roster against that receipt;\n            # the fallback path audits under the lock instead. There is no\n            # need to deserialize the old complete cognitive state again.\n            old_roster_hash = receipt.registered_roster_hash\n            new_metadata = registered_current_metadata(current_state)\n            if (old_roster_hash is None) != (new_metadata is None):\n                raise ValueError(\"current identity cannot switch registered custody contract\")\n            if (old_roster_hash is not None\n                    and new_metadata is not None\n                    and old_roster_hash != new_metadata[0]):\n                raise ValueError(\"registered causal owner roster changed within one identity\")\n"),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 SQLite life ledger audit boundary")
        source = source.replace(before, after)
    return source


def i1_sqlite_streaming_audit_source(source: str) -> str:
    """Avoid redundant owner metadata scans and hex conversion per occurrence.

    Applies only to generated I1lab; preserves every full hash-chain audit,
    canonical byte check, terminal sequence rule and SQL head/count check.
    """
    changes = (
        (
            "from dataclasses import dataclass\n",
            "from dataclasses import dataclass\nfrom hashlib import sha256\n",
        ),
        (
            "def _canonical_state(state: Mapping[str, object], identity: str) -> bytes:\n",
            "def _canonical_state_with_metadata(\n    state: Mapping[str, object], identity: str,\n) -> tuple[bytes, tuple[str, str, int, str, str] | None]:\n",
        ),
        (
            "    registered_current_metadata(state)\n    return canonical_causal_bytes(state)\n",
            "    metadata = registered_current_metadata(state)\n    return canonical_causal_bytes(state), metadata\n\n\ndef _canonical_state(state: Mapping[str, object], identity: str) -> bytes:\n    \"\"\"Keep canonical state bytes and owner-roster verification for all callers.\"\"\"\n    return _canonical_state_with_metadata(state, identity)[0]\n",
        ),
        (
            "            if _canonical_state(decoded, identity) != data:\n                raise ValueError(\"noncanonical state\")\n",
            "            canonical, metadata = _canonical_state_with_metadata(decoded, identity)\n            if canonical != data:\n                raise ValueError(\"noncanonical state\")\n",
        ),
        (
            "        previous = GENESIS_HASH\n        expected = 0\n",
            "        # The large decoded state is no longer needed during the full event audit.\n        del decoded\n        previous = GENESIS_HASH\n        previous_digest = bytes.fromhex(GENESIS_HASH)\n        expected = 0\n",
        ),
        (
            "            actual = sha256_hex(bytes.fromhex(previous) + payload)\n",
            "            actual_digest = sha256(previous_digest + payload).digest()\n            actual = actual_digest.hex()\n",
        ),
        (
            "            previous = actual\n            expected += 1\n",
            "            previous = actual\n            previous_digest = actual_digest\n            expected += 1\n",
        ),
        (
            "        metadata = registered_current_metadata(decoded)\n",
            "        # The current envelope was fully checked before streaming occurrences.\n",
        ),
        (
            "        payload = _canonical_state(initial_state, individual_id)\n        metadata = registered_current_metadata(initial_state)\n",
            "        payload, metadata = _canonical_state_with_metadata(\n            initial_state, individual_id,\n        )\n",
        ),
        (
            "            payload = _canonical_state(current_state, receipt.individual_id)\n",
            "            payload, new_metadata = _canonical_state_with_metadata(\n                current_state, receipt.individual_id,\n            )\n",
        ),
        (
            "            new_metadata = registered_current_metadata(current_state)\n",
            "",
        ),
        (
            "            head = receipt.journal_head\n            index = receipt.journal_count\n",
            "            head = receipt.journal_head\n            head_digest = bytes.fromhex(head)\n            index = receipt.journal_count\n",
        ),
        (
            "                event_hash = sha256_hex(bytes.fromhex(head) + canonical_causal_bytes(\n                    {\"event_id\": event_id, \"causal_event\": causal}\n                ))\n",
            "                event_digest = sha256(head_digest + canonical_causal_bytes(\n                    {\"event_id\": event_id, \"causal_event\": causal}\n                )).digest()\n                event_hash = event_digest.hex()\n",
        ),
        (
            "                head = event_hash\n                index += 1\n",
            "                head = event_hash\n                head_digest = event_digest\n                index += 1\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 SQL incremental audit boundary")
        source = source.replace(before, after)
    return source


def i1_sqlite_detached_owner_export_source(source: str) -> str:
    """Elide copies only for exact I1 owners with proven detached exports.

    SlowHistory.export_causal_state detaches both its state and lineage.
    ConsolidationSlot.export_causal_state returns a fresh envelope and the
    complete transaction exports its checkpoint and candidate trees deeply.
    All other owners retain a defensive deepcopy before SQLite custody.
    """
    old = "        state = deepcopy(owner.export_causal_state())\n"
    new = (
        "        exported = owner.export_causal_state()\n"
        "        # Explicitly scoped exact types only: never trust an unknown\n"
        "        # owner, subclass or mutable nested export by assumption.\n"
        "        from .consolidation_publication import SlowHistory\n"
        "        from i1.modules.consolidation_transaction import ConsolidationSlot\n"
        "        state = (exported if type(owner) in (SlowHistory, ConsolidationSlot)\n"
        "                 else deepcopy(exported))\n"
    )
    if source.count(old) != 1:
        raise ValueError("unreviewed I1 SQLite detached export boundary")
    return source.replace(old, new)


def i1_sqlite_journal_count_source(source: str) -> str:
    """Read exact journal count without allocating one full occurrence tuple."""
    before = '"count": len(journal.entries), "head": journal.head_hash,'
    after = '"count": journal.entry_count, "head": journal.head_hash,'
    if source.count(before) != 1:
        raise ValueError("unreviewed I1 SQLite capture journal-count anchor")
    return source.replace(before, after)


def i1_consolidation_runner_copy_source(source: str) -> str:
    """Avoid duplicating already detached private data in generated I1 only."""
    pairs = (
        (
            "            deepcopy(scoped), self.transaction.cut,\n",
            "            scoped, self.transaction.cut,\n",
        ),
        (
            "        return deepcopy(self.budget.export_causal_state())\n",
            "        return self.budget.export_causal_state()\n",
        ),
        (
            "        frozen = ConsolidationPassPlan.from_state(deepcopy(plan.export()))\n",
            "        frozen = ConsolidationPassPlan.from_state(plan.export())\n",
        ),
        (
            "        self._working = _json(self.transaction.candidate_copy())\n",
            "        self._working = self.transaction.candidate_copy()\n",
        ),
        (
            "        result = deepcopy(self._working)\n",
            "        result = self._working\n",
        ),
        (
            "            executor=lambda _base, _batch, _cut: deepcopy(result),\n",
            "            executor=lambda _base, _batch, _cut: result,\n",
        ),
        (
            '        without_digest = {k: deepcopy(v) for k, v in state.items() if k != "state_digest"}\n',
            '        without_digest = {k: v for k, v in state.items() if k != "state_digest"}\n',
        ),
        (
            "            restored_plan = ConsolidationPassPlan.from_state(deepcopy(plan_raw))\n",
            "            restored_plan = ConsolidationPassPlan.from_state(plan_raw)\n",
        ),
    )
    for before, after in pairs:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 pass-runner detached copy site")
        source = source.replace(before, after)
    return source


def i1_consolidation_digest_metadata_source(source: str) -> str:
    """Keep the current private checkpoint digest in the I1 transaction owner.

    The canonical candidate is an owned JSON tree. All its assignment sites
    are enumerated here; no caller can acquire a mutable candidate alias.
    The cache is derived metadata, not a new persisted/authoritative field.
    """
    if (source.count("self._candidate =") != 3
            or source.count("restored._candidate =") != 1):
        raise ValueError("unreviewed I1 candidate mutation sites")
    changes = (
        (
            "        self._initial = _owned(history_candidate)\n"
            "        self._candidate = _owned(history_candidate)\n",
            "        self._initial = _owned(history_candidate)\n"
            "        # Clone only the already validated private JSON tree.\n"
            "        self._candidate = deepcopy(self._initial)\n"
            "        self._candidate_digest_cached = _digest(self._initial)\n",
        ),
        (
            '"batch_digest": self._batch_digest, "initial_digest": _digest(self._initial),',
            '"batch_digest": self._batch_digest, "initial_digest": self._candidate_digest_cached,',
        ),
        (
            "    def candidate_digest(self) -> str:\n"
            "        return _digest(self._candidate)\n",
            "    def candidate_digest(self) -> str:\n"
            "        # Updated only at a validated candidate replacement.\n"
            "        return self._candidate_digest_cached\n",
        ),
        (
            "        self._candidate = deepcopy(\n"
            "            self._checkpoints[-1].candidate if self._checkpoints else self._initial\n"
            "        )\n"
            "        self._status = \"suspended\"\n",
            "        # Current candidate is already a private copy of the latest\n"
            "        # validated checkpoint; unfinished runner work lives elsewhere.\n"
            "        # Suspending does not replace the checkpoint candidate.\n"
            "        self._status = \"suspended\"\n",
        ),
        (
            "        digest = self._point_digest(name=name, candidate=candidate)\n"
            "        self._checkpoints.append(PassCheckpoint(name, deepcopy(candidate), digest))\n"
            "        self._candidate = candidate\n",
            "        digest = self._point_digest(name=name, candidate=candidate)\n"
            "        candidate_digest = _digest(candidate)\n"
            "        self._checkpoints.append(PassCheckpoint(name, deepcopy(candidate), digest))\n"
            "        self._candidate = candidate\n"
            "        self._candidate_digest_cached = candidate_digest\n",
        ),
        (
            "        restored._candidate = deepcopy(expected)\n"
            "        restored._status = status\n",
            "        restored._candidate = deepcopy(expected)\n"
            "        restored._candidate_digest_cached = _digest(restored._candidate)\n"
            "        restored._status = status\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 consolidation candidate digest anchor")
        source = source.replace(before, after)
    return source


def i1_memory_recall_source(source: str) -> str:
    """Reuse visible competitive refs once per I1 episodic recall.

    The generated I1-only transformation preserves scoring, thresholds, tie
    ordering, UC custody and original source snapshots.
    """
    signature = (
        "    def _relevance(\n"
        "        self,\n"
        "        episode: Episode,\n"
        "        st: STVersion | None,\n"
        "    ) -> float:\n"
    )
    if source.count(signature) != 1:
        raise ValueError("unreviewed generated I1 Memory relevance signature")
    source = source.replace(signature, signature.replace(
        "    ) -> float:\n",
        "        current_refs: set[str] | None = None,\n"
        "    ) -> float:\n",
    ))
    per_episode = (
        "        current_refs = {\n"
        "            element.contribution_ref for element in st.competitive\n"
        "        }\n"
    )
    if source.count(per_episode) != 1:
        raise ValueError("unreviewed generated I1 Memory competitive references")
    source = source.replace(per_episode, (
        "        if current_refs is None:\n"
        "            current_refs = {\n"
        "                element.contribution_ref for element in st.competitive\n"
        "            }\n"
    ))
    scored = ("        scored: list[RecallResult] = []\n"
              "        for episode in self._episodes:\n")
    if source.count(scored) != 1:
        raise ValueError("unreviewed generated I1 Memory recall loop")
    source = source.replace(scored, (
        "        visible_refs = (\n"
        "            {element.contribution_ref for element in st.competitive}\n"
        "            if st is not None else None\n"
        "        )\n"
        + scored
    ))
    call = "            relevance = self._relevance(episode, st)\n"
    if source.count(call) != 1:
        raise ValueError("unreviewed generated I1 Memory relevance call")
    return source.replace(
        call, "            relevance = self._relevance(episode, st, visible_refs)\n"
    )


def i1_canonical_active_value_source(source: str) -> str:
    """Switch the generated Stage4 value owner only for natural I1.

    All experimental arms still use the unchanged value owner; the
    canonical actor changes the exact owner at birth before any life step.
    """
    anchor = "        self.value_needs = ValueAndNeeds(config.value_needs)\n"
    replacement = (
        "        if type(self).__name__ == 'I1Runtime':\n"
        "            from .i1_active_value_needs import I1ActiveValueNeeds\n"
        "            self.value_needs = I1ActiveValueNeeds(config.value_needs)\n"
        "        else:\n"
        "            self.value_needs = ValueAndNeeds(config.value_needs)\n"
    )
    if source.count(anchor) != 1:
        raise ValueError("unreviewed generated Stage4 value owner initialization")
    return source.replace(anchor, replacement)


def i1_m11_active_publication_custody_source(source: str) -> str:
    """Generated M11 must preserve h <-> active Value/Needs identity.

    A torn or inconsistent publication cannot become the canonical current
    mortal state merely because both owner snapshots deserialize separately.
    Only the exact canonical natural I1 actor participates in this contract.
    """
    verification = '''def _verify_i1_active_publication_custody(runtime: Any) -> None:
    from .i1_natural_runtime import I1Runtime
    if type(runtime) is not I1Runtime:
        return
    from .i1_active_value_needs import validate_advisory_rows
    history = runtime.slow_history.read_committed()
    if type(history) is not dict or type(history.get("forms")) is not dict:
        raise RecoveryBlocked("missing canonical I1 consolidated active forms")
    forms = history["forms"]
    from .i1_cognitive_publication import (
        build_consolidated_owner_form, validate_owner_rows,
    )
    required = {"value_needs", "causal_model", "perception", "metacognition_health"}
    if set(forms) not in (set(), required):
        raise RecoveryBlocked("unapproved I1 active owner publication")
    expected = forms.get("value_needs", [])
    witnessed = history.get("procedural")
    if type(witnessed) is not list or any(type(row) is not dict for row in witnessed):
        raise RecoveryBlocked("invalid committed procedural source")
    if type(expected) is not list:
        raise RecoveryBlocked("invalid committed active Value/Needs form")
    validate_advisory_rows(expected)
    authorized = sorted(
        (row for row in witnessed if row.get("state") == "compiled_private"),
        key=lambda row: row["id"],
    )
    expected_bytes = canonical_causal_bytes(expected)
    if (expected_bytes != canonical_causal_bytes(authorized)
            or expected_bytes != canonical_causal_bytes(
                runtime.value_needs.active_observed_procedures()
            )):
        raise RecoveryBlocked("I1 active owner and consolidated history diverged")
    names = ("causal_model", "perception", "metacognition_health")
    for name in names:
        published = forms.get(name, [])
        recomputed = build_consolidated_owner_form(history, name) if forms else []
        live = runtime._i1_active_owner_views[name].observed_consolidated()
        validate_owner_rows(name, published)
        validate_owner_rows(name, live)
        published_bytes = canonical_causal_bytes(published)
        if (published_bytes != canonical_causal_bytes(recomputed)
                or published_bytes != canonical_causal_bytes(live)):
            # An empty private history must NEVER conceal a live published
            # owner form. This parity applies before the first publication
            # and to every authentic later SQLite generation.
            raise RecoveryBlocked("I1 active owner differs from published lived evidence")


'''
    anchor = "def _runtime_image(runtime: Any, *, individual_id: str) -> dict[str, Any]:\n"
    if source.count(anchor) != 1:
        raise ValueError("unreviewed M11 registered owner capture")
    source = source.replace(anchor, verification + anchor)
    original_capture = "    image = capture_registered_current_state(\n"
    if source.count(original_capture) != 1:
        raise ValueError("unreviewed M11 owner image source")
    source = source.replace(
        original_capture,
        "    _verify_i1_active_publication_custody(runtime)\n" + original_capture,
    )
    cold_anchor = (
        "    # Complete ledger bytes correspond to the current *generation*, not any\n"
    )
    if source.count(cold_anchor) != 1:
        raise ValueError("unreviewed M11 restored owner sync boundary")
    return source.replace(
        cold_anchor,
        "    _verify_i1_active_publication_custody(runtime)\n" + cold_anchor,
    )


def i1_waking_pending_source(source: str) -> str:
    """Avoid cloning the entire h on every awake step in natural I1."""
    old = (
        '        committed = set(self.slow_history.read_committed()'
        '["consolidated_episode_refs"])\n'
    )
    new = '        committed = self.slow_history.committed_episode_refs()\n'
    if source.count(old) != 1:
        raise ValueError("unreviewed Stage10 waking history read")
    source = source.replace(old, new)
    # The EpisodicMemory owner only appends uniquely numbered closed
    # episodes. Stage10 can publish IDs exclusively from its charged,
    # already-frozen Memory batches; it never deletes a closed episode.
    # Therefore pending = closed_count - published_count, with O(1) read
    # complexity rather than a full history iteration on EVERY waking step.
    pending_old = (
        '        pending = sum(episode.id not in committed '
        'for episode in self.memory.episodes)\n'
        '        relevant = min(1.0, len(self.memory.episodes)\n'
    )
    pending_new = (
        '        total = self.memory.episode_count\n'
        '        pending = total - len(committed)\n'
        '        if pending < 0:\n'
        '            raise ValueError("committed episodes exceed lived closed episodes")\n'
        '        relevant = min(1.0, total\n'
    )
    if source.count(pending_old) != 1:
        raise ValueError("unreviewed waking episode count semantics")
    source = source.replace(pending_old, pending_new)
    # Sleep selection can also consult immutable ownership metadata. Actual
    # episode bodies are still read only through the charged selection path.
    prior = (
        '                            tuple(self.slow_history.read_committed()'
        '["consolidated_episode_refs"])\n'
    )
    if source.count(prior) != 1:
        raise ValueError("unreviewed incremental sleep selection metadata")
    source = source.replace(
        prior,
        '                            tuple(sorted(self.slow_history.committed_episode_refs()))\n',
    )
    prior = (
        '                old_refs = set(\n'
        '                    self.slow_history.read_committed()["consolidated_episode_refs"]\n'
        '                )\n'
    )
    if source.count(prior) != 1:
        raise ValueError("unreviewed full sleep selection metadata")
    return source.replace(
        prior, '                old_refs = self.slow_history.committed_episode_refs()\n',
    )


def i1_private_consolidation_source(source: str) -> str:
    """Generated Stage10: active Value/Needs advisory, all other forms inert.

    Original Lab code and historic I1 arms keep the ordinary private-only
    identity rebase. Canonical I1 may publish a validated *non-executable*
    consultative index to the one Value/Needs owner without changing TD.
    """
    old = (
        '        if (candidate.get("forms") != self.slow_history.read_committed()["forms"]\n'
        '                or candidate.get("procedural")):\n'
    )
    new = (
        '        canonical = type(self).__name__ == "I1Runtime"\n'
        '        if ((not canonical and candidate.get("forms")\n'
        '             != self.slow_history.read_committed()["forms"])\n'
        '                or (canonical and set(candidate.get("forms", {}))\n'
        '                    != set(Stage10PublicationCoordinator.REQUIRED))):\n'
    )
    if source.count(old) != 1:
        raise ValueError("unreviewed I1 active-form publication guard")
    source = source.replace(old, new)
    # The exact candidate consumed by coordinator.prepare must be the SAME
    # versioned candidate that passed the paid sixth semantic checkpoint.
    # Never mutate an already validated transaction during publication.
    old_handler = "            advance = runner.advance_unit(algorithm.handle)\n"
    new_handler = (
        "            def canonical_paid_semantic_handler(candidate, unit, scoped, cut):\n"
        "                updated = (algorithm.handle_detached(candidate, unit, scoped, cut)\n"
        "                           if type(self).__name__ == 'I1Runtime'\n"
        "                           else algorithm.handle(candidate, unit, scoped, cut))\n"
        "                if (type(self).__name__ == 'I1Runtime'\n"
        "                        and unit.operation == 'index_maintenance'):\n"
        "                    from .i1_cognitive_publication import build_consolidated_owner_forms\n"
        "                    updated['forms'] = build_consolidated_owner_forms(updated)\n"
        "                return updated\n"
        "            advance = runner.advance_unit(canonical_paid_semantic_handler)\n"
    )
    if source.count(old_handler) != 1:
        raise ValueError("unreviewed I1 paid semantic handler")
    source = source.replace(old_handler, new_handler)
    old_rebaser = (
        '        # The final private rebase freezes the journal\'s exact current head.\n'
    )
    new_rebaser = (
        '        if canonical:\n'
        '            def publish_validated_advisory(candidate, baseline, updates):\n'
        '                return self.value_needs.prepare_stage10_advisory_rebase(\n'
        '                    candidate, baseline, updates,\n'
        '                )\n'
        '            rebasers = {\n'
        '                name: (publish_validated_advisory if name == "value_needs"\n'
        '                       else self._i1_active_owner_views[name].prepare_stage10_owner_rebase)\n'
        '                for name in Stage10PublicationCoordinator.REQUIRED\n'
        '            }\n'
        '        else:\n'
        '            rebasers = {\n'
        '                name: preserve_unmodified_active_form\n'
        '                for name in Stage10PublicationCoordinator.REQUIRED\n'
        '            }\n\n'
    )
    if source.count(old_rebaser) != 1:
        raise ValueError("unreviewed I1 Stage10 private rebase anchor")
    source = source.replace(old_rebaser, new_rebaser + old_rebaser)
    old_owner = (
        '                owner_rebasers={\n'
        '                    name: preserve_unmodified_active_form\n'
        '                    for name in Stage10PublicationCoordinator.REQUIRED\n'
        '                },\n'
    )
    if source.count(old_owner) != 1:
        raise ValueError("unreviewed I1 Stage10 coordinator owner rebasers")
    source = source.replace(old_owner, '                owner_rebasers=rebasers,\n')
    for name, reference in (
        ("causal_model", "self.causal_model"),
        ("perception", "self.stage3.perception"),
        ("metacognition_health", "self._meta_custody"),
    ):
        original = '                "' + name + '": ' + reference + ','
        replacement = (
            '                "' + name + '": (self._i1_active_owner_views["'
            + name + '"] if canonical else ' + reference + '),'
        )
        if source.count(original) != 1:
            raise ValueError("unreviewed Stage10 active owner map " + name)
        source = source.replace(original, replacement)
    return source



def generate(output: Path) -> dict[str, object]:
    output = output.resolve()
    # A mis-specified output must never clobber the checked-in cognition.
    if output == SOURCE_ROOT or SOURCE_ROOT in output.parents:
        raise ValueError("I1 build output must not be inside src/")
    if not (SOURCE_ROOT / "i0").is_dir() or not (SOURCE_ROOT / "i1").is_dir():
        raise ValueError("both baseline I0 and I1 source snapshot are required")
    if not (SOURCE_ROOT / "lab").is_dir():
        raise ValueError("independent laboratory runtime source unavailable")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("I1 output must be an empty directory")
    manifest: dict[str, object] = {
        "schema": GENERATED_SCHEMA,
        "i0_baseline_sha": SOURCE_MAIN_SHA,
        "build_mode": "independent_i1_and_i1lab_packages",
        "oracle_or_bench_transferred_into_individual": False,
        "files": {},
    }
    for input_package, output_package in (("i1", "i1"), ("lab", "i1lab")):
        source = SOURCE_ROOT / input_package
        dest = output / output_package
        for file in sorted(source.rglob("*.py")):
            relative = file.relative_to(source)
            contents = file.read_text(encoding="utf-8")
            transformed = rewrite(contents)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/memory.py"):
                transformed = i1_memory_recall_source(transformed)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/consolidation_batch.py"):
                transformed = i1_bounded_batch_selection_source(transformed)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/consolidation_pending_index.py"):
                transformed = i1_pending_projection_copy_source(transformed)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/consolidation_pass_runner.py"):
                transformed = i1_consolidation_runner_copy_source(transformed)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/consolidation_transaction.py"):
                transformed = i1_consolidation_digest_metadata_source(transformed)
            if (output_package == "i1"
                    and relative.as_posix() == "modules/consolidation_semantics.py"):
                # The source snapshot is immutable. I1-only cognitive changes
                # belong in disposable generated output, NEVER in src/i1.
                baseline = (SOURCE_ROOT / "i0" / relative).read_text(
                    encoding="utf-8"
                )
                if contents != baseline:
                    raise ValueError("I1 six-pass snapshot diverged from I0")
                template = SOURCE_ROOT / "i1_overlays" / "i1_semantics_template.txt"
                material = template.read_text(encoding="utf-8")
                if material.count("class LivedSixPassAlgorithm:") != 1:
                    raise ValueError("invalid isolated semantic compiler template")
                transformed = rewrite(material)
            if (output_package == "i1lab"
                    and relative.as_posix() == "journal_views.py"):
                transformed = i1_scoped_autobiographical_view_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "consolidation_lived_evidence.py"):
                transformed = i1_scoped_consolidation_evidence_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "journal.py"):
                transformed = i1_journal_bounded_view_source(transformed)
                transformed = i1_journal_full_integrity_copy_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "sqlite_life_store.py"):
                transformed = i1_sqlite_life_audit_canonical_source(transformed)
                transformed = i1_sqlite_streaming_audit_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "sqlite_runtime_custody.py"):
                transformed = i1_sqlite_journal_count_source(transformed)
                transformed = i1_sqlite_detached_owner_export_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "consolidation_postcut_journal.py"):
                transformed = i1_postcut_bounded_verification_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "consolidation_publication.py"):
                transformed = i1_committed_history_metadata_source(transformed)
                transformed = i1_publication_detached_candidate_source(transformed)
                transformed = i1_slow_history_preflight_no_full_birth_copy_source(transformed)
                transformed = i1_no_live_publication_rollback_source(transformed)
                transformed = i1_stage10_publication_bounded_count_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "stage4_runtime.py"):
                transformed = i1_canonical_active_value_source(transformed)
            if output_package == "i1lab" and relative.as_posix() == "world.py":
                transformed = i1_physiology_source(transformed)
            # Only i1_natural_runtime.I1Runtime installs the natural sleep
            # policy. Do not rewrite the common Stage11Sleep ancestor, which
            # would silently change historical A2.38/A2.39 ablation births.
            if (output_package == "i1lab"
                    and relative.as_posix() == "stage10_runtime.py"):
                transformed = i1_private_consolidation_source(transformed)
                transformed = i1_waking_pending_source(transformed)
                transformed = i1_no_meta_custody_rollback_source(transformed)
                transformed = i1_bounded_stage10_sleep_anchor_source(transformed)
            # I1-only M11 custody: admit ONLY the exact canonical I1
            # runtime, not any experimental Stage12 subclass with unknown
            # mutable owners or unregistered cold-state behavior. Retain the
            # existing exact Stage12 type and all M11 admission criteria.
            # Never alter the canonical src/lab or src/i0 M11 implementation.
            if output_package == "i1lab" and relative.as_posix() == "m11_transactional_mortal.py":
                required = "type(runtime) is Stage12Runtime"
                canonical = (
                    "(type(runtime) is Stage12Runtime "
                    "or type(runtime) is I1Runtime)"
                )
                if transformed.count(required) != 3:
                    raise ValueError("unreviewed I1 M11 runtime type gate")
                transformed = transformed.replace(required, canonical)
                import_anchor = "from .stage12_runtime import Stage12Runtime"
                if transformed.count(import_anchor) != 3:
                    raise ValueError("unreviewed I1 M11 local import scope")
                lines = transformed.splitlines(keepends=True)
                transformed = "".join(
                    line.replace(
                        import_anchor,
                        import_anchor + "\n"
                        + line[:len(line) - len(line.lstrip())]
                        + "from .i1_natural_runtime import I1Runtime",
                    ) if import_anchor in line else line
                    for line in lines
                )
                if transformed.count("from .i1_natural_runtime import I1Runtime") != 3:
                    raise ValueError("canonical I1 M11 import scopes not generated")
                # This private-copy walker must discover immutable proxies
                # in the I1/i1lab owner graph, not accidentally scan only I0.
                original_modules = 'mod.startswith("i0.") or mod.startswith("lab.")'
                if transformed.count(original_modules) != 1:
                    raise ValueError("unreviewed M11 frozen-proxy owner traversal")
                transformed = transformed.replace(
                    original_modules,
                    'mod.startswith("i1.") or mod.startswith("i1lab.")',
                )

                required_line = '        getattr(runtime, "_stage12_detector_policy", None),'
                if transformed.count(required_line) != 1:
                    raise ValueError("unreviewed I1 M11 constructor fingerprint")
                transformed = transformed.replace(
                    required_line,
                    required_line + '\n'
                    + '        getattr(runtime, "_i1_model_contract", None),',
                )
                # D1 water is a separate I1-only canonical cognitive owner.
                # Legacy I1 M11 birth hashes are unchanged when D1 is absent.
                cold_anchor = '        if (key == "metacognition_health"'
                if transformed.count(cold_anchor) != 1:
                    raise ValueError("unreviewed I1 water M11 cold owner hook")
                transformed = transformed.replace(
                    cold_anchor,
                    '        if key == "i1_lived_water_model":\n'
                    '            owner.install_m11_cold_state(\n'
                    '                deepcopy(value), capability=_M11_COLD_OWNER_TOKEN)\n'
                    '        elif (key == "metacognition_health"',
                )
                hash_anchor = (
                    '    return sha256_hex(canonical_causal_bytes('
                    '_contract_value(configuration)))'
                )
                if transformed.count(hash_anchor) != 1:
                    raise ValueError("unreviewed I1 M11 birth contract signature")
                transformed = transformed.replace(
                    hash_anchor,
                    '    if getattr(runtime, "_i1_water_contract", None) is not None:\n'
                    '        configuration = (*configuration,\n'
                    '            ("i1-water-firstperson-birth-v1", runtime._i1_water_contract))\n'
                    + hash_anchor,
                )
                # The canonical natural actor exposes three authoritative
                # owner views in the M11 roster. Their private cold installers
                # must receive the same authenticated M11 capability. Bind the
                # exact I1Runtime type in this separate cold-install function,
                # not only in birth/cold-factory admission scopes.
                cold_owner_anchor = (
                    '    current_owner_ids = {o.owner_id: o for o in runtime.causal_owners}\n'
                )
                if transformed.count(cold_owner_anchor) != 1:
                    raise ValueError("unreviewed M11 cold owner import scope")
                transformed = transformed.replace(
                    cold_owner_anchor,
                    '    from .i1_natural_runtime import I1Runtime\n'
                    + cold_owner_anchor,
                )
                cold_hook = '        if key == "i1_lived_water_model":'
                if transformed.count(cold_hook) != 1:
                    raise ValueError("unreviewed M11 active owner cold installer")
                transformed = transformed.replace(
                    cold_hook,
                    '        if (key in ("causal_model", "perception",'
                    ' "metacognition_health") and type(runtime) is I1Runtime):\n'
                    '            owner.install_m11_cold_state(\n'
                    '                deepcopy(value), capability=_M11_COLD_OWNER_TOKEN)\n'
                    '        elif key == "i1_lived_water_model":',
                )
                transformed = i1_m11_active_publication_custody_source(transformed)
                transformed = i1_m11_bounded_journal_source(transformed)
            # No stale absolute Python imports may silently reach I0.
            for line in transformed.splitlines():
                stripped = line.lstrip()
                if (re.match(r"^(from|import)\s+i0(?:\.|\s|$)", stripped)
                        or re.match(r"^(from|import)\s+lab(?:\.|\s|$)", stripped)):
                    raise ValueError("unisolated Python import in " + str(file))
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(transformed, encoding="utf-8")
            manifest["files"][str(target.relative_to(output))] = {
                "source_path": str(file.relative_to(SOURCE_ROOT)),
                "source_sha256": sha256(contents.encode()).hexdigest(),
                "built_sha256": sha256(transformed.encode()).hexdigest(),
            }
    # I1-only model/runtime overlays are namespaced source, not part of I0.
    overlays = SOURCE_ROOT / "i1_overlays"
    if overlays.exists():
        for file in sorted(overlays.glob("*.py")):
            transformed = rewrite(file.read_text(encoding="utf-8"))
            target = output / "i1lab" / file.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(transformed, encoding="utf-8")
            manifest["files"][str(target.relative_to(output))] = {
                "source_path": str(file.relative_to(SOURCE_ROOT)),
                "source_sha256": sha256(file.read_bytes()).hexdigest(),
                "built_sha256": sha256(transformed.encode()).hexdigest(),
            }
    # The build manifest contains source identity, but no hidden knowledge,
    # no actual birth and no scientific validation assertion.
    (output / "i1_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = generate(args.output)
    print(json.dumps({
        "schema": result["schema"],
        "source_main_sha": result["i0_baseline_sha"],
        "generated_python_modules": len(result["files"]),
        "output": str(args.output.resolve()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
