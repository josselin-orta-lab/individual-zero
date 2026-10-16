"""Stage-10 six genuine private semantic passes over verified lived projections.

Passes NEVER consult the Lab, WorldBody, oracle or a mutable active owner.
Every work unit is admitted by ConsolidationPassRunner after a real P-42
logical-UC debit. Rules remain *hypotheses*, procedural successes count
distinct episodes, and missing independent calibration evidence is never
upgraded to certainty. The Causal Model and Procedural Memory, not this
private candidate, are responsible for final integration at atomic commit.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from math import isfinite
from typing import Mapping
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.consolidation_lived_evidence import FrozenLivedReplayEvidence
from .consolidation_transaction import ConsolidationTransaction, ConsolidationCut, PASSES
from .consolidation_pass_runner import ConsolidationUnit, ConsolidationPassPlan
from .consolidation_budget import ConsolidationWorkBudget
from .consolidation_replay_agenda import ReplayAgendaPolicy


_OPERATIONS = {
    "episode_selection": "episode_scan",
    "interleaved_replay": "episode_replay",
    "hypothesis_extraction": "rule_extraction",
    "procedural_compilation": "skill_compilation",
    "kappa_recalibration": "kappa_recalibration",
    "index_maintenance": "index_maintenance",
}


@dataclass(frozen=True, slots=True)
class SemanticPassPolicy:
    version: str
    replay: ReplayAgendaPolicy
    skill_success_threshold: int
    nearby_context_radius: int
    rule_expiry_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("six-pass algorithm version must be declared")
        self.replay.validate()
        if (type(self.skill_success_threshold) is not int
                or self.skill_success_threshold < 2
                or type(self.nearby_context_radius) is not int
                or self.nearby_context_radius < 0
                or type(self.rule_expiry_steps) is not int
                or self.rule_expiry_steps < 1):
            raise ValueError("DC-16 evidence and expiration policy invalid")


class LivedSixPassAlgorithm:
    """Private computations attached to one frozen selection, no active writes."""

    def __init__(
        self, *, transaction: ConsolidationTransaction,
        evidence: FrozenLivedReplayEvidence,
        policy: SemanticPassPolicy,
    ) -> None:
        policy.validate()
        if (not isinstance(transaction, ConsolidationTransaction)
                or transaction.status != "active"
                or type(evidence) is not FrozenLivedReplayEvidence
                or evidence.cut != transaction.cut
                or evidence.batch_digest != transaction.batch_digest):
            raise ValueError("semantic algorithm requires verified pre-cut Lab projections")
        episode_projections = evidence.episode_projections()
        if set(episode_projections) != set(transaction.batch):
            raise ValueError("semantic input must match frozen active batch")
        originals = transaction.frozen_episodes_copy()
        owned = {}
        for ep_ref in transaction.batch:
            events = episode_projections[ep_ref]
            source_ids = originals[ep_ref].get("event_refs")
            if (type(events) is not list or type(source_ids) is not list
                    or [ev.get("event_id") for ev in events] != source_ids
                    or len(set(source_ids)) != len(source_ids)):
                raise ValueError("frozen event projections mismatch lived episode")
            for ev in events:
                if (type(ev) is not dict or type(ev.get("event_id")) is not str
                        or type(ev.get("kind")) is not str):
                    raise ValueError("untyped autobiographical projection")
                canonical_causal_bytes(ev)
            owned[ep_ref] = deepcopy(events)
        self.transaction = transaction
        self.policy = policy
        self._events = owned
        self._episodes = originals

    def make_plan(self, *, budget: ConsolidationWorkBudget,
                  replay_plan: ConsolidationPassPlan | None = None,
                  ) -> ConsolidationPassPlan | None:
        """Price plan construction. Pass 2 requires the separate paid agenda.

        For large batches the IncrementalReplayAgendaBuilder must construct
        replay_plan across sleep slots; there is no free synchronous shortcut.
        """
        tx = self.transaction
        if tx.status != "active" or tx.cursor >= len(PASSES):
            raise ValueError("inactive or finished private consolidation")
        if budget.open_world_step is None:
            raise ValueError("planning requires a sleeping budget slot")
        name = PASSES[tx.cursor]
        if name == "interleaved_replay":
            if replay_plan is None:
                raise ValueError("pass 2 requires a separately charged interleaved agenda")
            replay_plan.validate(tx, budget)
            return replay_plan
        if "semantic_plan_build" not in budget.config.operation_costs:
            raise ValueError("P-42 semantic planning cost must be registered")
        debit = budget.charge(operation="semantic_plan_build")
        if not debit.accepted:
            return None
        if name == "index_maintenance":
            refs = ((),)
        else:
            refs = tuple((episode,) for episode in tx.batch)
        units = tuple(ConsolidationUnit(
            unit_ref=f"{name}:{i:06d}",
            operation=_OPERATIONS[name],episode_refs=ep_refs,
            data={
                "algorithm_version":self.policy.version,
                "batch_digest":tx.batch_digest,
                "unit_index":i,
            },
        ) for i, ep_refs in enumerate(refs))
        result = ConsolidationPassPlan(
            consolidation_id=tx.id,pass_name=name,
            algorithm_version=self.policy.version,
            batch_digest=tx.batch_digest,
            source_candidate_digest=tx.candidate_digest,
            units=units,
        )
        result.validate(tx,budget)
        return result

    @staticmethod
    def _candidate(value):
        if type(value) is not dict or not isinstance(value.get("forms"),dict):
            raise ValueError("slow history candidate must contain an owned forms map")
        return value

    def _events_for(self, unit, scoped):
        if not unit.episode_refs:
            return ()
        ref=unit.episode_refs[0]
        if list(scoped) != [ref]:
            raise ValueError("priced unit can access only its detached episode")
        if canonical_causal_bytes(scoped[ref]) != canonical_causal_bytes(self._episodes[ref]):
            raise ValueError("semantic handler was given altered autobiography")
        return tuple(deepcopy(self._events[ref]))

    @staticmethod
    def _observed_pairs(events):
        """At most one physical command and result per simulated step."""
        sent, arrived = {}, {}
        for ordinal, event in enumerate(events):
            t = event.get("t_monde")
            if type(t) is not int:
                continue
            if event["kind"] == "command_experienced":
                sent.setdefault(t, []).append((ordinal, event))
            elif event["kind"] == "world_transition_experienced":
                arrived.setdefault(t, []).append((ordinal, event))
        for t in sorted(set(sent) & set(arrived)):
            if len(sent[t]) != 1 or len(arrived[t]) != 1:
                continue
            command_index, command = sent[t][0]
            result_index, physical = arrived[t][0]
            # The autobiographical projection preserves chronological event
            # refs. A future or unrelated transition cannot corroborate an
            # earlier command, even when its world-step number matches.
            if command_index >= result_index:
                continue
            if (command.get("primitive") in {
                    "se_deplacer", "collecter", "manger", "boire",
                    "fabriquer_outil", "poser_une_pierre",
                } and isinstance(physical.get("effects"), Mapping)):
                yield command, physical

    @staticmethod
    def _physical_result(command, transition):
        primitive=command["primitive"]
        effects=transition["effects"]
        if primitive=="boire":
            if type(effects.get("drank")) is bool:
                return ("drank",str(effects["drank"]).lower())
        elif primitive=="manger":
            ate=effects.get("ate")
            if type(ate) is str:
                return ("ate",ate)
        elif primitive=="collecter":
            collected=effects.get("collected")
            if isinstance(collected,Mapping):
                kind,count=collected.get("kind"),collected.get("quantity")
                if type(kind) is str and type(count) is int and count>=0:
                    return ("collected",f"{kind}:{count>0}")
        elif primitive=="fabriquer_outil":
            if type(effects.get("tool_crafted")) is bool:
                return ("tool_crafted",str(effects["tool_crafted"]).lower())
        elif primitive=="se_deplacer":
            if effects.get("movement") in {"moved","blocked"}:
                return ("movement",effects["movement"])
        elif primitive=="poser_une_pierre":
            count=effects.get("placed_stone_count")
            if type(count) is int and count>=0:
                return ("stone_placed",str(count>0).lower())
        return None

    def _extract_episode_rules(self, ep_ref, events, cut):
        output=[]
        for command,physical in self._observed_pairs(events):
            observed=self._physical_result(command,physical)
            if observed is None:
                continue
            params=command.get("parameters",{})
            if type(params) is not dict:
                continue
            predicate={
                "primitive":command["primitive"],
                "parameters":deepcopy(params),
                "observed_field":observed[0],
                "observed_value":observed[1],
            }
            rule_ref="hyp:"+sha256_hex(canonical_causal_bytes(predicate))[:28]
            output.append((rule_ref,{
                "id":rule_ref,"predicate":predicate,"status":"hypothese_causale",
                "source_episode_refs":[ep_ref],
                "source_event_refs":[command["event_id"],physical["event_id"]],
                "expires_at_step":cut.world_step+self.policy.rule_expiry_steps,
                "validated_for_safety":False,
            }))
        return output

    def _compile_from_proven_plans(self, cut):
        """Compile *private* one-step affordances from lived physical receipts.

        Earlier code required a nonexistent 'stage10_plan_applied' producer.
        Only an actual paired command/transition with an explicit positive
        effect can contribute a success. This establishes observed execution,
        NOT general safety, nutrition, a distal goal, or causal certainty.
        Distinct episodes are required. Nothing is installed in active owners.
        """
        records = {}
        for episode_ref in self.transaction.batch:
            events = self._events[episode_ref]
            for command, physical in self._observed_pairs(events):
                observed = self._physical_result(command, physical)
                if observed is None:
                    continue
                effect, value = observed
                # No witnessed pre-action position is present in this
                # autobiographical schema. A successful movement's *arrival*
                # cannot establish a reusable departure-site precondition.
                # Keep movement learning in online TD/geographical owners.
                if command["primitive"] == "se_deplacer":
                    continue
                succeeded = (
                    (effect == "drank" and value == "true")
                    or (effect == "ate" and value in ("berry_a", "berry_b"))
                    or (effect == "collected" and value.endswith(":True"))
                    or (effect == "tool_crafted" and value == "true")
                    or (effect == "movement" and value == "moved")
                    or (effect == "stone_placed" and value == "true")
                )
                params = command.get("parameters")
                pos = physical.get("position_after")
                if (type(params) is not dict or not isinstance(pos, Mapping)
                        or type(pos.get("x")) is not int
                        or type(pos.get("y")) is not int):
                    continue
                signature = sha256_hex(canonical_causal_bytes({
                    "primitive": command["primitive"],
                    "parameters": params,
                    "observed_field": effect,
                }))
                records.setdefault(signature, []).append({
                    "episode": episode_ref,
                    "events": (command["event_id"], physical["event_id"]),
                    "context": (pos["x"], pos["y"]),
                    "success": succeeded,
                    "primitive": command["primitive"],
                    "parameters": deepcopy(params),
                    "observed_field": effect,
                })
        result = []
        for signature in sorted(records):
            trials = records[signature]
            for anchor in sorted({r["context"] for r in trials if r["success"]}):
                candidates = [
                    row for row in trials if (
                        abs(row["context"][0] - anchor[0])
                        + abs(row["context"][1] - anchor[1])
                        <= self.policy.nearby_context_radius
                    )
                ]
                successes = {r["episode"] for r in candidates if r["success"]}
                failures = {r["episode"] for r in candidates if not r["success"]}
                if len(successes) < self.policy.skill_success_threshold:
                    continue
                total = len(successes | failures)
                evidence = [r for r in candidates if r["episode"] in successes
                            and r["success"]]
                example = evidence[0]
                item = {
                    "id": "skill:" + sha256_hex(canonical_causal_bytes({
                        "signature": signature, "anchor": list(anchor),
                    }))[:28],
                    # Physical command effects, not verified plan success.
                    "plan_signature": "observed_primitive:" + signature,
                    "primitive": example["primitive"],
                    "parameters": deepcopy(example["parameters"]),
                    "observed_field": example["observed_field"],
                    "evidence_scope": "experienced_local_physical_result",
                    "goal_success_inferred": False,
                    "safety_certified": False,
                    "near_context": {"x": anchor[0], "y": anchor[1],
                                     "radius": self.policy.nearby_context_radius},
                    "preconditions": [],
                    "source_episode_refs": sorted(successes),
                    "source_event_refs": sorted({
                        event for row in evidence for event in row["events"]
                    }),
                    "distinct_success_count": len(successes),
                    "distinct_trial_count": total,
                    "success_rate": len(successes) / total,
                    "state": "compiled_private",
                }
                result.append(item)
        result.sort(key=lambda row: row["id"])
        return result

    @staticmethod
    def _merge_private_procedures(previous, newly_compiled):
        """Retain trusted private evidence across separately paid sleep cuts.

        Counts only unique autobiographical episodes. An existing skill can
        receive more evidence from a disjoint new batch, but cannot silently
        change its action, contextual scope, or private/non-executable state.
        All saved records remain private SlowHistory, not active policies.
        """
        if type(previous) is not list or type(newly_compiled) is not list:
            raise ValueError("private procedures must be typed lists")
        combined = {}
        for row in previous:
            if (type(row) is not dict or type(row.get("id")) is not str
                    or row.get("state") != "compiled_private"
                    or row["id"] in combined):
                raise ValueError("invalid or duplicated committed private procedure")
            combined[row["id"]] = deepcopy(row)
        for row in newly_compiled:
            if (type(row) is not dict or type(row.get("id")) is not str
                    or row.get("state") != "compiled_private"):
                raise ValueError("invalid newly compiled private procedure")
            old = combined.get(row["id"])
            if old is None:
                combined[row["id"]] = deepcopy(row)
                continue
            immutable = (
                "plan_signature", "primitive", "parameters", "observed_field",
                "evidence_scope", "goal_success_inferred", "safety_certified",
                "near_context", "preconditions", "state",
            )
            if any(old.get(key) != row.get(key) for key in immutable):
                raise ValueError("conflicting private procedural identity")
            old_episodes = old.get("source_episode_refs")
            new_episodes = row.get("source_episode_refs")
            old_events = old.get("source_event_refs")
            new_events = row.get("source_event_refs")
            if (not all(type(v) is list for v in (
                    old_episodes, new_episodes, old_events, new_events))
                    or not old_episodes or not new_episodes
                    or len(set(old_episodes)) != len(old_episodes)
                    or len(set(new_episodes)) != len(new_episodes)
                    or len(set(old_events)) != len(old_events)
                    or len(set(new_events)) != len(new_events)
                    or set(old_episodes).intersection(new_episodes)
                    or set(old_events).intersection(new_events)):
                raise ValueError("previously consolidated evidence cannot be recounted")
            success = old["distinct_success_count"] + row["distinct_success_count"]
            trials = old["distinct_trial_count"] + row["distinct_trial_count"]
            if (type(success) is not int or type(trials) is not int
                    or success < 2 or trials < success
                    or success != len(old_episodes) + len(new_episodes)):
                raise ValueError("invalid cumulative independent trial counts")
            merged = deepcopy(old)
            merged["source_episode_refs"] = sorted(old_episodes + new_episodes)
            merged["source_event_refs"] = sorted(old_events + new_events)
            merged["distinct_success_count"] = success
            merged["distinct_trial_count"] = trials
            merged["success_rate"] = success / trials
            combined[row["id"]] = merged
        return [combined[k] for k in sorted(combined)]

    def handle(self, candidate, unit, scoped, cut:ConsolidationCut):
        """Pure work-unit handler; only detached immutable provenance arrives."""
        state=self._candidate(deepcopy(candidate))
        if cut != self.transaction.cut:
            raise ValueError("semantic handler cut mismatches frozen transaction")
        name=unit.operation
        if name not in set(_OPERATIONS.values()):
            raise ValueError("unknown priced semantic operation")
        events=self._events_for(unit,scoped)
        if name=="episode_scan":
            selected=state.setdefault("selected_episode_refs",[])
            ref=unit.episode_refs[0]
            if ref in selected:
                raise ValueError("selected episode replayed twice in pass 1")
            selected.append(ref)
        elif name=="episode_replay":
            if len(unit.episode_refs)!=1 or not isinstance(unit.data,Mapping):
                raise ValueError("replay unit missing its episode identity")
            ref=unit.episode_refs[0]
            event_ref=unit.data.get("event_ref")
            item=next((e for e in events if e["event_id"]==event_ref),None)
            if item is None:
                raise ValueError("interleaved agenda references unexperienced event")
            replayed=state.setdefault("replayed_event_refs",[])
            if event_ref in replayed:
                raise ValueError("cannot replay physical event twice in one pass")
            replayed.append(event_ref)
            state.setdefault("private_replay_observations",[]).append({
                "episode_ref":ref,"event_ref":event_ref,
                "event_kind":item["kind"],
                "projection_digest":sha256_hex(canonical_causal_bytes(item)),
            })
        elif name=="rule_extraction":
            all_rules={r["id"]:r for r in state.get("hypotheses",[])}
            for rule_ref,item in self._extract_episode_rules(unit.episode_refs[0],events,cut):
                prior=all_rules.get(rule_ref)
                if prior is None:
                    all_rules[rule_ref]=item
                else:
                    prior["source_episode_refs"]=sorted(
                        set(prior["source_episode_refs"]+item["source_episode_refs"]))
                    prior["source_event_refs"]=sorted(
                        set(prior["source_event_refs"]+item["source_event_refs"]))
            state["hypotheses"]=[all_rules[k] for k in sorted(all_rules)]
        elif name=="skill_compilation":
            # The per-episode scan is charged. Only the final one assembles
            # aggregates from independent, verified plan-execution reports.
            visited=state.setdefault("_private_procedural_scanned",[])
            ref=unit.episode_refs[0]
            if ref in visited:
                raise ValueError("procedural evidence counted twice")
            visited.append(ref)
            if len(visited)==len(self.transaction.batch):
                state["procedural"] = self._merge_private_procedures(
                    state.get("procedural", []),
                    self._compile_from_proven_plans(cut),
                )
                state.pop("_private_procedural_scanned")
        elif name=="kappa_recalibration":
            # Stage8/9 autobiographical comparison lacks the independent
            # calibration_key, confidence bucket and verification identity.
            # No replay can infer those counters, and no oracle can supply
            # them. Carry existing calibrated form, requiring the canonical
            # Meta owner's verified rebase at commit.
            checked=state.setdefault("_private_kappa_scanned",[])
            ref=unit.episode_refs[0]
            if ref in checked:
                raise ValueError("duplicated calibration scan")
            checked.append(ref)
            if len(checked)==len(self.transaction.batch):
                state["kappa_recalibration_status"]="no_new_independent_verifications"
                state.pop("_private_kappa_scanned")
        elif name=="index_maintenance":
            if unit.episode_refs:
                raise ValueError("index maintenance must have no episode input")
            state["hypotheses"]=[
                item for item in state.get("hypotheses",[])
                if item["expires_at_step"]>cut.world_step
            ]
            state["indices"]={
                "hypothesis_by_primitive":{
                    key:sorted(row["id"] for row in state["hypotheses"]
                               if row["predicate"]["primitive"]==key)
                    for key in sorted({row["predicate"]["primitive"]
                                       for row in state["hypotheses"]})
                },
                "procedural_by_signature":{
                    key:sorted(row["id"] for row in state.get("procedural",[])
                               if row["plan_signature"]==key)
                    for key in sorted({row["plan_signature"]
                                       for row in state.get("procedural",[])})
                },
            }
            merged=set(state.get("consolidated_episode_refs",[]))
            merged.update(self.transaction.batch)
            state["consolidated_episode_refs"]=sorted(merged)
        return state

    def validate(self, state):
        if type(state) is not dict or not isinstance(state.get("forms"),dict):
            return False
        if any(not isinstance(k,str) for k in state):
            return False
        if any(rule.get("status")!="hypothese_causale"
               or rule.get("validated_for_safety") is not False
               or len(rule.get("source_event_refs",()))!=len(set(rule["source_event_refs"]))
               for rule in state.get("hypotheses",[])):
            return False
        if any(item.get("distinct_success_count",0)<self.policy.skill_success_threshold
               or not 0<=item.get("success_rate",-1)<=1
               for item in state.get("procedural",[])):
            return False
        try:
            canonical_causal_bytes(state)
        except (TypeError,ValueError):
            return False
        return True
