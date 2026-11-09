"""Run one I3 life: (code, genome, world spec, life seed) -> one exact history.

No retry, no reset, no action after death. The per-step trace is laboratory
custody (spec 'traceability'), hashed in a chain; the mind never reads it.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from hashlib import sha256
import json
import time

from i3.modules.body import CognitiveBudget, CognitiveWork
from i3.modules.genome import digest as genome_digest
from i3.runtime.provenance import build_manifest, digest
from i3.modules.mind import Mind
from i3.modules.world import World, WorldSpec

REPLAY_GATE_POLICIES = {"p13_replay_gate_v1": "gate",
                        "p13_replay_gate_zero_perceived_cost_v1": "zero_perceived_cost"}


def run_life(genome: dict, spec: WorldSpec, life_seed: int, horizon: int,
             *, keep_trace: bool = False,
             protocol: str = "UNREGISTERED_ENGINEERING",
             learning_mode: str = "normal",
             observer_mind_digest: bool = False,
             effect_readout: str = "full",
             observer_decision_diagnostics: bool = False,
             score_addend_mode: str = "normal",
             observer_resource_acquisition: bool = False,
             observer_full_competition: bool = False,
             decision_policy: str = "reference",
             admission=None) -> dict:
    started = time.perf_counter()
    if decision_policy not in (
            "reference", "local_information_v1", "reference_branch_memory_v1",
            "reference_opportunity_memory_v1",
            "reference_frontier_information_v1",
            "genomic_omega_frontier_information_v1",
            "personal_recurrence_candidate_g_v1",
            "personal_relevance_candidate_h_v1",
            "personal_shared_prior_candidate_i_v1",
            "personal_shared_prior_candidate_i_omega0_ablation_v1",
            "candidate_f_shadow_upper_cost_reference_controller_v1",
            *REPLAY_GATE_POLICIES):
        raise ValueError("unknown decision policy")
    admission_receipt = None
    if decision_policy in REPLAY_GATE_POLICIES:
        # ADR-0017/ADR-0019: a replay-gate life runs only with a guard-minted
        # ticket bound to this exact World; scientific cohorts fail closed in
        # the guard until an explicit owner lift.
        from i3.runtime.admission import verify as verify_admission
        admission_receipt = verify_admission(admission, spec.name)
    elif admission is not None:
        raise ValueError("admission tickets are only defined for replay-gate policies")
    if decision_policy != "reference" and (
            learning_mode != "normal" or effect_readout != "full" or
            score_addend_mode != "normal"):
        raise ValueError("experimental policy does not implement historical ablation modes")
    if learning_mode not in (
            "normal", "shadow_discard", "discard_effects",
            "discard_values", "discard_replay"):
        raise ValueError("unknown P4b/P5a learning intervention")
    if type(observer_mind_digest) is not bool:
        raise TypeError("observer_mind_digest must be bool")
    if type(observer_decision_diagnostics) is not bool:
        raise TypeError("observer_decision_diagnostics must be bool")
    if type(observer_resource_acquisition) is not bool:
        raise TypeError("observer_resource_acquisition must be bool")
    if type(observer_full_competition) is not bool:
        raise TypeError("observer_full_competition must be bool")
    if effect_readout not in (
            "full", "blind_predictions", "blind_action_predictions",
            "blind_sleep_forecast", "blind_sources", "blind_all",
            "action_agnostic_prior"):
        raise ValueError("unknown P5b effect readout")
    if score_addend_mode not in (
            "normal", "discard_curiosity_bonus", "discard_risk_penalty",
            "discard_both_bonus_terms"):
        raise ValueError("unknown P5c score addend intervention")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer horizon required")
    manifest = build_manifest(genome, spec, life_seed, horizon, protocol)
    if decision_policy in REPLAY_GATE_POLICIES:
        manifest["experimental_policy"] = {
            "name": decision_policy, "mode": REPLAY_GATE_POLICIES[decision_policy],
            "protocol": "STAGE2_REPLAY_GATE", "admission": admission_receipt}
    if decision_policy == "local_information_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy, "unknown": "stationary_zero_delta_v1",
            "episodic_partition": "half_td_half_effect_v1"}
    elif decision_policy == "reference_branch_memory_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "score": "P1.3_reference_unchanged",
            "branch_memory": "global18_recent_personal_effects_v1",
            "td_memory": "P1.3_unchanged"}
    elif decision_policy == "reference_opportunity_memory_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "score": "P1.3_reference_unchanged",
            "branch_memory": "global18_recent_personal_effects_v1",
            "opportunity_memory": "generic_onset_recurrence_latest3_v1",
            "opportunity_use": "STORAGE_ONLY_NOT_READ_BY_DECISION",
            "td_memory": "P1.3_unchanged"}
    elif decision_policy == "reference_frontier_information_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "score": "predicted_distress_with_paid_frontier_water_information_v1",
            "old_addends": "curiosity_relevance_prudence_removed",
            "branch_memory": "global18_recent_personal_effects_v1",
            "td_memory": "P1.3_unchanged",
            "frontier_belief": "i3-frontier-actionable-belief/v1",
            "frontier_scope": "one_generic_new_cell_water_only",
            "food_information": "NOT_IMPLEMENTED",
            "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
    elif decision_policy == "genomic_omega_frontier_information_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "score": "candidate_f_genomic_omega_first_contact_then_personal_frontier_v1",
            "old_addends": "curiosity_relevance_prudence_removed",
            "simulation_mode": "candidate_f",
            "projection_accounting": "event_local_quadratic4",
            "first_contact_expectation": "genome_v4_omega_recent_rms_v1",
            "first_contact_kernel": "one_future_water_opportunity_v1",
            "post_contact": "personal_frontier_information_omega_free_v1",
            "branch_memory": "global18_recent_personal_effects_v1",
            "td_memory": "P1.3_unchanged",
            "frontier_scope": "one_generic_new_cell_water_only",
            "food_information": "NOT_IMPLEMENTED",
            "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
    elif decision_policy == "personal_recurrence_candidate_g_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "scope": "DEVELOPMENT_PILOT_NOT_STAGE1_GATE",
            "score":
                "personal_recurrence_information_with_decision_local_candidate_f_projection_v1",
            "old_addends": "curiosity_relevance_prudence_removed",
            "persistent_simulation_mode": "reference",
            "persistent_projection_accounting": "chunk_end",
            "active_simulation_mode": "candidate_f",
            "active_projection_accounting": "event_local_quadratic4",
            "first_contact_expectation":
                "paid_personal_onset_recurrence_omega0",
            "post_contact": "personal_frontier_information_omega_free_v1",
            "branch_memory": "global18_recent_personal_effects_v1",
            "opportunity_memory": "generic_onset_recurrence_latest3_v1",
            "omega_use": "NONE",
            "td_memory": "P1.3_unchanged",
            "frontier_scope": "one_generic_new_cell_water_only",
            "food_information": "NOT_IMPLEMENTED",
            "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
    elif decision_policy == "personal_relevance_candidate_h_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "scope": "DEVELOPMENT_PILOT_NOT_STAGE1_GATE",
            "architecture":
                "paid_relevance_probe_then_complete_final_decision_v1",
            "stage_a":
                "detached_personal_relevance_probe_fully_paid",
            "relevant_final":
                "complete_candidate_f_geometry_from_post_probe_body",
            "fallback_final":
                "complete_P1.3_from_post_probe_body",
            "score_sharing": "NONE_DOUBLE_COMPUTATION_INTENTIONAL",
            "persistent_simulation_mode": "reference",
            "persistent_projection_accounting": "chunk_end",
            "first_contact":
                "personal_recurrence_strict_relevance_omega0",
            "post_contact":
                "personal_actionable_belief_top_effect_relevance",
            "omega_use": "NONE",
            "branch_memory": "global18_recent_personal_effects_v1",
            "opportunity_memory": "generic_onset_recurrence_latest3_v1",
            "td_memory": "P1.3_unchanged",
            "frontier_scope": "one_generic_new_cell_water_only",
            "food_information": "NOT_IMPLEMENTED",
            "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
    elif decision_policy == "personal_shared_prior_candidate_i_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "scope": "DEVELOPMENT_SOFTWARE_GATE_NOT_STAGE1_LIVE_GATE",
            "architecture":
                "shared_prior_relevance_then_shared_competition_control_v1",
            "first_contact_prior":
                "genome_v4_omega_recent_personal_rms_v1",
            "perceived_first_contact":
                "all_unsupported_direct_resource_trials_common_candidate_f_matrix_v1",
            "imagined_first_contact":
                "personal_recurrence_water_future_opportunity_shared_omega_v1",
            "relevant_final":
                "shared_P1.3_competition_action_control_over_candidate_f_scores",
            "fallback_final":
                "complete_P1.3_base_scores_discard_both_bonus_terms",
            "post_contact":
                "candidate_h_1163_semantics_unchanged",
            "persistent_simulation_mode": "reference",
            "persistent_projection_accounting": "chunk_end",
            "branch_memory": "global18_recent_personal_effects_v1",
            "opportunity_memory": "generic_onset_recurrence_latest3_v1",
            "omega_use": "UNSUPPORTED_FIRST_CONTACT_ONLY",
            "td_memory": "P1.3_unchanged",
            "motor_authority": "P1.3_COMPETITION_AND_ACTION_CONTROL",
        }
    elif decision_policy == "personal_shared_prior_candidate_i_omega0_ablation_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "scope": "DEVELOPMENT_60_61_SAME_GENOME_OMEGA0_CONTROL",
            "architecture":
                "shared_prior_relevance_then_shared_competition_control_v1",
            "candidate_class": "PersonalSharedPriorCandidateIMind",
            "native_genome_omega": genome["genes"]["omega"],
            "applied_first_contact_omega": 0.0,
            "omega_source": "SAME_GENOME_SOFTWARE_ABLATION",
            "omega_use": "UNSUPPORTED_FIRST_CONTACT_ONLY",
            "only_allowed_difference": "first_contact_omega_override_0.0",
            "fallback_final":
                "complete_P1.3_base_scores_discard_both_bonus_terms",
            "post_contact": "candidate_h_1163_semantics_unchanged",
            "persistent_simulation_mode": "reference",
            "persistent_projection_accounting": "chunk_end",
            "motor_authority": "P1.3_COMPETITION_AND_ACTION_CONTROL"}
    elif decision_policy == "candidate_f_shadow_upper_cost_reference_controller_v1":
        manifest["experimental_policy"] = {
            "name": decision_policy,
            "scope": "DEVELOPMENT_CAUSAL_FALSIFIER_NOT_STAGE1_GATE",
            "motor_authority": "P1.3_REFERENCE_ONLY",
            "decision_cost": "CANDIDATE_F_SHADOW_PLUS_P1.3_REFERENCE",
            "learning_cost":
                "P1.3_REFERENCE_PLUS_CANDIDATE_PRIVATE_STORE_IF_FUNDED",
            "cost_matching_claim": "UPPER_COST_NOT_EXACT_MATCH",
            "shadow_policy": "genomic_omega_frontier_information_v1",
            "shadow_common_state": "REALIGNED_TO_ACTUAL_P1.3_BEFORE_EACH_DECISION",
            "shadow_private_memory": "global18_recent_actual_P1.3_effects_v1",
            "reference_score": "P1.3_reference_unchanged"}
    manifest_id = digest(manifest)
    evidence_head = manifest_id
    totals = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
              for c in ("energy", "vigilance")}
    shortfall_steps = 0
    world = World(spec)
    resource_observer = None
    if observer_resource_acquisition:
        from i3.runtime.resource_observer import ResourceObserver
        resource_observer = ResourceObserver()
    mind_type = Mind
    mind_kwargs = {}
    if decision_policy == "local_information_v1":
        from i3.modules.information_mind import InformationMind
        mind_type = InformationMind
    elif decision_policy == "reference_branch_memory_v1":
        from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
        mind_type = ReferenceBranchMemoryMind
    elif decision_policy == "reference_opportunity_memory_v1":
        from i3.modules.reference_opportunity_memory_mind import (
            ReferenceOpportunityMemoryMind)
        mind_type = ReferenceOpportunityMemoryMind
    elif decision_policy == "reference_frontier_information_v1":
        from i3.modules.reference_frontier_information_mind import (
            ReferenceFrontierInformationMind)
        mind_type = ReferenceFrontierInformationMind
    elif decision_policy == "genomic_omega_frontier_information_v1":
        from i3.archive.stage1.modules.genomic_omega_frontier_information_mind import (
            GenomicOmegaFrontierInformationMind)
        mind_type = GenomicOmegaFrontierInformationMind
    elif decision_policy == "personal_recurrence_candidate_g_v1":
        from i3.archive.stage1.modules.personal_recurrence_candidate_g_mind import (
            PersonalRecurrenceCandidateGMind)
        mind_type = PersonalRecurrenceCandidateGMind
    elif decision_policy == "personal_relevance_candidate_h_v1":
        from i3.archive.stage1.modules.personal_relevance_candidate_h_mind import (
            PersonalRelevanceCandidateHMind)
        mind_type = PersonalRelevanceCandidateHMind
    elif decision_policy in (
            "personal_shared_prior_candidate_i_v1",
            "personal_shared_prior_candidate_i_omega0_ablation_v1"):
        from i3.archive.stage1.modules.personal_shared_prior_candidate_i_mind import (
            PersonalSharedPriorCandidateIMind)
        mind_type = PersonalSharedPriorCandidateIMind
        if decision_policy == (
                "personal_shared_prior_candidate_i_omega0_ablation_v1"):
            mind_kwargs["first_contact_omega_override"] = 0.0
    elif decision_policy == "candidate_f_shadow_upper_cost_reference_controller_v1":
        from i3.archive.stage1.modules.candidate_f_upper_cost_reference_controller import (
            CandidateFUpperCostReferenceController)
        mind_type = CandidateFUpperCostReferenceController
    elif decision_policy in REPLAY_GATE_POLICIES:
        from i3.modules.p13_replay_gate_mind import P13ReplayGateMind
        mind_type = P13ReplayGateMind
        mind_kwargs["mode"] = REPLAY_GATE_POLICIES[decision_policy]
    mind = mind_type(genome, life_seed, effect_readout=effect_readout,
                observer_decision_diagnostics=(observer_decision_diagnostics or
                                               observer_resource_acquisition or
                                               observer_full_competition),
                observer_full_competition=observer_full_competition,
                score_addend_mode=score_addend_mode,
                **mind_kwargs)
    head = sha256(json.dumps([genome_digest(genome), spec.name, life_seed, horizon],
                             separators=(",", ":")).encode()).hexdigest()
    trace = []
    competition_trace = [] if observer_full_competition else None
    actions: Counter = Counter()
    drinks = meals = 0
    first_drink = None
    elapsed = 0.0
    learning_updates = replays_done = inactive_steps = 0
    observer_counts = {
        "no_processing_budget": 0, "no_funded_score": 0,
        "control_rejected": 0, "action_admitted": 0,
        "offered_options": 0, "scored_options": 0,
        "rejected_controls": 0,
        "offered_families": {k: 0 for k in
            ("resource", "movement", "exploration", "rest")},
        "scored_families": {k: 0 for k in
            ("resource", "movement", "exploration", "rest")}}
    while world.t < horizon and not world.dead:
        t0 = time.perf_counter()
        allowance = CognitiveBudget(world.body, world.laws)
        capture = world.capture()
        action, param, work, info = mind.decide(capture, allowance)
        if competition_trace is not None:
            from i3.runtime.competition_observer import capture_competition
            competition_trace.append(capture_competition(
                info=info, action=action, param=param, work=work,
                allowed=allowance, capture=capture))
        pending_resource = (resource_observer.prepare(
            cap=capture, mind=mind, info=info, action=action, param=param)
            if resource_observer is not None else None)
        if observer_decision_diagnostics:
            diagnostic = info["observer"]
            observer_counts[diagnostic["decision_outcome"]] += 1
            for item in ("offered_options", "scored_options", "rejected_controls"):
                observer_counts[item] += diagnostic[item]
            for kind in ("offered_families", "scored_families"):
                for family, value in diagnostic[kind].items():
                    observer_counts[kind][family] += value
        if work != allowance.work:
            raise ValueError("declared decision bill does not match consumed allowance")
        result = world.step(action, param, work)
        before_learning = result["body"]
        learning = CognitiveBudget(before_learning, world.laws)
        replay_limit = None
        if not result["dead"] and mind.last is not None:
            # Included in the prepaid control block, not in a learning ablation.
            mind.observe_outcome(result)
            replay_limit = mind.prepare_learning(result, learning)
        if replay_limit is not None:
            post_audit = world.pay_cognition(learning.work)
            result["body"] = world.body
            # P4b: run exactly the prepaid outcome-model computation on
            # a detached mind, then discard its new learned state. The actual
            # mind still keeps ordinary perception, spatial beliefs and the
            # paid sensorimotor orientation update. No fictitious cognition
            # is billed: the shadow computation really executes.
            if learning_mode == "shadow_discard":
                from copy import deepcopy
                target = deepcopy(mind)
            else:
                target = mind
            # Development-only selective ablations: run the normal prepaid
            # computation first and restore only one targeted state component.
            # Costs are not manually adjusted, and paid sensorimotor/spatial
            # state is not rolled back.
            if learning_mode == "discard_effects":
                from copy import deepcopy
                preserved = deepcopy(mind.effects)
            elif learning_mode == "discard_values":
                preserved = [v[:] for v in mind.values]
            else:
                preserved = None
            replays = target.learn_from_outcome(
                result, replay_limit=replay_limit,
                replay_retention=(learning_mode != "discard_replay"))
            if learning_mode == "discard_effects":
                mind.effects = preserved
            elif learning_mode == "discard_values":
                mind.values = preserved
            if replays != replay_limit:
                raise RuntimeError("executed replay count differs from prepaid count")
            learning_updates += 1
            replays_done += replays
        else:
            post_audit = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
                          for c in totals}
        phases = {
            "decision": {"work": asdict(work), "accounting": result["cognitive_accounting"],
                         "body_before": list(allowance.body),
                         "body_after_debit": list(allowance.remaining)},
            "learning": {"work": asdict(learning.work), "accounting": post_audit,
                         "body_before": list(before_learning),
                         "body_after_debit": list(world.body)},
        }
        if resource_observer is not None:
            resource_observer.commit(
                pending_resource, world=world, physical_body=before_learning,
                dead=result["dead"], phases=phases)
        accounting = {c: {k: result["cognitive_accounting"][c][k] + post_audit[c][k]
                           for k in totals[c]} for c in totals}
        work = CognitiveWork(*(getattr(work, k) + getattr(learning.work, k)
                               for k in ("cycles", "simulated_steps", "memory_items", "replays")))
        shortfall_steps += any(accounting[c]["unpaid"] > 1e-12 for c in totals)
        for channel in totals:
            for key in totals[channel]:
                totals[channel][key] += accounting[channel][key]
        elapsed += time.perf_counter() - t0
        actions[action if action is not None else "physical_inactivity"] += 1
        inactive_steps += action is None
        if action == "boire":
            drinks += 1
            first_drink = first_drink or world.t
        elif action == "manger":
            meals += 1
        record = {"t": world.t, "action": action, "param": param,
                  "option": info["option"], "body": list(result["body"]),
                  "pos": list(world.pos), "dead": list(result["dead"])}
        head = sha256((head + json.dumps(record, separators=(",", ":"),
                                         sort_keys=True)).encode()).hexdigest()
        evidence_head = digest({"previous": evidence_head, "record": record,
                                "work": asdict(work), "accounting": accounting,
                                "funding_phases": phases})
        if keep_trace:
            record["cognitive_work"] = asdict(work)
            record["cognitive_accounting"] = accounting
            record["funding_phases"] = phases
            record["info"] = info
            trace.append(record)
    steps = world.t
    out = {
        "manifest": manifest, "manifest_id": manifest_id,
        "evidence_head": evidence_head,
        "cognitive_accounting": {"schema": "i3-cognitive-funding/v2",
                                 "totals": totals, "shortfall_steps": shortfall_steps,
                                 "pending_replays": 0, "pending_energy": 0.0,
                                 "pending_vigilance": 0.0,
                                 "learning_updates": learning_updates,
                                 "replays_executed": replays_done,
                                 "inactive_steps": inactive_steps,
                                 "status": "SETTLED_FOR_DECLARED_WORK"},
        "world": spec.name, "life_seed": life_seed, "horizon": horizon,
        "genome": genome_digest(genome),
        "steps_lived": steps,
        "terminal": "dead" if world.dead else "censored",
        "death_causes": list(world.dead),
        "drinks": drinks, "meals": meals, "first_drink_step": first_drink,
        "actions": dict(sorted(actions.items())),
        "final_body": [round(x, 6) for x in world.body],
        "mean_step_ms": round(1000.0 * elapsed / max(1, steps), 4),
        "trace_head": head,
    }
    if decision_policy in REPLAY_GATE_POLICIES:
        r_hat, m_hat, horizon_of_use = mind.gate_inputs()
        out["experimental_policy"] = dict(manifest["experimental_policy"])
        out["admission"] = dict(admission_receipt)
        out["replay_gate"] = {
            "mode": mind.replay_gate_mode,
            "decisions_total": mind.decisions_total,
            "audited_decisions": mind.audited_decisions,
            "relevant_decisions": mind.relevant_decisions,
            "sleep_steps_seen_by_gate": mind.sleep_steps,
            "final_r_hat": r_hat, "final_m_hat": m_hat, "final_H": horizon_of_use,
            "last_gate": mind.last_gate,
        }
    if decision_policy == "local_information_v1":
        out["experimental_policy"] = dict(manifest["experimental_policy"])
        out["personal_effect_memory"] = {
            "capacity": mind.personal._samples.maxlen,
            "retained": len(mind.personal._samples),
            "recorded": mind.personal_records,
            "td_capacity": mind.m_max,
            "td_retained": len(mind.buffer)}
        if observer_mind_digest:
            out["personal_outcomes_sha256"] = digest(
                [asdict(s) for s in mind.personal._samples])
    elif decision_policy in (
            "reference_branch_memory_v1", "reference_opportunity_memory_v1",
            "reference_frontier_information_v1",
            "genomic_omega_frontier_information_v1",
            "personal_recurrence_candidate_g_v1",
            "personal_relevance_candidate_h_v1",
            "personal_shared_prior_candidate_i_v1",
            "personal_shared_prior_candidate_i_omega0_ablation_v1",
            "candidate_f_shadow_upper_cost_reference_controller_v1"):
        out["experimental_policy"] = dict(manifest["experimental_policy"])
        out["branch_effect_memory"] = {
            "capacity": mind.branch_memory._samples.maxlen,
            "retained": len(mind.branch_memory._samples),
            "recorded": mind.branch_records,
            "td_capacity": mind.m_max,
            "td_retained": len(mind.buffer)}
        if decision_policy == "reference_opportunity_memory_v1":
            out["opportunity_recurrence_memory"] = {
                "schema": "i3-opportunity-recurrence-runtime-summary/v1",
                "recorded": mind.opportunity_records,
                "snapshot": mind.opportunity_memory.snapshot(),
                "decision_use": "STORAGE_ONLY_NOT_READ_BY_DECISION"}
        if decision_policy == "personal_recurrence_candidate_g_v1":
            if hasattr(mind, "first_contact_omega"):
                raise RuntimeError(
                    "Candidate-G runtime pilot acquired genomic omega")
            if (mind.simulation_mode, mind.projection_accounting) != (
                    "reference", "chunk_end"):
                raise RuntimeError(
                    "Candidate-G persistent projector leaked")
            out["opportunity_recurrence_memory"] = {
                "schema": "i3-opportunity-recurrence-runtime-summary/v1",
                "recorded": mind.opportunity_records,
                "snapshot": mind.opportunity_memory.snapshot(),
                "decision_use": "FIRST_CONTACT_PERSONAL_SUPPORT_ONLY"}
            out["frontier_information"] = {
                "scope": "one_generic_new_cell_water_only",
                "belief_queries": mind.frontier_belief_queries,
                "actionable_water_queries": mind.actionable_water_queries,
                "frontier_options_scored": mind.frontier_options_scored,
                "positive_information_options":
                    mind.positive_information_options,
                "first_contact_queries": mind.first_contact_queries,
                "first_contact_options_scored":
                    mind.first_contact_options_scored,
                "positive_first_contact_options":
                    mind.positive_first_contact_options,
                "post_contact_queries": mind.post_contact_queries,
                "recurrence_supported_decisions":
                    mind.recurrence_supported_decisions,
                "information_active_decisions":
                    mind.information_active_decisions,
                "reference_only_decisions":
                    mind.reference_only_decisions,
                "persistent_simulation_mode": mind.simulation_mode,
                "persistent_projection_accounting":
                    mind.projection_accounting,
                "omega_source": "NONE_PERSONAL_RECURRENCE_ONLY",
                "food_information": "NOT_IMPLEMENTED",
                "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
        if decision_policy == "personal_relevance_candidate_h_v1":
            if hasattr(mind, "first_contact_omega"):
                raise RuntimeError(
                    "Candidate-H runtime pilot acquired genomic omega")
            if (mind.simulation_mode, mind.projection_accounting) != (
                    "reference", "chunk_end"):
                raise RuntimeError(
                    "Candidate-H persistent projector leaked")
            out["opportunity_recurrence_memory"] = {
                "schema": "i3-opportunity-recurrence-runtime-summary/v1",
                "recorded": mind.opportunity_records,
                "snapshot": mind.opportunity_memory.snapshot(),
                "decision_use":
                    "FIRST_CONTACT_RELEVANCE_SUPPORT_ONLY"}
            out["candidate_h_relevance"] = {
                "schema": "i3-candidate-h-runtime-summary/v1",
                "probes": mind.relevance_probes,
                "probe_unfunded": mind.relevance_probe_unfunded,
                "candidate_f_final": mind.relevance_candidate_final,
                "p13_final": mind.relevance_reference_final,
                "persistent_simulation_mode": mind.simulation_mode,
                "persistent_projection_accounting":
                    mind.projection_accounting,
                "omega_source": "NONE_PERSONAL_ONLY",
                "score_sharing":
                    "NONE_DOUBLE_COMPUTATION_INTENTIONAL"}
        if decision_policy in (
                "personal_shared_prior_candidate_i_v1",
                "personal_shared_prior_candidate_i_omega0_ablation_v1"):
            if (mind.simulation_mode, mind.projection_accounting) != (
                    "reference", "chunk_end"):
                raise RuntimeError(
                    "Candidate-I persistent projector leaked")
            out["opportunity_recurrence_memory"] = {
                "schema": "i3-opportunity-recurrence-runtime-summary/v1",
                "recorded": mind.opportunity_records,
                "snapshot": mind.opportunity_memory.snapshot(),
                "decision_use":
                    "IMAGINED_FIRST_CONTACT_SUPPORT_AND_POSTCONTACT_STORAGE"}
            out["candidate_i"] = {
                "schema": "i3-candidate-i-runtime-summary/v1",
                "first_contact_decisions":
                    mind.candidate_i_first_contact_decisions,
                "relevant_final":
                    mind.candidate_i_relevant_final,
                "base_fallback_final":
                    mind.candidate_i_base_fallback_final,
                "probe_unfunded":
                    mind.candidate_i_probe_unfunded,
                "first_contact_omega":
                    mind.first_contact_omega,
                "omega_source":
                    mind.first_contact_omega_source,
                "persistent_simulation_mode":
                    mind.simulation_mode,
                "persistent_projection_accounting":
                    mind.projection_accounting,
                "post_contact":
                    "CANDIDATE_H_1163_UNCHANGED",
                "motor_authority":
                    "P1.3_COMPETITION_AND_ACTION_CONTROL"}
            if decision_policy == (
                    "personal_shared_prior_candidate_i_omega0_ablation_v1"):
                if mind.first_contact_omega != 0.0:
                    raise RuntimeError(
                        "Candidate-I omega0 runtime control leaked native omega")
                out["candidate_i"].update({
                    "native_genome_omega": genome["genes"]["omega"],
                    "applied_first_contact_omega": 0.0,
                    "omega_source": "SAME_GENOME_SOFTWARE_ABLATION",
                    "omega_ablation": "FIRST_CONTACT_ONLY_SAME_GENOME"})
        if decision_policy == "reference_frontier_information_v1":
            out["frontier_information"] = {
                "scope": "one_generic_new_cell_water_only",
                "belief_queries": mind.frontier_belief_queries,
                "actionable_water_queries": mind.actionable_water_queries,
                "frontier_options_scored": mind.frontier_options_scored,
                "positive_information_options": mind.positive_information_options,
                "food_information": "NOT_IMPLEMENTED",
                "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
        if decision_policy == "genomic_omega_frontier_information_v1":
            out["frontier_information"] = {
                "scope": "one_generic_new_cell_water_only",
                "belief_queries": mind.frontier_belief_queries,
                "actionable_water_queries": mind.actionable_water_queries,
                "frontier_options_scored": mind.frontier_options_scored,
                "positive_information_options": mind.positive_information_options,
                "first_contact_queries": mind.first_contact_queries,
                "first_contact_options_scored": mind.first_contact_options_scored,
                "positive_first_contact_options":
                    mind.positive_first_contact_options,
                "post_contact_queries": mind.post_contact_queries,
                "first_contact_omega": mind.first_contact_omega,
                "omega_use": "FIRST_CONTACT_ONLY_UNSUPPORTED_DRINK",
                "simulation_mode": mind.simulation_mode,
                "projection_accounting": mind.projection_accounting,
                "food_information": "NOT_IMPLEMENTED",
                "multi_cell_joint_outcomes": "NOT_IMPLEMENTED"}
        if decision_policy == "candidate_f_shadow_upper_cost_reference_controller_v1":
            out["candidate_f_cost_control"] = {
                "schema": "candidate_f_shadow_upper_cost_reference_controller_v1",
                "motor_authority": "P1.3_REFERENCE_ONLY",
                "decision_cost":
                    "CANDIDATE_F_SHADOW_PLUS_P1.3_REFERENCE",
                "learning_cost":
                    "P1.3_REFERENCE_PLUS_CANDIDATE_PRIVATE_STORE_IF_FUNDED",
                "cost_matching_claim": "UPPER_COST_NOT_EXACT_MATCH",
                "decisions": mind.decisions,
                "shadow_branch_commits": mind.shadow_branch_commits,
                "shadow_branch_retained": len(mind.branch_memory._samples),
                "shadow_first_contact_omega": mind.first_contact_omega,
                "shadow_first_contact_queries": mind.shadow.first_contact_queries,
                "shadow_frontier_options_scored":
                    mind.shadow.frontier_options_scored,
                "shadow_positive_information_options":
                    mind.shadow.positive_information_options,
                "common_state_authority": "P1.3_REFERENCE",
                "shadow_motor_authority": False}
        if observer_mind_digest:
            out["branch_outcomes_sha256"] = digest(
                [asdict(s) for s in mind.branch_memory._samples])
            if decision_policy in (
                    "reference_opportunity_memory_v1",
                    "personal_recurrence_candidate_g_v1",
                    "personal_relevance_candidate_h_v1",
                    "personal_shared_prior_candidate_i_v1"):
                out["opportunity_recurrence_sha256"] = digest(
                    mind.opportunity_memory.snapshot())
    if effect_readout != "full" or observer_decision_diagnostics:
        out["effect_readout"] = effect_readout
    if score_addend_mode != "normal" or observer_decision_diagnostics:
        out["score_addend_mode"] = score_addend_mode
    if observer_decision_diagnostics:
        out["observer_decision_diagnostics"] = dict(observer_counts)
    if resource_observer is not None:
        out["observer_resource_acquisition"] = resource_observer.report()
    if competition_trace is not None:
        out["observer_full_competition"] = {
            "schema": "i3-p5e-full-paid-competition/v1",
            "status": "DEVELOPMENT_ONLY_EXTERNAL_WITNESS",
            "steps": competition_trace}
    if learning_mode != "normal" or observer_mind_digest:
        out["learning_intervention"] = learning_mode
        # Component ablations retain the base outcome pipeline and discard
        # only one declared learned substate; only full shadow_discard drops
        # the entire outcome update. This counter is pipeline executions,
        # NOT proof each individual learned component survived.
        out["retained_outcome_learning_updates"] = (
            learning_updates if learning_mode != "shadow_discard" else 0)
        out["shadow_discarded_outcome_updates"] = (
            learning_updates if learning_mode == "shadow_discard" else 0)
    if observer_mind_digest:
        # Observer-only postmortem/life-end signature. Never enters Mind.decide.
        # Tokens and locations are internal, relative to this individual's
        # first-person history; no external world schedule is exposed.
        effects = [[list(k), v] for k, v in
                   sorted(mind.effects.stats.items(), key=lambda item: repr(item[0]))]
        spatial = [[list(pos), hist] for pos, hist in sorted(mind.hist.items())]
        out["outcome_model_sha256"] = digest({
            "values": mind.values, "effects": effects,
            "buffer": list(mind.buffer)})
        out["spatial_beliefs_sha256"] = digest({
            "hist": spatial,
            "map": [[list(pos), cell] for pos, cell in sorted(mind.map.items())]})
        out["observer_internal_position"] = list(mind.pos)
    out["evidence_head"] = digest({"previous": evidence_head,
                                   "terminal": out["terminal"],
                                   "accounting": out["cognitive_accounting"]})
    if keep_trace:
        out["trace"] = trace
    out["run_elapsed_ms"] = round(1000.0 * (time.perf_counter() - started), 4)
    return out
