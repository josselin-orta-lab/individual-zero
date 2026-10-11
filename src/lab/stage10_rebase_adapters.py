"""Stage-10 exact post-cut owner rebase, no fabricated online learning.

Each owner supplies its current *causal* state and the full verified journal
suffix. The six passes stabilize frozen birth forms, while current online
learning remains authoritative. Rebase never modifies a live owner; only the
separate scheduler publication coordinator may activate the prepared states.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Mapping

from .consolidation_lived_evidence import FrozenLivedReplayEvidence
from .determinism import canonical_causal_bytes, sha256_hex
from .journal import HashChainedJournal
from .journal_views import JournalViews, AutobiographicalPolicy
from i0.modules.stage10_causal_model import Stage10CausalModel
from i0.modules.consolidation_transaction import ConsolidationTransaction

REQUIRED = frozenset({
    "value_needs", "metacognition_health", "perception", "causal_model",
})


def _form(candidate: object, owner_id: str) -> object:
    if (type(candidate) is not dict
            or candidate.get("form_source") != "owner_active_causal_cut"
            or not isinstance(candidate.get("forms"),dict)
            or not REQUIRED.issubset(candidate["forms"])
            or candidate.get("form_cut_digest") != sha256_hex(
                canonical_causal_bytes(candidate["forms"]))):
        raise ValueError("consolidation lacks exact canonical cut-point owner forms")
    return deepcopy(candidate["forms"][owner_id])


def _same_config(cut, live, *paths):
    for chain in paths:
        a,b=cut,live
        for key in chain:
            if not isinstance(a,Mapping) or not isinstance(b,Mapping):
                raise ValueError("invalid causal snapshot structure")
            a,b=a.get(key),b.get(key)
        if a!=b:
            raise ValueError("postcut rebase changed a normative owner configuration")


def _td_rebase(candidate, baseline, updates):
    cut=_form(candidate,"value_needs")
    _same_config(cut,baseline,("config_version",),
                 ("td_values","config_version"),("td_values","feature_version"))
    before=cut["td_values"]["update_counts"]
    after=baseline["td_values"]["update_counts"]
    counted=Counter()
    for event in updates:
        if event.kind!="td_update_published":
            raise ValueError("unexpected Value/Needs rebase record")
        payload=event.detached_payload()
        signatures=payload.get("updated_signatures")
        if (type(signatures) is not list
                or len(signatures)!=len(set(signatures))
                or any(type(s) is not str for s in signatures)):
            raise ValueError("invalid published TD feature delta witness")
        counted.update(signatures)
    for sig in set(before)|set(after)|set(counted):
        if (type(before.get(sig,0)) is not int
                or type(after.get(sig,0)) is not int
                or after.get(sig,0)-before.get(sig,0)!=counted[sig]):
            raise ValueError("online TD rebase does not match published causal journal")
    return deepcopy(baseline)


def _kappa_rebase(candidate, baseline, updates):
    cut=_form(candidate,"metacognition_health")
    _same_config(cut,baseline,
        ("stage10_custody_schema",),
        ("metacognition","kappa_active","config_version"),
        ("sleep_health","config_version"))
    before=cut["metacognition"]["kappa_active"]["credited_observations"]
    after=baseline["metacognition"]["kappa_active"]["credited_observations"]
    emitted=[]
    for event in updates:
        if event.kind!="kappa_update_published":
            raise ValueError("unexpected Meta-owner rebase record")
        payload=event.detached_payload()
        if (type(payload.get("verification_ref")) is not str
                or payload.get("outcome") not in {"confirmee","contredite"}
                or type(payload.get("calibration_key")) is not list):
            raise ValueError("unverified online kappa postcut publication")
        emitted.append(payload["verification_ref"])
    if (len(set(emitted))!=len(emitted)
            or len(after)-len(before)!=len(emitted)
            or not {tuple(row) for row in before}.issubset(
                {tuple(row) for row in after})):
        raise ValueError("kappa credits inconsistent with postcut journal")
    return deepcopy(baseline)


def _precision_rebase(candidate, baseline, updates):
    cut=_form(candidate,"perception")
    _same_config(cut,baseline,("precision_active","config_version"))
    def counts(state):
        return {row["source"]:int(row["n"])
                for row in state["precision_active"]["source_sums"]}
    before,after=counts(cut),counts(baseline)
    emitted=Counter()
    for event in updates:
        if event.kind!="perceptual_precision_update_published":
            raise ValueError("unexpected Perception rebase record")
        item=event.detached_payload()
        if (type(item.get("source")) is not str
                or type(item.get("verification_ref")) is not str
                or not isinstance(item.get("before"),(int,float))
                or not isinstance(item.get("after"),(int,float))):
            raise ValueError("unverified online precision publication")
        emitted[item["source"]]+=1
    for key in set(before)|set(after)|set(emitted):
        if after.get(key,0)-before.get(key,0)!=emitted[key]:
            raise ValueError("precision postcut sample count mismatch")
    return deepcopy(baseline)


def make_stage10_rebasers(
    *, model: Stage10CausalModel,
    transaction: ConsolidationTransaction,
    journal: HashChainedJournal,
    views: JournalViews,
    policies: Mapping[str, AutobiographicalPolicy],
):
    if type(model) is not Stage10CausalModel:
        raise TypeError("canonical Stage-10 Causal Model required")
    lived=FrozenLivedReplayEvidence(
        journal=journal,views=views,transaction=transaction,policies=policies,
    )
    physical={}
    for episode,projections in lived.episode_projections().items():
        physical[episode]={
            row["event_id"] for row in projections
            if row["kind"] in {
                "command_experienced", "world_transition_experienced",
            }
        }

    def causal(candidate,baseline,updates):
        cut=_form(candidate,"causal_model")
        _same_config(cut,baseline,("config_version",),("config_contract",),
                     ("consolidation_schema",))
        # Do not lose later causal inferences: only the *current* validated
        # owner's copy receives newly replayed but still tentative rules.
        current=model.export_causal_state()
        if canonical_causal_bytes(current)!=canonical_causal_bytes(baseline):
            raise ValueError("canonical Causal Model changed during private rebase")
        for item in updates:
            if item.kind not in {
                "causal_inference_status_published",
                "causal_safety_status_published",
                "causal_prediction_corrections_published",
            }:
                raise ValueError("unknown canonical causal postcut event")
        return model.prepare_consolidated_rules(
            rules=deepcopy(candidate.get("hypotheses",[])),
            physical_by_episode=physical,
        )

    return {
        "value_needs":_td_rebase,
        "metacognition_health":_kappa_rebase,
        "perception":_precision_rebase,
        "causal_model":causal,
    }
