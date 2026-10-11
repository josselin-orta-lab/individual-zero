"""Stage-10 extension of the single canonical Causal Model, never a second oracle.

Existing Stage-9 contingency/safety evidence and status transitions are left
unchanged. Consolidation may add only private, physically witnessed candidate
hypotheses. They become canonical, revisable *hypothese_causale* records at a
coordinated commit and cannot acquire a safety veto or an established status.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from lab.determinism import canonical_causal_bytes, sha256_hex
from .causal_model import CausalModel, CausalModelConfig, CanonicalContingency


class Stage10CausalModel(CausalModel):
    """One canonical causal owner with a strictly non-safety hypothesis tier."""

    consolidation_schema = "stage10-causal-consolidated-hypotheses-v1"

    def __init__(self, config: CausalModelConfig):
        super().__init__(config)
        self._consolidated_hypotheses: dict[str, dict[str, object]] = {}

    def export_causal_state(self) -> object:
        state = super().export_causal_state()
        state["consolidation_schema"] = self.consolidation_schema
        state["consolidated_hypotheses"] = [
            deepcopy(self._consolidated_hypotheses[k])
            for k in sorted(self._consolidated_hypotheses)
        ]
        return state

    @staticmethod
    def _validated_rule(item: object) -> dict[str, object]:
        if (type(item) is not dict or set(item) != {
            "id", "predicate", "status", "source_episode_refs",
            "source_event_refs", "expires_at_step", "validated_for_safety",
        } or type(item["id"]) is not str or not item["id"].startswith("hyp:")
                or type(item["predicate"]) is not dict
                or set(item["predicate"]) != {
                    "primitive","parameters","observed_field","observed_value",
                } or type(item["predicate"]["primitive"]) is not str
                or type(item["predicate"]["parameters"]) is not dict
                or type(item["predicate"]["observed_field"]) is not str
                or type(item["predicate"]["observed_value"]) is not str
                or item["status"] != "hypothese_causale"
                or item["validated_for_safety"] is not False
                or type(item["expires_at_step"]) is not int
                or item["expires_at_step"] < 1):
            raise ValueError("noncanonical or unsafe consolidation hypothesis")
        for key in ("source_episode_refs","source_event_refs"):
            refs=item[key]
            if (type(refs) is not list or not refs
                    or any(type(ref) is not str or not ref for ref in refs)
                    or refs != sorted(set(refs))):
                raise ValueError("physical evidence must be unique and sorted")
        if len(item["source_event_refs"]) < 2:
            raise ValueError("hypothesis must have paired physical witnesses")
        actual="hyp:"+sha256_hex(canonical_causal_bytes(item["predicate"]))[:28]
        if item["id"] != actual:
            raise ValueError("hypothesis ref changed its causal predicate")
        return deepcopy(item)

    def prepare_consolidated_rules(
        self, *, rules: list[dict[str,object]],
        physical_by_episode: Mapping[str, set[str]],
    ) -> dict[str,object]:
        """Return a private canonical-owner snapshot with deduplicated sources.

        Caller supplies ONLY a verified frozen DC-09 projection (not a bench
        trace or a fabricated list). All source refs must occur in the
        nominated lived episodes and never be double-counted.
        """
        candidate=deepcopy(self.export_causal_state())
        records={
            item["id"]:self._validated_rule(item)
            for item in candidate["consolidated_hypotheses"]
        }
        for raw in rules:
            item=self._validated_rule(raw)
            episodes=item["source_episode_refs"]
            observed=set()
            for episode in episodes:
                physical=physical_by_episode.get(episode)
                if physical is None:
                    raise ValueError("unverified episode in consolidated hypothesis")
                observed.update(physical)
            if not set(item["source_event_refs"]).issubset(observed):
                raise ValueError("rule source event lacks pre-cut physical projection")
            before=records.get(item["id"])
            if before is None:
                records[item["id"]]=item
                continue
            if before["predicate"] != item["predicate"]:
                raise ValueError("canonical predicate collision")
            before["source_episode_refs"]=sorted(
                set(before["source_episode_refs"])|set(episodes))
            before["source_event_refs"]=sorted(
                set(before["source_event_refs"])|set(item["source_event_refs"]))
            before["expires_at_step"]=max(
                before["expires_at_step"],item["expires_at_step"])
        candidate["consolidated_hypotheses"]=[
            records[ref] for ref in sorted(records)
        ]
        # Independently validate via the real canonical owner deserializer.
        checker=type(self)(self.config)
        checker.restore_causal_state(candidate)
        return candidate

    def restore_causal_state(self,state:object)->None:
        if (not isinstance(state,Mapping)
                or state.get("consolidation_schema") != self.consolidation_schema
                or type(state.get("consolidated_hypotheses")) is not list):
            raise ValueError("Stage-10 canonical model snapshot lacks rule tier")
        raw=deepcopy(state["consolidated_hypotheses"])
        rules={}
        for item in raw:
            checked=self._validated_rule(item)
            if checked["id"] in rules:
                raise ValueError("duplicate consolidated hypothesis identity")
            rules[checked["id"]]=checked
        # Fully validate original Stage-9 owner state on a detached instance.
        baseline=type(self)(self.config)
        super(Stage10CausalModel,baseline).restore_causal_state({
            key:deepcopy(value) for key,value in state.items()
            if key not in {"consolidation_schema","consolidated_hypotheses"}
        })
        self.__dict__.update(baseline.__dict__)
        self._consolidated_hypotheses=rules

    @staticmethod
    def _representation(rule):
        p=rule["predicate"]
        context=sha256_hex(canonical_causal_bytes(p["parameters"]))[:20]
        return CanonicalContingency(
            ref=rule["id"],version=1,
            predicate="experienced:"+p["primitive"]+":"+p["observed_field"]+
                ":"+p["observed_value"],
            subject_ref="primitive:"+p["primitive"],
            context_signature="parameters:"+context,
            causal_status="hypothese_causale",
            safety_status="aucun",
            evidence_refs=tuple(rule["source_event_refs"]),
            harmful_episodes=(),harmless_episodes=(),innate=False,
        )

    def get(self,contingency_ref:str):
        record=super().get(contingency_ref)
        if record is not None:
            return record
        rule=self._consolidated_hypotheses.get(contingency_ref)
        return None if rule is None else self._representation(rule)

    def contingencies(self,*,context_signature=None,status=None):
        original=super().contingencies(
            context_signature=context_signature,status=status,
        )
        additional=tuple(self._representation(item)
            for _,item in sorted(self._consolidated_hypotheses.items())
            if (context_signature is None or
                self._representation(item).context_signature==context_signature)
            and (status is None or status in {"hypothese_causale","aucun"}))
        return tuple(sorted(original+additional,key=lambda item:item.ref))
