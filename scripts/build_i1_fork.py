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



def i1_stage10_canonical_baseline_source(source: str) -> str:
    """Hold byte-exact owner baselines rather than live-state rollback copies.

    Applied only to the generated I1lab Stage10 coordinator, AFTER the
    no-live-rollback transform removes all exception-path old-state restores.
    Original owner snapshots still exist locally for detached preparation;
    the retained cross-boundary references are exact canonical bytes.
    """
    changes = (
        (
            "    source_history_state: object\n    baseline_owner_states: Mapping[str, object]\n",
            "    source_history_canonical: bytes\n    baseline_owner_canonical: Mapping[str, bytes]\n",
        ),
        (
            "        baseline = {\n            name: _copy_causal(owner.export_causal_state())\n            for name, owner in sorted(self.owners.items())\n        }\n",
            "        # The snapshots are needed only during rebase. Retain canonical\n        # bytes for precise pre-publication equality, not rollback copies.\n        baseline = {}\n        baseline_canonical = {}\n        for name, owner in sorted(self.owners.items()):\n            exported = owner.export_causal_state()\n            baseline_canonical[name] = canonical_causal_bytes(exported)\n            baseline[name] = deepcopy(exported)\n",
        ),
        (
            "            if canonical_causal_bytes(owner.export_causal_state()) != canonical_causal_bytes(baseline[name]):\n",
            "            if (canonical_causal_bytes(owner.export_causal_state())\n                    != baseline_canonical[name]):\n",
        ),
        (
            "        previous_history = self.history.export_causal_state()\n",
            "        source_history_canonical = canonical_causal_bytes(\n            self.history.export_causal_state()\n        )\n",
        ),
        (
            "            source_history_state=previous_history,\n            baseline_owner_states=baseline,\n",
            "            source_history_canonical=source_history_canonical,\n            baseline_owner_canonical=baseline_canonical,\n",
        ),
        (
            "        if canonical_causal_bytes(before_history) != canonical_causal_bytes(prepared.source_history_state):\n",
            "        if canonical_causal_bytes(before_history) != prepared.source_history_canonical:\n",
        ),
        (
            "            if (canonical_causal_bytes(owner.export_causal_state())\n                    != canonical_causal_bytes(prepared.baseline_owner_states[name])):\n",
            "            if (canonical_causal_bytes(owner.export_causal_state())\n                    != prepared.baseline_owner_canonical[name]):\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 Stage10 canonical baseline anchor")
        source = source.replace(before, after)
    if ("prepared.baseline_owner_states" in source
            or "prepared.source_history_state" in source):
        raise ValueError("unmigrated I1 Stage10 rollback snapshot references")
    return source


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
        # The recomputation is read-only and immediately serialized for
        # parity. Keep published owner snapshots detached elsewhere.
        recomputed = (
            build_consolidated_owner_form(history, name, detach_evidence=False)
            if forms else []
        )
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


def i1_stage11_owned_geography_lookup_source(source: str) -> str:
    """Avoid full ledger/survey materialization for first-person lookups.

    Exact generated i1lab Stage11 source only; I0 and Lab originals
    preserve their source contracts. Physical capture and survey charging
    still precede registration, and all cold-export integrity remains.
    """
    changes = (
        (
            "        over_capacity = (\n            (capture.x, capture.y) not in {\n                tuple(site[:2])\n                for site in geo.export_causal_state()[\"visits\"]\n            }\n            and geo.distinct_sites >= geo.config.max_distinct_sites\n        )\n",
            "        # The owned visit dictionary answers this question directly.\n        # Test capacity first, avoiding a lookup until the bound is reached.\n        over_capacity = (\n            geo.distinct_sites >= geo.config.max_distinct_sites\n            and not geo.has_recorded_site((capture.x, capture.y))\n        )\n",
        ),
        (
            "                earlier_survey = (\n                    next((q for q in geo.surveys\n                          if q.position == (capture.x, capture.y)), None)\n                    if geo.config.refresh_surveys else None\n                )\n",
            "                earlier_survey = (\n                    geo.observed_survey_at((capture.x, capture.y))\n                    if geo.config.refresh_surveys else None\n                )\n",
        ),
        (
            "                    current_survey = next(\n                        q for q in geo.surveys\n                        if q.position == (capture.x, capture.y)\n                    )\n",
            "                    current_survey = geo.observed_survey_at(\n                        (capture.x, capture.y)\n                    )\n                    if current_survey is None:\n                        raise LookupError(\"recorded current survey is unavailable\")\n",
        ),
        (
            "        frozen_geography = (\n            None if self.exploration.geographic is None\n            else self.exploration.geographic.export_causal_state()\n        )\n",
            "        # Phase-0 must freeze route data before Phase-1 observations, but\n        # copying the entire ledger is pointless unless a grounded route\n        # search can actually be requested in this cycle.\n        demand_skip_geo_preflight = (\n            self.exploration.geographic is not None\n            and self._stage11_config.geographic_preflight\n            and self._stage11_config.geographic_preflight_requires_frontier\n            and not raw_geo_targets\n        )\n        frozen_geography = (\n            self.exploration.geographic.export_causal_state()\n            if (demand_skip_geo_preflight\n                and self._stage11_config.geographic_route_enabled)\n            else None\n        )\n",
        ),
        (
            "        demand_skip_geo_preflight = (\n            self.exploration.geographic is not None\n            and self._stage11_config.geographic_preflight\n            and self._stage11_config.geographic_preflight_requires_frontier\n            and not raw_geo_targets\n        )\n        self._stage11_prospective_state = frozen\n",
            "        self._stage11_prospective_state = frozen\n",
        ),
        (
            "        known = {\n            ref for ref, _ in self.exploration.export_causal_state()[\"questions\"]\n        }\n",
            "        # Capture only existing causal question IDs BEFORE Phase-1; do not\n        # materialize the full geographic owner to answer a membership test.\n        known = self.exploration.known_causal_question_refs()\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 Stage11 geographic lookup anchor")
        source = source.replace(before, after)
    return source


def i1_stage11_paid_exploration_probe_source(source: str) -> str:
    """Avoid two full lifetime Exploration exports around paid Phase-1.

    The latest actual visit and survey record mutations are tracked by their
    return values. The unchanged question rows and immutable geographic
    fields are compared directly. Full export is retained for real updates
    and for M11 persistence. Apply AFTER geo lookup transformations.
    """
    changes = (
        (
            "            previous = self.exploration.export_causal_state()\n",
            "            # Capture questions and immutable geographic markers only.\n            # Actual visit/survey writes are checked via operation results.\n            previous = self.exploration.phase_observation_probe()\n",
        ),
        (
            "            geo = self.exploration.geographic\n            if geo is not None and geo.config.observe_routes and not over_capacity:\n",
            "            geo = self.exploration.geographic\n            survey_recorded = False\n            if geo is not None and geo.config.observe_routes and not over_capacity:\n",
        ),
        (
            "                if geo.record_survey(capture):\n                    current_survey = geo.observed_survey_at(\n",
            "                if geo.record_survey(capture):\n                    survey_recorded = True\n                    current_survey = geo.observed_survey_at(\n",
        ),
        (
            "            current = self.exploration.export_causal_state()\n            if current != previous:\n                self._write(\n                    kind=\"stage11_exploration_updated\", cycle=cycle,\n",
            "            # No source-owned counters/observations can change in this\n            # hook except via the paid visit and survey operations above.\n            # Rebuild the full canonical event state only on a real change.\n            if (new_geo_visit or survey_recorded\n                    or self.exploration.phase_observation_probe() != previous):\n                current = self.exploration.export_causal_state()\n                self._write(\n                    kind=\"stage11_exploration_updated\", cycle=cycle,\n",
        ),
    )
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 paid Exploration differential source")
        source = source.replace(before, after)
    return source


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
            if input_package == "i1" and relative.parts[0] == "runtime":
                continue  # Built into i1lab below, never twice in generated i1.
            if input_package == "lab" and relative.as_posix() in {"world.py", "journal.py", "journal_views.py", "consolidation_lived_evidence.py", "consolidation_postcut_journal.py", "sqlite_life_store.py", "sqlite_runtime_custody.py"}:
                continue  # Versioned native I1 world, journal and lived views.
            contents = file.read_text(encoding="utf-8")
            transformed = rewrite(contents)
            if (output_package == "i1lab"
                    and relative.as_posix() == "consolidation_publication.py"):
                transformed = i1_committed_history_metadata_source(transformed)
                transformed = i1_publication_detached_candidate_source(transformed)
                transformed = i1_slow_history_preflight_no_full_birth_copy_source(transformed)
                transformed = i1_no_live_publication_rollback_source(transformed)
                transformed = i1_stage10_publication_bounded_count_source(transformed)
                transformed = i1_stage10_canonical_baseline_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "stage4_runtime.py"):
                transformed = i1_canonical_active_value_source(transformed)
            # Only i1_natural_runtime.I1Runtime installs the natural sleep
            # policy. Do not rewrite the common Stage11Sleep ancestor, which
            # would silently change historical A2.38/A2.39 ablation births.
            if (output_package == "i1lab"
                    and relative.as_posix() == "stage11_runtime.py"):
                transformed = i1_stage11_owned_geography_lookup_source(transformed)
                transformed = i1_stage11_paid_exploration_probe_source(transformed)
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
    overlays = SOURCE_ROOT / "i1" / "runtime"
    if overlays.exists():
        for file in sorted(overlays.glob("*.py")):
            if file.name == "__init__.py":
                continue  # Preserve the authentic isolated Lab package root.
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
